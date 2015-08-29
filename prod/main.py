## school-tagging --> an educative Student / Classroom
##    Response Systems designed to help teaching and merge into
##    academic research.
##    Copyright (C) 2014  Stefano Merlo, Federico Sangati, Giovanni Moretti.
## This program comes with ABSOLUTELY NO WARRANTY.
## This is free software, and you are welcome to redistribute it
## under certain conditions (i.e. attribution); for details refer
##     to 'LICENSE.txt'.
"""This module manages the http requests/response to the appengine.
It depends from the objects.py module, that contains all objects."""

# coding: utf-8
# pylint: disable=import-error, no-member, maybe-no-member, no-init
# [school-tagging] webapp

import objects as objs
import labelsDictionary as labdict
import webapp2
import jinja2
import os
import datetime
import logging

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
        params["env"] = os.environ["DEV_WORKFLOW_STATUS"]
        return self.jinja_env.get_template(template).render(params)

    def render_page(self, template, **kw):
        """Render a jinja2 template."""
        self.write(self.render_str(template, **kw))

    def add_cookie(self, kind, value):
        """Set a cookie in the html response."""
        expires_time = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        self.response.set_cookie(kind, value=str(value),
                                 httponly=True, expires=expires_time)

    def get_cookie(self, kind):
        """Get cookie from http response."""
        return self.request.cookies.get(kind)

    def clear_cookies(self):
        """Clear all application-related cookies."""
        self.response.delete_cookie("schooltagging-username")
        self.response.delete_cookie("schooltagging-lesson-id")
        self.response.delete_cookie("schooltagging-role")


    def get_role_from_cookie(self):
        """Get if student or teacher from the cookie."""
        return self.get_cookie("schooltagging-role")

    def get_from_cookie(self):
        """Return the user object from the cookie."""
        username = self.get_cookie("schooltagging-username")
        lesson_str_id = self.get_cookie("schooltagging-lesson-id")
        role = self.get_cookie("schooltagging-role")
        if not username or not role or not lesson_str_id:
            return False
        if role == "student":
            user = objs.getStudent(username, int(lesson_str_id))
        elif role == "teacher":
            user = objs.getTeacher(username)
        return user

class StartPage(MainHandler):
    """Handler from the initial start page."""
    def get(self):
        """GET method."""
        link = None
        user = self.get_from_cookie()
        if user and user.currentLessonID:
            lesson = objs.getLesson(user.currentLessonID)
            if lesson:
                if self.get_role_from_cookie() == "teacher":
                    link = "/t/dashboard"
                elif self.get_role_from_cookie() == "student":
                    link = "/s/dashboard"
        self.render_page("start.html", resumeDashboardLink=link)

