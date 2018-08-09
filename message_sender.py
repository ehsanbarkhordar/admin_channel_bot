# import ibm_db
import asyncio
import traceback
from datetime import datetime

from balebot.models.base_models import Peer
from balebot.models.constants.peer_type import PeerType
from balebot.models.messages import TextMessage, TemplateMessage, TemplateMessageButton, PhotoMessage
from balebot.utils.logger import Logger
from bot_config import BotConfig
from constant.message import ReadyMessage
from db.db_handler import db, get_unpublished_content, get_accept_content, get_category_by_id, get_logo_by_id


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

            if self.check_next and datetime.now().time() == datetime.strptime('6:00PM', '%I:%M%p') \
                    and self.database_handler.connect() and self.updater.network_connected():
                self.check_next = False
                stmt = get_accept_content()
                if stmt:
                    rows = stmt
                    if len(rows) == 0:
                        self.check_next = True
                    for row in rows:
                        category = get_category_by_id(row.category_id)
                        logo = get_logo_by_id(row.channel_logo_id)
                        text_message = TextMessage(ReadyMessage.request_content_text.format(row.channel_name,
                                                                                            row.channel_nick_name,
                                                                                            row.channel_description,
                                                                                            category.name))

                        photo_message = PhotoMessage(logo.file_id, logo.access_hash, "channel", logo.file_size,
                                                     "image/jpeg", None, 250,
                                                     250, file_storage_version=1,
                                                     caption_text=text_message)

                        self.bot.send_message(message=photo_message,
                                              peer=Peer(PeerType.group, peer_id=BotConfig.channel.get("channel_id"),
                                                        access_hash=BotConfig.channel.get("channel_access_hash")),
                                              )
                else:
                    self.check_next = True

            else:
                self.logger.debug("db connected: {}".format("ff", extra={"tag": "info"}))
                self.logger.debug(
                    "network connected: {}".format("dfd", extra={"tag": "info"}))
                self.logger.debug("check_next: {}".format(self.check_next), extra={"tag": "info"})

                self.perform_check_failure_counter += 1
                if self.perform_check_failure_counter > BotConfig.max_perform_check_failure:
                    self.perform_check_failure_counter = 0
                    self.logger.error("Err", extra={"tag": "err"})
                    quit(1)

            self.async_loop.call_later(BotConfig.check_interval, self.check)

    def start(self):
        self.database_handler.connect()
        self.check()
        self.logger.debug("start run", extra={"tag": "info"})

    def stop(self):
        self.running = False
        self.logger.warning("PollBank bot stoped", extra={"tag": "info"})

    # def unset_is_checked(self, messages_ids):
    #     if len(messages_ids) > 0:
    #
    #         update_where = ""
    #         for message_id in messages_ids:
    #             update_where += (" ID = {} OR".format(message_id))
    #         update_where = update_where[0:-2]
    #
    #         update_query = Queries.update_unset_is_checked.format(
    #             PollDatabaseConfig.message_table, update_where)
    #
    #         self.database_handler.query(update_query)
    #
    # def set_sent_messages_to_db(self, sent_ids):
    #
    #     if len(sent_ids) > 0:
    #         update_where = ""
    #         for message_id in sent_ids:
    #             update_where += (" ID = {} OR".format(message_id))
    #         update_where = update_where[0:-2]
    #
    #         update_query = Queries.update_set_is_sent.format(
    #             PollDatabaseConfig.message_table, update_where)
    #
    #         self.database_handler.query(update_query)
    #
    # def set_failed_messages_to_db(self, failed_ids):
    #
    #     if len(failed_ids) > 0:
    #
    #         update_where = ""
    #         for message_id in failed_ids:
    #             update_where += (" ID = {} OR".format(message_id))
    #         update_where = update_where[0:-2]
    #
    #         update_query = Queries.update_set_is_failed.format(
    #             PollDatabaseConfig.message_table, update_where)
    #
    #         self.database_handler.query(update_query)
    #
    # def send_success_callback(self, result, data):
    #     changed_check_flag = False
    #
    #     status = data.get("status", None)
    #
    #     message_id = status.message_id
    #     sent_ids = status.sent_ids
    #     failed_ids = status.failed_ids
    #     total_rows = status.total_rows
    #
    #     sent_ids.append(message_id)
    #
    #     if len(sent_ids) == PollConfig.active_next_limit:
    #         self.check_next = True
    #         changed_check_flag = True
    #
    #     if len(sent_ids) + len(failed_ids) == total_rows:
    #
    #         self.logger.warning("finish sending one pack of messages with success",
    #                             extra={"sent": len(sent_ids), "failure": len(failed_ids),
    #                                    "total": total_rows, "is_successful": False, "tag": "info"})
    #
    #         self.set_sent_messages_to_db(sent_ids=sent_ids)
    #         self.set_failed_messages_to_db(failed_ids=failed_ids)
    #
    #         if not changed_check_flag:
    #             self.check_next = True
    #
    # def send_failure_callback(self, result, data):
    #
    #     status = data.get("status", None)
    #
    #     user_phone_number = status.phone_number
    #     message_text = status.message_text
    #     message_id = status.message_id
    #     retry_number = status.retry_number
    #     sent_ids = status.sent_ids
    #     failed_ids = status.failed_ids
    #     total_rows = status.total_rows
    #
    #     if retry_number < PollConfig.max_retries:
    #         message = TextMessage(text=message_text)
    #         status.retry_number += 1
    #
    #         self.bot.send_message_by_phone(message=message,
    #                                        user_phone=user_phone_number,
    #                                        success_callback=self.send_success_callback,
    #                                        failure_callback=self.send_failure_callback,
    #                                        status=status)
    #     else:
    #         failed_ids.append(message_id)
    #
    #         self.logger.warning("sending message failed",
    #                             extra={"message_id": message_id, "is_successful": True, "tag": "err"})
    #
    #         if len(sent_ids) + len(failed_ids) == total_rows:
    #
    #             if len(failed_ids) == total_rows:
    #                 self.logger.warning("finish sending one pack of messages with failure",
    #                                     extra={"sent": len(sent_ids), "failure": len(failed_ids),
    #                                            "total": total_rows, "is_successful": False, "tag": "err"})
    #
    #                 # self.unset_is_checked(messages_ids=failed_ids)
    #                 self.set_failed_messages_to_db(failed_ids=failed_ids)
    #
    #                 self.updater.connect_network()
    #
    #                 self.total_send_failure_counter += 1
    #                 if self.total_send_failure_counter >= PollConfig.max_total_send_failure:
    #                     self.total_send_failure_counter = 0
    #                     self.logger.error(Error.poll_bank_problem, extra={"tag": "err"})
    #                     # quit(1)
    #
    #             else:
    #                 self.logger.warning("finish sending one pack of messages",
    #                                     extra={"sent": len(sent_ids), "failure": len(failed_ids),
    #                                            "total": total_rows, "is_successful": True, "tag": "info"})
    #
    #                 self.set_sent_messages_to_db(sent_ids=sent_ids)
    #                 self.set_failed_messages_to_db(failed_ids=failed_ids)
    #
    #             self.check_next = True
