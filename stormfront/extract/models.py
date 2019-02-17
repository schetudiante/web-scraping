from peewee import *
database = MySQLDatabase(
            'stormfront_scrape',
            host='localhost',
            passwd='notasecurepassword',
            user='stormfront_scrape')

database.connect()

class BaseModel(Model):
    class Meta:
        database = database

class Forum(BaseModel):
    url = CharField(db_column='url', max_length=512)
    title = CharField(db_column='title', max_length=512)
    categories = CharField(db_column='categories', max_length=1024)
    
    class Meta: 
        db_table = 'forums'

class Thread(BaseModel):
    url = CharField(db_column='url', max_length=512)
    title = CharField(db_column='title', max_length=1024)
    forum = ForeignKeyField(Forum, db_column='thread', null=True)
    timestamp = DateTimeField(db_column='timestamp')

    class Meta:
        db_table = 'threads'

class Comment(BaseModel):
    thread = ForeignKeyField(Thread, db_column='thread')
    author = CharField(db_column='author', max_length=256)
    comment_num = IntegerField(db_column='comment_id')
    timestamp = DateTimeField(db_column='timestamp')
    content = TextField(db_column='content')
    links = TextField(db_column='links')

    class Meta:
        db_table = 'comments'
   
