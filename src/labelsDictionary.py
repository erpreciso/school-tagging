# coding: utf-8

def labels(template, language):
    d = {
            "teacherLogin.html": {
                "page_title": {
                    "EN": "school-tagging|teacher|login",
                    "IT": "school-tagging|insegnante|entra",
                    },
                "login_title": {
                    "EN": "LOGIN",
                    "IT": "LOGIN",
                    },
                "insert_username_password": {
                    "EN": "Please insert your username and password",
                    "IT": "Please insert your username and password",
                    },
                "username": {
                    "EN": "Username",
                    "IT": "Username",
                    },
                "password": {
                    "EN": "Password",
                    "IT": "Password",
                    },
                "lesson_name": {
                    "EN": "Lesson name",
                    "IT": "Lesson name",
                    },
                "login_button": {
                    "EN": "Login",
                    "IT": "Login",
                    },
                "signup_title": {
                    "EN": "SIGNUP",
                    "IT": "SIGNUP",
                    },
                "do_not_have_account": {
                    "EN": "Do not have an account yet?",
                    "IT": "Do not have an account yet?",
                    },
                "signup_button": {
                    "EN": "Signup",
                    "IT": "Signup",
                    },
                "message_title": {
                    "EN": "MESSAGE",
                    "IT": "ATTENZIONE",
                    },
                "lesson_name_in_use": {
                    "EN": "Lesson name already in use",
                    "IT": u"Lesson name already in use",
                    },        
                "provide_lesson_name": {
                    "EN": "Please provide a name for the lesson",
                    "IT": "Please provide a name for the lesson",
                    },
                "password_not_correct": {
                    "EN": "Password not correct",
                    "IT": u"Password not correct",
                    },
                "username_not_existing": {
                    "EN": "Username not existing",
                    "IT": "Username not existing",
                    },
                "re-enter_login": {
                    "EN": "Please re-enter username and password in the LOGIN area",
                    "IT": "Please re-enter username and password in the LOGIN area",
                    },
                "username_already_used": {
                    "EN": "Username already in use",
                    "IT": "Username already in use",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
                                
                },
        "teacherDashboard.html": {
                "page_title": {
                    "EN": "school-tagging|teacher|dashboard",
                    "IT": "school-tagging|insegnante|cruscotto",
                    },
                "teacher_title": {
                    "EN": "Teacher",
                    "IT": "Teacher",
                    },
                "logout": {
                    "EN": "Logout",
                    "IT": "Logout",
                    },
                "lesson_name_title": {
                    "EN": "Lesson name (pass to students)",
                    "IT": "Lesson name (pass to students)",
                    },
                "enrolled_students": {
                    "EN": "Enrolled students (click to view stats)",
                    "IT": "Enrolled students (click to view stats)",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
              },
        "studentDashboard.html": {
                "page_title": {
                    "EN": "school-tagging|student|dashboard",
                    "IT": "school-tagging|studente|cruscotto",
                    },
                "logout": {
                    "EN": "Logout",
                    "IT": "Logout",
                    },
                "lesson_name_title": {
                    "EN": "Lesson name",
                    "IT": "Lesson name",
                    },
                "student_title": {
                    "EN": "Student",
                    "IT": "Student",
                    },
              },
         "studentLogin.html": {
                "page_title": {
                    "EN": "school-tagging|student|login",
                    "IT": "school-tagging|studente|entra",
                    },
                "enter_username_and_lesson": {
                    "EN": "Please enter your name and your session ID provided by your teacher",
                    "IT": "Please enter your name and your session ID provided by your teacher",
                    },
                "name_and_surname": {
                    "EN": "Name and Last Name",
                    "IT": "Name and Last Name",
                    },
                "session_id": {
                    "EN": "Session ID",
                    "IT": "Session ID",
                    },
                "login_button": {
                    "EN": "Go to class exercise",
                    "IT": "Go to class exercise",
                    },
                "name_already_in_use": {
                    "EN": "Name already in use",
                    "IT": u"Name already in use",
                    },
                "lesson_not_started": {
                    "EN": "Lesson not started yet",
                    "IT": "Lesson not started yet",
                    },
                "message_title": {
                    "EN": "MESSAGE",
                    "IT": "ATTENZIONE",
                    },
               },
    }
    res = {}
    t = d[template]
    for k in t.keys():
        res[k] = t[k][language]
    return res
