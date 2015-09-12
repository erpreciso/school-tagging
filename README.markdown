# School-Tagging project plan

## Abstract

### Idea, target and goals

School-Tagging is a teaching supporting game-like web application; it's a tool for primary school teachers to assess student's knowledge status on specific subjects, using interactive, and possibly competitive/collaborative, exercises.

Answers provided by students and validated by the teacher (or automatic assessment) could constitute, in a large scale scenario, a valuable source of linguistic annotation. The platform can therefore be seen also as a crowdsourcing system to create novel linguistic resources to be used by the scientific community in the Natural Language Processing field.

Although the platform is subject-independent, we are currently focusing on language exercises based on standard school curriculum. Since exercises will mainly be focused on grammatical analysis, target are primary school's teachers and students. It may varies depending on the exercise type.

### Objectives / Mission: which needs are satisfied

Scientific research: produce data to be used in computational linguistic academic research. [TODO 2]

Didactic: support teacher in primary schools with a tool that is promoting collaboration between teacher and students, rather than merely machine feedbacks.

### Golden rules

1. All material produced is used for didattic and scientific purposes, both in the interaction student/teacher and then in the sentence's annotation. Every student is a collaborator, more than a user.

2. Simplicity, without compromises. On top of the child and the parent, also grandpa should be able to use the app without manuals or specific classes. If something looks complicated, it need to be fixed.

3. The teacher is above technology. App logic doesn't allow a decision that has not been validated by a human. Technology can teach only if well directed, otherwise is harmful.

### Innovation compared to other existing

* Collaboration between teacher and classroom is essential and cannot be overruled by the machine since answers are not known in advance;

* Exercise pool can potentially be infinite, and it doesn't need a preparation work done by the teacher to instruct the machine;

* All results are usable by the scientific community

### Development status at today

A working demo is currently live in production with the base exercise: assign the correct part-of-speech (i.e., verb, noun, adjective, adverb, etc.) to each word in a sentence. We're carrying over both technical tests and quality tests of the experience proposed in partnership with a primary school and a classroom of children.

## Project Description

### What's the product and which needs address

School-Tagging is a web-based project for classrooms which aims at promoting the collaboration between schools and researchers to enhance language skills and technologies.

Language exercises are abundant in all education levels. Both literature and history classes adopt language comprehension tasks; grammar exercises, writing tests and learning a foreign language are all intrinsically about language. Language is also a big research topic pertaining to the fields of (Computational) Linguistics and Digital Humanities (DH). These disciplines rely on human annotated resources for capturing language regularities, developing Natural Language Processing (NLP) applications, and DH tools.

The idea behind School-Tagging is to recast traditional pencil & paper language exercises into digital game-oriented learning activities, to:

1. stimulate students' interest and motivation;

2. promote cooperation among classmates with the help of teachers;

3. support scientific researchers related to language analysis and technologies. 

Today's young generations are already fully immersed in technology, and teachers face a challenge of keeping their full attention on taught material. This often leads to classroom technologies being received with suspicion. Our platform would encourage teachers to incorporate a controlled level of technology in the class to keep students more engaged by means of game-like interactive activities, without abandoning traditional training methods and social dynamics.

A typical School-Tagging activity involves students solving exercises with digital devices in physical classrooms. Students’ answers are checked in real-time by the teacher who can always promote discussions. Anonymized answers are collected and made openly available for scientific purposes, thereby promoting a virtuous cycle between education and academic research while supporting students’ engagement and linguistic development.

This project aims to create different game experiences that are both interactive, challenging and data-producer, and plug into a web platform that is accessible from teacher and students during the lesson, and from researchers to analyze data produced.

### Need 1: Scientific mission

Since the majority of existing teaching tools make use of "supervised" machine learning, i.e. the systems learn to perform a language analysis task from large amounts of annotated data, the availability of such data is crucial to the good performance of the systems. Researchers often experience issues when collecting these so-called training data, since it is an expensive and time-consuming task. Through the School-Tagging platform, instead, students do language exercises and create high-quality training data at the same time. Given the variety of tasks performed in classrooms, such training data can be divided into different proficiency levels according to the grades under consideration (e.g., primary, secondary school, etc.), and also into different subjects (e.g., grammar, history, literature, etc.). Such training data would therefore cover a variety of topics and difficulty levels, contributing to training a variety of natural language processing systems.

