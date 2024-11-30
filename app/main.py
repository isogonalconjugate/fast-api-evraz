# app/main.py

from fastapi import FastAPI
from app.api.v1.endpoints.router import router as api_router
from app.core.logger import logger

app = FastAPI(title="Code Analyzer")

@app.on_event("startup")
async def startup_event():
    logger.info("Приложение запущено.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Приложение остановлено.")

app.include_router(api_router, prefix="/api/v1")