class TeacherHandler(MainHandler):
    """Main teacher pages handler."""
    def get(self, action):
        """GET method."""
        if action == "dashboard":
            self.initialize_dashboard()
        elif action == "logout":
            self.logout()
        elif action == "timeIsUp":
            self.end_exercise()
        elif action == "askStats":
            self.send_stats()
        else:
            self.render_login_page()

    def render_login_page(self, message=None):
        """Render teacher login page."""
        templ = "teacherLogin.html"
        if message:
            msg = labdict.labels(templ, objs.DEFAULT_LANGUAGE)[message]
        else:
            msg = None
        self.render_page(templ,
                         labels=labdict.labels(templ, objs.DEFAULT_LANGUAGE),
                         message=msg)

    def post(self, action):
        """POST method."""
        if action == "login":
            self.login()
        elif action == "signup":
            self.signup()
        elif action == "askStudentStats":
            self.produce_student_stats(self.read("student"))


    def login(self):
        """Login the teacher."""
        fullname = self.read("username")
        username = fullname.replace(" ", "_")
        password = self.read("password")
        if objs.teacherUsernameExists(username):
            teacher = objs.getTeacher(username)
            if password == teacher.password:
                lesson_name = self.read("lesson_name")
	        logging.info(lesson_name)
                if lesson_name:
                    if lesson_name not in objs.getOpenLessonsNames():
                        teacher.connect()
                        self.add_cookie("schooltagging-role", "teacher")
                        self.add_cookie("schooltagging-username", username)
                        self.start_lesson(teacher)
                        return self.redirect("/t/dashboard")
                    else:
                        message = "lesson_name_in_use"
                else:
                    message = "provide_lesson_name"
            else:
                message = "password_not_correct"
        else:
            message = "username_not_existing"
        return self.render_login_page(message)

    def logout(self):
        """Logout the teacher."""
        teacher = self.get_from_cookie()
        if teacher:
            self.clear_cookies()
            if teacher.currentExercise:
                exercise = objs.getExercise(teacher.currentExercise)
                if exercise:
                    exercise.end()
            if teacher.currentLessonID:
                lesson = objs.getLesson(teacher.currentLessonID)
                if lesson:
                    lesson.end()
                teacher.logout()
        return self.redirect("/t/login")

    def signup(self):
        """Signup teacher."""
        fullname = self.read("username")
        username = fullname.replace(" ", "_")
        if not objs.teacherUsernameExists(username):
            password = self.read("password")
            objs.createTeacher(username, password, fullname)
            message = "re-enter_login"
        else:
            message = "username_already_used"
        return self.render_login_page(message)

    def start_lesson(self, teacher):
        """Start a lesson."""
        lesson_name = self.read("lesson_name")
        if lesson_name not in objs.getOpenLessonsNames():
            lesson = objs.Lesson()
            lesson.start(lesson_name, teacher)
            self.add_cookie("schooltagging-lesson-id", str(lesson.key.id()))
            return self.redirect("/t/dashboard")
        else:
            message = "lesson_name_in_use"
        return self.render_login_page(message)

    def send_stats(self):
        """Send lesson stats to the teacher."""
        teacher = self.get_from_cookie()
        if not teacher:
            return self.redirect("/t/login")
        if not teacher.currentLessonID:
            return self.redirect("/t/login")
        lesson = objs.getLesson(teacher.currentLessonID)
        if lesson:
            return lesson.produceAndSendStats()
        else:
            return self.redirect("/t/login")

    def produce_student_stats(self, student_name):
        """Produce stats regarding students."""
        teacher = self.get_from_cookie()
        if not teacher:
            return self.redirect("/t/login")
        if not teacher.currentLessonID:
            return self.redirect("/t/login")
        student = objs.getStudent(student_name, teacher.currentLessonID)
        if student:
            return student.produceAndSendOwnStats()
        else:
            return self.redirect("/t/login")

    def initialize_dashboard(self):
        """Create teacher dashboard."""
        teacher = self.get_from_cookie()
        if not teacher:
            return self.redirect("/t/login")
        if not teacher.currentLessonID:
            return self.redirect("/t/login")
        language = teacher.language or objs.DEFAULT_LANGUAGE
        lesson = objs.getLesson(teacher.currentLessonID)
        if lesson:
            templ = "teacherDashboard.html"
            student_labels = []
            for student_name in lesson.students:
                student = objs.getStudent(student_name, teacher.currentLessonID)
                if student:
                    student_labels.append({"username":student_name,
                                          "fullname":student.fullname})
            return self.render_page(templ,
                                teacherName=teacher.fullname,
                                lesson_name=teacher.currentLessonName,
                                students=student_labels,
                                token=teacher.token,
                                language=language,
                                labels=labdict.labels(templ, language),
                                )
        else:
            return self.redirect("/t/login")

    def end_exercise(self):
        """Terminate an exercise."""
        teacher = self.get_from_cookie()
        exercise = objs.getExercise(teacher.currentExercise)
        if exercise:
            exercise.end()

