import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from balebot.bot import Bot

from balebot.models.base_models import Peer
import bot as my_bot
from balebot.models.messages import TextMessage
from constant.message import ReadyMessage, TMessage
from bot_config import BotConfig
from db.db_handler import remove_content, insert_content, Content, insert_logo, Logo, Type, insert_type, remove_type, \
    insert_category, Category, remove_logo, insert_content_to_category, remove_category
from utils.utils import eng_to_arabic_number, arabic_to_eng_number, phone_number_validation


class TestMyBot(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.bot = MagicMock()
        my_bot.dispatcher = MagicMock()
        self.update = MagicMock()
        self.update.get_effective_user.return_value = Peer(peer_type="User", peer_id=745695, access_hash="1654")

    def test_arabic_to_eng_number(self):
        arabic_number = "۰۱۲۳۴۵۶۷۸۹"
        self.assertEqual(arabic_to_eng_number(arabic_number), "0123456789")

    def test_eng_to_arabic_number(self):
        arabic_number = "0123456789"
        self.assertEqual(eng_to_arabic_number(arabic_number), "۰۱۲۳۴۵۶۷۸۹")

    def test_phone_number_validation(self):
        phone_number = "09300520717"
        self.assertEqual(phone_number_validation(phone_number), True)
        phone_number = "07300520717"
        self.assertEqual(phone_number_validation(phone_number), False)
        phone_number = "+989158751843"
        self.assertEqual(phone_number_validation(phone_number), True)
        phone_number = "+9891"
        self.assertEqual(phone_number_validation(phone_number), False)

    def test_success_call_back(self):
        user_data = MagicMock()
        self.assertEqual(my_bot.success_send_message(None, user_data), None)

    def test_failure_call_back(self):
        user_data = MagicMock()
        print(user_data)
        self.assertEqual(my_bot.failure_send_message(None, user_data), None)

    def test_remove_content(self):
        logo_id = insert_logo(
            logo=Logo(file_id=15131, access_hash="15311351", file_size=151615, thumb="asd5asdasda"))
        content = Content(name="name", description="adasd", nick_name="dasdas", logo_id=logo_id,
                          user_id=131511, access_hash="415311", publish_date=datetime.now())
        content_id = insert_content(content=content)
        self.assertEqual(remove_content(content_id), True)

    def test_remove_type(self):
        type = Type(name="الکی")
        type_id = insert_type(type)
        insert_category(Category(name="دولکی", type_id=type_id))
        self.assertEqual(remove_type(type_id), True)

    def test_remove_category(self):
        category_id=insert_category(Category(name="دولکی", type_id=1))
        logo_id = insert_logo(
            logo=Logo(file_id=15131, access_hash="15311351", file_size=151615, thumb="asd5asdasda"))
        content = Content(name="name", description="adasd", nick_name="dasdas", logo_id=logo_id,
                          user_id=131511, access_hash="415311", publish_date=datetime.now())
        content_id = insert_content(content=content)
        insert_content_to_category(content_id, category_id)
        self.assertEqual(remove_category(category_id), True)
    #


    def test_remove_logo(self):
        # logo_id = insert_logo(
        #     logo=Logo(file_id=15131, access_hash="15311351", file_size=151615, thumb="asd5asdasda"))
        # content = Content(name="name", description="adasd", nick_name="dasdas", logo_id=logo_id,
        #                   user_id=131511, access_hash="415311", publish_date=datetime.now())
        # insert_content(content=content)
        remove_logo(26)

    def remove_content_to_category(self):
        pass
    # def test_edit_content(self):
    #     # bot = MagicMock()
    #     update = MagicMock()
    #     logo_id = insert_logo(
    #         logo=Logo(file_id=15131, access_hash="15311351", file_size=151615, thumb="asd5asdasda"))
    #     content = Content(name="name", description="adasd", nick_name="dasdas", logo_id=logo_id,
    #                       user_id=131511, access_hash="415311", publish_date=datetime.now())
    #     content_id = insert_content(content=content)
    #     # update.get_effective_user.return_value = Peer(peer_type="User", peer_id=745695, access_hash="1654")
    #     update.get_effective_message.return_value = TextMessage("Edited")
    #     # update.dispatcher.get_conversation_data(update, "content_id",content_id)
    #     # update.dispatcher.get_conversation_data(update, "field", TMessage.content_name)
    #
    #     my_bot.dispatcher.set_conversation_data(update, "content_id",content_id)
    #
    #     # my_bot.dispatcher.get_conversation_data.return_value = content_id
    #
    #     self.assertEqual(my_bot.submit_new_text_change(my_bot.dispatcher.bot, update), None)
