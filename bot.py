import datetime
import os

from balebot.filters import TemplateResponseFilter, TextFilter, DefaultFilter, PhotoFilter
from balebot.handlers import MessageHandler, CommandHandler
from balebot.models.base_models import Peer
from balebot.models.constants.peer_type import PeerType
from balebot.models.messages import TemplateMessageButton, TextMessage, TemplateMessage, PhotoMessage
from db.db_handler import create_all_table, get_category, \
    insert_content, insert_logo, Logo, Content, \
    get_logo_by_fileid_access_hash, insert_category, Category, get_unpublished_content, get_category_by_id, \
    get_logo_by_id, change_publish_status, change_text_content, get_content_by_id, Type, insert_type, get_all_type, \
    get_type_by_name, change_logo, insert_content_to_category, get_type_by_id, change_type, \
    remove_type, remove_category, change_category, change_category_content
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


def success_send_message_and_edit_again(response, user_data):
    kwargs = user_data['kwargs']
    update = kwargs["update"]
    content_id = kwargs["content_id"]
    bot = kwargs["bot"]
    user_peer = update.get_effective_user()
    my_logger.info(LogMessage.success_send_message, extra={"user_id": user_peer.peer_id, "tag": "info"})
    update.body.message.text_message = TMessage.accept_with_edit + " - " + eng_to_arabic_number(content_id)
    add_or_reject_content(bot, update)


def is_admin(user_id):
    user_id = str(user_id)
    for admin_id in BotConfig.admin_list:
        if admin_id == user_id:
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


# ============================================== Buttons ===================================================
admin_buttons = [
    TemplateMessageButton(text=TMessage.get_sent_content, value=TMessage.get_sent_content, action=0),
    TemplateMessageButton(text=TMessage.request_content, value=TMessage.request_content, action=0),
    TemplateMessageButton(text=TMessage.manage_category, value=TMessage.manage_category, action=0),
    TemplateMessageButton(text=TMessage.manage_type, value=TMessage.manage_type, action=0),
    # TemplateMessageButton(text=TMessage.search_content, value=TMessage.search_content, action=0),
    TemplateMessageButton(text=TMessage.set_publish_time, value=TMessage.set_publish_time, action=0),
    TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]
user_buttons = [
    TemplateMessageButton(text=TMessage.request_content, value=TMessage.request_content, action=0),
    # TemplateMessageButton(text=TMessage.search_content, value=TMessage.search_content, action=0),
    TemplateMessageButton(text=TMessage.info, value=TMessage.info, action=0)]

