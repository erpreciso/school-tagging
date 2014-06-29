from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import channel
import logging
import json
import random
import re

class User(ndb.Model):
	username = ndb.StringProperty()
	status = ndb.StringProperty()
	currentLesson = ndb.StringProperty()
	lessons = ndb.StringProperty(repeated=True)
	token = ndb.StringProperty()
	currentSession = ndb.StringProperty()

	def connect(self):
		logging.info(self.key)
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
		self.put()
		memcache.set("Student:" + self.username + "|CurrentLesson:" + cl, self)
		
	
	def joinLesson(self, lessonName):
		assert lessonName in getOpenLessonsNames()
		lesson = getLesson(lessonName)
		lesson.addStudent(self)
		self.currentLesson = lessonName
		self.save()
		self.alertTeacherImArrived()
		
	def alertTeacherImArrived(self):
		lesson = getLesson(self.currentLesson)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "student arrived",
			"message": {
				"studentName": self.username
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
	def logout(self):
		self.alertTeacherImLogout()
		self.token = ""
		self.currentLesson = ""
		self.status = ""
		self.save()
			
	def alertTeacherImLogout(self):
		# TODO merge all messages to alert teacher
		lesson = getLesson(self.currentLesson)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "student logout",
			"message": {
				"studentName": self.username
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
class Teacher(User):
	password = ndb.StringProperty()
	def save(self):
		self.put()
		memcache.set("Teacher:" + self.username, self)
		
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
			memcache.set("Teacher:" + username, teacher)
	if teacher:
		return teacher
	else:
		return False

def getStudent(username, currentLesson):
	student = memcache.get("Student:" + username + \
					"|CurrentLesson:" + currentLesson)
	if not student:
		q = Student.query(Student.username == username,
							Student.currentLesson == currentLesson)
		student = q.get()
		if student:
			memcache.set("Student:" + username + \
					"|CurrentLesson:" + currentLesson, student)
	if student:
		return student
	else:
		return False
		
def getFromID(id):
	user = memcache.get("ID:" + id)
	if not user:
		user = ndb.Key("Teacher", int(id)).get() \
							or ndb.Key("Student", int(id)).get()
		#~ user = ndb.get_by_id(int(id))
		if user:
			memcache.set("ID:" + str(id), user)
			return user
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
		self.put()
		memcache.set("Lesson:" + self.lessonName, self)
	
	def addStudent(self, student):
		self.students.append(student.username)
		self.save()
	
	def removeStudent(self, student):
		self.students.remove(student)
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
			memcache.set("Lesson:" + lessonName, lesson)
	if lesson:
		return lesson
	else:
		return False
	
def getSentence():
	pool = open("sentence-pool.txt").readlines()
	i = int(random.random() * len(pool))
	return pool[i]
	
def clean():
	ndb.delete_multi(Lesson.query().fetch(keys_only=True))
	#~ ndb.delete_multi(Session.query().fetch(keys_only=True))
	ndb.delete_multi(Student.query().fetch(keys_only=True))
	ndb.delete_multi(Teacher.query().fetch(keys_only=True))
	memcache.flush_all()


class Session(ndb.Model):
	teacher = ndb.StringProperty()
	lesson = ndb.StringProperty()
	students = ndb.StringProperty(repeated=True)
	exerciseText = ndb.StringProperty()
	target = ndb.IntegerProperty()
	answersProposed = ndb.StringProperty(repeated=True)
	exerciseWords = ndb.StringProperty(repeated=True)
	

	def save(self):
		self.put()
		memcache.set("Session:" + str(self.key.id), self)
		return self.key.id()
		
	def start(self, lessonName):
		self.lesson = lessonName
		lesson = getLesson(lessonName)
		self.teacher = lesson.teacher
		self.students = lesson.students
		self.exerciseText = getSentence()
		self.exerciseWords = re.split(' ', self.exerciseText)
		self.answersProposed = ["noun", "adj", "verb"]
		self.target = int(random.random() * len(self.exerciseWords))
		id = self.save()
		message = {
			"type": "session",
			"message": {
				"id": id,
				"wordsList": self.exerciseWords,
				"answersProposed": self.answersProposed
				},
			}
		message = json.dumps(message)
		for studentName in self.students:
			student = getStudent(studentName, self.lesson)
			channel.send_message(student.token, message)
		
