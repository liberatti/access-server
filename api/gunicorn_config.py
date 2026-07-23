import fcntl
import os.path
import threading
import time
import traceback

import schedule
from nxcore.middleware.logging_manager import logger, LoggingManager

import config as _config
from api.tools.vpn_tool import VPNTool
from api.tools.firewall_tool import FirewallTool
from api.tasks import install_task

LoggingManager(loglevel=_config.LOGLEVEL)


try:
    import gevent.monkey

    gevent.monkey.patch_all()
except ImportError:
    pass


stop_event = threading.Event()

lock_handle = open(os.path.join(_config.DB_PATH, "as.lock"), "a+")

try:
    fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    logger.info("Lock acquired, AS is the main instance")
    is_main = True
except BlockingIOError:
    is_main = False


def _scheduler():
    while not stop_event.is_set():
        try:
            schedule.run_pending()
        except Exception as ex:
            traceback.print_exception(ex)
            logger.error(f"Error running scheduled task: {ex}")
        time.sleep(1)


def post_fork(server, worker):
    nxg_role = "worker"
    if is_main:
        nxg_role = "main"
        if not os.path.exists(f"{_config.DB_PATH}/app.duckdb"):
            install_task()
        VPNTool.start_service(wait=False)
        FirewallTool.create_firewall()
    # else:
    #    schedule.every(60).seconds.do(update_node_config)
    threading.Thread(target=_scheduler, daemon=True).start()
    logger.info(f"AS started as {nxg_role}")


def on_reload(server):
    global scheduler_started
    stop_event.set()
    scheduler_started = False


def on_exit(server):
    stop_event.set()
    logger.info("AS stopped")


workers = 1
worker_class = "gevent"
async_mode = "gevent"
preload_app = False
bind = "0.0.0.0:5000"
scheduler_started = False
accesslog = "-"
errorlog = "-"
loglevel = _config.LOGLEVEL