allow_publish_dict = {0: "بررسی نشده", 1: "تایید انتشار", -1: "رد شده", 2: "تایید با شرط اصلاح"}
category_options = [
    TemplateMessageButton(text=TMessage.add_category, value=TMessage.add_category, action=0),
    TemplateMessageButton(text=TMessage.edit_category, value=TMessage.edit_category, action=0),
    TemplateMessageButton(text=TMessage.remove_category, value=TMessage.remove_category, action=0),
    TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
type_options = [TemplateMessageButton(text=TMessage.add_type, value=TMessage.add_type, action=0),
                TemplateMessageButton(text=TMessage.edit_type, value=TMessage.edit_type, action=0),
                TemplateMessageButton(text=TMessage.remove_type, value=TMessage.remove_type, action=0),
                TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]

content_change_option = [
    TemplateMessageButton(text=TMessage.content_name, value=TMessage.content_name, action=0),
    TemplateMessageButton(text=TMessage.content_nick_name, value=TMessage.content_nick_name, action=0),
    TemplateMessageButton(text=TMessage.content_description, value=TMessage.content_description, action=0),
    TemplateMessageButton(text=TMessage.content_category, value=TMessage.content_category, action=0),
    TemplateMessageButton(text=TMessage.content_logo, value=TMessage.content_logo, action=0),
    TemplateMessageButton(text=TMessage.preview, value=TMessage.preview, action=0)]


# ============================================== Admin Panel ===================================================
def admin_panel(bot, update):
    user_peer = update.get_effective_user()
    general_message = TextMessage(ReadyMessage.start_conversation)
    template_message = TemplateMessage(general_message=general_message, btn_list=admin_buttons)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


@dispatcher.message_handler(TextFilter(pattern=Regex.number_regex))
def show_content(bot, update):
    user_peer = update.get_effective_user()
    message = update.get_effective_message()
    if isinstance(message, TextMessage):
        content_id = update.get_effective_message().text
        content_id = arabic_to_eng_number(content_id)
        next_function = success_send_message_and_start_again
    else:
        content_id = dispatcher.get_conversation_data(update, "content_id")
        next_function = success_send_message_and_edit_again
    user_id = user_peer.peer_id
    if not is_admin(user_id):
        return 0
    content = get_content_by_id(content_id)
    if content is None:
        general_message = TextMessage(ReadyMessage.content_not_found)
        btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
        template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
        kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(template_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message, kwargs=kwargs)
        dispatcher.finish_conversation(update)
        return 0
    content_to_category_obj = content.content_to_category[0]
    category = get_category_by_id(content_to_category_obj.category_id)
    content_type = get_type_by_id(category.type_id)
    logo = get_logo_by_id(content.logo_id)
    allow_publish = allow_publish_dict.get(content.allow_publish)
    text_message = TextMessage(ReadyMessage.request_content_text.format(eng_to_arabic_number(content.id),
                                                                        content.name,
                                                                        content.description,
                                                                        category.name.replace(" ", "_"),
                                                                        content_type.name.replace(" ", "_"),
                                                                        content.nick_name,
                                                                        content.nick_name) + "\n"
                               + ReadyMessage.publish_status.format(allow_publish))
    photo_message = PhotoMessage(logo.file_id, logo.access_hash, "channel", logo.file_size, "image/jpeg", None, 250,
                                 250, file_storage_version=1, caption_text=text_message)
    kwargs = {"message": photo_message, "content_id": content_id, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(photo_message, user_peer, success_callback=next_function,
                     failure_callback=failure_send_message, kwargs=kwargs)


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
                         failure_callback=failure_send_message, kwargs=kwargs)
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

        content_to_category_obj = content.content_to_category[0]
        category = get_category_by_id(content_to_category_obj.category_id)
        logo = get_logo_by_id(content.logo_id)
        content_type = get_type_by_id(category.type_id)
        text_message = TextMessage(
            (ReadyMessage.request_content_text.format(eng_to_arabic_number(content.id),
                                                      content.name,
                                                      content.description,
                                                      category.name.replace(" ", "_"),
                                                      content_type.name.replace(" ", "_"),
                                                      content.nick_name,
                                                      content.nick_name)))
        photo_message = PhotoMessage(logo.file_id, logo.access_hash, "channel", logo.file_size, "image/jpeg", None, 250,
                                     250, file_storage_version=1, caption_text=text_message)

        template_message = TemplateMessage(general_message=photo_message, btn_list=btn_list)
        kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(template_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


@dispatcher.message_handler(
    TemplateResponseFilter(keywords=[TMessage.accept, TMessage.accept_with_edit, TMessage.reject]))
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
                         failure_callback=failure_send_message, kwargs=kwargs)
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
        general_message = TextMessage(ReadyMessage.what_to_edit)
        option_list = [
            TemplateMessageButton(text=TMessage.content_name, value=TMessage.content_name, action=0),
            TemplateMessageButton(text=TMessage.content_nick_name, value=TMessage.content_nick_name, action=0),
            TemplateMessageButton(text=TMessage.content_description, value=TMessage.content_description, action=0),
            TemplateMessageButton(text=TMessage.content_category, value=TMessage.content_category, action=0),
            TemplateMessageButton(text=TMessage.content_logo, value=TMessage.content_logo, action=0),
            TemplateMessageButton(text=TMessage.preview, value=TMessage.preview, action=0),
            TemplateMessageButton(
                text=TMessage.accept, value=TMessage.accept + " - " + eng_to_arabic_number(content.id), action=0)]
        template_message = TemplateMessage(general_message=general_message, btn_list=option_list)
        kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(template_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message, kwargs=kwargs)
        dispatcher.register_conversation_next_step_handler(
            update, [CommandHandler("start", start_conversation),
                     MessageHandler(TemplateResponseFilter(keywords=[TMessage.content_logo]), get_new_logo),
                     MessageHandler(TemplateResponseFilter(
                         keywords=[TMessage.content_name, TMessage.content_nick_name, TMessage.content_description]),
                         get_new_text),
                     MessageHandler(TemplateResponseFilter(keywords=[TMessage.content_category]),
                                    show_types_for_content),
                     MessageHandler(TemplateResponseFilter(keywords=[TMessage.preview]), show_content),
                     MessageHandler(TemplateResponseFilter(keywords=[TMessage.accept, TMessage.reject,
                                                                     TMessage.accept_with_edit]),
                                    add_or_reject_content),
                     MessageHandler(DefaultFilter(), start_conversation)])


def get_new_text(bot, update):
    user_peer = update.get_effective_user()
    field = update.get_effective_message().text_message
    dispatcher.set_conversation_data(update, "field", field)
    general_message = TextMessage(ReadyMessage.enter_new_text.format(field))
    btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), submit_new_text_change),
                 MessageHandler(TemplateResponseFilter(keywords=[TMessage.accept, TMessage.reject,
                                                                 TMessage.accept_with_edit]),
                                add_or_reject_content),
                 MessageHandler(DefaultFilter(), start_conversation)])


