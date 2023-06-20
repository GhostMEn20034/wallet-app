import fastapi
from client import db

router = fastapi.APIRouter(
    prefix='/currencies'
)


@router.get("/")
async def get_currencies():
    return await db["currencies"].find().sort("code", 1).to_list(length=None)
