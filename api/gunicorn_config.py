import fcntl
import os.path
import threading
import time
import traceback

import schedule
from nxcore.middleware.logging_manager import logger, LoggingManager

import config as _config
from api.tasks import install_task, update_task
from api.tools.vpn_tool import VPNTool
from api.tools.firewall_tool import FirewallTool

LoggingManager(loglevel=_config.LOGLEVEL)

stop_event = threading.Event()


def _scheduler():
    """
    Background loop that runs scheduled tasks.
    """
    while not stop_event.is_set():
        try:
            schedule.run_pending()
        except Exception as ex:
            traceback.print_exception(ex)
            logger.error(f"Error running scheduled task: {ex}")
        time.sleep(1)


def when_ready(server):
    """
    Gunicorn hook called when the server is ready to handle requests.
    Initializes the database and schedules periodic tasks.

    Args:
        server: The Gunicorn server instance.
    """
    global scheduler_started
    if scheduler_started:
        return
    scheduler_started = True
    os.makedirs(_config.DB_PATH, exist_ok=True)
    lock_file = os.path.join(_config.DB_PATH, "app.sqlite.lock")
    with open(lock_file, "a+") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            __override_existing = False
            if not os.path.exists(os.path.join(_config.DB_PATH, "app.sqlite")):
                install_task()
                __override_existing = True
            update_task(override_existing=__override_existing)
            schedule.every(6).hours.do(update_task)

            if VPNTool.is_initialized():
                VPNTool.start_service(wait=False)
                FirewallTool.create_firewall()

            logger.info("Main task scheduled.")
        except BlockingIOError:
            logger.info("Initialization skipped: lock held by another worker.")
            return
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
            os.unlink(lock_file)
    threading.Thread(target=_scheduler, daemon=True).start()
    logger.info("IPXa started.")


def on_reload(server):
    """
    Gunicorn hook called before reloading the server.
    Stops the scheduler and restarts it after reloading.

    Args:
        server: The Gunicorn server instance.
    """
    global scheduler_started
    stop_event.set()
    scheduler_started = False
    when_ready(server)


def on_exit(server):
    """
    Gunicorn hook called when the server is exiting.
    Stops the background scheduler.

    Args:
        server: The Gunicorn server instance.
    """
    stop_event.set()
    logger.info("IPXa stopped")


workers = _config.WORKERS
threads = _config.THREADS
preload_app = False
bind = "0.0.0.0:5000"
scheduler_started = False
accesslog = "-" if _config.LOGLEVEL in ["DEBUG", "INFO"] else None
errorlog = "-"
loglevel = _config.LOGLEVEL
