import re

from balebot.filters import TemplateResponseFilter, TextFilter, DefaultFilter, PhotoFilter
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.base_models import Peer
from balebot.models.constants.peer_type import PeerType
from balebot.models.messages import TemplateMessageButton, TextMessage, TemplateMessage, PhotoMessage
from db.db_handler import create_all_table, get_all_categories, get_category_by_name, \
    insert_content, insert_logo, Logo, Content, \
    get_logo_by_fileid_access_hash, insert_category, Category, get_unpublished_content, get_category_by_id, \
    get_logo_by_id, change_publish_status, change_description, get_content_by_id, Type, insert_type, get_all_type, \
    get_type_by_name, change_logo
from balebot.updater import Updater
from balebot.utils.logger import Logger
from bot_config import BotConfig
from constant.message import ReadyMessage, TMessage, LogMessage, Regex
import asyncio

from message_sender import MessageSender
from utils.utils import eng_to_arabic_number, arabic_to_eng_number

updater = Updater(token=BotConfig.bot_token, loop=asyncio.get_event_loop())
dispatcher = updater.dispatcher

my_logger = Logger.logger
create_all_table()

post_sender = MessageSender()
post_sender.bot = dispatcher.bot
post_sender.updater = updater
post_sender.dispatcher = dispatcher
post_sender.logger = my_logger
post_sender.start()


def success_send_message(response, user_data):
    kwargs = user_data['kwargs']
    update = kwargs["update"]
    user_peer = update.get_effective_user()
    my_logger.info(LogMessage.success_send_message, extra={"user_id": user_peer.peer_id, "tag": "info"})


def failure_send_message(response, user_data):
    kwargs = user_data['kwargs']
    bot = kwargs["bot"]
    message = kwargs["message"]
    update = kwargs["update"]
    try_times = int(kwargs["try_times"])
    if try_times < BotConfig.max_total_send_failure:
        try_times += 1
        user_peer = update.get_effective_user()
        my_logger.error(LogMessage.fail_send_message, extra={"user_id": user_peer.peer_id, "tag": "error"})
        kwargs = {"message": message, "update": update, "bot": bot, "try_times": try_times}
        bot.respond(update=update, message=message, success_callback=success_send_message,
                    failure_callback=failure_send_message, kwargs=kwargs)
    else:
        my_logger.error(LogMessage.max_fail_retried, extra={"tag": "error"})


def success_send_message_and_start_again(response, user_data):
    kwargs = user_data['kwargs']
    update = kwargs["update"]
    bot = kwargs["bot"]
    user_peer = update.get_effective_user()
    my_logger.info(LogMessage.success_send_message, extra={"user_id": user_peer.peer_id, "tag": "info"})
    start_conversation(bot, update)


def is_admin(user_id):
    user_id = str(user_id)
    for admin in BotConfig.admin_list:
        if admin.get("user_id") == user_id:
            return True
    return False