def submit_new_text_change(bot, update):
    user_peer = update.get_effective_user()
    new_text = update.get_effective_message().text
    content_id = dispatcher.get_conversation_data(update, "content_id")
    field = dispatcher.get_conversation_data(update, "field")
    result = None
    if field == TMessage.content_name:
        result = change_text_content(content_id, name=new_text)
    elif field == TMessage.content_nick_name:

        result = change_text_content(content_id, nick_name=new_text)
    elif field == TMessage.content_description:

        result = change_text_content(content_id, description=new_text)
    if not result:

        text_message = TextMessage(ReadyMessage.error)
    else:
        text_message = TextMessage(ReadyMessage.replace_successfully.format(field))
    kwargs = {"message": text_message, "content_id": content_id, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_edit_again,
                     failure_callback=failure_send_message, kwargs=kwargs)


def show_types_for_content(bot, update):
    user_peer = update.get_effective_user()
    if not is_admin(user_peer.peer_id):
        return 0
    types = get_all_type()
    if not types:
        text_message = TextMessage(ReadyMessage.no_type_available)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message, kwargs=kwargs)
        return 0
    btn_list = []
    type_list = []
    for a_type in types:
        btn_list.append(TemplateMessageButton(text=a_type.name, value=a_type.name, action=0))
        type_list.append(a_type.name)
    general_message = TextMessage(ReadyMessage.choose_type)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TemplateResponseFilter(keywords=type_list), choose_category),
                 MessageHandler(DefaultFilter(), start_conversation)])


def choose_category(bot, update):
    user_peer = update.get_effective_user()
    type_name = update.get_effective_message().text_message
    a_type = get_type_by_name(type_name)
    categories = get_category(type_id=a_type.id)
    if not categories:
        text_message = TextMessage(ReadyMessage.no_category_available)
        content_id = dispatcher.get_conversation_data(update, "content_id")
        kwargs = {"message": text_message, "content_id": content_id, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_edit_again,
                         failure_callback=failure_send_message, kwargs=kwargs)
        return 0
    dispatcher.set_conversation_data(update, "type_id", a_type.id)
    btn_list = []
    category_list = []
    for category in categories:
        btn_list.append(TemplateMessageButton(text=category.name, value=category.name, action=0))
        category_list.append(category.name)
    general_message = TextMessage(ReadyMessage.choose_category)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TemplateResponseFilter(category_list), change_category_of_content),
                 MessageHandler(DefaultFilter(), start_conversation)])


def change_category_of_content(bot, update):
    user_peer = update.get_effective_user()
    category_name = update.get_effective_message().text_message
    content_id = dispatcher.get_conversation_data(update, "content_id")
    type_id = dispatcher.get_conversation_data(update, "type_id")
    category = get_category(category_name=category_name, type_id=type_id)
    change_category_content(content_id, category.id)
    text_message = TextMessage(ReadyMessage.category_changed_successfully.format(category_name))
    kwargs = {"message": text_message, "content_id": content_id, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_edit_again,
                     failure_callback=failure_send_message, kwargs=kwargs)


def get_new_logo(bot, update):
    user_peer = update.get_effective_user()
    text_message = TextMessage(ReadyMessage.send_new_logo)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(PhotoFilter(), replace_logo),
                 MessageHandler(DefaultFilter(), start_conversation)])


