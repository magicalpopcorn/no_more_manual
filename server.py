#!python
# -*- coding: utf-8 -*-
import sys
import time
import uuid
from multiprocessing import Process
from typing import Dict, List

from fastapi import FastAPI

from src.lib import logger
from src.server.routes import accounts, characters, tasks

app = FastAPI(title="RoK Automation", version="3.0.0")
task_registry: Dict[str, Dict] = {}  # keep track of running jobs

logger.setup_logger()
# Register routers (resource-based)
app.include_router(characters.router)
app.include_router(accounts.router)
app.include_router(tasks.router)


@app.get("/api/v1/healthcheck")
async def healthcheck():
    return {"status": "ok"}
