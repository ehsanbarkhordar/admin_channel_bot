import re

from balebot.filters import TemplateResponseFilter, TextFilter, DefaultFilter, LocationFilter, PhotoFilter
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.base_models import Peer
from balebot.models.constants.peer_type import PeerType
from balebot.models.messages import TemplateMessageButton, TextMessage, TemplateMessage, PhotoMessage
from db.db_handler import create_all_table, get_all_categories, get_category_by_name, \
    insert_content, insert_logo, Logo, Content, \
    get_logo_by_fileid_access_hash, insert_category, Category, get_unpublished_content, get_category_by_id, \
    get_logo_by_id, change_publish_status, change_description, get_content_by_id, Type, insert_type, get_all_type, \
    get_type_by_name
from balebot.updater import Updater
from balebot.utils.logger import Logger
from bot_config import BotConfig
from constant.message import ReadyMessage, TMessage, LogMessage, Regex
import asyncio

from message_sender import MessageSender
from utils.utils import eng_to_arabic_number, arabic_to_eng_number

updater = Updater(token=BotConfig.bot_token,
                  loop=asyncio.get_event_loop())
bot = updater.bot
dispatcher = updater.dispatcher

my_logger = Logger.logger
create_all_table()

post_sender = MessageSender()
post_sender.bot = bot
post_sender.updater = updater
post_sender.dispatcher = dispatcher
post_sender.logger = my_logger
post_sender.start()


def success(response, user_data):
    user_data = user_data['kwargs']
    user_peer = user_data["user_peer"]
    my_logger.info(LogMessage.success_send_message, extra={"user_id": user_peer.peer_id, "tag": "info"})


def start_again(response, user_data):
    user_data = user_data['kwargs']
    peer = user_data["user_peer"]
    update = user_data["update"]
    my_logger.info(LogMessage.success_send_message, extra={"user_id": peer.peer_id, "tag": "info"})
    start_conversation(bot, update)


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
    user_id = str(user_id)
    for admin in BotConfig.admin_list:
        if admin.get("user_id") == user_id:
            return True
    return False


# ============================================== Start Conversation ===================================================
@dispatcher.message_handler(
    filters=[TemplateResponseFilter(keywords=[TMessage.start, TMessage.back]), TextFilter(keywords="start")])
def start_conversation(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    if is_admin(user_id):
        admin_panel(bot, update)
    else:
        user_panel(bot, update)


# ============================================== Admin Panel ===================================================
def admin_panel(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    if not is_admin(user_id):
        return 0
    btn_list = [
        TemplateMessageButton(text=TMessage.get_sent_content, value=TMessage.get_sent_content, action=0),
        TemplateMessageButton(text=TMessage.add_category, value=TMessage.add_category, action=0),
        TemplateMessageButton(text=TMessage.add_type, value=TMessage.add_type, action=0),
        TemplateMessageButton(text=TMessage.send_content, value=TMessage.send_content, action=0),
        TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]
    general_message = TextMessage(ReadyMessage.start_conversation)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.get_sent_content]))
