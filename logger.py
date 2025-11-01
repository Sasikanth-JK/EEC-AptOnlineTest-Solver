import logging

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("EEC_AptOnlineTest_Solver")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

LOGGER = setup_logger()
LOGGER.info("Logger is set up.")