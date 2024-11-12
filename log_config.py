import logging

logging.basicConfig(
    filename='service_logs.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_logger(name):
    return logging.getLogger(name)