def replace_logo(bot, update):
    user_peer = update.get_effective_user()
    photo_message = update.get_effective_message()
    new_logo = Logo(photo_message.file_id, photo_message.access_hash, photo_message.file_size, photo_message.thumb)
    content_id = dispatcher.get_conversation_data(update, "content_id")
    insert_logo(new_logo)
    logo = get_logo_by_fileid_access_hash(photo_message.file_id, photo_message.access_hash)
    change_logo(content_id, logo.id)
    change_publish_status(content_id, "1")
    text_message = TextMessage(ReadyMessage.replace_logo_successfully)
    kwargs = {"message": text_message, "content_id": content_id, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_edit_again,
                     failure_callback=failure_send_message, kwargs=kwargs)


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


# ============================================ Manage Type & Category=================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.manage_type, TMessage.manage_category]))
def show_options(bot, update):
    user_peer = update.get_effective_user()
    text_message = update.get_effective_message().text_message
    if not is_admin(user_peer.peer_id):
        return 0
    general_message = TextMessage(ReadyMessage.choose_type)
    if text_message == TMessage.manage_category:
        btn_list = category_options
    else:
        btn_list = type_options
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Add Category ===================================================
@dispatcher.message_handler(TemplateResponseFilter(
    keywords=[TMessage.add_category, TMessage.edit_category, TMessage.remove_category, TMessage.edit_type,
              TMessage.remove_type]))
def show_types(bot, update):
    user_peer = update.get_effective_user()
    if not is_admin(user_peer.peer_id):
        return 0
    text_message = update.get_effective_message().text_message
    types = get_all_type()
    if not types:
        text_message = TextMessage(ReadyMessage.no_type_available)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message, kwargs=kwargs)
        return 0
    btn_list = []
    type_list = []
    for a_type in types:
        btn_list.append(TemplateMessageButton(text=a_type.name, value=a_type.name, action=0))
        type_list.append(a_type.name)
    general_message = TextMessage(ReadyMessage.choose_type)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    next_func_dict = {TMessage.add_category: get_category_name, TMessage.edit_category: show_categories,
                      TMessage.remove_category: show_categories, TMessage.edit_type: get_new_type_name,
                      TMessage.remove_type: remove_a_type}
    dispatcher.set_conversation_data(update, "next_func", add_category)
    dispatcher.set_conversation_data(update, "request", text_message)
    next_function = next_func_dict.get(text_message)
    dispatcher.register_conversation_next_step_handler(
        update,
        [CommandHandler("start", start_conversation),
         MessageHandler(TemplateResponseFilter(keywords=type_list), next_function),
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
    cat_type = get_type_by_name(type_name=type_name)
    new_category = Category(name=category_name, type_id=cat_type.id)
    result = insert_category(new_category)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message, kwargs=kwargs)
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


def show_categories(bot, update):
    user_peer = update.get_effective_user()
    type_name = update.get_effective_message().text_message
    dispatcher.set_conversation_data(update, "type_name", type_name)
    request = dispatcher.get_conversation_data(update, "request")
    if request == TMessage.edit_category:
        next_function = get_category_new_name
        dispatcher.set_conversation_data(update, "next_func", add_category)
    elif request == TMessage.remove_category:
        next_function = remove_a_category
    else:
        next_function = start_conversation
    tpe = get_type_by_name(type_name)
    categories = get_category(type_id=tpe.id)
    if not categories:
        text_message = TextMessage(ReadyMessage.no_category_available)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message, kwargs=kwargs)
        return 0
    btn_list = []
    category_list = []
    for category in categories:
        btn_list.append(TemplateMessageButton(text=category.name, value=category.name, action=0))
        category_list.append(category.name)
    general_message = TextMessage(ReadyMessage.choose_category)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update,
        [CommandHandler("start", start_conversation),
         MessageHandler(TemplateResponseFilter(keywords=category_list), next_function),
         MessageHandler(DefaultFilter(), start_conversation)])


def get_category_new_name(bot, update):
    user_peer = update.get_effective_user()
    category_name = update.get_effective_message().text_message
    dispatcher.set_conversation_data(update, "category_name", category_name)
    text_message = TextMessage(ReadyMessage.enter_category_new_name)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(TextFilter(), edit_category_text),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def edit_category_text(bot, update):
    user_peer = update.get_effective_user()
    category_new_name = update.get_effective_message().text
    type_name = dispatcher.get_conversation_data(update, "type_name")
    category_name = dispatcher.get_conversation_data(update, "category_name")
    tpe = get_type_by_name(type_name)
    category = get_category(category_name=category_name, type_id=tpe.id)
    result = change_category(category.id, category_new_name)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.edit_name_successfully.format(category_name, category_new_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


def remove_a_category(bot, update):
    user_peer = update.get_effective_user()
    category_name = update.get_effective_message().text_message
    type_name = dispatcher.get_conversation_data(update, "type_name")
    tpe = get_type_by_name(type_name)
    category = get_category(category_name=category_name, type_id=tpe.id)
    result = remove_category(category.id)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message,
                         kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.deleted_successfully.format(category_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Add type ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.add_type]))
