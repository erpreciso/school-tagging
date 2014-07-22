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
                    "IT": "ENTRA",
                    },
                "insert_username_password": {
                    "EN": "Please insert your username and password",
                    "IT": "Pregasi inserire il proprio nome utente e la password",
                    },
                "username": {
                    "EN": "Username",
                    "IT": "Nome utente",
                    },
                "password": {
                    "EN": "Password",
                    "IT": "Password",
                    },
                "lesson_name": {
                    "EN": "Lesson name",
                    "IT": "Nome della lezione",
                    },
                "login_button": {
                    "EN": "Login",
                    "IT": "Entra nel sito",
                    },
                "signup_title": {
                    "EN": "SIGNUP",
                    "IT": "REGISTRATI",
                    },
                "do_not_have_account": {
                    "EN": "Do not have an account yet?",
                    "IT": "Non sei ancora registrato?",
                    },
                "signup_button": {
                    "EN": "Signup",
                    "IT": "Registrati",
                    },
                "message_title": {
                    "EN": "MESSAGE",
                    "IT": "ATTENZIONE",
                    },
                "lesson_name_in_use": {
                    "EN": "Lesson name already in use",
                    "IT": u"Il nome scelto per la lezione non è al momento disponibile",
                    },        
                "provide_lesson_name": {
                    "EN": "Please provide a name for the lesson",
                    "IT": "Prego inserire un nome per la lezione",
                    },
                "password_not_correct": {
                    "EN": "Password not correct",
                    "IT": u"La password non è corretta",
                    },
                "username_not_existing": {
                    "EN": "Username not existing",
                    "IT": "Nome utente sconosciuto",
                    },
                "re-enter_login": {
                    "EN": "Please re-enter username and password in the LOGIN area",
                    "IT": "Ri-digitare il nome utente e la password nell'area ENTRA",
                    },
                "username_already_used": {
                    "EN": "Username already in use",
                    "IT": "Nome utente non disponibile",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
                                
                },
        "teacherDashboard.html": {
                "page_title": {
                    "EN": "school-tagging|teacher|dashboard",
                    "IT": "",
                    },
                "teacher_title": {
                    "EN": "Teacher",
                    "IT": "Insegnante",
                    },
                "logout": {
                    "EN": "Logout",
                    "IT": "Disconnetti",
                    },
                "lesson_name_title": {
                    "EN": "Lesson name (pass to students)",
                    "IT": "Nome della lezione (da comunicare agli studenti)",
                    },
                "enrolled_students": {
                    "EN": "Enrolled students (click to view stats)",
                    "IT": "Studenti collegati (cliccare sul nome per visualizzare le statistiche",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
                "": {
                    "EN": "",
                    "IT": "",
                    },
               },
    }
    res = {}
    t = d[template]
    for k in t.keys():
        res[k] = t[k][language]
    return res
