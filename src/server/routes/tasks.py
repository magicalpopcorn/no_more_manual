import asyncio
import sys
import time
from datetime import datetime, timezone
from multiprocessing import Process

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.lib import logger
from src.server.db import sync_tasks_collection, tasks_collection
from src.server.models import TaskRecord, TaskRequest

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])
task_registry = {}  # keep track of running jobs


@router.post("")
async def run_task(request: TaskRequest):
    logger.debug(f"Received request\n{request}")

    # Insert task into MongoDB (initial state)
    task_record = TaskRecord(**request.model_dump())
    logger.debug(f"Created task record\n{task_record}")
    await tasks_collection.insert_one(task_record.model_dump(by_alias=True))

    proc = Process(target=execute_task, args=(task_record,), daemon=True)
    proc.start()

    task_registry[task_record.id] = proc

    return {"task_id": task_record.id, "status": "running", "log_file": logger.log_file}


@router.post("/{task_id}/stop")
async def stop_task(task_id: str):
    if task_id in task_registry:
        proc: Process = task_registry[task_id]
        logger.debug(f"Stopping task {task_id}, process: {proc}")
        if proc and proc.is_alive():
            proc.terminate()
            await tasks_collection.update_one(
                {"_id": task_id},
                {"$set": {"status": "stopped", "finished_at": datetime.now(timezone.utc)}},
            )
        return {"task_id": task_id, "status": "stopped"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")


def execute_task(request: TaskRecord):
    """
    Create and execute a new task asynchronously.
    Client sends only mode, instance_name, and tasks list.
    Server assigns UUID and manages lifecycle.
    """
    start_time = time.time()
    print("Starting import...")
    try:
        from src.lib import boot, logger, task
        from src.lib.agent.walker import Walker
        from src.lib.const import ActionMode
    except ImportError as e:
        print(f"Import error: {e}")
        sync_tasks_collection.update_one(
            {"_id": request.id},
            {"$set": {"status": "failed", "finished_at": datetime.now(timezone.utc)}},
        )
        sys.exit(1)
    else:
        import_time = time.time() - start_time
        print(f"Import time: {import_time:.4f} seconds")

    logger.setup_logger()
    logger.debug(f"log_file {logger.log_file}")
    # task is now running
    sync_tasks_collection.update_one(
        {"_id": request.id},
        {"$set": {"status": "running", "log_file": str(logger.log_file)}},
    )

    try:
        boot.init_instance(request.instance_name)

        action_mode = ActionMode(request.mode)
        walker = Walker()

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
        walker.execute(action_mode)
        # time.sleep(10)  # simulate long-running task
        logger.info("Finished !")
        sync_tasks_collection.update_one(
            {"_id": request.id},
            {"$set": {"status": "completed", "finished_at": datetime.now(timezone.utc)}},
        )

    except Exception:
        logger.exception("Exception in run_tool")
        sync_tasks_collection.update_one(
            {"_id": request.id},
            {"$set": {"status": "failed", "finished_at": datetime.now(timezone.utc)}},
        )
    finally:
        logger.info("Task ended")
