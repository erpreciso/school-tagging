from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging


class Person(ndb.Model):
	name = ndb.StringProperty()
	currentLesson = ndb.StringProperty()


		
class Teacher(Person):
	lessons = ndb.StringProperty(repeated=True)
	def safe_put(self):
		memcache.set("teacher:" + self.name, self)
		self.put()
		
class Student(Person):
	def safe_put(self):
		memcache.set("student:" + self.name, self)
		self.put()

class Lesson(ndb.Model):
	name = ndb.StringProperty()
	sessions = ndb.StringProperty(repeated=True)
	teacher = ndb.StringProperty()
	students = ndb.StringProperty(repeated=True)
	
	def safe_put(self):
		memcache.set("lesson:" + self.name, self)
		self.put()

def add_teacher(strTeacher, strLesson):
	objTeacher = Teacher(id=strTeacher)
	objTeacher.name = strTeacher
	objTeacher.lessons = []
	objTeacher.currentLesson = strLesson
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
	objStudent.safe_put()
	return objStudent

def get_current_lesson_student_list(strTeacher):
	"""return list of string students for the current lesson of the teacher."""
	objTeacher = get_teacher(strTeacher)
	strCurrentLesson = objTeacher.currentLesson
	objCurrentLesson = get_lesson(strCurrentLesson)
	students = objCurrentLesson.students
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
	objLesson.students.append(strStudent)
	objLesson.safe_put()
	return strLesson
	

class Session():
	def __init__(self, lesson):
		self.question = None
		self.lesson = lesson
		self.students = {}
	def add_student(self, student):
		self.students[student] = {"answers": [], "correct": False}
	def set_question(self, question):
		self.question = question
	def assign_to_students(self):
		for student in self.students.keys():
			student.assign_session(self)
	def is_correct_answer(self, answer):
		return self.question.is_right_answer(answer)

#~ class Student():
	#~ def __init__(self, name):
		#~ self.name = name
		#~ self.current_lesson = None   # str lesson ID
	#~ def assign_session(self, session):
		#~ self.sessions[session] = {"answers": [], "correct": True}
	#~ def add_answer(self, session, answer):
		#~ my = self.sessions[session]
		#~ my["answers"].append(answer)
		#~ my["correct"] = session.is_correct_answer(answer)
		
	#~ def sessions_token(self):
		#~ return len(self.sessions.keys())
	#~ def corrects(self):
		#~ return len([student for student in self.sessions.keys() if \
					#~ self.sessions[student]["correct"] == True])
		
class Question():
	def __init__(self):
		self.id = None
		self.sentence = None
		self.words = None
		self.author = None

class FindTheElement(Question):
	def __init__(self):
		self.description = "Find the Element"
		self.to_find = None  # what we're looking for
		self.answers = []  # which word is the correct answer
	def __repr__(self):
		result = '\nType:"' + self.description + '"'
		result = result + "\nInstructions: given the sentence, find the " + self.to_find
		result = result + "\nSentence:" + self.sentence
		return result
	def is_right_answer(self, answer):
		return answer in self.answers

class WhichType(Question):
	def __init__(self):
		self.description = "Which type is this"
		self.instructions = ""
		self.options = []    # options provided
		self.answer = None    # only one possible answer
	def __repr__(self):
		result = '\nType:"' + self.description + '"'
		result = result + "\nInstructions: select the correct type of the word indicated"
		result = result + "\nSentence:" + self.sentence
		result = result + "\nOptions:" + str(self.options)
		return result
	def is_right_answer(self, answer):
		return answer == self.answer


LESSONS = {}

#~ { lesson ID : <obj Lesson> }

STATUS = {"lessons": {}, "teachers": {}}

#~ { "lessons" : { lesson ID : teacher name, ... },
  #~ "teachers": { teacher name : lesson ID, ... }}


	
	
	
	





	