def get_sent_content(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    if not is_admin(user_id):
        return 0
    unpublished_content = get_unpublished_content()
    if not unpublished_content:
        text_message = TextMessage(ReadyMessage.no_new_content_recently)
        kwargs = {"update": update, "message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=start_again, failure_callback=failure,
                         kwargs=kwargs)
        return 0
    for content in unpublished_content:
        btn_list = [
            TemplateMessageButton(text=TMessage.accept,
                                  value=TMessage.accept + " - " + eng_to_arabic_number(content.id), action=0),
            TemplateMessageButton(text=TMessage.reject,
                                  value=TMessage.reject + " - " + eng_to_arabic_number(content.id), action=0),
            TemplateMessageButton(text=TMessage.accept_with_edit,
                                  value=TMessage.accept_with_edit + " - " + eng_to_arabic_number(content.id),
                                  action=0)]
        category = get_category_by_id(content.category_id)
        logo = get_logo_by_id(content.channel_logo_id)
        text_message = TextMessage((ReadyMessage.request_content_text.format(content.channel_name,
                                                                             content.channel_description,
                                                                             category.name,
                                                                             content.channel_nick_name,
                                                                             content.channel_nick_name)))
        photo_message = PhotoMessage(logo.file_id, logo.access_hash, "channel", logo.file_size, "image/jpeg", None, 250,
                                     250, file_storage_version=1, caption_text=text_message)

        template_message = TemplateMessage(general_message=photo_message, btn_list=btn_list)
        kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
    dispatcher.finish_conversation(update)


@dispatcher.message_handler(
    TemplateResponseFilter(keywords=[TMessage.accept, TMessage.reject, TMessage.accept_with_edit]))
def add_or_reject_content(bot, update):
    user_peer = update.get_effective_user()
    message_text = update.get_effective_message().text_message
    message = message_text.split("-")
    action = message[0]
    action = action.rstrip()
    action = action.lstrip()
    content_id = message[1]
    content_id = content_id.rstrip()
    content_id = content_id.lstrip()
    content_id = arabic_to_eng_number(content_id)
    dispatcher.set_conversation_data(update, "content_id", content_id)
    content = get_content_by_id(content_id)
    if content.is_sent != 0:
        text_message = TextMessage(ReadyMessage.channel_sent_before)
        kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
        return 0
    client_peer = Peer(PeerType.user, peer_id=content.user_id, access_hash=content.access_hash)
    if action == TMessage.accept:
        change_publish_status(content_id, "1")
        text_message = TextMessage(ReadyMessage.accept_content.format(content.channel_name, content.channel_nick_name))
        kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
        client_text_message = TextMessage(
            ReadyMessage.accept_content_client.format(content.channel_name, content.channel_nick_name))
        kwargs = {"message": client_text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(client_text_message, client_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
    elif action == TMessage.reject:
        change_publish_status(content_id, "-1")
        text_message = TextMessage(ReadyMessage.reject_content.format(content.channel_name, content.channel_nick_name))
        kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
        client_text_message = TextMessage(
            ReadyMessage.reject_content_client.format(content.channel_name, content.channel_nick_name))
        kwargs = {"message": client_text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(client_text_message, client_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
    elif action == TMessage.accept_with_edit:
        change_publish_status(content_id, "2")
        text_message = TextMessage(
            ReadyMessage.replace_description.format(content.channel_name, content.channel_nick_name))
        kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
        client_text_message = TextMessage(
            ReadyMessage.accept_content_with_edit_client.format(content.channel_name, content.channel_nick_name))
        kwargs = {"message": client_text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(client_text_message, client_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(TextFilter(), replace_description),
                                                        MessageHandler(TemplateResponseFilter(
                                                            keywords=[TMessage.accept, TMessage.reject,
                                                                      TMessage.accept_with_edit]),
                                                            add_or_reject_content),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def replace_description(bot, update):
    user_peer = update.get_effective_user()
    new_description = update.get_effective_message().text
    content_id = dispatcher.get_conversation_data(update, "content_id")
    change_description(content_id, new_description)
    change_publish_status(content_id, "1")
    text_message = TextMessage(ReadyMessage.replace_description_success_fully)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Add Category ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.add_category]))
def get_category_name(bot, update):
    user_peer = update.get_effective_user()
    text_message = TextMessage(ReadyMessage.enter_category_name)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(TextFilter(), add_category),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def add_category(bot, update):
    user_peer = update.get_effective_user()
    category_name = update.get_effective_message().text
    new_category = Category(name=category_name)
    result = insert_category(new_category)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
        return 0
    if result == ReadyMessage.duplicated_category:
        text_message = TextMessage(ReadyMessage.duplicated_category)
        kwargs = {"update": update, "message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=start_again, failure_callback=failure,
                         kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.category_added_successfully.format(category_name))
    kwargs = {"update": update, "message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=start_again, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Add type ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.add_type]))
def get_type_name(bot, update):
    user_peer = update.get_effective_user()
    text_message = TextMessage(ReadyMessage.enter_type_name)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(TextFilter(), add_type),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def add_type(bot, update):
    user_peer = update.get_effective_user()
    type_name = update.get_effective_message().text
    new_type = Type(name=type_name)
    result = insert_type(new_type)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure,
                         kwargs=kwargs)
        return 0
    if result == ReadyMessage.duplicated_type:
        text_message = TextMessage(ReadyMessage.duplicated_type)
        kwargs = {"update": update, "message": text_message, "user_peer": user_peer, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=start_again, failure_callback=failure,
                         kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.type_added_successfully.format(type_name))
    kwargs = {"update": update, "message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=start_again, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== User Panel ===================================================
def user_panel(bot, update):
    user_peer = update.get_effective_user()
    btn_list = [TemplateMessageButton(text=TMessage.send_content, value=TMessage.send_content, action=0),
                TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]
    general_message = TextMessage(ReadyMessage.start_conversation)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=TMessage.send_content),
                                                            send_content),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.send_content]))
