from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import channel
import logging
import json

class User(ndb.Model):
	username = ndb.StringProperty()
	status = ndb.StringProperty()
	currentLesson = ndb.StringProperty()
	lessons = ndb.StringProperty(repeated=True)
	token = ndb.StringProperty()

	def connect(self):
		self.token = channel.create_channel(str(self.key.id()))
		self.status = "connected"
		self.save()
	
	def assignLesson(self, lessonName):
		self.currentLesson = lessonName
		self.lessons.append(lessonName)
		self.save()

class Student(User):

	def save(self):
		if self.currentLesson == None:
			cl = "Empty"
		else:
			cl = self.currentLesson
		memcache.set("Student:" + self.username + "|CurrentLesson:" + cl, self)
		self.put()
	
	def joinLesson(self, lessonName):
		assert lessonName in getOpenLessonsNames()
		lesson = getLesson(lessonName)
		lesson.addStudent(self)
		self.currentLesson = lessonName
		self.save()
		self.alertTeacherImArrived()
		#~ send message to teacher that the user is connected
		
	def alertTeacherImArrived(self):
		lesson = getLesson(self.currentLesson)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "student arrived",
			"message": {
				"student": self.username
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
class Teacher(User):
	password = ndb.StringProperty()
	def save(self):
		memcache.set("Teacher:" + self.username, self)
		self.put()
	
def teacherUsernameExists(username):
	if getTeacher(username):
		return True
	else:
		return False

def getTeacher(username):
	teacher = memcache.get("Teacher:" + username)
	if not teacher:
		q = Teacher.query(Teacher.username == username)
		teacher = q.get()
		if teacher:
			memcache.set("Teacher:" + self.username, self)
	if teacher:
		return teacher
	else:
		return False

def getStudent(username, currentLesson):
	student = memcache.get("Student:" + self.username + \
					"|CurrentLesson:" + self.currentLesson)
	if not student:
		q = Student.query(Student.username == username,
							Student.currentLesson == currentLesson)
		student = q.get()
		if student:
			memcache.set("Student:" + self.username + \
					"|CurrentLesson:" + self.currentLesson, self)
	if student:
		return student
	else:
		return False
		
def studentAlreadyConnected(username):
	q = Student.query(Student.username == username, Student.currentLesson != "")
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
		memcache.set("Lesson:" + self.lessonName, self)
		self.put()
	
	def addStudent(self, student):
		self.students.append(student.username)
		self.save()
	
def getOpenLessonsNames():
	q = Lesson.query(Lesson.status == "open")
	if q.count(limit=None) > 0:
		lessons = q.fetch(limit=None)
		return [lesson.lessonName for lesson in lessons]
	else:
		return []

def getLesson(lessonName):
	lesson = memcache.get("Lesson:" + lessonName)
	if not lesson:
		q = Lesson.query(Lesson.lessonName == lessonName)
		lesson = q.get()
		if lesson:
			memcache.set("Lesson:" + self.lessonName, self)
	if lesson:
		return lesson
	else:
		return False

#~ class Vars(ndb.Model):
	#~ key = ndb.StringProperty()
	#~ value = ndb.StringProperty()
	#~ list = ndb.StringProperty(repeated=True)
	
def clean():
	ndb.delete_multi(Lesson.query().fetch(keys_only=True))
	#~ ndb.delete_multi(Session.query().fetch(keys_only=True))
	ndb.delete_multi(Student.query().fetch(keys_only=True))
	ndb.delete_multi(Teacher.query().fetch(keys_only=True))
	memcache.flush_all()
