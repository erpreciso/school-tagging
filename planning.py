# -*- coding: cp1252 -*-
import school_tagging_core_process as st

antje = st.Teacher(name="Antje")
stefano = st.Student(name="Stefano")
lorena = st.Student(name="Lorena")

lesson = st.Lesson(teacher=antje)

question_1 = st.WhichType()
question_1.id = "ex1"
question_1.sentence = "I am always doing things I can’t do. That is how I get to do them."
question_1.words = question_1.sentence.split(" ")
question_1.options = ["adverb", "noun"]
question_1.answer = "adverb"

question_2 = st.FindTheElement()
question_2.sentence = "You miss 100 percent of the shots you never take."
question_2.to_find = "adverb"
question_2.answers = [0, 3]

session_1 = st.Session(lesson=lesson)

session_1.add_student(stefano)
session_1.add_student(lorena)

session_1.set_question(question_1)
session_1.assign_to_students()
stefano.add_answer(session_1, "adverb")
lorena.add_answer(session_1, "name")

session_2 = st.Session(lesson)
session_2.set_question(question_2)
session_2.add_student(stefano)
session_2.add_student(lorena)
session_2.assign_to_students()
stefano.add_answer(session_2, 0)
lorena.add_answer(session_2, 3)

print "Stefano took", stefano.sessions_token(), "exercises"
print "Stefano gave", stefano.corrects(), "correct answers"

print "Lorena took", lorena.sessions_token(), "exercises"
print "Lorena gave", lorena.corrects(), "correct answers"
"""
print "The teacher is", lesson.teacher.name
print "The classroom gave", lesson.corrects(), "correct answers"
"""

