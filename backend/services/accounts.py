from client import db
from services.currency_utils import get_conversion_rates
from services.get_current_dates import get_current_dates


async def get_accounts(user_id, primary_currency, reverse: bool, sort_by="name"):
    conversion_rates = await get_conversion_rates(primary_currency) if sort_by == "balance" else {}
    # conversion_rates = {"USD": 1, "UAH": 36.8}
    pipeline = [
        {
            "$match": {
                "user.id": user_id
            }
        },
        {
            "$project": {
                "name": 1,
                "balance": {"$round": ["$balance", 2]},
                "bank_account": 1,
                "currency": 1,
                "color": 1,
                "created_at": 1,
                "converted_balance": {
                    "$round": [
                        {"$multiply": ["$balance", {"$divide": [conversion_rates[primary_currency],
                                                                {"$arrayElemAt": [list(conversion_rates.values()), {
                                                                    "$indexOfArray": [list(conversion_rates.keys()),
                                                                                      "$currency"]}]}]}]}, 2]
                } if sort_by == "balance" else None
            }
        },
        {
            "$sort": {"converted_balance": -1 if reverse else 1} if sort_by == "balance" else {
                sort_by: -1 if reverse else 1}
        }
    ]

    accounts = await db["accounts"].aggregate(pipeline).to_list(50)
    return accounts


async def get_account(user_id, account_id):
    dates = get_current_dates()

    pipeline = [
        {
            "$match": {
                "user.id": user_id,
                "_id": account_id
            }
        },
        {
            '$lookup': {
                'from': 'balanceTrend',
                'localField': '_id',
                'foreignField': 'account_id',
                'as': 'balanceTrend'
            }
        },
        {
            '$addFields': {
                # use the datetimes from the function to filter the balanceTrend documents
                'current_period': {
                    '$let': {
                        'vars': {
                            'filtered_balanceTrend': {
                                '$filter': {
                                    'input': '$balanceTrend',
                                    'as': 'item',
                                    'cond': {
                                        '$and': [
                                            {
                                                '$gte': [
                                                    '$$item.date',
                                                    dates['thirty_days_ago']
                                                ]
                                            },
                                            {
                                                '$lte': [
                                                    '$$item.date',
                                                    dates['end_of_current_day']
                                                ]
                                            },
                                            # {
                                            #     '$eq': [
                                            #         '$$item.initial',
                                            #         False
                                            #     ]
                                            # }
                                        ]
                                    }
                                }
                            }
                        },
                        'in': {
                            '$cond': {
                                'if': {'$eq': ['$$filtered_balanceTrend', []]},
                                'then': [
                                    {
                                        '$arrayElemAt': [
                                            '$balanceTrend',
                                            -1
                                        ]
                                    }
                                ],
                                'else': '$$filtered_balanceTrend'
                            }
                        }
                    }
                },
                'past_period': {
                    '$let': {
                        'vars': {
                            'filtered_balanceTrend': {
                                '$filter': {
                                    'input': '$balanceTrend',
                                    'as': 'item',
                                    'cond': {
                                        '$and': [
                                            {
                                                '$gte': [
                                                    '$$item.date',
                                                    dates['sixty_days_ago']
                                                ]
                                            },
                                            {
                                                '$lt': [
                                                    '$$item.date',
                                                    dates['thirty_days_ago']
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        },
                        'in': {
                            '$cond': {
                                'if': {'$eq': ['$$filtered_balanceTrend', []]},
                                'then': [
                                    {
                                        '$arrayElemAt': [
                                            '$balanceTrend',
                                            {
                                                '$indexOfArray': [
                                                    '$balanceTrend.date',
                                                    {
                                                        '$min': '$balanceTrend.date'
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ],
                                'else': '$$filtered_balanceTrend'
                            }
                        }
                    },
                }

            }
        },
        {"$addFields": {
            "current_period": {
                "$sortArray": {
                    "input": "$current_period",
                    "sortBy": {"date": 1}
                }
            },
            "percentage_change": {
                "$let": {
                    "vars": {
                        "last_current": {"$last": "$current_period"},
                        'last_past': {
                            '$arrayElemAt':
                                ['$past_period', -1]
                        },
                    },
                    "in": {
                        "$round": [
                            {'$multiply': [
                                {'$divide': [
                                    {'$subtract':
                                        ['$$last_current.balance', '$$last_past.balance']}, '$$last_past.balance']
                                 },
                                100]
                            }, 2]
                    }
                }
            },
        }},
        {'$project':
            {'balanceTrend': 0,
             'past_period': 0}
         }
    ]

    account = await db["accounts"].aggregate(pipeline).to_list(length=None)
    return account[0]
