from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import channel
import json
import random
import re
import codecs
import string
import datetime
import logging

MAX_IDLE_ALLOWED = 100 # minutes
DEFAULT_LANGUAGE = "IT"

class decoder(json.JSONDecoder):
     # http://stackoverflow.com/questions/10885238/python-change-list-type-for-json-decoding
     def __init__(self, list_type=list, **kwargs):
          json.JSONDecoder.__init__(self, **kwargs)
          # Use the custom JSONArray
          self.parse_array = self.JSONArray
          # Use the python implemenation of the scanner
          self.scan_once = json.scanner.py_make_scanner(self)
          self.list_type = list_type

     def JSONArray(self, s_and_end, scan_once, **kwargs):
          values, end = json.decoder.JSONArray(s_and_end, scan_once, **kwargs)
          return self.list_type(values), end

class JsonSetEncoder(json.JSONEncoder):
     def default(self, obj):  # pylint: disable=method-hidden
          if isinstance(obj, frozenset):
                result = list(obj)
                if result and isinstance(result[0], tuple) and len(result[0]) == 2:
                     return dict(result)
                return result
          return json.JSONEncoder.default(self, obj)

def itemset(d):
     return frozenset(d.items())

def cleanIdleObjects():
     q = Teacher.query(Teacher.currentLessonID != None)
     if q.count(limit=None) > 0:
          teachers = q.fetch(limit=None)
          for teacher in teachers:
                idle = datetime.datetime.now() - teacher.lastAction
                if idle > datetime.timedelta(minutes=MAX_IDLE_ALLOWED):
                     lesson = getLesson(teacher.currentLessonID)
                     if lesson:
                          lesson.end()
                     teacher.logout()
     q = Student.query(Student.currentLessonID != None)
     if q.count(limit=None) > 0:
          students = q.fetch(limit=None)
          for student in students:
                idle = datetime.datetime.now() - teacher.lastAction
                if idle > datetime.timedelta(minutes=MAX_IDLE_ALLOWED):
                     student.logout()
     q = Lesson.query(Lesson.open == True)
     if q.count(limit=None) > 0:
          lessons = q.fetch(limit=None)
          for lesson in lessons:
                teacher = getTeacher(lesson.teacher)
                if teacher and teacher.currentLessonID == None:
                     lesson.end()
     q = Exercise.query(Exercise.open == True)
     if q.count(limit=None) > 0:
          exercises = q.fetch(limit=None)
          for exercise in exercises:
                teacher = getTeacher(exercise.teacher)
                if teacher and teacher.currentLessonID == None:
                     exercise.end()

class Answer(ndb.Model):
     exercise = ndb.IntegerProperty()
     content = ndb.StringProperty()
     correct = ndb.BooleanProperty()
     
class User(ndb.Model):
     fullname = ndb.StringProperty()
     username = ndb.StringProperty()
     currentLessonID = ndb.IntegerProperty()
     currentLessonName = ndb.StringProperty()
     lessons = ndb.IntegerProperty(repeated=True)
     token = ndb.StringProperty()
     currentExercise = ndb.IntegerProperty()
     lastAction = ndb.DateTimeProperty(auto_now=True)
     language = ndb.StringProperty()
     answers = ndb.StructuredProperty(Answer, repeated=True)

     def connect(self):
          duration = 60 # minutes
          self.token = channel.create_channel(str(self.key.id()),
                                                     duration_minutes=duration)
          self.save()
     
     def assignLesson(self, lessonID, lessonName):
          self.currentLessonID = lessonID
          self.currentLessonName = lessonName
          self.lessons.append(lessonID)
          self.save()
          
     def askMeToRefresh(self):
          message = json.dumps({"type": "askMeRefresh"})
          channel.send_message(self.token, message)

