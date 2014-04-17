	# coding: utf-8
# [school-tagging] webapp
# module st
# this module contains the core logic of the game

import logging
try:
	from google.appengine.ext import ndb
	from google.appengine.api import memcache
except:
	pass

class Teacher():
	def __init__(self, name):
		self.name = name
		self.lessons = []
		self.current_lesson = None
	def set_lesson(self, lesson):
		self.current_lesson = lesson

class Lesson():
	def __init__(self, teacher):
		self.sessions = []
		self.teacher = teacher
	def save(self):
		memcache.add("lesson:%s" % self.teacher.name, self)

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
	def save(self):
		memcache.add("session:%s" % self.teacher.name, self)

class Student():
	def __init__(self, name):
		self.name = name
		self.sessions = {}
	def assign_session(self, session):
		self.sessions[session] = {"answers": [], "correct": True}
	def add_answer(self, session, answer):
		my = self.sessions[session]
		my["answers"].append(answer)
		my["correct"] = session.is_correct_answer(answer)
		
	def sessions_token(self):
		return len(self.sessions.keys())
	def corrects(self):
		return len([student for student in self.sessions.keys() if \
					self.sessions[student]["correct"] == True])
		
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


def start_lesson(username):
	teacher = Teacher(name=username)
	lesson = Lesson(teacher)
	teacher.lessons.append(lesson)
	return lesson

def get_lesson(username):
	teacher = Teacher(name=username)  # TODO replace with datastore instances
	lesson = memcache.get("lesson:%s" % teacher.name)
	return lesson

def start_session(lesson):
	teacher = lesson.teacher
	session = Session(lesson)
	lesson.sessions.append(session)
	memcache.add("current_session:%s" % lesson, session)
	return session
	
def get_current_session(lesson):
	return memcache.get("current_session:%s" % lesson)
	
	

