import logging
import subprocess
import redis

from celery import shared_task
from django.conf import settings

from api.models import TestRunRequest, TestEnvironment


logger = logging.getLogger(__name__)
MAX_RETRY = 10

REDIS_CLIENT = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def handle_task_retry(instance: TestRunRequest, retry: int) -> None:
    if retry < MAX_RETRY:
        countdown = 2 ** retry
        logger.warning(f'Test Environment is busy, Retrying in {countdown}')
        instance.save_logs(logs=f"Failed to run tests on env {instance.env.name} retrying in {countdown} seconds.")
        instance.mark_as_retrying()
        execute_test_run_request.s(instance.id, retry + 1).apply_async(countdown=countdown)
    else:
        logger.error(
            f"Failed to run tests(ID:{instance.id}) on env {instance.env.name} after retrying {MAX_RETRY} times."
        )
        instance.save_logs(logs=f"Failed to run tests on env {instance.env.name} after retrying {MAX_RETRY} times.")
        instance.mark_as_failed_to_start()


@shared_task
def execute_test_run_request(instance_id: int, retry: int = 0) -> None:
    instance = TestRunRequest.objects.get(id=instance_id)
    
    LOCK_EXPIRE = settings.TEST_RUN_REQUEST_TIMEOUT_SECONDS + 1 # 1 second extra to Expire LOCK
    task_lock = REDIS_CLIENT.lock(f'lock_{__name__}.execute_test_run_request._{instance.env.name}', LOCK_EXPIRE)

    acquire_lock = lambda: task_lock.acquire(blocking=False)
    release_lock = lambda: task_lock.release()
  
    if not acquire_lock():
        handle_task_retry(instance, retry)
        return
    try:
        if instance.env.is_busy():
            handle_task_retry(instance, retry)
            return

        logger.info(f'{instance_id}-{instance.env.name} is free')
        env = TestEnvironment.objects.get(name=instance.env.name)
        env.lock()

        cmd = instance.get_command()


        logger.info(f'Running tests(ID:{instance_id}), CMD({" ".join(cmd)}) on env {instance.env.name}')
        instance.mark_as_running()
        initial_part = settings.TEST_BASE_CMD
        len_base_cmd = len(initial_part)

        commands = cmd[len_base_cmd:]

        result = 0
        for command in commands:
            run = subprocess.Popen(initial_part + [command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            result = result + run.wait(timeout=settings.TEST_RUN_REQUEST_TIMEOUT_SECONDS)
            instance.save_logs(logs=run.stdout.read())

        env.unlock()
        if result == 0:
            instance.mark_as_success()
        else:
            instance.mark_as_failed()
        logger.info(f'tests(ID:{instance_id}), CMD({" ".join(cmd)}) on env {instance.env.name} Completed successfully.')
    except Exception as e:
        logger.error(f'Unexpected fail on task execution: {e}')
        instance.mark_as_failed()
    finally:
        release_lock()