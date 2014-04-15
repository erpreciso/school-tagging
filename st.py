	# coding: utf-8
# [school-tagging] webapp
# module st
# this module contains the core logic of the game

from google.appengine.ext import ndb
from google.appengine.api import memcache

def create_lesson(teacher):
	lesson = Lesson(teacher)
	return lesson

def get_lesson(teacher):
	lesson = memcache.get("lesson:%s" % teacher)
	return lesson
	
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
class Person():
	pass
		
class Student(Person):
	def __init__(self, name=None):
		self.name = name
		self.exercises = []
	def assign_exercise(self, exercise):
		self.exercises.append(exercise)
	def exercises_token(self):
		""" return the number of exercises done"""
		return len(self.exercises)
	def corrects(self):
		"""return the count of correct exercises"""
		result = 0
		for exercise in self.exercises:
			if exercise.is_correct():
				result += 1
		return result
	def answers(self, session, answer):
		for exercise in self.exercises:
			if exercise.question == session.question:
				exercise.answers.append(answer)
				if exercise.is_correct():
					session.corrects += 1

class Teacher(Person):
	def __init__(self, name=None):
		self.name = name
		self.sessions = [] # list of session he partecipated
class Session():
	def __init__(self, lesson):
		self.question = None
		self.lesson = lesson
		lesson.add_session(self)
		self.corrects = 0
		self.students = self.lesson.students
	def add_question(self, question):
		self.question = question
	def assign_to_classroom(self):
		for student in self.students:
			exercise = Exercise(question=self.question)
			student.assign_exercise(exercise)
class Exercise():
	def __init__(self, question):
		self.question = question
		self.answers = []
	def is_correct(self):
		for a in self.answers:
			if self.question.is_right_answer(a):
				return True
		return False

class Lesson():
	def __init__(self, teacher):
		self.students = []
		self.sessions = []
		self.teacher = teacher
	def add_student(self, student):
		self.students.append(student)
	def add_session(self, session):
		self.sessions.append(session)
	
	def save(self):
		memcache.add("%s:%s" % ("lesson:", self.teacher), self)
		
		
	def corrects(self):
		"""return the count of correct answer given for all exercises"""
		pass
