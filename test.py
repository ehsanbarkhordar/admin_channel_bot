import datetime

from db.db_handler import insert_content, Content

content=Content(name="fdsad", description="dsdsd",
                          nick_name='dsad', logo_id=1,
                          user_id=132, access_hash="dasda", type_id=1,publish_date=datetime.datetime.now())
content_id=insert_content(content)
print(content_id)