class Student(User):
     def produceOwnStats(self):
          statsDict = {"correct": 0, "wrong": 0, "missing": 0}
          exercises = [s.exercise for s in self.answers]
          for exerciseID in exercises:
              exercise = getExercise(exerciseID)
              if exercise:
                  for sa in self.answers:
                      if sa.exercise == exerciseID:
                          answer = sa.content
                          if answer == "MISSING":
                              statsDict["missing"] += 1
                          elif answer == exercise.validatedAnswer:
                              statsDict["correct"] += 1
                          elif answer != exercise.validatedAnswer:
                              statsDict["wrong"] += 1
          return statsDict

     def produceAndSendOwnStats(self):
         statsDict = self.produceOwnStats()
         message = {"type": "studentStats",
               "message": {"stats": statsDict, "student": self.username}}
         self.sendMessageToTeacher(message)
     
     def save(self):
          if self.currentLessonID == None:
                cl = "Empty"
          else:
                cl = self.currentLessonID
          r = self.put()
          memcache.flush_all()
          memcache.set("Student:" + self.username + \
                          "|CurrentLesson:" + str(cl), self)
          return r
          
     def joinLesson(self, lessonName):
          assert lessonName in getOpenLessonsNames()
          lesson = getLessonFromName(lessonName)
          lesson.addStudent(self)
          self.currentLessonID = lesson.key.id()
          self.currentLessonName = lessonName
          self.answers = []
          self.save()
          self.alertTeacherImArrived()
          return lesson.key.id()
     
     def exitLesson(self):
          if self.currentLessonID:
              lesson = getLesson(self.currentLessonID)
              if lesson:
                  lesson.removeStudent(self)
                  message = {"type": "lessonTerminated"}
                  message = json.dumps(message)
                  channel.send_message(self.token, message)
                  self.currentLessonID = None
                  self.currentLessonName = None
                  self.save()
     
     def exitExercise(self):
          if self.currentExercise:
                exercise = getExercise(self.currentExercise)
                exercise.removeStudent(self)
                self.currentExercise = None
                self.save()
     
     def logout(self):
          self.alertTeacherImLogout()
          self.exitLesson()
          self.exitExercise()
          self.token = None
          self.save()
                
     def sendMessageToTeacher(self, message):
          lesson = getLesson(self.currentLessonID)
          if lesson and lesson.teacher:
                teacher = getTeacher(lesson.teacher)
                if teacher and teacher.token:
                  message = json.dumps(message)
                  return channel.send_message(teacher.token, message)
     
     def alertTeacherImArrived(self):
          message = {"type": "studentArrived",
                "message": {
                     "studentName": self.username,
                     "studentFullName": self.fullname
                     }}
          self.sendMessageToTeacher(message)
          
     def alertTeacherImLogout(self):
          message = {
                "type": "studentLogout",
                "message": {"studentName": self.username}
                }
          return self.sendMessageToTeacher(message)
     
     def alertTeacherImAlive(self):
          message = {"type": "studentAlive",
                "message": {"studentName": self.username}}
          self.sendMessageToTeacher(message)
     
     def alertTeacherImOffline(self):
          message = {"type": "studentDisconnected",
                "message": {"studentName": self.username}}
          self.sendMessageToTeacher(message)

     def alertTeacherAboutMyFocus(self, status):
          message = {"type": "studentFocusStatus",
                "message": {"studentName": self.username, "focus": status}}
          self.sendMessageToTeacher(message)

class Teacher(User):
     password = ndb.StringProperty()
     def save(self):
          self.put()
          memcache.set("Teacher:" + self.username, self)
          
     def logout(self):
          self.currentLessonID = None
          self.currentLessonName = None
          self.currentExercise = None
          self.token = None
          self.save()
          
     def sendPingToStudent(self, studentName):
          student = getStudent(studentName, self.currentLessonID)
          message = {"type": "pingFromTeacher"}
          message = json.dumps(message)
          channel.send_message(student.token, message)

def teacherUsernameExists(username):
     if getTeacher(username):
          return True
     else:
          return False

def createTeacher(username, password, fullname):
     teacher = Teacher()
     teacher.username = username
     teacher.fullname = fullname
     teacher.password = password
     teacher.language = DEFAULT_LANGUAGE
     teacher.save()
     return

