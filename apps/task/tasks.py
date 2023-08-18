from celery import shared_task
from .execute import run_task
from celery.utils.log import get_logger

logger = get_logger(__name__)


@shared_task()
def run_task_job(task_id: int, params: dict, plan_id: str):
    run_task(task_id, params, plan_id)
    logger.info("异步任务执行结束")
