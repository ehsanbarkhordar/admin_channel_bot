import os
from datetime import datetime


class BotConfig:
    rows_per_query = int(os.environ.get('ROWS_PER_QUERY', None) or 3)
    max_retries = int(os.environ.get('MAX_RETRIES', None) or 3)
    check_interval = float(os.environ.get('CHECK_INTERVAL', None) or 0.5)
    time_sleep = float(os.environ.get('TIME_SLEEP', None) or 0.5)

    max_perform_check_failure = int(os.environ.get('MAX_PERFORM_CHECK_FAILURE', None) or 5)
    max_total_send_failure = int(os.environ.get('MAX_TOTAL_SEND_FAILURE', None) or 10)
    active_next_limit = int(os.environ.get('ACTIVE_NEXT_LIMIT', None) or 40)

    bot_token = os.environ.get('TOKEN', None) or "1f9610ea2f56c115f880fc602a729ea09aecee53"
    bot_user_id = os.environ.get('USER_ID', None) or "41"

    send_delay = float(os.environ.get('SEND_DELAY', None) or 2)
    start_publish_hour = int(os.environ.get('START_PUBLISH_HOUR', None) or "18")
    stop_after = int(os.environ.get('STOP_AFTER', None) or "0")
    stop_publish_hour = start_publish_hour + stop_after

    admin_list = [{"user_id": "1428351868", "access_hash": "-2295479097333507622"},
                  {"user_id": "1188642847", "access_hash": "-4703513440482963863"},
                  {"user_id": "201707397", "access_hash": "-2163233886830599507"},
                  {"user_id": "1458898994", "access_hash": "-5085852276019395860"}]
    channel = {"name": "کانال تستی", "channel_id": "24335167", "channel_access_hash": "1766074642907138471"}