def getTeacher(username):
     teacher = memcache.get("Teacher:" + username)
     if not teacher:
          q = Teacher.query(Teacher.username == username)
          teacher = q.get()
          if teacher:
                memcache.set("Teacher:" + username, teacher)
     if teacher:
          return teacher
     else:
          return False

def getStudent(username, currentLessonID):
     username = str(username)
     student = memcache.get("Student:" + username + \
                "|CurrentLesson:" + str(currentLessonID))
     if not student:
          q = Student.query(Student.username == username,
                Student.currentLessonID == currentLessonID)
          student = q.get()
          if student:
                memcache.flush_all()
                memcache.set("Student:" + username + \
                     "|CurrentLesson:" + str(currentLessonID), student)
     if student:
          return student
     else:
          return False
          
def getFromID(sid):
     user = memcache.get("ID:" + sid)
     if not user:
          user = ndb.Key("Teacher", int(sid)).get() \
                or ndb.Key("Student", int(sid)).get()
          if user:
                memcache.set("ID:" + str(sid), user)
     if user:
          return user
     else:
          return False
     
def studentAlreadyConnected(username, lessonName):
     q = Student.query(Student.username == username,
          Student.currentLessonName == lessonName)
     if q.get():
          return True
     else:
          return False
     
class Lesson(ndb.Model):
     lessonName = ndb.StringProperty()
     teacher = ndb.StringProperty()
     open = ndb.BooleanProperty()
     exercises = ndb.IntegerProperty(repeated=True)
     students = ndb.StringProperty(repeated=True)
     datetime = ndb.DateTimeProperty(auto_now_add=True)

     def start(self, lessonName, teacher):
          self.lessonName = lessonName
          self.teacher = teacher.username
          self.open = True
          self.students = []
          self.exercises = []
          lessonID = self.save()
          teacher.assignLesson(lessonID, lessonName)

     def save(self):
          self.put()
          memcache.set("Lesson:" + str(self.key.id()), self)
          return self.key.id()

     def end(self):
          teacher = getTeacher(self.teacher)
          for studentName in self.students:
                student = getStudent(studentName, self.key.id())
                student.exitLesson()
          teacher.currentLessonID = None
          teacher.currentLessonName = None
          teacher.save()
          self.open = False
          self.save()
          
     def addStudent(self, student):
          self.students.append(student.username)
          self.save()
     
     def addExercise(self, exerciseID):
          self.exercises.append(exerciseID)
          self.save()
     
     def removeStudent(self, student):
          if student.username in self.students:
                self.students.remove(student.username)
                self.save()
     
     def produceAndSendStats(self):
          teacher = getTeacher(self.teacher)
          allStudents = []
          listOfStudentsStats = []
          stats = None
          if self.exercises:
              stats = []
              for exerciseID in self.exercises:
                  ses = getExercise(exerciseID)
                  if ses:
                      studentAnswers = ses.generateAnswersDict("studentAnswer")
                      students = studentAnswers.keys()
                      allStudents += self.students
                      if students:
                          for st in students:
                              alreadyTracked = [s["studentName"] for s in listOfStudentsStats]
                              if st not in alreadyTracked:
                                  student = getStudent(st, self.key.id())
                                  if student:
                                      ownStats = student.produceOwnStats()          
                                      ownDict = {"studentName": st, "stats": ownStats}
                                      listOfStudentsStats.append(ownDict) 
                          corrects = [st for st in students \
                              if studentAnswers[st] == ses.validatedAnswer]
                          stats += corrects
          statsDict = {}
          if stats:
              for name in stats:
                  if name in statsDict.keys():
                      statsDict[name] += 1
                  else:
                      statsDict[name] = 1
          for student in students:
              if student not in statsDict.keys():
                  statsDict[student]= 0
          message = {
          "type": "lessonStats",
          "message": {
                "stats": statsDict,
                "fullstats": listOfStudentsStats
          }
          }
          message = json.dumps(message)
          channel.send_message(teacher.token, message)
     
def getOpenLessonsID():
     q = Lesson.query(Lesson.open == True)
     if q.count(limit=None) > 0:
          lessons = q.fetch(limit=None)
          return [lesson.key.id() for lesson in lessons]
     else:
          return []

