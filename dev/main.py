import webapp2
from google.appengine.api import channel

class MainPage(webapp2.RequestHandler):
    def get(self):
        token = channel.create_channel("id1")
        self.response.out.write(getHtml(token))

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

def getHtml(token):
    return """
<html>
<style type="text/css">
body {
  font-family : sans-serif;
}
</style> 
<body>
<div>The token is <strong>""" + token + """</strong></div>
<script src="/static/jquery.min.js"></script>
  <script>
    channel = new goog.appengine.Channel('""" + token + """');
    socket = channel.open();
    socket.onopen = onOpened;
    socket.onmessage = onMessage;
    socket.onerror = onError;
    socket.onclose = onClose;
  </script>
</body>
</html>
"""
