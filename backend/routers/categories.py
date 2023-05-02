import fastapi
from typing import List
from client import db
from dependencies import get_current_user
from schemes import auth
from schemes.categories import Category

router = fastapi.APIRouter(
    prefix='/categories',
    tags=['categories']
)


@router.get("/", response_model=List[Category])
async def get_categories(user_token: auth.UserId = fastapi.Depends(get_current_user)):
    categories = await db["categories"].find().to_list(50)
    return categories