def getOpenLessonsNames():
     q = Lesson.query(Lesson.open == True)
     if q.count(limit=None) > 0:
          lessons = q.fetch(limit=None)
          return [lesson.lessonName for lesson in lessons]
     else:
          return []
     
def getLesson(lessonID):
     lesson = memcache.get("Lesson:" + str(lessonID))
     if not lesson:
          lesson = ndb.Key("Lesson", lessonID).get()
          if lesson:
                memcache.set("Lesson:" + str(lessonID), lesson)
     if lesson:
          return lesson
     else:
          return False
     
def getLessonFromName(lessonName):
     q = Lesson.query(Lesson.lessonName == lessonName)
     lesson = q.get()
     if lesson:
          return lesson
     else:
          return False

def getExercise(exerciseID):
     exercise = memcache.get("Exercise:" + str(exerciseID))
     if not exercise:
          exercise = ndb.Key("Exercise", exerciseID).get()
          if exercise:
                memcache.set("Exercise:" + str(exerciseID), exercise)
     if exercise:
          return exercise
     else:
          return False
     
def getSentence():
     pool = codecs.open("sentence-pool.txt", encoding="UTF-8").readlines()
     i = int(random.random() * len(pool))
     return pool[i]

def getWords(sentence):
     """return word list, random choice within words."""
     r = re.compile('[^%s]+' % re.escape(string.punctuation))
     raw_pool = re.split(' ', sentence)
     pool = [r.match(p) for p in raw_pool]
     goods = []
     words = []
     for p in range(len(pool)):
          if pool[p]:
                goods += [True]
                words += [pool[p].group()]
          else:
                goods += [False]
                words += [raw_pool[p]]
     target = int(random.random() * len(words))
     while not goods[target]:
          target = int(random.random() * len(words))
     return words, target
     
def getAnswersProposed(exerciseType):
     return json.loads(open("lists/answers.json","r").read())[exerciseType]

def clean():
     ndb.delete_multi(Lesson.query().fetch(keys_only=True))
     ndb.delete_multi(Exercise.query().fetch(keys_only=True))
     ndb.delete_multi(Student.query().fetch(keys_only=True))
     ndb.delete_multi(Teacher.query().fetch(keys_only=True))
     memcache.flush_all()

class Exercise(ndb.Model):
     teacher = ndb.StringProperty()
     open = ndb.BooleanProperty()
     lesson = ndb.IntegerProperty()
     type = ndb.StringProperty()
     students = ndb.StringProperty(repeated=True)
     datetime = ndb.DateTimeProperty(auto_now_add=True)
     exerciseText = ndb.StringProperty()
#            sentence to be analized from the student
     target = ndb.IntegerProperty()
#            index of the word that the student should recognize
     answersProposed = ndb.PickleProperty(repeated=True)
#            options available for the student
     exerciseWords = ndb.StringProperty(repeated=True)
#            list of the words componing the exercise
     validatedAnswer = ndb.StringProperty()