# ============================================== Start Conversation ===================================================
@dispatcher.message_handler(
    filters=[TemplateResponseFilter(keywords=[TMessage.start, TMessage.back]), TextFilter(keywords="start"),
             DefaultFilter()])
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
        TemplateMessageButton(text=TMessage.request_content, value=TMessage.request_content, action=0),
        TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]
    general_message = TextMessage(ReadyMessage.start_conversation)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message,
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
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message,
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
        logo = get_logo_by_id(content.logo_id)
        text_message = TextMessage((ReadyMessage.request_content_text.format(content.name,
                                                                             content.description,
                                                                             category.name,
                                                                             content.nick_name,
                                                                             content.nick_name)))
        photo_message = PhotoMessage(logo.file_id, logo.access_hash, "channel", logo.file_size, "image/jpeg", None, 250,
                                     250, file_storage_version=1, caption_text=text_message)

        template_message = TemplateMessage(general_message=photo_message, btn_list=btn_list)
        kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(template_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
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
    client_peer = Peer(PeerType.user, peer_id=content.user_id, access_hash=content.access_hash)
    dispatcher.set_conversation_data(update, "client_peer", client_peer)
    if content.is_sent != 0:
        text_message = TextMessage(ReadyMessage.content_sent_before)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    if action == TMessage.accept:
        change_publish_status(content_id, "1")
        text_message = TextMessage(ReadyMessage.accept_content.format(content.name, content.nick_name))
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        client_text_message = TextMessage(
            ReadyMessage.accept_content_client.format(content.name, content.nick_name))
        kwargs = {"message": client_text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(client_text_message, client_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    elif action == TMessage.reject:
        change_publish_status(content_id, "-1")
        btn_list = [TemplateMessageButton(text=TMessage.no_reason, value=TMessage.no_reason, action=0)]
        general_message = TextMessage(
            ReadyMessage.reject_content.format(content.name, content.nick_name))
        template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
        kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(template_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        dispatcher.register_conversation_next_step_handler(
            update, [CommandHandler("start", start_conversation),
                     MessageHandler(TextFilter(), reject_reason),
                     MessageHandler(TemplateResponseFilter(keywords=[TMessage.accept, TMessage.reject,
                                                                     TMessage.accept_with_edit]),
                                    add_or_reject_content),
                     MessageHandler(DefaultFilter(), start_conversation)])
        return 0
    elif action == TMessage.accept_with_edit:
        change_publish_status(content_id, "2")
        btn_list = [TemplateMessageButton(text=TMessage.change_logo, value=TMessage.change_logo, action=0)]
        general_message = TextMessage(
            ReadyMessage.replace_description.format(content.name, content.nick_name))
        template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
        kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(template_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        client_text_message = TextMessage(
            ReadyMessage.accept_content_with_edit_client.format(content.name, content.nick_name))
        kwargs = {"message": client_text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(client_text_message, client_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        dispatcher.register_conversation_next_step_handler(
            update, [CommandHandler("start", start_conversation),
                     MessageHandler(TextFilter(), replace_description),
                     MessageHandler(TemplateResponseFilter(keywords=[TMessage.change_logo]), replace_logo),
                     MessageHandler(TemplateResponseFilter(keywords=[TMessage.accept, TMessage.reject,
                                                                     TMessage.accept_with_edit]),
                                    add_or_reject_content),
                     MessageHandler(DefaultFilter(), start_conversation)])


def replace_description(bot, update):
    user_peer = update.get_effective_user()
    new_description = update.get_effective_message().text
    content_id = dispatcher.get_conversation_data(update, "content_id")
    change_description(content_id, new_description)
    btn_list = [TemplateMessageButton(text=TMessage.change_logo, value=TMessage.change_logo, action=0),
                TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    general_message = TextMessage(ReadyMessage.replace_description_successfully)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TemplateResponseFilter(keywords=[TMessage.change_logo]), replace_logo),
                 MessageHandler(TemplateResponseFilter(keywords=[TMessage.accept, TMessage.reject,
                                                                 TMessage.accept_with_edit]),
                                add_or_reject_content),
                 MessageHandler(DefaultFilter(), start_conversation)])


def replace_logo(bot, update):
    user_peer = update.get_effective_user()
    text_message = TextMessage(ReadyMessage.send_new_logo)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(PhotoFilter(), get_new_logo),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_new_logo(bot, update):
    user_peer = update.get_effective_user()
    photo_message = update.get_effective_message()
    new_logo = Logo(photo_message.file_id, photo_message.access_hash, photo_message.file_size, photo_message.thumb)
    content_id = dispatcher.get_conversation_data(update, "content_id")
    insert_logo(new_logo)
    logo = get_logo_by_fileid_access_hash(photo_message.file_id, photo_message.access_hash)
    change_logo(content_id, logo.id)
    change_publish_status(content_id, "1")
    text_message = TextMessage(ReadyMessage.replace_logo_successfully)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


def reject_reason(bot, update):
    user_peer = update.get_effective_user()
    reason_text = update.get_effective_message().text
    content_id = dispatcher.get_conversation_data(update, "content_id")
    client_peer = dispatcher.get_conversation_data(update, "client_peer")
    content = get_content_by_id(content_id)
    client_text_message = TextMessage(ReadyMessage.reject_content_client.format(
        content.name, content.nick_name) + "\n" + ReadyMessage.reason.format(reason_text))
    kwargs = {"message": client_text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(client_text_message, client_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message,
                     kwargs=kwargs)
    btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    general_message = TextMessage(ReadyMessage.reason_sent_to_client)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Add Category ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.add_category]))
def choose_type(bot, update):
    user_peer = update.get_effective_user()
    types = get_all_type()
    btn_list = []
    type_list = []
    for type in types:
        btn_list.append(TemplateMessageButton(text=type.name, value=type.name, action=0))
        type_list.append(type.name)
    general_message = TextMessage(ReadyMessage.choose_type)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(TemplateResponseFilter(keywords=type_list),
                                                                       get_category_name),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def get_category_name(bot, update):
    user_peer = update.get_effective_user()
    type_name = update.get_effective_message().text_message
    dispatcher.set_conversation_data(update, "type_name", type_name)
    text_message = TextMessage(ReadyMessage.enter_category_name)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(TextFilter(), add_category),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def add_category(bot, update):
    user_peer = update.get_effective_user()
    category_name = update.get_effective_message().text
    type_name = dispatcher.get_conversation_data(update, "type_name")
    type = get_type_by_name(type_name=type_name)
    new_category = Category(name=category_name, type_id=type.id)
    result = insert_category(new_category)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    if result == ReadyMessage.duplicated_category:
        text_message = TextMessage(ReadyMessage.duplicated_category)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.category_added_successfully.format(category_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Add type ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.add_type]))
def get_type_name(bot, update):
    user_peer = update.get_effective_user()
    text_message = TextMessage(ReadyMessage.enter_type_name)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message,
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
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    if result == ReadyMessage.duplicated_type:
        text_message = TextMessage(ReadyMessage.duplicated_type)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.type_added_successfully.format(type_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== User Panel ===================================================
def user_panel(bot, update):
    user_peer = update.get_effective_user()
    btn_list = [TemplateMessageButton(text=TMessage.request_content, value=TMessage.request_content, action=0),
                TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]
    general_message = TextMessage(ReadyMessage.start_conversation)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message,
                     kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(
                                                            TemplateResponseFilter(keywords=TMessage.request_content),
                                                            request_content),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.request_content]))