One type of output training data can be the treebank, basis for some linguistic technology systems such as proof-reading, speech-to-text recognition and language translation. These are currently produced manually with a huge investment of resources, and for languages different from English they're somewhat still at an early stage (e.g. the Turin Treebank, for the italian language, contains around 3000 sentences, not enough for any advanced linguistic model). Annotation schemes are largely consistent with what used in secondary school didactics, allowing School-Tagging to be an unheard-of tool to create good quality material without using incremental resources, being just a support tool for topics already in every curriculum.

We will make use of collected data to build annotated language resources and make them openly available to NLP and DH research communities at large. It has been shown that such language resources are essential for the development of more advanced linguistic theories, and for building state of the art NLP systems. It also benefits the emerging DH research field which can use students’ solutions of language comprehension tasks (e.g., history, literature, foreign language) to annotate language data and develop novel tools for humanities scholars. Finally, since building language annotation is extremely costly, this solution would enable the scientists to considerably cut the cost of building linguistic resources.

Student's responses function as one collective intelligence, which produces annotated resources. Such language resources remain essential for the development of more advanced linguistic knowledge, and for building state-of-the-art NLP systems by  training language technologies that are widely used in today's society (e.g., Machine Translation, Automatic Question Answering).  Besides, they contribute to the progress of Digital Humanities research, which exploits language annotation for developing better tools for humanities scholars (e.g., Historical Content Analysis).

### Need 2: Educational Mission [TODO 9]

School-Tagging is a social and innovative web platform which aims at using the full capabilities of today's Internet technologies, enabling a type of real-time multiuser interaction which was inconceivable only few years ago. However, it preserves the offline modality, essential in social dynamics: the classroom remains the central physical space where the learning process takes place, and it is only partially replaced by a virtual environment. Differently from typical e-learning environments, it is the teacher, not the machine, who leads the learning activity, i.e., she is able to monitor students' individual and aggregated answers and provide them real-time feedback.

The project promotes cooperation among students with the help of teachers, who can monitor in real-time students’ individual and aggregated answers and encourage open discussions.

It aims at setting up a collaboration between schools and scientific research. Student’s responses function as one collective intelligence which produces annotated resources. Students are more engaged when using game-like interactive tools, and feel empowered by solving language tasks that contribute to scientific researchers. 

We believe that this tool will provide students with a more engaging educational environment, and teachers with a more effective way to keep students motivated. Today’s young generations are fully immersed in technology, and teachers are having a harder time keeping their full attention. Our platform would encourage teachers to incorporate a controlled level of technology in the class to keep students more engaged by means of game-like interactive activities, without abandoning traditional training methods and social dynamics. The immediate feedback that students receive by the teacher is extremely beneficial for the learning process, and represents a big advantage over classical settings where students typically get the correction of their homework several hours or days after it has been completed. The realization by students that their effort will turn out useful for scientific research has been proven extremely effective in boosting their motivation in related Citizen Science projects, such as Fold.it and Zooniverse.org. 

### How does our (current) tool works

There are two user entities: teachers and students. After a teacher logs in the platform, she can start a new session by choosing a unique string identifier. This token is communicated to the students in the classroom, who have to use it to access the session. As they do so, their names become visible on the teacher's interface. After all students have accessed the platform, the teacher can choose a single exercise instance (e.g., a sentence to annotate) which is sent to all the students. As the students answer, the teacher is able to monitor in real-time each single answer and all aggregated answers via an interactive chart. After all students have answered (or the teacher decides that the time is up), the teacher can optionally promote some discussion in the class (e.g., asking specific students to justify the chosen answer). Finally, she is asked to select the correct answer. This validation generates an immediate feedback to the students. All answers are permanently written in a centralised datastore, which allows to keep track of students and classrooms progress as well as makes the data available for research purposes.

Currently two languages are supported, English and Italian, but the tool is scalable and ready to include as many languages as needed both in the interface and also in content.

### Status of the project at today

* Literature study on e-learning and crowdsourcing regarding available systems and methodologies.

* Definition of the conceptual paradigm of a novel platform independent of specific language exercises.

* Implementation of a preliminary prototype of the back-end engine using the Google Application Engine (GAE): authentication, data-store, student and teacher interfaces and users interaction.

* Selection of a simple grammar exercise as an instance of the paradigm: assign the correct part-of-speech (i.e., verb, noun, adjective, adverb, etc.) to each word in a sentence.

* Creation of a mockup of the student and teacher interface (see [ninjamock](ninjamock.com/s/hcdmrz))

* First meeting with the principal and grammar teacher of a local school (6-9 grade) to understand their needs and establish the intersection between school programs and scientific research in the grammar domain.

* Implementation of a preliminary prototype version of the front-end (student and teacher web interface, see school-tagging.appspot.com).

