import textwrap
import logging
import errno
import os


def indent(text, amount, ch=' '):
    return textwrap.indent(text, amount*ch)


def get_common_logger(format, filename):
    logging.basicConfig(level=logging.DEBUG,
                        format=format,
                        filename=filename,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    global_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(global_formatter)
    logging.getLogger().addHandler(console)
    return logging


def get_logger(log_path, level, label, formatter=None):
    try:
        os.makedirs(os.path.dirname(log_path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    handler = logging.FileHandler(log_path, mode='w')
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger = logging.getLogger(label)
    logger.addHandler(handler)
    return logger
