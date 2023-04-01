from dotenv import load_dotenv
import motor.motor_asyncio
import os

load_dotenv(".env")


client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("URL"))
db = client.wallet


# loop = client.get_io_loop()
# loop.run_until_complete(do_find_one())