#            index of the teacher's validated answer in the answersProposed list
 
     def addNdbAnswer(self, role, userName, answer):
         if role == "student" and not self.open:
             return None
         if role == "student" and self.open:
             student = getStudent(userName, self.lesson)
             if userName not in self.students:
                 self.students.append(userName)
                 self.save()
             try:
                 sortedAnswer = json.loads(answer, cls=decoder, list_type=frozenset, object_hook=itemset)
                 answer = json.dumps(sortedAnswer, cls=JsonSetEncoder)
             except:
                 answer = answer
             student.answers.append( \
                       Answer(exercise=self.key.id(),content=answer))
             return student.save()
         elif role == "teacher":
             try:
                 sortedValid = json.loads(answer, cls=decoder, list_type=frozenset, object_hook=itemset)
                 valid = json.dumps(sortedValid, cls=JsonSetEncoder)
             except:
                 valid = answer
             self.validatedAnswer = valid
             return self.save()

     def sendFeedbackToStudents(self):
          for studentName in self.students:
                student = getStudent(studentName, self.lesson)
                exerciseAnswers = [a.content for a in student.answers if a.exercise == self.key.id()]
                if exerciseAnswers and exerciseAnswers[0] != "MISSING":
                    answer = exerciseAnswers[0]
                    message = {
                    "type": "validAnswer",
                    "message": {
                         "validAnswer": self.validatedAnswer,
                         "myAnswer": answer,
                         "dict": getAnswersProposed(self.type)
                         }
                    }
                else:
                    message = {
                    "type": "exerciseExpired",
                    "message": {
                         "validAnswer": self.validatedAnswer,
                         "dict": getAnswersProposed(self.type)
                    }
                }
                message = json.dumps(message)
                channel.send_message(student.token, message)
          
     def save(self):
          self.put()
          memcache.set("Exercise:" + str(self.key.id()), self)
          return self.key.id()
          
     def sendStatusToTeacher(self):
          if self.open:
                teacher = getTeacher(self.teacher)
                if teacher:
                    status = {
                      "type": "exerciseStatus",
                      "message": {
                          "dictAnswers": getAnswersProposed(self.type),
                          "possibleAnswers": self.generateAnswersDict("answerStudent"),
                          "totalAnswers": {
                            "answered": self.generateAnswersDict("studentAnswer").keys(),
                            "missing": [s for s in self.students \
                                if s not in self.generateAnswersDict("studentAnswer").keys()]
                          }
                          },
                      }
                    channel.send_message(teacher.token, json.dumps(status))

     def generateAnswersDict(self, dicttype):
        # depending of the parameter, return a dict
		# "answerStudent": return {answer1:[student1, student2], answer2:[], answer3:[student3]}
		# "studentAnswer": return {student1: answer1, student2: answer2}
         dictanswers = {}
         for studentName in self.students:
             student = getStudent(studentName, self.lesson)
             if student:
                 for objAnswer in student.answers:
                     if self.key.id() == objAnswer.exercise:
                         answer = objAnswer.content
                         if dicttype == "answerStudent":
                             if answer in dictanswers.keys():
                                 dictanswers[answer] += [studentName]
                             else:
                                 dictanswers[answer] = [studentName]
                         elif dicttype == "studentAnswer":
                             if studentName in dictanswers.keys():
                                 dictanswers[studentName] += [answer]
                             else:
                                 dictanswers[studentName] = [answer]
         return dictanswers

     def removeStudent(self, student):
          if student.username in self.students:
                self.students.remove(student.username)
                self.save()
     
     def addStudent(self, student):
          if student.username not in self.students:
                self.students.add(student.username)
                self.save()

     def end(self):
          for studentName in self.students:
                student = getStudent(studentName, self.lesson)
                if student:
                     if self.key.id() not in [a.exercise for a in student.answers]:
                         student.answers.append( \
                               Answer(exercise=self.key.id(),content="MISSING"))
                         student.save() 
                self.open = False
                self.save()
          
     def start(self, lessonID, exerciseType,category=""):
          self.lesson = lessonID
          lesson = getLesson(lessonID)
          self.teacher = lesson.teacher
          self.students = lesson.students
          self.exerciseText = getSentence()
          self.type = exerciseType
          self.category = category
          if exerciseType == "complex" :
                self.exerciseWords, self.target = getWords(self.exerciseText)
                self.target = -1
                self.answersProposed = []
          else:
                self.exerciseWords, self.target = getWords(self.exerciseText)
                self.answersProposed = getAnswersProposed(self.type)
          self.open = True
          sid = self.save()
          lesson.addExercise(sid)
          teacher = getTeacher(self.teacher)
          teacher.currentExercise = self.key.id()
          teacher.save()
          message = {
                "type": "exerciseExercise",
                "message": {
                    "id": sid,
                    "wordsList": self.exerciseWords,
                    "answersProposed": self.answersProposed,
                    "target": self.target,
                    "category": self.category
                    },
                }
          message = json.dumps(message)
          channel.send_message(teacher.token, message)
          for studentName in self.students:
                student = getStudent(studentName, self.lesson)
                if student:
                    student.currentExercise = sid
                    student.save()
                    channel.send_message(student.token, message)
          self.sendStatusToTeacher()