def get_type_name(bot, update):
    user_peer = update.get_effective_user()
    if not is_admin(user_peer.peer_id):
        return 0
    text_message = TextMessage(ReadyMessage.enter_type_name)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(), add_type),
                 MessageHandler(DefaultFilter(), start_conversation)])


def add_type(bot, update):
    user_peer = update.get_effective_user()
    type_name = update.get_effective_message().text
    new_type = Type(name=type_name)
    result = insert_type(new_type)
    if result is False:
        text_message = TextMessage(ReadyMessage.error)
    elif result == ReadyMessage.duplicated_type:
        text_message = TextMessage(ReadyMessage.duplicated_type)
    else:
        text_message = TextMessage(ReadyMessage.type_added_successfully.format(type_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


def get_new_type_name(bot, update):
    user_peer = update.get_effective_user()
    type_name = update.get_effective_message().text_message
    dispatcher.set_conversation_data(update, "type_name", type_name)
    text_message = TextMessage(ReadyMessage.enter_new_type_name)
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(update,
                                                       [CommandHandler("start", start_conversation),
                                                        MessageHandler(TextFilter(), edit_type),
                                                        MessageHandler(DefaultFilter(), start_conversation)])


def edit_type(bot, update):
    user_peer = update.get_effective_user()
    new_type_name = update.get_effective_message().text
    type_name = dispatcher.get_conversation_data(update, "type_name")
    a_type = get_type_by_name(type_name)
    result = change_type(a_type.id, new_type_name)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message, kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.edit_name_successfully.format(type_name, new_type_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


def remove_a_type(bot, update):
    user_peer = update.get_effective_user()
    type_name = update.get_effective_message().text_message
    a_type = get_type_by_name(type_name)
    result = remove_type(a_type.id)
    if not result:
        text_message = TextMessage(ReadyMessage.error)
        kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(text_message, user_peer, success_callback=success_send_message,
                         failure_callback=failure_send_message, kwargs=kwargs)
        return 0
    text_message = TextMessage(ReadyMessage.deleted_successfully.format(type_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== User Panel ===================================================
def user_panel(bot, update):
    user_peer = update.get_effective_user()
    general_message = TextMessage(ReadyMessage.start_conversation)
    template_message = TemplateMessage(general_message=general_message, btn_list=user_buttons)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.request_content]))
def request_content(bot, update):
    dispatcher.clear_conversation_data(update)
    user_peer = update.get_effective_user()
    general_message = TextMessage(ReadyMessage.choose_content_type)
    all_types = get_all_type()
    if not all_types:
        message = TextMessage(ReadyMessage.no_content_type_available)
        kwargs = {"message": message, "update": update, "bot": bot, "try_times": 1}
        bot.send_message(message, user_peer, success_callback=success_send_message_and_start_again,
                         failure_callback=failure_send_message, kwargs=kwargs)
        return 0
    type_name_list = []
    btn_list = []
    for type in all_types:
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
    dispatcher.set_conversation_data(update, "content_type_name", content_type_name)
    text_message = TextMessage(ReadyMessage.enter_content_name.format(content_type_name))
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
    content_type_name = dispatcher.get_conversation_data(update, "content_type_name")
    text_message = TextMessage(ReadyMessage.enter_content_nick_name.format(content_type_name))
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    dispatcher.set_conversation_data(update, "success_callback", get_content_nick_name)
    dispatcher.set_conversation_data(update, "text_filter", Regex.nick_name)
    bot.send_message(text_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(pattern=Regex.nick_name), get_content_nick_name),
                 MessageHandler(TextFilter(), wrong_case),
                 MessageHandler(DefaultFilter(), start_conversation)])


