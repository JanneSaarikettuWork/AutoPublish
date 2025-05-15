import logging
import logging.handlers

def setup_logging(logger, log_file):

    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # file_handler = logging.FileHandler(log_file)
    
    # Create a rotating file handler with a maximum size of 512 KB and 10 backup files
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=512*1024, backupCount=10)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter with the levelname limited to 3 characters and add them to handlers
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname).3s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # # Examples
    # logger.debug("This is a debug message")
    # logger.info("This is an info message")
    # logger.warning("This is a warning message")
    # logger.error("This is an error message")
    # logger.critical("This is a critical message")