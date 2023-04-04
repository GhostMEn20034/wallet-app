from fastapi import FastAPI
from routers import users, auth, accounts, records

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(records.router)
