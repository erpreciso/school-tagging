# coding: utf-8
# [school-tagging] webapp

import objects as objs
import labelsDictionary as labdict
import webapp2
import jinja2
import os
import datetime
import logging
import json

class MainHandler(webapp2.RequestHandler):
    template_dir = os.path.join(os.path.dirname(__file__), 'pages')
    jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
        autoescape = True)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def read(self,param):
        return self.request.get(param)
        
    def renderStr(self, template, **params):
        params["env"] = os.environ["DEV_WORKFLOW_STATUS"]
        return self.jinja_env.get_template(template).render(params)
        
    def renderPage(self, template, **kw):
        self.write(self.renderStr(template, **kw))

    def addCookie(self, kind, value):
        expiresTime = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        self.response.set_cookie(kind, value=str(value), httponly=True, expires=expiresTime)
    
    def getCookie(self, kind):
        return self.request.cookies.get(kind)
    
    def clearCookies(self):
        self.response.delete_cookie("schooltagging-username")
        self.response.delete_cookie("schooltagging-lessonID")
        self.response.delete_cookie("schooltagging-role")
    
    
    def getRoleFromCookie(self):
        return self.getCookie("schooltagging-role")
        
    def getFromCookie(self):
        username = self.getCookie("schooltagging-username")
        lessonStrID = self.getCookie("schooltagging-lessonID")
        role = self.getCookie("schooltagging-role")
        if not username or not role or not lessonStrID:
            return False
        if role == "student":
            user = objs.getStudent(username, int(lessonStrID))
        elif role == "teacher":
            user = objs.getTeacher(username)
        return user

class StartPage(MainHandler):
    def get(self):
        link = None
        user = self.getFromCookie()
        if user and user.currentLessonID:
            lesson = objs.getLesson(user.currentLessonID)
            if lesson:
                if self.getRoleFromCookie() =="teacher":
                    link = "/t/dashboard"
                elif self.getRoleFromCookie() == "student":
                    link = "/s/dashboard"
        self.renderPage("start.html", resumeDashboardLink=link)
        
class TeacherHandler(MainHandler):
    def get(self, action):
        if action == "dashboard":
            self.initializeDashboard()
        elif action == "logout":
            self.logout()
        elif action == "timeIsUp":
            self.endExercise()
        elif action == "askStats":
            self.sendStats()
        else:
	    self.renderLoginPage()

    def renderLoginPage(self, message=None):
        t = "teacherLogin.html"
        if message:
            m = labdict.labels(t, objs.DEFAULT_LANGUAGE)[message]
        else:
            m = None
        self.renderPage(t, labels=labdict.labels(t, objs.DEFAULT_LANGUAGE), message=m)
        
    def post(self, action):
        if action == "login":
            self.login()
        elif action == "signup":
            self.signup()
        elif action == "askStudentStats":
            self.produceStudentStats(self.read("student"))
    

    def login(self):
        fullname = self.read("username")
        username = fullname.replace(" ", "_")
        password = self.read("password")
        if objs.teacherUsernameExists(username):
            teacher = objs.getTeacher(username)
            if password == teacher.password:
                lessonName = self.read("lessonName")
                if lessonName:
                    if lessonName not in objs.getOpenLessonsNames():
                        teacher.connect()
                        self.addCookie("schooltagging-role", "teacher")
                        self.addCookie("schooltagging-username", username)
                        self.startLesson(teacher)
                        return self.redirect("/t/dashboard")
                    else:
                        message = "lesson_name_in_use"
                else:
                    message = "provide_lesson_name"
            else:
                message = "password_not_correct"
        else:
            message = "username_not_existing"
        return self.renderLoginPage(message)
        
    def logout(self):
        teacher = self.getFromCookie()
        if teacher:
            self.clearCookies()
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
        fullname = self.read("username")
        username = fullname.replace(" ", "_")
        if not objs.teacherUsernameExists(username):
            password = self.read("password")
            objs.createTeacher(username, password, fullname)
            message = "re-enter_login"
        else:
            message = "username_already_used"
        return self.renderLoginPage(message)
    
    def startLesson(self, teacher):
        lessonName = self.read("lessonName")
        if lessonName not in objs.getOpenLessonsNames():
            lesson = objs.Lesson()
            lesson.start(lessonName, teacher)
            self.addCookie("schooltagging-lessonID", str(lesson.key.id()))
            return self.redirect("/t/dashboard")
        else:
            message = "lesson_name_in_use"
        return self.renderLoginPage(message)
    
    def sendStats(self):
        teacher = self.getFromCookie()
        if not teacher:
            return self.redirect("/t/login")
        if not teacher.currentLessonID:
            return self.redirect("/t/login")
        lesson = objs.getLesson(teacher.currentLessonID)
        if lesson:
            return lesson.produceAndSendStats()
        else:
            return self.redirect("/t/login")
    
    def produceStudentStats(self, studentName):
        teacher = self.getFromCookie()
        if not teacher:
            return self.redirect("/t/login")
        if not teacher.currentLessonID:
            return self.redirect("/t/login")
        student = objs.getStudent(studentName, teacher.currentLessonID)
        if student:
            return student.produceAndSendOwnStats()
        else:
            return self.redirect("/t/login")

    def initializeDashboard(self):
        teacher = self.getFromCookie()
        if not teacher:
	    return self.redirect("/t/login")
	if not teacher.currentLessonID:
	    return self.redirect("/t/login")
	language = teacher.language or objs.DEFAULT_LANGUAGE
	lesson = objs.getLesson(teacher.currentLessonID)
	if lesson:
	    templ = "teacherDashboard.html"
	    studentLabels = []
	    for studentName in lesson.students:
	        student = objs.getStudent(studentName, teacher.currentLessonID)
                if student:
		    studentLabels.append({"username":studentName,"fullname":student.fullname})
	    return self.renderPage(templ ,
				teacherName=teacher.fullname,
				lessonName=teacher.currentLessonName,
				students=studentLabels,
				token=teacher.token,
				language=language,
				labels=labdict.labels(templ, language),
				)
	else:
	    return self.redirect("/t/login")

    def endExercise(self):
        teacher = self.getFromCookie()
        exercise = objs.getExercise(teacher.currentExercise)
        if exercise:
            exercise.end()

