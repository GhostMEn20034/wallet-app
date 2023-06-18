import fastapi
from client import db
from schemes import auth, dashboard
from dependencies import get_current_user
from services.dashboard import get_cash_flow, get_expense_structure
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

    primary_currency = user.get("primary_currency")

    conversion_rates = await get_conversion_rates(primary_currency)

    cash_flow = await get_cash_flow([account.get("_id") for account in accounts], filters.dict(), conversion_rates)
    expense_structure = await get_expense_structure([account.get("_id") for account in accounts], filters.dict(),
                                                    conversion_rates)

    return {
        "expense_structure": {"by_category": expense_structure[0].get("by_category"),
                              "total_expense": expense_structure[0].get("total_expense")},
        "primary_currency": primary_currency,
        "cash_flow": cash_flow,
    }
