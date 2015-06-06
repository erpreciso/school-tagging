import os
import json
import webapp2
import jinja2
import logging
from google.appengine.api import channel

USERS = []

class MainHandler(webapp2.RequestHandler):
    """Main handler to be inherited from extension-specific handlers."""
    template_dir = os.path.join(os.path.dirname(__file__), 'pages')
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
        autoescape=True)

    def write(self, *a, **kw):
        """Write out the response."""
        self.response.out.write(*a, **kw)

    def read(self, param):
        """Read a parameter in the http request."""
        return self.request.get(param)

    def render_str(self, template, **params):
        """Print a jinjia2 template using the global variable from yaml file,
        dev or prod."""
        return self.jinja_env.get_template(template).render(params)

    def render_page(self, template, **kw):
        """Render a jinja2 template."""
        self.write(self.render_str(template, **kw))


class StartPage(MainHandler):
    """Handler from the main page."""
    def get(self):
        """GET method."""
        global USERS
        user_id = "User-" + str(len(USERS))
        tk = channel.create_channel(user_id)
        USERS.append([user_id, tk])
        self.render_page("index.html", token=tk, username=user_id)


class TextReceivedPage(webapp2.RequestHandler):
    def post(self):
        sender = self.request.get("from")
        txt = self.request.get("text")
        for user in USERS:
            message = json.dumps({"message_content": txt, "sender": sender})
            channel.send_message(user[1], message)

app = webapp2.WSGIApplication([
    ('/', StartPage),
    ('/text', TextReceivedPage),
], debug=True)

