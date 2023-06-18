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

    return cash_flow[0]


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
                }}
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

    return expense_structure
