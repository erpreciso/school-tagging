# coding: utf-8
# [school-tagging] webapp

import objects as objs
import webapp2
import jinja2
import os
import re
import random
import string
import hashlib
import logging
import json
from google.appengine.api import channel
from google.appengine.ext import ndb
from google.appengine.api import memcache

LANGUAGE = "IT"

class MainHandler(webapp2.RequestHandler):
	template_dir = os.path.join(os.path.dirname(__file__), 'pages')
	jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
		autoescape = True)
	def writeout(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def readout(self,param):
		return self.request.get(param)
		
	def render_str(self, template, **params):
		return self.jinja_env.get_template(template).render(params)
		
	def render_page(self, template, **kw):
		self.writeout(self.render_str(template, **kw))

class teacherLessonStart(MainHandler):
	def writePage(self, username):
		self.render_page(
				"TeacherLessonStart.html",
				labels = dictLabelBook["TeacherLessonStart"],
				language = LANGUAGE,
				username = username,
				)
	def get(self):
		username = self.request.cookies.get("schooltagging-user")
		if username:
			self.writePage(username)
		else:
			self.redirect("/login")
	
	def post(self):
		lessonName = self.request.get("lessonName")
		username = self.request.cookies.get("schooltagging-user")
		objs.addLesson(username, lessonName)
		self.response.set_cookie('schooltagging-lesson', lessonName)
		return self.redirect("/dashboard")

class teacherLogin(MainHandler):
	error = None
	def writePage(self):
		self.render_page(
				"TeacherLogin.html",
				labels = dictLabelBook["TeacherLogin"],
				language = LANGUAGE,
				error = self.error,
				)
				
	def get(self, *a):
		self.writePage()
		
	def post(self, *a):
		user = objs.User()
		user.setUsername(self.request.get("username"))
		user.setPassword(self.request.get("password"))
		status = user.get()
		if status == "OK":
			self.response.set_cookie('schooltagging-user', user.username)
			self.redirect("/lessonstart")
			return
		else:
			self.error = status
			self.writePage()

class teacherSignup(MainHandler):
	error = None
	def writePage(self):
		self.render_page(
				"TeacherSignup.html",
				labels = dictLabelBook["TeacherSignup"],
				language = LANGUAGE,
				error = self.error,
				)
	def get(self):
		self.writePage()
		
	def post(self):
		user = objs.User()
		user.setUsername(self.request.get("username"))
		user.setPassword(self.request.get("password"))
		user.setVerifyPassword(self.request.get("verify"))
		status = user.save()
		logging.info(status)
		if status == "OK":
			self.response.set_cookie('schooltagging-user', user.username)
			self.redirect("/lessonstart")
			return
		else:
			self.error = status
			self.writePage()
			
app = webapp2.WSGIApplication([
	webapp2.Route(
			r'/t',
			handler=teacherLogin,
			name="teacherLogin"),
	webapp2.Route(
			r'/lessonstart',
			handler=teacherLessonStart,
			name="teacherLessonStart"),
	webapp2.Route(
			r'/signup',
			handler=teacherSignup,
			name="teacherSignup"),
	webapp2.Route(
			r'/<:[a-zA-Z0-9]*>',
			handler=teacherLogin,
			name="jolly"),
			])

dictLabelBook = {
	"TeacherLogin": {
		"username": {
			"EN": "Username",
			"IT": "Nome utente",
			},
		"password": {
			"EN": "Password",
			"IT": "Password",
			},
		"or_signup": {
			"EN": "or Signup",
			"IT": "oppure registrati",
			},
		"login": {
			"EN": "Login",
			"IT": "Entra",
			},
		},
	"TeacherSignup": {
		"username": {
			"EN": "Username",
			"IT": "Nome utente",
			},
		"password": {
			"EN": "Password",
			"IT": "Password",
			},
		"verify": {
			"EN": "Verify password",
			"IT": "Ripeti la password",
			},
		"register": {
			"EN": "Register my data",
			"IT": "Registrami",
			},
		},
	"TeacherLessonStart": {
		"lesson_name": {
			"EN": "Lesson name",
			"IT": "Nome per la lezione",
			},
		"": {
			"EN": "",
			"IT": "",
			},
		"welcome": {
			"EN": "Welcome",
			"IT": "Benvenuto",
			},
		"start": {
			"EN": "Start the lesson",
			"IT": "Inizia la lezione",
			},
		},
	}
			
