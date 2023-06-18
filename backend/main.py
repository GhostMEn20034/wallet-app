from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, auth, accounts, records, verify_user, categories, currencies, dashboard
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(records.router)
app.include_router(verify_user.router)
app.include_router(categories.router)
app.include_router(currencies.router)
app.include_router(dashboard.router)


@app.get('/test')
async def test():
    return {"status": "OK"}