def send_content(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()
    general_message = TextMessage(ReadyMessage.choose_content_type)
    types_list = get_all_type()
    type_name_list = []
    btn_list = []
    for type in types_list:
        type_name_list.append(type.name)
        btn_list += [TemplateMessageButton(text=type.name, value=type.name, action=0)]
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TemplateResponseFilter(keywords=type_name_list), get_content_type),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_type(bot, update):
    user_peer = update.get_effective_user()
    content_type_name = update.get_effective_message().text
    content_type = get_type_by_name(content_type_name)
    dispatcher.set_conversation_data(update, "content_type_id", content_type.id)
    text_message = TextMessage(ReadyMessage.enter_content_name)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), get_content_name),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_name(bot, update):
    user_peer = update.get_effective_user()
    channel_name = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "channel_name", channel_name)
    text_message = TextMessage(ReadyMessage.enter_content_nick_name)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), get_channel_nick_name),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_nick_name(bot, update):
    user_peer = update.get_effective_user()
    channel_nick_name = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "channel_nick_name", channel_nick_name)
    text_message = TextMessage(ReadyMessage.enter_content_description)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), get_channel_description),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_description(bot, update):
    user_peer = update.get_effective_user()
    channel_description = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "channel_description", channel_description)
    general_message = TextMessage(ReadyMessage.choose_content_category)
    category_list = get_all_categories()
    category_name_list = []
    btn_list = []
    for category in category_list:
        category_name_list.append(category.name)
        btn_list += [TemplateMessageButton(text=category.name, value=category.name, action=0)]
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TemplateResponseFilter(keywords=category_name_list), get_channel_category),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_category(bot, update):
    user_peer = update.get_effective_user()
    channel_category_name = update.get_effective_message().text_message
    channel_category = get_category_by_name(channel_category_name)
    dispatcher.set_conversation_data(update, "channel_category_id", channel_category.id)
    text_message = TextMessage(ReadyMessage.upload_content_log)
    kwargs = {"message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success, failure_callback=failure, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(PhotoFilter(), get_channel_logo),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_channel_logo(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    access_hash = user_peer.access_hash
    logo = update.get_effective_message()
    logo_obj = Logo(file_id=logo.file_id, access_hash=logo.access_hash, file_size=logo.file_size, thumb=logo.thumb)
    insert_logo(logo_obj)
    logo = get_logo_by_fileid_access_hash(logo.file_id, logo.access_hash)
    channel_name = dispatcher.get_conversation_data(update, "channel_name")
    channel_description = dispatcher.get_conversation_data(update, "channel_description")
    channel_nick_name = dispatcher.get_conversation_data(update, "channel_nick_name")
    channel_category_id = dispatcher.get_conversation_data(update, "channel_category_id")
    content_type_id = dispatcher.get_conversation_data(update, "content_type_id")
    content_obj = Content(channel_name=channel_name, channel_description=channel_description,
                          channel_nick_name=channel_nick_name,
                          category_id=channel_category_id, channel_logo_id=logo.id,
                          user_id=user_id, access_hash=access_hash, type_id=content_type_id)
    insert_content(content_obj)
    text_message = TextMessage(ReadyMessage.success_send_content)
    kwargs = {"update": update, "message": text_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=start_again, failure_callback=failure, kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Info ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.info]))
def info(bot, update):
    user_peer = update.get_effective_user()
    btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    general_message = TextMessage(ReadyMessage.information)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "user_peer": user_peer, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success, failure_callback=failure,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Default ===================================================
@dispatcher.message_handler(DefaultFilter())
def default(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    if is_admin(user_id):
        admin_panel(bot, update)
    else:
        user_panel(bot, update)


updater.run()