class DataHandler(MainHandler):
    def get(self, kind):
        requester = self.getFromCookie()
        requesterRole = self.getRoleFromCookie()
        if requesterRole == "teacher":
            if kind == "simple_exercise_request":
                lessonID = requester.currentLessonID
                exercise = objs.Exercise()
                exercise.start(lessonID, "simple")
            elif kind == "complex_exercise_request":
                lessonID = requester.currentLessonID
                exercise = objs.Exercise()
                exercise.start(lessonID, "complex",self.request.get('category'))

    def post(self, kind):
        requester = self.getFromCookie()
        requesterRole = self.getRoleFromCookie()
        if requesterRole == "teacher":
            teacher = requester
            if kind == "teacherValidation":
                valid = self.request.get("valid")
                exercise = objs.getExercise(teacher.currentExercise)
                exercise.addNdbAnswer("teacher", teacher.username, valid)
                exercise.sendFeedbackToStudents()
            if kind == "getSessionStatus":
                exercise = objs.getExercise(teacher.currentExercise)
                exercise.sendStatusToTeacher()
        if requesterRole == "student":
            student = requester
            if kind == "answer":
                answer = self.request.get("answer")
                exerciseIdSent = self.request.get("exerciseID")
                if str(exerciseIdSent) == str(student.currentExercise):
                    exercise = objs.getExercise(student.currentExercise)
                    if student.username not in exercise.students:
                        exercise.addStudent(student)
                    if exercise.addNdbAnswer("student", student.username, answer):
                        logging.info("Answer from <" + student.username + "> saved in datastore")
                        exercise.sendStatusToTeacher()
                    else:
                        logging.error("Warning! Answer not saved")
                else:
                    logging.error("Student " + student.fullname + "Sent answer of a different exercise")    