class DataHandler(MainHandler):
    """Manage data incoming from clients."""
    def get(self, kind):
        """GET method."""
        requester = self.get_from_cookie()
        requester_role = self.get_role_from_cookie()
        if requester_role == "teacher":
            if kind == "simple_exercise_request":
                lesson_id = requester.currentLessonID
                exercise = objs.Exercise()
                exercise.start(lesson_id, "simple")
            elif kind == "complex_exercise_request":
                lesson_id = requester.currentLessonID
                exercise = objs.Exercise()
                exercise.start(lesson_id, "complex",
                               self.request.get('category'))

    def post(self, kind):
        """POST method."""
        requester = self.get_from_cookie()
        requester_role = self.get_role_from_cookie()
        if requester_role == "teacher":
            teacher = requester
            if kind == "teacherValidation":
                valid = self.request.get("valid")
                exercise = objs.getExercise(teacher.currentExercise)
                exercise.addNdbAnswer("teacher", teacher.username, valid)
                exercise.sendFeedbackToStudents()
            if kind == "getSessionStatus":
                exercise = objs.getExercise(teacher.currentExercise)
                exercise.sendStatusToTeacher()
        if requester_role == "student":
            student = requester
            if kind == "answer":
                answer = self.request.get("answer")
                exercise_id_sent = self.request.get("exerciseID")
                if str(exercise_id_sent) == str(student.currentExercise):
                    exercise = objs.getExercise(student.currentExercise)
                    if student.username not in exercise.students:
                        exercise.addStudent(student)
                    if exercise.addNdbAnswer("student",
                                               student.username, answer):
                        exercise.sendStatusToTeacher()
                    else:
                        logging.error("Warning! Answer not saved")
                else:
                    logging.error("Student " + student.fullname +
                                  "Sent answer of a different exercise")

class StudentHandler(MainHandler):
    """Handler for students pages."""
    def get(self, action):
        """GET method."""
        if action == "dashboard":
            self.initialize_dashboard()
        elif action == "login":
            self.render_login_page()
        elif action == "logout":
            self.logout()

    def post(self, action):
        """POST method."""
        if action == "login":
            self.login()

    def render_login_page(self, message=None):
        """Render student login page."""
        templ = "studentLogin.html"
        if message:
            msg = labdict.labels(templ, objs.DEFAULT_LANGUAGE)[message]
        else:
            msg = None
        self.render_page(templ,
                         labels=labdict.labels(templ, objs.DEFAULT_LANGUAGE),
                         message=msg)

    def login(self):
        """Login a student."""
        student = objs.Student()
        student.fullname = self.read("username")
        student.username = student.fullname.replace(" ", "_")
        student.language = objs.DEFAULT_LANGUAGE
        lesson_name = self.read("lesson_name")
        if lesson_name in objs.getOpenLessonsNames():
            if not objs.studentAlreadyConnected(student.username, lesson_name):
                student.save()
                student.connect()
                self.add_cookie("schooltagging-role", "student")
                self.add_cookie("schooltagging-username", student.username)
                lesson_id = student.joinLesson(lesson_name)
                self.add_cookie("schooltagging-lesson-id", lesson_id)
                return self.redirect("/s/dashboard")
            else:
                message = "name_already_in_use"
        else:
            message = "lesson_not_started"
        self.render_login_page(message)

    def initialize_dashboard(self):
        """Create student dashboard."""
        student = self.get_from_cookie()
        if not student:
            self.clear_cookies()
            return self.redirect("/s/login")
        templ = "studentDashboard.html"
        language = student.language or objs.DEFAULT_LANGUAGE
        self.render_page(templ,
                    studentFullName=student.fullname,
                    lesson_name=student.currentLessonName,
                    token=student.token,
                    language=language,
                    labels=labdict.labels(templ, language),
                    )
    def logout(self):
        """Logout a student."""
        student = self.get_from_cookie()
        if student:
            self.clear_cookies()
            student.logout()
        return self.redirect("/s/login")

class DeleteHandler(MainHandler):
    """Delete all cookies."""
    def get(self):
        """GET method."""
        objs.clean()
        for name in self.request.cookies.iterkeys():
            self.response.delete_cookie(name)
        return self.redirect("/start")

