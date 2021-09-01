import sys
import logging

def init_logger(log_path):
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setLevel(logging.DEBUG)
	stdout_handler.setFormatter(formatter)

	file_handler = logging.FileHandler(log_path)
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(formatter)

	logger.addHandler(file_handler)
	logger.addHandler(stdout_handler)

	return logger
