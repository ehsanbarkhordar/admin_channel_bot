import asyncio
from datetime import datetime

from balebot.models.base_models import Peer
from balebot.models.constants.peer_type import PeerType
from balebot.models.messages import TextMessage, PhotoMessage
from balebot.utils.logger import Logger
from bot_config import BotConfig
from constant.message import ReadyMessage, LogMessage
from db.db_handler import db, get_accept_content, get_category_by_id, get_logo_by_id, \
    change_is_sent


class MessageSender:
    def __init__(self):

        self.logger = Logger.get_logger()
        self.async_loop = asyncio.get_event_loop()
        self.my_bot = None
        self.bot = None
        self.dispatcher = None
        self.updater = None
        self.database_handler = db

        self.check_next = True
        self.running = True

        self.perform_check_failure_counter = 0
        self.total_send_failure_counter = 0

    def check(self):
        if self.running:
            now = datetime.now().time()
            now_hour = now.hour
            if self.check_next and BotConfig.stop_publish_hour >= now_hour >= BotConfig.start_publish_hour \
                    and self.database_handler.connect() and self.updater.network_connected():
                self.check_next = False
                stmt = get_accept_content()
                if stmt:
                    rows = stmt
                    if len(rows) == 0:
                        self.check_next = True

                    def send_message(id_index, loop):
                        if id_index >= len(rows):
                            self.check_next = True
                            return 0
                        row = rows[id_index]
                        category = get_category_by_id(row.category_id)
                        logo = get_logo_by_id(row.channel_logo_id)
                        text_message = TextMessage(ReadyMessage.request_content_text.format(row.channel_name,
                                                                                            row.channel_nick_name,
                                                                                            row.channel_description,
                                                                                            category.name))
                        photo_message = PhotoMessage(logo.file_id, logo.access_hash, "channel", logo.file_size,
                                                     "image/jpeg", None, 250,
                                                     250, file_storage_version=1, caption_text=text_message)
                        user_peer = Peer(PeerType.group, peer_id=BotConfig.channel.get("channel_id"),
                                         access_hash=BotConfig.channel.get("channel_access_hash"))
                        kwargs = {"message": text_message, "content_id": row.id, "user_peer": user_peer, "try_times": 1}
                        self.bot.send_message(message=photo_message, peer=user_peer,
                                              success_callback=self.success_sent_message,
                                              failure_callback=self.failure_sent_message, kwargs=kwargs)
                        id_index += 1
                        loop.call_later(BotConfig.send_delay, send_message, id_index, loop)

                    my_send_loop = asyncio.get_event_loop()
                    my_send_loop.call_soon(send_message, 0, my_send_loop)
                else:
                    self.check_next = True
            else:
                self.logger.debug("db connected: {}".format("ff", extra={"tag": "info"}))
                self.logger.debug(
                    "network connected: {}".format("dfd", extra={"tag": "info"}))
                self.logger.debug("check_next: {}".format(self.check_next), extra={"tag": "info"})

            self.async_loop.call_later(BotConfig.check_interval, self.check)

    def start(self):
        self.database_handler.connect()
        self.check()
        self.logger.debug("start run", extra={"tag": "info"})

    def stop(self):
        self.running = False
        self.logger.warning("PollBank bot stoped", extra={"tag": "info"})

    def success_sent_message(self, response, user_data):
        user_data = user_data['kwargs']
        user_peer = user_data["user_peer"]
        content_id = user_data["content_id"]
        change_is_sent(content_id, "1")
        self.logger.info(LogMessage.success_send_message, extra={"user_id": user_peer.peer_id, "tag": "info"})

    def failure_sent_message(self, response, user_data):
        user_data = user_data['kwargs']
        user_peer = user_data["user_peer"]
        content_id = user_data["content_id"]
        try_times = int(user_data["try_times"])
        message = user_data["message"]
        if try_times < BotConfig.max_total_send_failure:
            try_times += 1
            self.logger.error(LogMessage.fail_send_message, extra={"user_id": user_peer.peer_id, "tag": "error"})
            kwargs = {"message": message, "content_id": content_id, "user_peer": user_peer, "try_times": try_times}
            self.bot.send_message(message, user_peer, success_callback=self.success_sent_message,
                                  failure_callback=self.failure_sent_message, kwargs=kwargs)
        else:
            change_is_sent(content_id, "2")
            self.logger.error(LogMessage.max_fail_retried, extra={"tag": "error"})