* Release of the preliminary version of the prototype on [github](https://github.com/erpreciso/school-tagging). The current version of the prototype can be tested at [school-tagging.appspot.com](http://school-tagging.appspot.com/start). In order to simulate multiple users on the same machine we recommend to open the webapp on different browsers (Chrome, Firefox, or Safari). Two sessions can run on the same browser only if one is set to "private" mode.

* Second meeting with the local school. Presentation of the prototype. Plans to further develop the application with full morphology annotations and more interactive, game-like exercises.

### How our idea is innovative and how it fit into current knowledge status, academic context, market and competitors

Many e-learning technologies are being introduced in European school systems, the great majority of which is commercially oriented. A big portion of these systems are Learning Management Systems (e.g., [blackboard.com](http://www.blackboard.com), [moodle.org](https://moodle.org/)) which provide the infrastructure to help the administration, tracking, reporting of e-learning resources, but typically do not include actual content.

Other training-oriented tools typically consist of non-collaborative solutions, i.e., the computer acts as a teacher offering a finite set of exercises, while already knowing the correct answers (e.g., [khanacademy.org](https://www.khanacademy.org/), [softschools.com](http://www.softschools.com/), and [VISL games](http://beta.visl.sdu.dk/games_gym.html)).

Solutions which are more similar to our project, are those which are collaborative and classroom oriented (e.g., [socrative](http://socrative.com/), [infuselearning.com](http://www.infuselearning.com/), [getkahoot.com](https://getkahoot.com/), [clickerschool.com](https://www.clickerschool.com)). However, they typically offer very rigid exercise templates (e.g., multiple answers questions, true/false), which either contain predefined answers or need to be filled in by the teacher at home. Most importantly, the answers to these tests are not used for scientific purposes.

The type of prototype we have implemented sits in the boundary between existing e-learning technology and citizen-science solutions, but our paradigm can be considered unique.

In the School-Tagging platform, for a given task there are a potentially infinite number of language exercises (i.e., the sentences provided to the system), and their solution is not previously known. The teacher has a central role in the choice of the exercise type and the validation process, and students are made aware that their effort can help a bigger scientific quest. This last element brings our platform closer to existing citizen-science and game with a purpose (GWAP) projects (e.g., [fold.it](http://fold.it), [zooniverse.org](https://www.zooniverse.org/), [wordrobe.org](http://wordrobe.org) {BasileBos2012LREC}, [phrasedetectives](https://anawiki.essex.ac.uk/phrasedetectives/)} {Chamberlain08phrasedetectives}) and other GWAP and human computation systems (e.g., the [ESP game](http://en.wikipedia.org/wiki/ESP_game) {von2004labeling}, and [duolingo.com](http://duolingo.com) {vonAhn:2013}). However, none of the these crowdsourcing systems offers a collaborative multi-user and real-time environment for classrooms with exercises which are tightly aligned with school programs and linguistic research.  

The concept of a crowdsourcing application for educational activities has been also suggested in {Skarzauskaite12:crowdEducation}. Finally {Chamberlain:2013fk} presents a more complete overview of different crowdsourcing solutions for language annotation using different methodologies.

For a detailed competitors analysis refer to the next section.


### Which are our keywords? How we'd like to be found from search engines?

Learning Technologies, Educational Games, Crowdsourcing, Linguistic Annotation, Cooperative Learning

## People

### Clients, stakeholders. User need analysis (UNA): which needs we target for each user

1. **Students**

The ST platform improves student engagement during exercise sessions in the classroom and promotes cooperation among the classmates with the teacher's assistance. It enables them to receive an immediate feedback from the teacher right after submitting each answer, and ask questions in case of difficulty.

This activity it's not meant for students to learn new concepts, but to assimilate those already discussed in a normal lesson; School-Tagging cannot be considered a replacement for the unique human experience between teacher and student, the scope would have been completely different. It's the teacher's call to support School-Tagging use with other learning tecnique such as memoization, spaced repetition and focused/diffused mode; School-Tagging can be considered applicable to the learning tecnique based on trial/ errors / feedbacks. [TODO 1]

Benefits: the project aims at improving their engagement during exercise sessions in the classroom and promote cooperation among them with the teacher’s assistance. The tool also enables them to receive an immediate feedback right after submitting each answer. An immediate benefit can be the gamification experience as break to a normal classroom routine, the using of multimedia tools to make the student feeling more "Modern", and the possibility to engage in cooperation/competition schemas within classmates.

UNA: A usability study will be conducted to see how this methodology compares with traditional ones (WP1). [TODO 3]

2. **Teachers**

The platform allows the teacher to control the classroom activity as she follows them step by step in real-time. It also provides a way to monitor overall class progress over longer time, as well as particular students, and guide those who have particular needs. Additionally, teachers can tailor the exercise sets to the class level and interest.

Benefits: The tool enables them to monitor students in the classroom and guide those who have particular needs. The system makes it easier for the teacher to control the whole classroom as he/she follows them step by step in real-time. Additionally, he/she can choose exercises based on the class level. 

Accordingly with the 2nd golden rule for this project, the tool doesn't need any training, neither for the teacher nor for students. Development will try to be as more focused as possible on a clear and self-explaining design, to avoid the teacher spend time on classroom setup or informatics trainings.

UNA: We have already conducted a preliminary assessment of the needs of the teachers (see Section “Maturity of the Project”). We therefore decided to keep the exercises as similar as possible to the traditional ones in terms of content, but give them a new interactive form by means of digital technologies. [TODO 4]

3. **Language Researchers**

The collected annotated data can be made openly available to NLP and DH research communities. Most state-of-the-art systems in Human Language Technology research are based on supervised approaches, requiring large amounts of annotated data to be trained. The collection of such data is a resource- and time-consuming task. The ST platform enables the creation of high-quality training data to happen at the same time as education goals are being achieved.

Benefits: the collected annotated data will be made openly available for other researchers to use. Since most state-of-the-art approaches in Human Language Technology research are “supervised”, i.e. the systems learn to perform a language analysis task from large amounts of annotated data, the availability of such data is crucial to the good performance of the systems. Researchers often experience issues when collecting these so-called training data, since it is an expensive and time-consuming task. Through the CLASS platform, instead, students do language exercises and create high-quality training data at the same time. Given the variety of tasks performed in classrooms, such training data can be divided into different proficiency levels according to the grades under consideration (e.g., primary, secondary school, etc.), and also into different subjects (e.g., grammar, history, literature, etc.). Such training data would therefore cover a variety of topics and difficulty levels, contributing to training a variety of natural language processing systems.

UNA: The members of the DH group have been doing research and data collection in the field of NLP for several years. Therefore they are relatively well aware of the issues and the requirements of researchers in this field. Furthermore, FBK employs around 30 researchers active in the human language technology area. If necessary, they will be involved in an additional user need analysis. [TODO 5]

4. **Stakeholders** [TODO 6]

5. **Competitors**

* Who they are, who will loose from this project, which competition can be triggered, how we can benefit (win/win)

### All Competitor's analysis

## Duolingo

* mission and target needs/users

* why different from us why we're better / worse

* their gamification and didattic/pedagogic aspect

* threats and opportunities

* patents owned

* how they communicate

* what/how they share

* Competitor's academic side: are they open source? Are they capable to share data produced? Are they actually sharing? How are data shared, simple and accessible?

## Blackboard.com

## Moodle.org

## Khanacademy

## Softschools.com

## VISL

## socrative

## infuselearning

## getkahoot

## clickerschool

## zooniverse


### Project Members and collaborative tools

Project is born from an idea of the current project coordinator and game-logic creator, Federico, that met a smart creative software self-taught developer that transformed the idea in something live and playable, Stefano.

We choose to keep the source code open source, and we manage developers contribution with forks and pull requests on the main project repo on [github/erpreciso/school-tagging](https://github.com/erpreciso/school-tagging)

The team also uses github internal process of bug tracking and milestones, keeping discussion threads sticking to each version to be released. Document's sharing is maintained via the hyper-flexible Google Docs and the commenting feature.

We strongly encourage crowdsourcing and open contribution to the project en every aspect, from game design to front-end coding. But Stefano and Federico will remain ultimate responsible for the coding and the designing of the published application, in order to keep an unique conflict resolution hub.

### Developers

Active developers are:

* **Federico Sangati (FBK)** project coordinator and designer of exercises logic units

Federico Sangati has been an NLP researcher for the last 8 years. He has focused on Syntactic Parsing and built tools for Corpora Processing and Analysis. In the last few years he has developed a strong interest towards citizen-science and crowdsourcing systems, and has attended a number of dedicated meetings and established a network of people involved in this field. With the help of other volunteer developers he has built a web-based platform which represents the starting point of the CLASS project (see also “Maturity of the project” section). He has managed to establish a contact with a local secondary school who has agreed to join the WP1 of the project, should it be granted EU fundings.

Principal investigator, researcher. He will be in charge of the research activities of the project leading its scientific part. This will include choosing the data to be annotated, collecting and analysing them, disseminating them at scientific venues, leading the implementation activities by defining the requirements of the CLASS platform and evaluating different versions of it.

* **Stefano Merlo (back-end developer)** software developer and designer, creator if the back-end structure, responsible for exercise logic implementation and version control coordinator.

[TODO 7]

* **Giovanni Moretti (FBK, front-end developer)** final user interface designer for the application

[TODO 7]

For the next releases, plan is to hire also:

* **Game Designer** evaluate ludic aspect, current status, enhancements

* **Pedagogue** to analyze the learning side of the project, evaluating is the paradigms are valid and appropriate for our targets, and simulating and testing new exercise experiences from a didactic point of view

* **Public Relations and Social Media expert** to analyze and evaluate the best strategy for a social media presence for the distribution of the tool. She will also plan presence in forum in dedicated groups, in specialistics webistes, in academic circuits, in conferences and events

* **Expert in social dynamics**  to analyze interactions between actors (teacher/student, student/student, student/classroom) like competition or collaboration

* **Administrative support** accountants, commercials, etc

Potentially the team can grow exponentially since it's open source. For a new contributor it's easy to start working with us since the code repository host, [github](https://github.com/erpreciso/school-tagging), offers a wide range of collaborative tools ready for integration. Steps are same for any other open source project: fork the code, work on that, exchange opinions, questions and feedbacks by email, keep track of issues and resolution by the github issue tracker, then submit a pull request to integrate the development in the mainstream. The version control responsible will evaluate the proposal from a pure technical point of view (no conflict with existing code) since the scope should already been evaluated in an earlier stage, and will integrate the request in the master repo. It will then pushed to production at the next scheduled release. In case of a major change that require an immediate extended testing, the project team can evaluate an extraordinary release in production, but this need to be approved by the majority.

All the technical specs are listed in the dedicated section of the document, so a potential contributor can evaluate if he has the required technical background. Since the main project developer are mostly self-taught for several part of the development aspects, we strongly encourage new technologies or recasting to be proposed, providing mission and golden rules are preserved.

### Other members

* FBK-DH (Sara Tonelli, Rachele Sprugnoli, Stefano Menini)

The FBK-DH (Digital Humanities) group is a recent joint research team which makes use of NLP techniques for developing tools and applications embedded in web based platforms for people working in the humanities, e.g., historians, museums curators, philologists (see also dh.fbk.eu/projects).

Sara Tonelli took part in the FP7 TERENCE project (terenceproject.eu), where she investigated the potential of NLP applied to educational technologies. More recently, she was included among the participants to the COST Action IS1401 “Strengthening Europeans’ capabilities by establishing the European literacy network”. Given this link, the CLASS system will also be presented to the COST Action participants, in order to collect feedback from the community of experts in educational technologies. >>

Research manager. She will be in charge of the management of the project, dealing with the organization of the experimentation (e.g. purchase of equipment, contacts with schools, coordination of the different players involved as well as control over the project workflow). She will also collaborate with the PI in the research activities, for instance the data analysis.

* Micaela Vettori (FBK - innovazione e relazioni con il territorio)

* Nicola Cetrano (Dirigente Istituto comprensivo di Povo) 

* Anna Favàri (Insegnante di Italiano Istituto comprensivo di Povo)

* Robero Rossi (Tecnico Informatico Scuola Istituto comprensivo di Povo)


## Development Plans

[TODO 8]

### Release 0.0: "proof of concept"

* **Milestones**

1. tool backbone (interactivity, simple gamification, login process, data storage and exporting)

2. live demo to be presented to a primary school for testing and feedback collection

* when: now

* game types:

In the current prototype we have implemented 2 grammar game-exercises. 

1. In the first one, the CHOOSE-WORD,  students are presented with a sentence and they have to select all entities (morphemes, single words or word sequences) that belong to a specific grammatical category. An entity can be a discontinuous span such as the italic verb in "She *has* always *wanted* to visit China.

2. In the second exercise, the CHOOSE-CATEGORY, students have to provide syntactic information of a linguistic entity which is highlighted in a given sentence.

The two exercises are complementary to each other with respect to the type of annotation the students input into the system. The first exercise identifies how each sentence is segmented into linguistic units (entities), each being mapped to a coarse grammatical category. The second exercise, enables to ask students more fine grained syntactic information about highlighted entities (e.g. number for nouns, mode and tense for verbs).

Currently, the set of sentences from which exercises are generated is a pre-built corpus of few hundred sentences in both English and Italian. In future versions of the platform, we are planning to allow teachers to input their own sentences or extract them automatically from the Internet.

* Testing plan

We have conducted a pilot study of the current platform in the computer-science lab of an Italian junior-high school equipped with 16 PCs. Two different classrooms (grade 6 and 9) participated in the test with a total number of 48 students, divided in 4 different groups. They have accessed the online platform using the Chrome browser installed in the local machines. The students responded very positively to the novel methodology: in an anonymous questionnaire the overall majority has answered that they liked the system (88.5%), that the teacher's feedback was useful (77.1%) and that they would like to use the system regularitly in class (87.5%).


### Release x.0

* which milestone accomplished
* what's new
	* which needs have been solved
	* new game architecture: explain with a graph or a drawing or a flowchart
	* new target / spreading
	* new collaboration
	* added value! new pubblicity, new collaboration, new academic support
* what has been fixed
* testing plan: who test, how, where to share results.To be included in testing: Did the teachers believe that they put in reasonable effort before, during, and after the activity with reference to the outcomes their pupils achieved (you might want to study the effect size of the ST intervention)?
* resources needed: people, finance, time, know-how
* marketing plan
	* new commercial possibilities
	* price strategy
	* where to distribute, how to innovate distribution
	* advertise, PR: investment and which channels to use, communication strategy
* estimation of the variability for each point: what can be an accellerator, what a risk
* Is search for simplicity part of each milestone?
* Risks

### Release 2.0

............

### Various development ideas to clusterize in releases

[Authentication] Currently only the teacher can authenticate in the system whereas students can access only with the session name provided by the teacher. This simplifies the process since a standard authentication system for students would create a big barrier (as students easily forget their passwords). However this prevents the system from keeping track of the progress of the same student across different sessions. A possible solution would be to create a classroom entity and request the teacher to insert once for all the names of the student in each classroom.

[Exercise Set] The current set of sentence in the system is rather limited. In future versions, we would like to introduce the possibility for the teacher to insert her own sentences or integrate an automatic system, which could crawl them from the Web.

[Home mode] Even though the current modality is envisioned for a classroom, we would like to consider a similar system for students who want to practice at home. Since the teacher cannot always be available for real-time validation, we would consider using some aggregator methods \cite{endriss-fernandez:2013} for deciding the correct answer based on a number of answers to the same exercise provided by students at the same time.

[Gamification] The current prototype offers only to teachers the possibility to monitor the progress of the students. In the future, we plan to include more advance gamification strategies, e.g., badges and points to assign to students as they progress with their learning activities.


[Finalize Grammar Prototype] Overview: Completion of the current grammar prototype in collaboration with the partner school.  Intermediate tests and usability assessments. Deliverable: Release of code of the Grammar prototype on GitHub.  Report with usability assessment and initial evaluation of collected data.

[Grammar Prototype Data Collection] Overview: Test previous prototype in multiple secondary schools (grades 8-10).  Collect annotated data and produce annotated resources for NLP research.  Collection of data until 1st Nov 2015. Deliverable: Report with usability assessment and evaluation of quality of collected data.  Risks (low): Problem in finding  partner schools. This risk can be mitigated by contacting in advance FBK personnel involved in educational projects with local schools. 

[Building a DH Prototype] Overview: Choice and feasibility assessment of a new prototype for a new discipline within the Digital Humanities. Possible options are: language comprehension (history or literature) foreign language acquisition (ancient language or modern language).  Select a secondary school where the prototype (grades 9-12) should be tested.  Build a second prototype for the chosen discipline, and integrate it in the same web platform used for the previous prototype. This will allow us to reuse as much as possible the back-end and front-end code of previous prototype. 
Deliverable: Release of code of the second prototype on GitHub Report on usability assessment and initial evaluation of collected data.
Risks (low): The prototype cannot be implemented on time. The risk related to this activity is rather low, since this second prototype version is an adaptation of the first one.  

[DH Prototype Data Collection] Overview: Test the second prototype in multiple schools (grades 8-10).  Collecting annotated data and produce annotated resources for DH research.
Deliverable: Report on usability assessment and evaluation of quality of collected data.
Risks (low): Risks are the same as in WP2. Also the solution to mitigate them is the same.

[Data Analysis] Overview: Data analysis and final results for data collected in WP2 and WP4. 
Deliverable: Release of all data collected during the project together with a final report.

[Future ambitious releases, too much high but worth to notice]

## Documentation

### How we'll manage project status update? Communication plan

Project plan: github page
The present project plan will be reviewed four times a year; meeting dates are publicy available in the shared calendar.

Status and update of the project: Blog: xxxxxxxxxxx. It will be updated on a monthly basis, as specified in the calendar
We'll schedule a (monthly?) update of the blog, and we'll decide on the go who will bw responsible.
See [github blog](http://www.markschabacker.com/blog/2012/09/15/blog_with_github_pages/)

Calendar: to keep track of project updates, conferences, milestones

Webpage: github-webpage containing both the main project documents and the vignette landing page

Wiki: github-wiki for the academic deocumentation on exercises logic and teaching aspect

Issue tracking and milestones: github system

Multimedia: github wiki

Video application mockup: [link](https://www.youtube.com/watch?v=ZFhHNWUJJKQ&list=UU-3SBPdqwrnuWxE3HQE1FSw)


### Technical specification (technologies used, versions, support until when, plan to upgrade)

The current project's  implementation is based on the [Google Application Engine (GAE) framework](https://cloud.google.com/appengine). GAE enabled us to quickly develop a web-based prototype, which was easily deployable on the Internet, while eliminating all efforts in maintaining a local server, and providing immediate integration of a cloud system for data hosting (the datastore). This technology allows full scalability up to an unrestricted number of users: with no extra effort, the platform could be potentially extended to an unrestricted number of schools across different countries, producing a significantly large volume of multilingual and cross-cultural annotated data. This could foster the creation of a network of students and teachers who could exchange not only their experience, but could provide suggestions for improving the system, while building an international community of expert users.

The backend is implemented in Python, which makes use of two main libraries: [webapp2](https://webapp-improved.appspot.com) (lightweight Python web framework compatible with Google App Engine) and [jinja2](http://jinja.pocoo.org) (full featured template engine for Python).

The frontend development is based on Javascript, and makes use of the [HighCharts](http://www.highcharts.com) graphical library for displaying interactive charts on the teacher interface.

Two main interface templates are available, one for the teacher and one for the students. The Google Channel API is used as interaction framework to enable real-time communication between the students and the teacher. The interactions between the server and the javascript clients works by opening a unique channel using a token identifier.

Regarding the Data Storage, we are using the Google App Engine Datastore, which is built on top of the Bigtable distributed storage system {Chang:2008} with implementation of memcache to improve performance and avoid transactions latency issues and accessible via the [NDB Python API](http://cloud.google.com/appengine/docs/python/ndb), through which the datastore can be exported in JSON format.

The entire source code is openly available on [github](https://github.com/erpreciso/school-tagging)

### User guide

Technical user guide it's minimal since the tool is self explaining. It will contain didactic analysis of the various exercises

### Requirements to be planned: how to collect, how to update

A fundamental need is to collect user's feedback on new features nice-to-have, or ideas or anything. Goal is not to remain a good prototype without a clear and shared purpose but become a real tool with defined scope.

Periodically we'll also collect a customer satisfaction to understand if an update is needed, or if some external changes (i.e. new legislation on BES may open new opportunities) may have impacted the current status.

### Relevant pubblications

Following is the list of relevant publications:

* M. Hosseini, K. Phalp, J. Taylor, and R. Ali. The four pillars of crowdsourcing: a reference model. IEEE Eighth International Conference on Research Challenges in Information Science, May 2014.

* L. von Ahn. Duolingo: Learn a language for free while helping to translate the web. In Proceedings of the 2013 International Conference on Intelligent User Interfaces, IUI ’13, pages 1–2, New York, NY, USA, 2013. ACM.

* M. Fossati, C. Giuliano, and S. Tonelli. Outsourcing framenet to the crowd. In Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics, pages 742–747, Sofia, Bulgaria, August 2013.

* U. Endriss and R. Fernandéz. Collective annotation of linguistic resources: Basic principles and a formal model. In Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics, pages 539–549, Sofia, Bulgaria, August 2013.

* N. Venhuizen, V. Basile, K. Evang, and J. Bos. Gamification for word sense labeling. In Proceedings of the 10th International Conference on Computational Semantics, pages 397–403, Potsdam, Germany, 2013.

* P. Manohar and S. Roy. Crowd, the teaching assistant: Educational assessment crowdsourcing. In B. Hartman and E. Horvitz, editors, HCOMP. AAAI, 2013.

* M. Skaržauskaitė. The application of crowd sourcing in educational activities. Social Technologies, 2(1):67–76, 2012.

* L. von Ahn and L. Dabbish. Designing games with a purpose. Commun. ACM, 51(8):58–67, Aug. 2008.

* J. Chamberlain, M. Poesio, and U. Kruschwitz. Phrase detectives - a web-based collaborative annotation game. In In Proceedings of I-Semantics, 2008.

* L. Von Ahn and L. Dabbish. Labeling images with a computer game. In Proceedings of the SIGCHI conference on Human factors in computing systems, pages 319–326. ACM, 2004.

## Business Plan

### Costs (of the total project, and related to single milestones)

Divide between setup and running costs, and preview what will be one shot and what will be regular.
 In this section you will need to estimate the overall cost of the project.
1.) Project Budget
A detailed, line-item budget should be divided into categories such as salaries, fringe benefits, travel, supplies, and equipment. Make sure to also include any overhead costs (called "indirect costs") that will be associated with the project.
2.) Budget Narrative
The budget narrative is basically a list of commentary needed to clarify and justify the figures on your budget.
3.) Additional Financial Statements
Some project proposals may require additional financial statements, such as a profit and loss statement, a recent tax return, an annual report, or a list of funding sources.

### Cost examples to be planned in various releases

* **Humar Resources**

Travel expenses for the dissemination activity. Since the development of the system  is based on a well-defined research idea, we expect an interesting research outcome to be generated during the project. Therefore, the involved researchers will take part in at least two international conferences to present the project results to the scientific community.

Subcontracting: In order to organize the project work and plan with teachers the development and use of the CLASS system, we foresee some extra work for the personnel involved in the two schools under consideration. Therefore, we devoted a small part of the budget to cover teachers overtime for meetings and training (in WP1 and WP3).

* **Hardware**
The cost of 25 tablets that students can borrow to take part in the tagging activities (as part of WP1, WP2, WP3, WP4). The number corresponds to the estimated number of students in a class. This cost is necessary since not all schools rely on sufficient equipment (i.e., a device per student). The tablet model will be chosen in order to limit the costs while providing the students with the necessary functionalities. All needed software will be strictly freeware (i.e., web browser). With the consent of the teachers, students will be allowed to use either their own devices or those owned by the school instead of borrowing project-owned tablets.

1 PC (laptop or mac-mini) for the teacher to create a wireless area network (WAN) for testing the applications in the classroom, in case a school is not equipped with WiFi Internet. In schools with WiFi, teachers can rely on their own device or use one of the project tablets. 


### Commercial opportunity

Which is the value proposition? what is actually bringing value and cash?

### Go-to-market plan

Here to describe business opportunity already established, and identify principal subjects with whom to deal (commitment, customers, providers, sponsors, collaborators).

Also to describe which is the license, and why this choice for this business model.

How the project can be self-sustainable? Where are incentives for the open source development?

Evaluate pro/cons of to be intergrated in a bigger platform.


The aim of the current project is to build a fully functioning prototype to be tested on a limited number of classrooms. We have chosen to use the Google Application Engine (GAE) since it enabled us to quickly develop web-based prototypes which are easily deployable on the Internet and integrates a cloud system for data hosting. The system has no costs for the limited number of users we intend to include during the funding period. 

GAE technology allows scalability up to an unrestricted number of users: with no extra effort, the platform could be potentially extended to an unrestricted number of schools across different European countries, producing a significantly large volume of multilingual and cross-cultural annotated data. This could foster the creation of a network of students and teachers who could exchange not only their experience, but could provide suggestions for improving the system while building a community of expert users across different countries. 

Above a certain user quota GAE has a cost which is proportional to the number of requests. By the end of the project, a plan will be needed for ensuring the sustainability of the project, along the following guidelines:

Since the principal users of the system are  teachers and students, it should remain free for schools. They should in turn agree to make the anonymized collected data free for non commercial use. 

The system shall remain open-source to allow other developers to build novel game-exercise along the same back-end and front-end templates, and preferably, incorporating them within the same web platform.

As for commercial organizations, a certain fee would apply for embedding  the platform in their educational software or making use of the collected data. Together with donations and other possible funding partners, this would help to cover the maintenance costs and possibly promote further expansion of the platform.

### Investment plan

How to promote fundraising and crowfunding?

### Resources availability

What is available now and after, and what is temporary?

### Environmental impact

The app will be designed to be as much simple and cross-platform as possible, in order to be used with IT hardware resources already available to users, without requiring incremental cost in terms of energy or purchase of device.

## Risks

Possible risks and single point of failures that may jeopardize the entire project
Project Risk Management
This section details the major project risks and delineates the plans to alleviate or control them. Make sure to address each risk's likelihood of occurring as well as its impact on the project and the organization.
1.) Risk Management Plan
This is the detailed plan of action to minimize and contain any risk factors that may come up as the project progresses.
2.) Risk Register
Be sure to include this line-item list of risks and counter efforts.

Risks (medium): Partner school’s classrooms are not equipped with WiFi and digital technologies. Possible solutions are: Using computer labs (although not big enough to hold an entire classroom).  Providing tablets to students to be used during working sessions and provide a laptop to the teachers to function as a hot-spot running a local network (solution has been successfully tested).

