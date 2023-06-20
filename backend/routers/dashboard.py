import fastapi
from client import db
from schemes import auth, dashboard
from dependencies import get_current_user
from services.dashboard import (get_cash_flow,
                                get_expense_structure,
                                get_balance_by_currencies,
                                get_account_sum,
                                get_last_five_records)
from services.currency_utils import get_conversion_rates

router = fastapi.APIRouter(
    prefix='/dashboard',
    tags=['dashboard'],
)


@router.get("/")
async def get_statistic(user_token: auth.UserId = fastapi.Depends(get_current_user),
                        filters: dashboard.DashboardFilter = fastapi.Depends(dashboard.DashboardFilter)):
    user = await db["users"].find_one({"_id": user_token.id})
    accounts = await db["accounts"].find({"user_id": user_token.id}).to_list(length=None)

    account_ids = [account.get("_id") for account in accounts] if not filters.account_id else [filters.account_id]

    primary_currency = user.get("primary_currency")

    conversion_rates = await get_conversion_rates(primary_currency)

    cash_flow = await get_cash_flow(account_ids, filters.dict(), conversion_rates)
    expense_structure = await get_expense_structure(account_ids, filters.dict(),
                                                    conversion_rates)
    balance_by_currencies = await get_balance_by_currencies(account_ids)

    account_sum = await get_account_sum(account_ids, conversion_rates)
    last_records = await get_last_five_records(account_ids, filters.dict())

    return {
        "primary_currency": primary_currency,
        "cash_flow": cash_flow,
        "expense_structure": expense_structure,
        "balance_by_currencies": balance_by_currencies,
        "dashboard": {"account_sum": account_sum.get("account_sum") if account_sum else None,
                      "cash_flow": cash_flow.get("cash_flow_diff") if cash_flow else None,
                      "spending": expense_structure.get(
                          "total_expense") if expense_structure else None},
        "last_records": last_records
    }