def wrong_case(bot, update):
    user_peer = update.get_effective_user()
    success_callback = dispatcher.get_conversation_data(update, "success_callback")
    text_filter = dispatcher.get_conversation_data(update, "text_filter")
    general_message = TextMessage(ReadyMessage.wrong_case_happened)
    btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(pattern=text_filter), success_callback),
                 MessageHandler(TextFilter(), wrong_case),
                 MessageHandler(DefaultFilter(), start_conversation)])


def get_content_nick_name(bot, update):
    user_peer = update.get_effective_user()
    nick_name = update.get_effective_message().text
    dispatcher.set_conversation_data(update, "content_nick_name", nick_name)
    content_type_name = dispatcher.get_conversation_data(update, "content_type_name")
    text_message = TextMessage(ReadyMessage.enter_content_description.format(content_type_name))
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
    content_type_id = dispatcher.get_conversation_data(update, "content_type_id")
    content_type_name = dispatcher.get_conversation_data(update, "content_type_name")
    general_message = TextMessage(ReadyMessage.choose_content_category.format(content_type_name))
    category_list = get_category(type_id=content_type_id)
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
    content_type_id = dispatcher.get_conversation_data(update, "content_type_id")
    category = get_category(category_name=category_name, type_id=content_type_id)
    dispatcher.set_conversation_data(update, "category_id", category.id)
    content_type_name = dispatcher.get_conversation_data(update, "content_type_name")
    text_message = TextMessage(ReadyMessage.upload_content_log.format(content_type_name))
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
    logo_id = insert_logo(logo_obj)
    content_type_name = dispatcher.get_conversation_data(update, "content_type_name")
    content_name = dispatcher.get_conversation_data(update, "content_name")
    content_description = dispatcher.get_conversation_data(update, "content_description")
    content_nick_name = dispatcher.get_conversation_data(update, "content_nick_name")
    category_id = dispatcher.get_conversation_data(update, "category_id")
    if datetime.datetime.now().hour > BotConfig.start_publish_hour:
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        publish_date = tomorrow.replace(hour=18, minute=0)
    else:
        publish_date = datetime.datetime.now().replace(hour=18, minute=0)
    content_obj = Content(name=content_name, description=content_description,
                          nick_name=content_nick_name, logo_id=logo_id, user_id=user_id, access_hash=access_hash,
                          publish_date=publish_date)
    content_id = insert_content(content_obj)
    insert_content_to_category(content_id, category_id)
    text_message = TextMessage(ReadyMessage.success_send_content.format(content_type_name))
    my_logger.info(LogMessage.new_content_submitted, extra={"user_id": user_peer.peer_id, "tag": "info"})
    kwargs = {"message": text_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(text_message, user_peer, success_callback=success_send_message_and_start_again,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.finish_conversation(update)


# ============================================== Info ===================================================
@dispatcher.message_handler(TemplateResponseFilter(keywords=[TMessage.set_publish_time]))
def get_publish_hour(bot, update):
    user_peer = update.get_effective_user()
    user_id = user_peer.peer_id
    if not is_admin(user_id):
        return 0
    btn_list = [TemplateMessageButton(text=TMessage.back, value=TMessage.back, action=0)]
    general_message = TextMessage(ReadyMessage.send_new_publish_hour)
    template_message = TemplateMessage(general_message=general_message, btn_list=btn_list)
    kwargs = {"message": template_message, "update": update, "bot": bot, "try_times": 1}
    bot.send_message(template_message, user_peer, success_callback=success_send_message,
                     failure_callback=failure_send_message, kwargs=kwargs)
    dispatcher.register_conversation_next_step_handler(
        update, [CommandHandler("start", start_conversation),
                 MessageHandler(TextFilter(pattern=Regex.number_regex), set_publish_hour),
                 MessageHandler(DefaultFilter(), start_conversation)])


def set_publish_hour(bot, update):
    user_peer = update.get_effective_user()
    start_publish_hour = update.get_effective_message().text
    start_publish_hour = arabic_to_eng_number(start_publish_hour)
    start_publish_hour = int(start_publish_hour)
    user_id = user_peer.peer_id
    if not is_admin(user_id):
        return 0
    if 23 >= start_publish_hour >= 0:
        start_publish_hour = str(start_publish_hour)
        os.environ['START_PUBLISH_HOUR'] = start_publish_hour
        text_message = TextMessage(ReadyMessage.set_publish_hour_successfully)
    else:
        text_message = TextMessage(ReadyMessage.invalid_publish_hour)
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
