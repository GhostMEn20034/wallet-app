from fastapi import FastAPI
from routers import user, auth, account

app = FastAPI()
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(account.router)
