from client import db
from services.currency_utils import get_conversion_rates
import datetime
import calendar


def first_and_last_days_of_the_month():
    year = datetime.date.today().year
    month = datetime.date.today().month

    first_day = datetime.datetime(year, month, 1)
    days_in_the_month = calendar.monthrange(year, month)[1]

    last_day = datetime.datetime(year, month, days_in_the_month)

    return first_day, last_day


async def get_cash_flow(account_ids, filters, conversion_rates):
    dates = first_and_last_days_of_the_month()
    start_date = filters.get("start_date") if filters.get("start_date") else dates[0]
    end_date = filters.get("end_date") if filters.get("end_date") else dates[1]

    pipeline = [
        {
            "$match": {
                "account_id": {"$in": account_ids},
                "created_at": {"$gt": start_date, "$lte": end_date},
                "record_type": {"$in": ["Expense", "Income"]}
            }
        },
        {
            "$lookup": {
                "from": "accounts",
                "localField": "account_id",
                "foreignField": "_id",
                "as": "account"
            }
        },
        {"$unwind": "$account"},
        {"$addFields": {
            "converted_amount": {
                "$round": [
                    {"$multiply": ["$amount", {"$divide": [1,
                                                           {"$arrayElemAt": [list(conversion_rates.values()), {
                                                               "$indexOfArray": [list(conversion_rates.keys()),
                                                                                 "$account.currency"]}]}]}]}, 2]
            }
        }},
        {"$group": {
            "_id": "$record_type",
            "total_amount": {"$sum": "$converted_amount"}
        }},
        {"$group": {
            "_id": None,
            "total_amount_income": {"$sum": {"$cond": [{"$eq": ["$_id", "Income"]}, "$total_amount", 0]}},
            "total_amount_expense": {"$sum": {"$cond": [{"$eq": ["$_id", "Expense"]}, "$total_amount", 0]}}
        }},
        {"$addFields": {
            "cash_flow_diff": {"$round": [{"$subtract": ["$total_amount_income", "$total_amount_expense"]}, 2]}
        }},
        {"$project": {
            "_id": 0,
            "total_amount_income": {"$round": ["$total_amount_income", 2]},
            "total_amount_expense": {"$round": ["$total_amount_expense", 2]},
            "cash_flow_diff": 1

        }}
    ]

    cash_flow = await db["records"].aggregate(pipeline).to_list(length=None)

    return cash_flow[0] if cash_flow else None


async def get_expense_structure(account_ids, filters, conversion_rates):
    dates = first_and_last_days_of_the_month()
    start_date = filters.get("start_date") if filters.get("start_date") else dates[0]
    end_date = filters.get("end_date") if filters.get("end_date") else dates[1]

    pipeline = [
        {
            "$match": {
                "account_id": {"$in": account_ids},
                "created_at": {"$gt": start_date, "$lte": end_date},
                "record_type": "Expense"
            }
        },
        {
            "$lookup": {
                "from": "accounts",
                "localField": "account_id",
                "foreignField": "_id",
                "as": "account"
            }
        },
        {"$unwind": "$account"},
        {
            "$addFields": {
                "converted_amount": {
                    "$round": [{"$multiply": ["$amount",
                                              {"$divide": [1, {"$arrayElemAt": [list(conversion_rates.values()),
                                                                                {"$indexOfArray": [list(
                                                                                    conversion_rates.keys()),
                                                                                    "$account.currency"]}]}]}]}, 2]
                }
            }
        },
        {"$facet": {
            "by_category": [
                {"$group": {
                    "_id": "$category",
                    "total_amount": {"$sum": "$converted_amount"}
                }},
                {"$sort": {"total_amount": 1}}
            ],
            "total_expense": [
                {"$group": {
                    "_id": None,
                    "total_expense": {"$sum": "$converted_amount"}
                }},
                {"$project": {
                    "_id": 0,
                    "total_expense": {"$round": ["$total_expense", 2]}
                }}
            ]
        }},
        {"$project": {
            "by_category": 1,
            "total_expense": {"$first": "$total_expense.total_expense"}
        }}
    ]

    expense_structure = await db["records"].aggregate(pipeline).to_list(length=None)

    final_result = {"by_category": expense_structure[0].get("by_category"),
                    "total_expense": expense_structure[0].get("total_expense")} if expense_structure[0].get(
        "total_expense") else None

    print(final_result.get("by_category"))
    return final_result


async def get_balance_by_currencies(account_ids):
    pipeline = [
        {"$match": {
            "_id": {"$in": account_ids},
        }},
        {"$group": {
            "_id": "$currency",
            "balance_by_currency": {"$sum": "$balance"}
        }},
        {"$sort": {"balance_by_currency": 1}},
        {"$project": {
            "_id": 1,
            "balance_by_currency": {"$round": ["$balance_by_currency", 2]}
        }}
    ]

    balance_by_currencies = await db["accounts"].aggregate(pipeline).to_list(length=None)

    return balance_by_currencies


async def get_account_sum(account_ids, conversion_rates):
    pipeline = [
        {"$match": {
            "_id": {"$in": account_ids}
        }},
        {"$addFields": {
            "converted_balance": {
                "$round": [{"$multiply": ["$balance",
                                          {"$divide": [1, {"$arrayElemAt": [list(conversion_rates.values()),
                                                                            {"$indexOfArray": [list(
                                                                                conversion_rates.keys()),
                                                                                "$currency"]}]}]}]}, 2]
            }
        }},
        {"$group": {
            "_id": None,
            "account_sum": {"$sum": "$converted_balance"}
        }},
        {"$project": {
            "_id": 0,
            "account_sum": {"$round": ["$account_sum", 2]}
        }}
    ]

    account_sum = await db["accounts"].aggregate(pipeline).to_list(length=None)

    return account_sum[0] if account_sum else None


async def get_last_five_records(account_ids, filters):
    dates = first_and_last_days_of_the_month()
    start_date = filters.get("start_date") if filters.get("start_date") else dates[0]
    end_date = filters.get("end_date") if filters.get("end_date") else dates[1]

    pipeline = [
        {"$match": {
            "account_id": {"$in": account_ids},
            "created_at": {"$gt": start_date, "$lte": end_date},
        }},
        {
            "$lookup": {
                "from": "accounts",
                "localField": "account_id",
                "foreignField": "_id",
                "as": "account"
            }
        },
        {"$unwind": "$account"},
        {"$addFields": {
            "account_name": "$account.name",
            "account_currency": "$account.currency",
            "account_color": "$account.color",
        }},
        {"$sort": {"created_at": -1}},
        {"$limit": 5}
    ]

    last_records = await db["records"].aggregate(pipeline).to_list(length=None)

    return last_records if last_records else None
