from balebot.filters import TemplateResponseFilter, TextFilter, DefaultFilter, LocationFilter, PhotoFilter
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.messages import TemplateMessageButton, TextMessage, TemplateMessage
from db.db_handler import create_all_table, get_all_categories, get_category_by_name, \
    get_all_channels, get_channel_by_name, insert_content, insert_logo, Logo, Content, \
    get_logo_by_fileid_access_hash
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
        admin_panel(bot, update)
    else:
        user_panel(bot, update)


def admin_panel(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    btn_list = [
        TemplateMessageButton(text=TMessage.get_new_content, value=TMessage.get_new_content, action=0),
        TemplateMessageButton(text=TMessage.add_channel, value=TMessage.add_channel, action=0),
        TemplateMessageButton(text=TMessage.send_content, value=TMessage.send_content, action=0),
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


def user_panel(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
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
                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=TMessage.send_content),
                                                            choose_your_channel),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.send_content]))
def choose_your_channel(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()
    general_message = TextMessage(ReadyMessage.choose_your_channel)
    btn_list = []
    channel_list = get_all_channels()
    channel_name_list = []
    for channel in channel_list:
        channel_name_list.append(channel.name)
        btn_list += [TemplateMessageButton(text=channel.name, value=channel.name, action=0)]
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=channel_name_list),
                                                            get_post_channel),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def get_post_channel(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()

    post_channel_name = update.get_effective_message().text_message
    post_channel = get_channel_by_name(post_channel_name)

    dispatcher.set_conversation_data(update, "post_channel_id", post_channel.id)
    text_message = TextMessage(ReadyMessage.enter_channel_name)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            TextFilter(), get_channel_name),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_name(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()

    channel_name = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "channel_name", channel_name)

    text_message = TextMessage(ReadyMessage.enter_channel_nick_name)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            TextFilter(), get_channel_nick_name),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_nick_name(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()

    channel_nick_name = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "channel_nick_name", channel_nick_name)

    text_message = TextMessage(ReadyMessage.enter_channel_description)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            TextFilter(), get_channel_description),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_description(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()

    channel_description = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "channel_description", channel_description)

    general_message = TextMessage(ReadyMessage.choose_channel_category)
    category_list = get_all_categories()
    category_name_list = []
    btn_list = []
    for category in category_list:
        category_name_list.append(category.name)
        btn_list += [TemplateMessageButton(text=category.name, value=category.name, action=0)]
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=category_name_list),
                                                            get_channel_category),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_category(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()

    channel_category_name = update.get_effective_message().text_message
    channel_category = get_category_by_name(channel_category_name)
    dispatcher.set_conversation_data(update, "channel_category_id", channel_category.id)

    text_message = TextMessage(ReadyMessage.upload_channel_log)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            PhotoFilter(), get_channel_logo),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_logo(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    access_hash = user_peer.access_hash
    logo = update.get_effective_message()
    logo_obj = Logo(file_id=logo.file_id, access_hash=logo.access_hash, file_size=logo.file_size, thumb=logo.thumb)
    insert_logo(logo_obj)
    logo = get_logo_by_fileid_access_hash(logo.file_id, logo.access_hash)
    post_channel_id = dispatcher.get_conversation_data(update, "post_channel_id")
    channel_name = dispatcher.get_conversation_data(update, "channel_name")
    channel_nick_name = dispatcher.get_conversation_data(update, "channel_nick_name")
    channel_description = dispatcher.get_conversation_data(update, "channel_description")
    channel_category_id = dispatcher.get_conversation_data(update, "channel_category_id")
    content_obj = Content(channel_name=channel_name, channel_description=channel_description,
                          channel_nick_name=channel_nick_name,
                          category_id=channel_category_id, channel_logo_id=logo.id,
                          post_for_channel_id=post_channel_id,
                          user_id=user_id, access_hash=access_hash)
    insert_content(content_obj)
    text_message = TextMessage(ReadyMessage.upload_channel_log)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


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
