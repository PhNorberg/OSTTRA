from fastapi import FastAPI, Request
import asyncpg
import asyncio
from .api.messages import router as messages_router 

import logging 

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI()

app.include_router(messages_router)

@app.on_event("startup")
async def startup():
    retries = 5
    while retries > 0:
        try:
            app.state.pool = await asyncpg.create_pool(
                user='postgres',
                password='postgres123',
                database='postgres',
                host='db'
            )
            log.info("Connected to database")
            break   
        except Exception as e:
            log.info(f"Database connection failed: {e}. Trying again.")
            retries -= 1
            await asyncio.sleep(5)
    
    if retries == 0:
        log.error(f"Failed to connect to database after 5 retries. Giving up")

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

@app.get("/")
async def root():
    return {"Welcome to this Message service. Interact with it through the API endpoints found in the README!"}