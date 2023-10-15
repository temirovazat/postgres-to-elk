import logging
from logging.handlers import RotatingFileHandler

FILE_SIZE = 50000000

logger = logging.getLogger('__main__')
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler('main.log', maxBytes=FILE_SIZE, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stdout_handler = logging.StreamHandler()
logger.addHandler(stdout_handler)
