from google.appengine.ext import ndb
from google.appengine.api import channel

class User(ndb.Model):
	username = ndb.StringProperty()
	status = ndb.StringProperty()
	currentLesson = ndb.StringProperty()
	lessons = ndb.StringProperty(repeated=True)
	token = ndb.StringProperty()
	
	
	def save(self):
		self.put()

	def connect(self):
		self.token = channel.create_channel(str(self.key.id()))
		self.status = "connected"
		self.save()
	
	def assignLesson(self, lessonName):
		self.currentLesson = lessonName
		self.lessons.append(lessonName)
		self.save()

class Student(User):
	pass
	
class Teacher(User):
	password = ndb.StringProperty()
	
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

def getLesson(lessonName):
	q = Lesson.query(Lesson.lessonName == lessonName)
	lesson = q.get()
	if lesson:
		return lesson
	else:
		return False
		
def getStudent(username, currentLesson):
	q = Student.query(Student.username == username,
						Student.currentLesson == currentLesson)
	student = q.get()
	if student:
		return student
	else:
		return False
		
def studentAlreadyConnected(username):
	q = Student.query(Student.username == username, currentLesson != "")
	if q.get():
		return True
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
	
	def addStudent(self, student):
		self.students.append(student)
		self.save()
	
def getOpenLessonsNames():
	q = Lesson.query(Lesson.status == "open")
	if q.count(limit=None) > 0:
		lessons = q.fetch(limit=None)
		return [lesson.lessonName for lesson in lessons]
	else:
		return []
