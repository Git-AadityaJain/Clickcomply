import datetime


def log_file_upload(file_name, file_format, file_size, status):
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    status_indicator = '[SUCCESS]' if status else '[FAILURE]'
    log_message = f"{current_time} {status_indicator} Uploaded file: '{file_name}' (Format: {file_format}, Size: {file_size} bytes)"
    print(log_message)
