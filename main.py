import logging

from fastapi import FastAPI
from apps.core_dependency.redis_dependency import RedisDependency
from contextlib import asynccontextmanager

from apps.middleware.auth import SlidingTokenMiddleware
from apps.auth.router import router as auth_router

import uvicorn

redis_dependency = RedisDependency()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_dependency.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(SlidingTokenMiddleware)

app.include_router(auth_router)

logging.basicConfig(level=logging.DEBUG)

@app.get("/")
async def index():
    return {"status": "It's ALIVE!"}

uvicorn.run(app, host="0.0.0.0", port=8000)