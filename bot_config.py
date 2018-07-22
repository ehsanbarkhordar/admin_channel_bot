import os


class BotConfig:
    rows_per_query = int(os.environ.get('ROWS_PER_QUERY', None) or 50)
    max_retries = int(os.environ.get('MAX_RETRIES', None) or 3)
    check_interval = float(os.environ.get('CHECK_INTERVAL', None) or 0.5)
    time_sleep = float(os.environ.get('TIME_SLEEP', None) or 0.5)

    max_perform_check_failure = int(os.environ.get('MAX_PERFORM_CHECK_FAILURE', None) or 50)
    max_total_send_failure = int(os.environ.get('MAX_TOTAL_SEND_FAILURE', None) or 10)
    active_next_limit = int(os.environ.get('ACTIVE_NEXT_LIMIT', None) or 40)

    bot_token = os.environ.get('TOKEN', None) or "386f13d7a666aece40fc1c6612a85b63aead250f"
    bot_user_id = os.environ.get('USER_ID', None) or "41"

    admin_list = [{"user_id": "", "access_hash": ""}, {"user_id": "", "access_hash": ""}]
