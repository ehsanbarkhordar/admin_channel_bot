import os
from datetime import datetime


class BotConfig:
    rows_per_query = int(os.environ.get('ROWS_PER_QUERY', 3))
    max_retries = int(os.environ.get('MAX_RETRIES', 3))
    check_interval = float(os.environ.get('CHECK_INTERVAL', 0.5))
    time_sleep = float(os.environ.get('TIME_SLEEP', 0.5))
    max_perform_check_failure = int(os.environ.get('MAX_PERFORM_CHECK_FAILURE', 5))
    max_total_send_failure = int(os.environ.get('MAX_TOTAL_SEND_FAILURE', 10))
    active_next_limit = int(os.environ.get('ACTIVE_NEXT_LIMIT', 40))
    bot_token = os.environ.get('TOKEN', "41b8be7154997607cbd78cc0d36bbbed86def470")
    send_delay = float(os.environ.get('SEND_DELAY', 2))
    start_publish_hour = int(os.environ.get('START_PUBLISH_HOUR', 19))
    stop_after = int(os.environ.get('STOP_AFTER', "1"))
    stop_publish_hour = start_publish_hour + stop_after
    admin_list = ["1428351868", "1188642847", "201707397", "1458898994"]
    channel = {"name": "کانال تستی", "channel_id": "24335167", "channel_access_hash": "1766074642907138471"}
