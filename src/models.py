import time, uuid # uuid可以用来生成唯一性的ID来标记对象
from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

def next_id():
	return '%015d%s000' % (int(time.time()*1000), uuid.uuid4().hex)

class Video(Model):
	__table__ = 'videos'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')

	aid = StringField(ddl='varchar(50)')
	mid = StringField(ddl='varchar(50)')
	cid = StringField(ddl='varchar(1000)')
	ctime = IntegerField()
	duration = IntegerField()
	coin = IntegerField()
	danmaku = IntegerField()
	favorite = IntegerField()
	like = IntegerField()
	reply = IntegerField()
	share = IntegerField()
	view = IntegerField()
	video_num = IntegerField()
	title = StringField(ddl='varchar(200)')

