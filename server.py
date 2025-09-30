#!python
# -*- coding: utf-8 -*-
import sys
import time
import uuid
from multiprocessing import Process
from typing import Dict, List

from fastapi import FastAPI

from src.server.models import TaskRequest

start_time = time.time()
print("Starting import...")
try:
    from src import boot, const, logger, task
    from src.agent.walker import Walker
    from src.const import ActionMode
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
else:
    import_time = time.time() - start_time
    print(f"Import time: {import_time:.4f} seconds")
    logger.info("Imports completed.")


app = FastAPI(title="RoK Automation", version="3.0.0")
task_registry: Dict[str, Dict] = {}  # keep track of running jobs

logger.setup_logger()


def execute_task(task_id: str, request: TaskRequest):
    """Wrapper to run your existing tool logic."""
    try:
        boot.init_instance(request.instance_name)

        action_mode = ActionMode(request.mode)
        walker = Walker(action_mode)

        # Register requested tasks
        if "farm_rss" in request.tasks:
            walker.register_task(task.Gather().gather)
        if "24h_boost" in request.tasks:
            walker.register_task(task.UseItems().use_24h_gather_boost)
        if "claim_alliance_resources" in request.tasks:
            walker.register_task(task.Collect().claim_alliance_rss)
        if "purchase_items" in request.tasks:
            walker.register_task(task.Collect().purchase_items)
        if "collect_info" in request.tasks:
            walker.register_task(task.Report().collect_info)

        logger.info(f"Running walker with mode={action_mode}, tasks={request.tasks}")
        walker.execute()
        logger.info("Finished !!!")

    except Exception:
        logger.exception("Exception in run_tool", stack_info=True)
    finally:
        logger.info("Task ended")


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/run_task")
async def run_task(request: TaskRequest):
    task_id = str(uuid.uuid4())
    logger.debug(f"Received task {task_id}\n{request}")

    task_registry[task_id] = {
        "mode": request.mode,
        "tasks": request.tasks,
        "running": True,
        "process": None,
    }

    proc = Process(target=execute_task, args=(task_id, request), daemon=True)
    proc.start()

    task_registry[task_id]["process"] = proc

    return {
        "status": "running",
        "task_id": task_id,
        "log_file": str(logger.LOG_FOLDER / "macro.log"),
    }


@app.post("/stop_task")
async def stop_task(task_id: str):
    if task_id in task_registry:
        proc = task_registry[task_id]["process"]
        logger.debug(f"Stopping task {task_id}, process: {proc}")
        if proc.is_alive():
            proc.terminate()  # ✅ force kill
            proc.join(timeout=1)
            task_registry[task_id]["running"] = False
            return {"status": "terminated", "task_id": task_id}
        return {"status": "already_stopped", "task_id": task_id}
    return {"status": "not_found", "task_id": task_id}


@app.get("/task_status")
async def task_status(task_id: str):
    if task_id in task_registry:
        proc = task_registry[task_id]["process"]
        running = proc.is_alive()
        task_registry[task_id]["running"] = running
        return {"task_id": task_id, "running": running}
    return {"task_id": task_id, "running": False}
