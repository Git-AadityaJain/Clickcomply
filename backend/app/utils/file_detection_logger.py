from app.core.logging import logger


def log_file_detection(filename, file_format, file_size):
    logger.info(f'✅ FILE_DETECTED: {filename} ({file_format} format, {file_size})')


def log_file_storage(stored_path):
    logger.info(f'✅ FILE_STORED: {stored_path}')