class ConnectionHandler(MainHandler):
    "Manage connections."""
    def post(self, action):
        """ channel service interrupted from yaml"""
        user = objs.getFromID(self.request.get('from'))
        if user:
            if user.__class__.__name__ == "Student":
                student = user
                if action == "disconnected":
                    return student.alertTeacherImOffline()

class ChannelHandler(MainHandler):
    """Manage channels requests."""
    def get(self):
        """GET method."""
        requester = self.get_from_cookie()
        idle = datetime.datetime.now() - requester.lastAction
        if idle < datetime.timedelta(minutes=objs.MAX_IDLE_ALLOWED):
            return requester.connect()
        else:
            return requester.logout()

class PingHandler(MainHandler):
    """Manage pings for student alive."""
    def post(self):
        """POST method."""
        requester = self.get_from_cookie()
        requester_role = self.get_role_from_cookie()
        if requester_role == "teacher":
            teacher = requester
            student_name = self.read("student")
            return teacher.sendPingToStudent(student_name)
        elif requester_role == "student":
            student = requester
            return student.alertTeacherImAlive()

class LosingFocusHandler(MainHandler):
    """When the student looses focus on the browser."""
    def post(self):
        """POST method."""
        requester = self.get_from_cookie()
        status = self.request.get("focus")
        requester_role = self.get_role_from_cookie()
        assert requester_role == "student"
        student = requester
        if student:
            student.alertTeacherAboutMyFocus(status)

class ForceLogoutStudentHandler(MainHandler):
    """Force logout for a student."""
    def post(self):
        """POST method."""
        requester = self.get_from_cookie()
        requester_role = self.get_role_from_cookie()
        if requester_role == "teacher":
            teacher = requester
            student_name = self.read("student")
            student = objs.getStudent(student_name, teacher.currentLessonID)
            if student:
                return student.logout()

class ExportPage(MainHandler):
    """Export data in json."""
    def get(self):
        """GET method."""
        data = objs.exportJson()
        return self.write(data)

class JollyHandler(MainHandler):
    """Redirect to start."""
    def get(self, dummy):
        """GET method."""
        return self.redirect("/start")

class HelpHandler(MainHandler):
    """Help page."""
    # currently the hyperlink to get here, originally in "wrapper.html",
    # has been removed.
    def get(self):
        """GET method."""
        return self.render_page("helpIndex.html")

#pylint: disable=no-self-use
class CleanIdle(MainHandler):
    """Clean open objects."""
    def get(self):
        """GET method."""
        objs.cleanIdleObjects()

class LanguageHandler(MainHandler):
    """To manage languages."""
    def post(self):
        """POST method."""
        requester = self.get_from_cookie()
        if requester:
            language = self.read("language")
            requester.language = language
            requester.save()
            return

class LanguageDictionaryHandler(MainHandler):
    """Manage language dictionary."""
    def get(self):
        """GET method."""
        requester = self.get_from_cookie()
        if requester:
            requester.sendMeLanguageDict()

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
#pylint: disable=invalid-name
app = webapp2.WSGIApplication([
    webapp2.Route(r'/t/<action>', handler=TeacherHandler, name="teacher"),
    webapp2.Route(r'/s/<action>', handler=StudentHandler, name="student"),
    webapp2.Route(r'/data/<kind>', handler=DataHandler, name="data"),
    webapp2.Route(r'/_ah/channel/<action>/', handler=ConnectionHandler,
                  name="connection"),
    ("/export", ExportPage),
    ("/start", StartPage),
    ("/admin/delete", DeleteHandler),
    ("/ping", PingHandler),
    ("/focus", LosingFocusHandler),
    ("/forceLogoutStudent", ForceLogoutStudentHandler),
    ("/help", HelpHandler),
    ("/admin/clean", CleanIdle),
    ("/channelExpired", ChannelHandler),
    ("/language", LanguageHandler),
    ("/get_language_dict", LanguageDictionaryHandler),
    (PAGE_RE, JollyHandler),
            ])