def exportJson():
     dictj = {"lessons":{}, "exercises":{}, "students":{}, "teachers":{}}
     q = Lesson.query()
     if q:
         for lesson in q:
             id = str(lesson.key.id())
             dictj["lessons"][id] = {"name": lesson.lessonName}
             dictj["lessons"][id]["students"] = lesson.students
             dictj["lessons"][id]["teacher"] = lesson.teacher
             dictj["lessons"][id]["datetime"] = lesson.datetime.isoformat()
             dictj["lessons"][id]["open"] = lesson.open
             dictj["lessons"][id]["exercises"] = {}
             for exerciseId in lesson.exercises:
                 exercise = getExercise(exerciseId)
                 s = {"open": exercise.open}
                 sid = str(exercise.key.id())
                 s["students"] = exercise.students
                 s["teacher"] = exercise.teacher
                 s["type"] = exercise.type
                 s["datetime"] = exercise.datetime.isoformat()
                 s["exerciseText"] = exercise.exerciseText
                 s["target"] = exercise.target
                 s["answersProposed"] = exercise.answersProposed
                 s["validatedAnswer"] = exercise.validatedAnswer
                 s["exerciseWords"] = exercise.exerciseWords
                 dictj["lessons"][id]["exercises"][sid] = s
     q = Exercise.query()
     if q:
         for exercise in q:
             id = str(exercise.key.id())
             dictj["exercises"][id] = {"open": exercise.open}
             dictj["exercises"][id]["students"] = exercise.students
             dictj["exercises"][id]["type"] = exercise.type
             dictj["exercises"][id]["datetime"] = exercise.datetime.isoformat()
             dictj["exercises"][id]["target"] = exercise.target
             dictj["exercises"][id]["exerciseText"] = exercise.exerciseText
             dictj["exercises"][id]["answersProposed"] = exercise.answersProposed
             dictj["exercises"][id]["validatedAnswer"] = exercise.validatedAnswer
             dictj["exercises"][id]["exerciseWords"] = exercise.exerciseWords
     q = Teacher.query()
     if q:
         for teacher in q:
             id = str(teacher.key.id())
             dictj["teachers"][id] = {"username": teacher.username}
             dictj["teachers"][id]["fullname"] = teacher.fullname
             dictj["teachers"][id]["currentLessonID"] = teacher.currentLessonID
             dictj["teachers"][id]["currentLessonName"] = teacher.currentLessonName
             dictj["teachers"][id]["lessons"] = teacher.lessons
             dictj["teachers"][id]["token"] = teacher.token
             dictj["teachers"][id]["currentExercise"] = teacher.currentExercise
             dictj["teachers"][id]["lastAction"] = teacher.lastAction.isoformat()
             dictj["teachers"][id]["language"] = teacher.language
             dictj["teachers"][id]["password"] = teacher.password
             dictj["teachers"][id]["answers"] = {}
             for answer in teacher.answers:
                 s = {"content": answer.content}
                 s["correct"] = answer.correct
                 dictj["teachers"][id]["answers"][answer.exercise] = s
     q = Student.query()
     if q:
         for student in q:
             id = str(student.key.id())
             dictj["students"][id] = {"username": student.username}
             dictj["students"][id]["fullname"] = student.fullname
             dictj["students"][id]["currentLessonID"] = student.currentLessonID
             dictj["students"][id]["currentLessonName"] = student.currentLessonName
             dictj["students"][id]["lessons"] = student.lessons
             dictj["students"][id]["token"] = student.token
             dictj["students"][id]["currentExercise"] = student.currentExercise
             dictj["students"][id]["lastAction"] = student.lastAction.isoformat()
             dictj["students"][id]["language"] = student.language
             dictj["students"][id]["answers"] = {}
             for answer in student.answers:
                 s = {"content": answer.content}
                 s["correct"] = answer.correct
                 dictj["students"][id]["answers"][answer.exercise] = s
     return json.dumps(dictj)
