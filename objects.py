from google.appengine.ext import ndb
from google.appengine.api import channel

class Teacher(ndb.Model):
	username = ndb.StringProperty()
	password = ndb.StringProperty()
	status = ndb.StringProperty()
	currentLesson = ndb.StringProperty()
	lessons = ndb.StringProperty(repeated=True)
	def save(self):
		self.put()

	def connect(self):
		self.token = channel.create_channel(str(self.key.id()))
		self.status = "connected"
		self.save()
	
	def assignLesson(lessonName):
		self.currentLesson = lessonName
		self.lessons.append(lessonName)
		self.save()

def teacherUsernameExists(username):
	if getTeacher(username):
		return True
	else:
		return False

def getTeacher(username):
	q = Teacher.query(Teacher.username == username)
	teacher = q.get()
	if teacher:
		return teacher
	else:
		return False

class Lesson(ndb.Model):
	lessonName = ndb.StringProperty()
	teacher = ndb.StringProperty()
	status = ndb.StringProperty()
	sessions = ndb.StringProperty(repeated=True)
	students = ndb.StringProperty(repeated=True)
	def save(self):
		self.put()
	
def getOpenLessonsNames():
	q = Lesson.query(Lesson.status == "open")
	if q.count(limit=None) > 0:
		lessons = q.fetch(limit=None)
		return [lesson.lessonName for lesson in lessons]
	else:
		return []
