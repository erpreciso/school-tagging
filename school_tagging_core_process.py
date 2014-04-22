from time import localtime, strftime
from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging

def nowtime():
	return strftime("%Y-%m-%d-%H:%M:%S", localtime())

class Person(ndb.Model):
	name = ndb.StringProperty()
	currentLesson = ndb.StringProperty()
	connected = ndb.BooleanProperty()

class Teacher(Person):
	lessons = ndb.StringProperty(repeated=True)
	def safe_put(self):
		memcache.set("teacher:" + self.name, self)
		self.put()
		
class Student(Person):
	answers = ndb.PickleProperty()
	def safe_put(self):
		memcache.set("student:" + self.name, self)
		self.put()

class Lesson(ndb.Model):
	name = ndb.StringProperty()
	sessions = ndb.StringProperty(repeated=True)
	teacher = ndb.StringProperty()
	students = ndb.StringProperty(repeated=True)
	currentSession = ndb.StringProperty()
	
	def safe_put(self):
		memcache.set("lesson:" + self.name, self)
		self.put()

def add_teacher(strTeacher, strLesson):
	objTeacher = Teacher(id=strTeacher)
	objTeacher.name = strTeacher
	objTeacher.lessons = []
	objTeacher.currentLesson = strLesson
	objTeacher.connected = True
	objTeacher.safe_put()
	update_teachers_list("add", strTeacher)
	return objTeacher

def get_teachers_list():
	lst = memcache.get("teachers_list")
	if not lst:
		lst = []
		q = Teacher.query()
		if q.get():
			lst = [t.name for t in q]
		memcache.add("teachers_list", lst)
	return lst
				
def update_teachers_list(command, strTeacher):
	lst = get_teachers_list()
	if command == "add":
		lst.append(strTeacher)
		memcache.set("teachers_list", lst)
	return

def add_student(strStudent, strLesson):
	objStudent = Student(id=strStudent)
	objStudent.name = strStudent
	objStudent.currentLesson = strLesson
	objStudent.answers = {}
	objStudent.connected = True
	objStudent.safe_put()
	return objStudent

def disconnect_student(strStudent):
	student = get_student(strStudent)
	if student:
		student.connected = False
		student.safe_put()
	
	
def get_current_lesson_student_list(strTeacher):
	"""return list of string students for the current lesson of the teacher."""
	objTeacher = get_teacher(strTeacher)
	strCurrentLesson = objTeacher.currentLesson
	objCurrentLesson = get_lesson(strCurrentLesson)
	students = [s for s in objCurrentLesson.students \
						if get_student(s).connected == True]
	return students

def get_teacher(strTeacher):
	t = memcache.get("teacher:" + strTeacher)
	if not t:
		k = ndb.Key("Teacher", strTeacher)
		t = k.get()
		memcache.add("teacher:" + strTeacher, t)
	return t

def get_student(strStudent):
	t = memcache.get("student:" + strStudent)
	if not t:
		k = ndb.Key("Student", strStudent)
		t = k.get()
		memcache.add("student:" + strStudent, t)
	return t

def add_lesson(strTeacher, strLesson):
	objTeacher = add_teacher(strTeacher, strLesson)
	objLesson = Lesson(id=strLesson)
	objLesson.name = strLesson
	objLesson.teacher = strTeacher
	objLesson.safe_put()
	return objLesson

def get_lesson(strLesson):
	t = memcache.get("lesson:" + strLesson)
	if not t:
		k = ndb.Key("Lesson", strLesson)
		t = k.get()
		memcache.add("lesson:" + strLesson, t)
	return t

def join_lesson(strStudent, strTeacher):
	objTeacher = get_teacher(strTeacher)
	strLesson = objTeacher.currentLesson
	objStudent = add_student(strStudent, strLesson)
	objLesson = get_lesson(strLesson)
	if strStudent not in objLesson.students:
		objLesson.students.append(strStudent)
	objLesson.safe_put()
	return strLesson
	
class Session(ndb.Model):
	start = ndb.StringProperty()
	exercise = ndb.PickleProperty()
	exerciseType = ndb.PickleProperty()
	lesson = ndb.StringProperty()
	students = ndb.StringProperty(repeated=True)
	
	def safe_put(self):
		memcache.set("session:" + self.start, self)
		self.put()

def add_session(objLesson, objExercise, objExerciseType):
	strSession = nowtime()
	objSession = Session(id=strSession)
	objSession.start = strSession
	objSession.lesson = objLesson.name
	objSession.exercise = objExercise
	objSession.exerciseType = objExerciseType
	objSession.students = objLesson.students
	objSession.safe_put()
	objLesson.currentSession = strSession
	objLesson.safe_put()
	return strSession

def get_session(strSession):
	t = memcache.get("session:" + strSession)
	if not t:
		k = ndb.Key("Session", strSession)
		t = k.get()
		memcache.add("session:" + strSession, t)
	return t

def add_answer(objStudent, objLesson, strExerciseType, strAnswer):
	strSession = objLesson.currentSession
	objSession = get_session(strSession)
	if strSession in objStudent.answers.keys():
		objStudent.answers[strSession].append(strAnswer)
	else:
		objStudent.answers[strSession] = [strAnswer]
	booCorrect = strAnswer in objSession.exerciseType["answers"]
	logging.info(booCorrect)
	
#~ class Session():
	#~ def __init__(self, lesson):
		#~ self.question = None
		#~ self.lesson = lesson
		#~ self.students = {}
	#~ def add_student(self, student):
		#~ self.students[student] = {"answers": [], "correct": False}
	#~ def set_question(self, question):
		#~ self.question = question
	#~ def assign_to_students(self):
		#~ for student in self.students.keys():
			#~ student.assign_session(self)
	#~ def is_correct_answer(self, answer):
		#~ return self.question.is_right_answer(answer)
		
#~ class Question():
	#~ def __init__(self):
		#~ self.id = None
		#~ self.sentence = None
		#~ self.words = None
		#~ self.author = None
#~ 
#~ class FindTheElement(Question):
	#~ def __init__(self):
		#~ self.description = "Find the Element"
		#~ self.to_find = None  # what we're looking for
		#~ self.answers = []  # which word is the correct answer
	#~ def __repr__(self):
		#~ result = '\nType:"' + self.description + '"'
		#~ result = result + "\nInstructions: given the sentence, find the " + self.to_find
		#~ result = result + "\nSentence:" + self.sentence
		#~ return result
	#~ def is_right_answer(self, answer):
		#~ return answer in self.answers
#~ 
#~ class WhichType(Question):
	#~ def __init__(self):
		#~ self.description = "Which type is this"
		#~ self.instructions = ""
		#~ self.options = []    # options provided
		#~ self.answer = None    # only one possible answer
	#~ def __repr__(self):
		#~ result = '\nType:"' + self.description + '"'
		#~ result = result + "\nInstructions: select the correct type of the word indicated"
		#~ result = result + "\nSentence:" + self.sentence
		#~ result = result + "\nOptions:" + str(self.options)
		#~ return result
	#~ def is_right_answer(self, answer):
		#~ return answer == self.answer
