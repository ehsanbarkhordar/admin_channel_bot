from balebot.filters import TemplateResponseFilter, TextFilter, DefaultFilter, LocationFilter
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.messages import TemplateMessageButton, TextMessage, TemplateMessage, JsonMessage
from db.db_handler import create_all_table, get_all_categories, get_category_by_name, get_logo_by_id
from balebot.updater import Updater
from balebot.utils.logger import Logger
from bot_config import BotConfig
from constant.message import ReadyMessage, TMessage, LogMessage, Regex
import asyncio

updater = Updater(token=BotConfig.bot_token,
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

my_logger = Logger.logger
create_all_table()


def success(response, user_data):
    user_data = user_data['kwargs']
    user_peer = user_data["user_peer"]
    my_logger.info(LogMessage.success_send_message, extra={"user_id": user_peer.peer_id, "tag": "info"})


def failure(response, user_data):
    user_data = user_data['kwargs']
    user_peer = user_data["user_peer"]
    try_times = int(user_data["try_times"])
    message = user_data["message"]
    if try_times < BotConfig.max_total_send_failure:
        try_times += 1
        my_logger.error(LogMessage.fail_send_message, extra={"user_id": user_peer.peer_id, "tag": "error"})
        kwargs = {"message": message, "user_peer": user_peer, "try_times": try_times}
        bot.send_message(message, user_peer, success_callback=success, failure_callback=failure, kwargs=kwargs)
    else:
        my_logger.error(LogMessage.max_fail_retried, extra={"tag": "error"})


def is_admin(user_id):
    for admin in BotConfig.admin_list:
        if admin.get("user_id") == user_id:
            return True
    return False


@dispatcher.message_handler(
    filters=[TemplateResponseFilter(keywords=[TMessage.start, TMessage.back]), TextFilter(keywords="start")])
def start_conversation(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    if is_admin(user_id):
        btn_list = [
            TemplateMessageButton(text=TMessage.get_new_content, value=TMessage.get_new_content, action=0),
            TemplateMessageButton(text=TMessage.add_channel, value=TMessage.add_channel, action=0),
            TemplateMessageButton(text=TMessage.send_content, value=TMessage.send_content, action=0),
            TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]
    else:
        btn_list = [TemplateMessageButton(text=TMessage.send_content, value=TMessage.send_content, action=0),
                    TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]
    general_message = TextMessage(ReadyMessage.start_conversation)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    my_logger.info(LogMessage.info, extra={"user_id": user_id, "tag": "info"})
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        CommandHandler("info", info),
                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=TMessage.send_content),
                                                            choose_your_channel),

                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=TMessage.info),
                                                            info)
                                                        ])


@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.send_content]))
def choose_your_channel(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()

    general_message = TextMessage(ReadyMessage.choose_your_channel)
    btn_list = []
    channel_list = [{"name": "کانال آموزش قرآن", "user_id": 2, "access_hash": 32153},
                    {"name": "کانال آموزش زبان", "user_id": 2, "access_hash": 32153}]
    for channel in channel_list:
        btn_list += [TemplateMessageButton(text=channel.get("name"), value=channel.get("name"), action=0)]

    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)

    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        CommandHandler("info", info),
                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=TMessage.back),
                                                            start_conversation),
                                                        MessageHandler(TextFilter(), info)])


@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.info]))
def info(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    general_message = TextMessage(ReadyMessage.information)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    my_logger.info(LogMessage.info, extra={"user_id": user_id, "tag": "info"})
    dispatcher.finish_conversation(update)


updater.run()
