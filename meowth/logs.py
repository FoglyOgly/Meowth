import sys
import logging
import logging.handlers

def init_loggers():
    # d.py stuff
    dpy_logger = logging.getLogger("discord")
    dpy_logger.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    dpy_logger.addHandler(console)

    # Meowth

    logger = logging.getLogger("meowth")

    meowth_format = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(meowth_format)
    logger.setLevel(logging.INFO)

    logfile_path = 'logs/meowth.log'
    fhandler = logging.handlers.RotatingFileHandler(
        filename=str(logfile_path), encoding='utf-8', mode='a',
        maxBytes=400000, backupCount=20)
    fhandler.setFormatter(meowth_format)

    logger.addHandler(fhandler)

    # logger.addHandler(stdout_handler)

    return logger