# coding: utf-8
# [school-tagging] webapp

import webapp2
import jinja2
import os

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

class HomePageHandler(MainHandler):
	def get(self):
		self.render_page("content.html")

app = webapp2.WSGIApplication([
    ('/', HomePageHandler)
], debug=True)