class StudentHandler(MainHandler):
    def get(self, action):
        if action == "dashboard":
            self.initializeDashboard()
        elif action == "login":
            self.renderLoginPage()
        elif action == "logout":
            self.logout()
        
    def post(self, action):
        if action == "login":
            self.login()
    
    def renderLoginPage(self, message=None):
        t = "studentLogin.html"
        if message:
            m = labdict.labels(t, objs.DEFAULT_LANGUAGE)[message]
        else:
            m = None
        self.renderPage(t, labels=labdict.labels(t, objs.DEFAULT_LANGUAGE), message=m)

    def login(self):
        student = objs.Student()
        student.fullname = self.read("username")
        student.username = student.fullname.replace(" ", "_")
        student.language = objs.DEFAULT_LANGUAGE
        lessonName = self.read("lessonName")
        if lessonName in objs.getOpenLessonsNames():
            if not objs.studentAlreadyConnected(student.username, lessonName):
                student.save()
                student.connect()
                self.addCookie("schooltagging-role", "student")
                self.addCookie("schooltagging-username", student.username)
                lessonID = student.joinLesson(lessonName)
                self.addCookie("schooltagging-lessonID", lessonID)
                return self.redirect("/s/dashboard")
            else:
                message = "name_already_in_use"
        else:
            message = "lesson_not_started"
        self.renderLoginPage(message)
        
    def initializeDashboard(self):
        student = self.getFromCookie()
        if not student:
            self.clearCookies()
            return self.redirect("/s/login")
        templ = "studentDashboard.html"
        language = student.language or objs.DEFAULT_LANGUAGE
        self.renderPage(templ,
                    studentFullName=student.fullname,
                    lessonName=student.currentLessonName,
                    token=student.token,
                    language=language,
                    labels=labdict.labels(templ, language),
                    )
    def logout(self):
        student = self.getFromCookie()
        if student:
            self.clearCookies()
            student.logout()
        return self.redirect("/s/login")
        
class DeleteHandler(MainHandler):
    def get(self):
        objs.clean()
        for name in self.request.cookies.iterkeys():
            self.response.delete_cookie(name)
        return self.redirect("/start")

class ConnectionHandler(MainHandler):
    def post(self, action):
        """ channel service interrupted from yaml"""
        a = self.request.get('from')
        user = objs.getFromID(a)
        if user:
            if user.__class__.__name__ == "Student":
                student = user
                if action == "disconnected":
                    return student.alertTeacherImOffline()

class ChannelHandler(MainHandler):
    def get(self):
        requester = self.getFromCookie()
        idle = datetime.datetime.now() - requester.lastAction
        if idle < datetime.timedelta(minutes=objs.MAX_IDLE_ALLOWED):
            return requester.connect()
        else:
            return requester.logout()
        
class PingHandler(MainHandler):
    def post(self):
        requester = self.getFromCookie()
        requesterRole = self.getRoleFromCookie()
        if requesterRole == "teacher":
            teacher = requester
            studentName = self.read("student")
            return teacher.sendPingToStudent(studentName)
        elif requesterRole == "student":
            student = requester
            return student.alertTeacherImAlive()
            
class LosingFocusHandler(MainHandler):
    def post(self):
		requester = self.getFromCookie()
		status = self.request.get("focus")
		requesterRole = self.getRoleFromCookie()
		assert requesterRole == "student"
		student = requester
		if student:
                    student.alertTeacherAboutMyFocus(status)
    
class ForceLogoutStudentHandler(MainHandler):
    def post(self):
        requester = self.getFromCookie()
        requesterRole = self.getRoleFromCookie()
        if requesterRole == "teacher":
            teacher = requester
            studentName = self.read("student")
            student = objs.getStudent(studentName, teacher.currentLessonID)
            if student:
                return student.logout()
        
class ExportPage(MainHandler):
    def get(self):
        data = objs.exportJson()
        return self.write(data)
        
class JollyHandler(MainHandler):
    def get(self, jolly):
        return self.redirect("/start")
    
class HelpHandler(MainHandler):
    # currently the hyperlink to get here, originally in "wrapper.html",
    # has been removed.
    def get(self):
        return self.renderPage("helpIndex.html")

class CleanIdle(MainHandler):
    def get(self):
        objs.cleanIdleObjects()

class LanguageHandler(MainHandler):
    def post(self):
        requester = self.getFromCookie()
        if requester:
            language = self.read("language")
            requester.language = language
            requester.save()
            return
        
        
PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([
    webapp2.Route(r'/t/<action>',
    handler = TeacherHandler, name="teacher"),
    webapp2.Route(r'/s/<action>',
    handler = StudentHandler, name="student"),
    webapp2.Route(r'/data/<kind>',
    handler=DataHandler, name="data"),
    webapp2.Route(r'/_ah/channel/<action>/',
    handler=ConnectionHandler, name="connection"),
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
    (PAGE_RE, JollyHandler),
            ])