def request_content(bot, update):
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
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TemplateResponseFilter(keywords=type_name_list), get_content_type),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_type(bot, update):
    user_peer = update.get_effective_user()
    content_type_name = update.get_effective_message().text_message
    content_type = get_type_by_name(content_type_name)
    dispatcher.set_conversation_data(update, "content_type_id", content_type.id)
    text_message = TextMessage(ReadyMessage.enter_content_name)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), get_content_name),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_name(bot, update):
    user_peer = update.get_effective_user()
    content_name = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "content_name", content_name)
    text_message = TextMessage(ReadyMessage.enter_content_nick_name)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), get_content_nick_name),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_nick_name(bot, update):
    user_peer = update.get_effective_user()
    nick_name = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "content_nick_name", nick_name)
    text_message = TextMessage(ReadyMessage.enter_content_description)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), get_content_description),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_description(bot, update):
    user_peer = update.get_effective_user()
    description = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "content_description", description)
    general_message = TextMessage(ReadyMessage.choose_content_category)
    category_list = get_all_categories()
    category_name_list = []
    btn_list = []
    for category in category_list:
        category_name_list.append(category.name)
        btn_list += [TemplateMessageButton(text=category.name, value=category.name, action=0)]
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TemplateResponseFilter(keywords=category_name_list), get_content_category),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_category(bot, update):
    user_peer = update.get_effective_user()
    category_name = update.get_effective_message().text_message
    category = get_category_by_name(category_name)
    dispatcher.set_conversation_data(update, "category_id", category.id)
    text_message = TextMessage(ReadyMessage.upload_content_log)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(PhotoFilter(), get_content_logo),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_logo(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    access_hash = user_peer.access_hash
    logo = update.get_effective_message()
    logo_obj = Logo(file_id=logo.file_id, access_hash=logo.access_hash, file_size=logo.file_size, thumb=logo.thumb)
    insert_logo(logo_obj)
    logo = get_logo_by_fileid_access_hash(logo.file_id, logo.access_hash)
    content_name = dispatcher.get_conversation_data(update, "content_name")
    content_description = dispatcher.get_conversation_data(update, "content_description")
    content_nick_name = dispatcher.get_conversation_data(update, "content_nick_name")
    category_id = dispatcher.get_conversation_data(update, "category_id")
    content_type_id = dispatcher.get_conversation_data(update, "content_type_id")
    content_obj = Content(name=content_name, description=content_description,
                          nick_name=content_nick_name,
                          category_id=category_id, logo_id=logo.id,
                          user_id=user_id, access_hash=access_hash, type_id=content_type_id)
    insert_content(content_obj)
    text_message = TextMessage(ReadyMessage.success_send_content)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Info ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.info]))
def info(bot, update):
    user_peer = update.get_effective_user()
    btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    general_message = TextMessage(ReadyMessage.information)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message,
                     kwargs=kwargs)
    dispatcher.finish_conversation(update)


updater.run()
