import webapp2
import logging
from google.appengine.api import channel

class MainPage(webapp2.RequestHandler):
    def get(self):
        token = channel.create_channel("id1")
        self.response.out.write(getHtml(token))

class TextReceivedPage(webapp2.RequestHandler):
    def post(self):
        txt = self.request.get("text")
	logging.info(txt)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/text', TextReceivedPage),
], debug=True)

def getHtml(token):
    return """
<!DOCTYPE html>
<html>
<head>
  <style type="text/css">
  body {
    font-family : sans-serif;
  }
  </style> 
  <script src="/static/jquery.min.js"></script>
  <script type="text/javascript" src="/_ah/channel/jsapi"></script>
  <script>
    function sendText(textToSend) { 
      $.post("/text",{"text": textToSend});
    };
    $(document).ready(function(){
      $("#send_text").click(function(event){sendText($("textarea").val())});
    });
      

  </script>
</head>
<body>
  <div>The token is <strong>""" + token + """</strong></div>
  <div>
    <div>Listen the teacher, and fill the text area below</div>
    <textarea id="txt" cols=40></textarea>
    <button id="send_text">Send text</button>
  </div>
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
