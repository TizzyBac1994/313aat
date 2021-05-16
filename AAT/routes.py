from flask import render_template, url_for, redirect, request, flash
from AAT import app, db
from AAT.models import (
    AttemptAnswer, User, Course, Module, Staff, Student, Assessment, FormativeAssessment,
    SummativeAssessment, QuestionAndValue, Question, MultipleChoiceQuestion,
    MultipleChoiceOption, FillTheBlanksQuestion, AssessmentAttempt, staff_modules,
    StudentFeedback
)

from AAT.forms import (
    LoginForm, MCQForm, QuestionsAnswered, StaffRegistrationForm, StudentRegistrationForm,
    StudentFeedbackForm, CreateSummativeAssessment, CreateAssessment,
    CreateFormativeAssessment, FTBQform, TakeAssessment, TakeMCQ, AnswerFTBQform,
    TestForm
)

from flask_login import (
    login_user, logout_user, current_user, login_required
)
from sqlalchemy import desc

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/register")
def register():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        redirect(url_for('home'))
    return render_template('register/register_menu.html')

@app.route("/register/student", methods=['GET', 'POST'])
def student_register():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        redirect(url_for('home'))
    form = StudentRegistrationForm()
    form.course_id.choices = [(c.id, c.name) for c in Course.query.order_by('name')]
    if form.validate_on_submit():
        student = Student(first_name=form.first_name.data, last_name=form.last_name.data,
                          email=form.email.data, password=form.password.data,
                          student_number=form.student_number.data, course_id=form.course_id.data,
                          graduation_date=form.graduation_date.data)
        db.session.add(student)
        db.session.commit()
        login_user(student)
        flash('Thank you for registering, ' + student.first_name + "!")
        return redirect(url_for('home'))
    return render_template('register/student_register_form.html', form=form)

@app.route("/register/staff", methods=['GET', 'POST'])
def staff_register():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        redirect(url_for('home'))
    form = StaffRegistrationForm()
    if form.validate_on_submit():
        staff = Staff(first_name=form.first_name.data, last_name=form.last_name.data,
                          email=form.email.data, password=form.password.data,
                          job_title=form.job_title.data)
        db.session.add(staff)
        db.session.commit()
        login_user(staff)
        flash('Thank you for registering, ' + staff.first_name + "!")
        return redirect(url_for('home'))
    return render_template('register/staff_register_form.html', form=form)

@app.route("/assessments")
@login_required
def assessments():
    return render_template("assessments/assessments_index.html")

@app.route("/MCQ", methods=["GET", "POST"])
@login_required
def MCQ():
    if current_user.type == 'student':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    form = MCQForm()
    if form.validate_on_submit():
        new_question = MultipleChoiceQuestion(correct_answer_id=form.correct_answer_id.data, question_text=form.question_text.data, hint=form.hint.data, category=form.category.data)
        db.session.add(new_question)
        db.session.commit()

        answer_1 = MultipleChoiceOption(value=form.answer_1.data, question_id=new_question.id)
        answer_2 = MultipleChoiceOption(value=form.answer_2.data, question_id=new_question.id)
        answer_3 = MultipleChoiceOption(value=form.answer_3.data, question_id=new_question.id)
        answer_4 = MultipleChoiceOption(value=form.answer_4.data, question_id=new_question.id)

        db.session.add(answer_1)
        db.session.add(answer_2)
        db.session.add(answer_3)
        db.session.add(answer_4)
        db.session.commit()

        # in the multiple_choice_option table each set of choices follow each other so doing += answer_1.id
        # offsets the 1-4 value inputted in the form to match whats stored in the database.
        new_question.correct_answer_id += answer_1.id -1
        db.session.commit()
        flash("question added")
        return redirect(url_for("home"))

    return render_template('MCQ.html', form=form)

@app.route("/student-feedback/<int:assessment_id>", methods=["GET", "POST"])
@login_required
def student_feedback_for_assessment(assessment_id):
    if current_user.type == "staff":
        flash('Only students can leave feedback!')
        redirect(url_for('home'))
    form = StudentFeedbackForm()
    assessment = Assessment.query.get_or_404(assessment_id)
    if form.validate_on_submit():
        feedback = StudentFeedback(student_id=current_user.id, assessment_id=assessment_id, content=form.content.data, rating=form.rating.data)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback Submitted', 'success')
        return redirect(url_for("home"))
    return render_template('student-feedback.html', form=form, assessment=assessment)

@app.route("/student-feedback/create", methods=["GET", "POST"])
@login_required
def student_feedback():
    if current_user.type == "staff":
        flash('Only students can leave feedback!')
        redirect(url_for('home'))
    form = StudentFeedbackForm()
    if form.validate_on_submit():
        feedback = StudentFeedback(student_id=current_user.id, content=form.content.data, rating=form.rating.data)
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback Submitted', 'success')
        return redirect(url_for("home"))
    return render_template('student-feedback.html', form=form, assessment=None)

@app.route("/staffFeedback", methods=["GET", "POST"])
@login_required
def staffFeedback():
    form = StaffFeedbackForm()
    
    feedback = []
    student = ''
    student_number = ''
    
    if request.method == 'POST':
        student_number = request.form.get('student_number')
        student = Student.query.filter_by(student_number=student_number).first()
        feedback = student.feedback
    return render_template('staffFeedback.html',feedback=feedback,form=form)

@app.route("/manage-questions/<int:assessment_id>", methods=["GET", "POST"])
@login_required
def manage_questions(assessment_id):
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    questions = QuestionAndValue.query.filter_by(assessment_id=assessment_id).all()
    return render_template('manage-questions.html', questions=questions)

@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    if current_user.type != 'staff':
        flash('Only staff can do that!')
        return redirect(url_for('home'))
    # Deletes specified question from the assessment

    question_delete = Question.query.get_or_404(id)
    question_and_value_delete = QuestionAndValue.query.get_or_404(id)

    db.session.delete(question_delete)
    db.session.delete(question_and_value_delete)
    db.session.commit()
    return redirect(f'/manage-questions/<int:id>')

@app.route("/editMCQ/<int:id>", methods=["GET", "POST"])
@login_required
def editMCQ(id):
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    form = MCQForm()
    edit_question = Question.query.get_or_404(id)
    load_data = MultipleChoiceOption.query.filter_by(question_id=id).all()
    load_correct_answer = MultipleChoiceQuestion.query.filter_by(id=id).first()

    if request.method == "POST":
        edit_question.question_text = request.form['question_text']
        edit_question.hint = request.form['hint']
        edit_question.category = request.form['category']

        load_data[0].value = request.form['Answer1']
        load_data[1].value = request.form['Answer2']
        load_data[2].value = request.form['Answer3']
        load_data[3].value = request.form['Answer4']
        load_correct_answer.correct_answer_id = request.form['correct_answer']

        db.session.commit()
        return redirect(f'/manage-questions/1')
        
    else:
        return render_template('editMCQ.html', edit_question=edit_question, form=form, load_data=load_data, load_correct_answer=load_correct_answer)

@app.route("/manage-assessments/<int:user_id>", methods=["GET", "POST"])
@login_required
def manage_assessments(user_id):
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))

    #staff = Module.query.filter(staff_modules.c.staff_id==user_id).all()

    staff = Assessment.query.filter((Assessment.module_id == staff_modules.c.module_id) & (staff_modules.c.staff_id == user_id)).all()
        
        #(staff_modules.c.staff_id==user_id) & (staff_modules.c.module_id == Assessment.module_id) )


    return render_template('manage-assessments.html', staff=staff)

@app.route("/delete-assessment/<int:id>", methods=["GET", "POST"])
@login_required
def delete_assessment(id):
    if current_user.type != 'staff':
        flash('Only staff can do that!')
        return redirect(url_for('home'))
    # Deletes specified assessment

    question_delete = Question.query.filter((Question.id == QuestionAndValue.question_id) & (QuestionAndValue.assessment_id == id)).all()
    mcq_options_delete = MultipleChoiceOption.query.filter((MultipleChoiceOption.question_id == QuestionAndValue.question_id) & (QuestionAndValue.assessment_id == id)).all()
    mcq_delete = MultipleChoiceQuestion.query.filter((MultipleChoiceQuestion.id == QuestionAndValue.question_id) & (QuestionAndValue.assessment_id == id)).all()
    ftb_delete = FillTheBlanksQuestion.query.filter((FillTheBlanksQuestion.id == QuestionAndValue.question_id) & (QuestionAndValue.assessment_id == id)).all()

    question_and_value_delete = QuestionAndValue.query.filter(QuestionAndValue.assessment_id == id).all()
    assessment_delete = Assessment.query.get_or_404(id)

    for k in mcq_options_delete:
        db.session.delete(k)

    for l in mcq_delete:
        db.session.delete(l)

    for m in ftb_delete:
        db.session.delete(m)

    for j in question_and_value_delete:
        db.session.delete(j)
        
    for i in question_delete:
        db.session.delete(i)

    db.session.delete(assessment_delete)
    db.session.commit()
    return redirect(f'/manage-assessments/4')

@app.route("/summative-assessment", methods=["GET", "POST"])
@login_required
def summative_assessment():
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    form_1 = CreateAssessment()
    form_2 = CreateSummativeAssessment()

    if form_1.validate_on_submit(): 
        new_summative_assessment = SummativeAssessment(deadline=form_2.deadline.data, return_date=form_2.return_date.data, \
        time_limit_seconds= form_2.time_limit_seconds.data, mark_criteria=form_2.mark_criteria.data, title=form_1.title.data, set_date=form_1.set_date.data, max_marks=form_1.max_marks.data, \
        passing_mark=form_1.passing_mark.data, module_id=form_1.module_id.data, type="summative")

        db.session.add(new_summative_assessment)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("create-summative-assessment.html", form_1=form_1, form_2=form_2)

@app.route("/formative-assessment", methods=["GET", "POST"])
@login_required
def formative_assessment():
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    form_1 = CreateAssessment()
    form_2 = CreateFormativeAssessment()
    formatives = Assessment.query.order_by(desc('set_date')).first()

    if form_1.validate_on_submit():
        new_formative_assessment = FormativeAssessment(title=form_1.title.data, set_date=form_1.set_date.data, max_marks=form_1.max_marks.data, \
        passing_mark=form_1.passing_mark.data, module_id=form_1.module_id.data, type="formative")

        db.session.add(new_formative_assessment)
        db.session.commit()
        return redirect(url_for("/manage-questions/"))

    return render_template("create-formative-assessment.html", form_1=form_1, form_2=form_2, formatives=formatives)

@app.route('/FTBQ', methods=['GET', 'POST'])
@login_required
def ftbq():
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    form = FTBQform()
    
    if form.validate_on_submit():
        
        
        question_text, answers_text = FTBQ_submit(form)
        question = FillTheBlanksQuestion(question_text = question_text, hint = form.hint.data, category = form.category.data, answer_1 = answers_text[0], answer_2 = answers_text[1], answer_3 = answers_text[2], answer_4 = answers_text[3], answer_5 = answers_text[4], answer_6 = answers_text[5], answer_7 = answers_text[6], answer_8 = answers_text[7])
        db.session.add(question)
        db.session.commit()
        flash("Question added")
        return render_template('ftbq.html', form=form)

    return render_template('ftbq.html', form=form)

@app.route("/editFTBQ/<int:id>", methods=["GET", "POST"])
@login_required
def editFTBQ(id):
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    form = FTBQform()
    q = FillTheBlanksQuestion.query.filter_by(id=id).first() 
    
    fill_counter = 0
    question_text = q.question_text
    qt_split = question_text.split(" ")
    answers_list = [q.answer_1, q.answer_2, q.answer_3, q.answer_4, q.answer_5, q.answer_6, q.answer_7, q.answer_8]
    for count, value in enumerate(answers_list):
        if value == None:
            answers_list[count] = ""
    
    for i in range(0, len(qt_split)):
        if qt_split[i][:4] == "[Fil":
            qt_split[i] = answers_list[fill_counter]
            answers_list[fill_counter] = i + 1
            fill_counter += 1
    question_text = " ".join(qt_split)
    
    if form.validate_on_submit():
        question_text, answers_index = FTBQ_submit(form)

        q.question_text = question_text
        q.hint = form.hint.data
        q.category = form.category.data
        q.answer_1 = answers_index[0]
        q.answer_2 = answers_index[1]
        q.answer_3 = answers_index[2]
        q.answer_4 = answers_index[3]
        q.answer_5 = answers_index[4]
        q.answer_6 = answers_index[5]
        q.answer_7 = answers_index[6]
        q.answer_8 = answers_index[7]
        
        db.session.commit()
        return redirect(f'/manage-questions/1')
    
    return render_template('editFTBQ.html', form=form, q=q, question_text = question_text, answers_list = answers_list)

def FTBQ_submit(form):
    question_text = form.question_text.data
    question_text_array = question_text.split()
    #answers are inputted into the form as indexs of the where the answers are in the question
    answers_index = [form.answer_1.data, form.answer_2.data, form.answer_3.data, form.answer_4.data, form.answer_5.data, form.answer_6.data, form.answer_7.data, form.answer_8.data]
    #lambda function taken from https://stackoverflow.com/questions/18411560/sort-list-while-pushing-none-values-to-the-end
    answers_index =  sorted(answers_index, key=lambda x: (x is None, x))
    answers_text = []

    #uses the indexs of the answers to put the answers into answers_text and replace them in the question with [Fill_#X]
    for i in range(0,len(answers_index)) :
        if answers_index[i] == None:
            answers_text.append(answers_index[i])
        else:
            answers_index[i] -= 1
            if answers_index[i] < len(question_text_array):
                answers_text.append(question_text_array[answers_index[i]])
                question_text_array[answers_index[i]] = "[Fill_#" + str(i) + "]"  

    question_text = " ".join(question_text_array) 
    return question_text, answers_text

@app.route("/statistics")
@login_required
def statistics():
    return render_template('statistics.html')

@app.route("/statistics/assessment-statistics")
@login_required
def assessment_statistics():
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    return render_template("statistics/staff-assessment-stats.html")

@app.route("/statistics/student-statistics")
@login_required
def student_statistics():
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    students = Student.query.all()
    return render_template("statistics/staff-student-stats.html", students=students)

@app.route("/statistics/student-statistics/<int:student_number>")
@login_required
def individual_student_statistics(student_number):
    if current_user.type != 'staff':
        flash('Only staff can access that page!')
        return redirect(url_for('home'))
    student = Student.query.filter_by(student_number=student_number).first()
    return render_template("statistics/staff-individual-student-stats.html", student=student)


@app.route("/answer-FTBQ/<int:id>", methods=["GET", "POST"])

def answer_FTBQ(id):
    form = AnswerFTBQform()
    q = FillTheBlanksQuestion.query.filter_by(id=id).first()
    answers_list = [q.answer_1, q.answer_2, q.answer_3, q.answer_4, q.answer_5, q.answer_6, q.answer_7, q.answer_8]
    
    answers_count = 0
    for i in range(8):
        if answers_list[i] != None:
            answers_count += 1

    if form.validate_on_submit():
        answers_attempts = [form.answer_1.data, form.answer_2.data, form.answer_3.data, form.answer_4.data, form.answer_5.data, form.answer_6.data, form.answer_7.data, form.answer_8.data]
        for i in range(answers_count):
            flash(i)
            if answers_list[i] == answers_attempts[i]:
                # put actual logic here
                flash("Answer " + str(i) + " correct")
            else:
                flash("Answer " + str(i) + " incorrect")
                
        flash("submitted")

    return render_template("answer-FTBQ.html",answers_count = answers_count, form = form, text = q.question_text, hint = q.hint, category = q.category, answer_1 = q.answer_1)

@app.route("/take-mcq/<int:id>", methods=["GET", "POST"])
@login_required
def take_mcq(id):
    form = TakeMCQ()
    load_question = Question.query.filter_by(id=id).first()
    load_answers = MultipleChoiceOption.query.filter(MultipleChoiceOption.question_id == id).all()
    load_correct_answer = MultipleChoiceQuestion.query.filter(MultipleChoiceQuestion.id == id).first()
    idStr = str(id)

    if form.validate_on_submit():
        if request.form['answer'] == str(load_correct_answer.correct_answer_id):
            flash("Correct Answer")
            return redirect(f'/take-mcq/'+ idStr)
        else:
            flash("Incorrect Answer")
            return redirect(f'/take-mcq/' + idStr)
    else:
        return render_template("answer-mcq.html", load_answers=load_answers, load_correct_answer = load_correct_answer, load_question=load_question, form=form)

@app.route("/test-form", methods=["GET", "POST"])
def test_form():
    form = TestForm()
    if request.method == "POST":
        questions_answered = QuestionsAnswered(needed=4)
        form.hidden.data = 2
        form.hidden.validators.append(questions_answered)
    if form.validate_on_submit():
        form.hidden.validators.remove(questions_answered)
        flash("Submitted without errors!")
        return redirect(url_for('test_form'))
    try:
        if questions_answered in form.hidden.validators:
            form.hidden.validators.remove(questions_answered)
    except:
        pass
    return render_template('test-form.html', form=form)

@app.route("/assessments/<int:assessment_id>/create-attempt", methods=["POST"])
@login_required
def create_assessment_attempt(assessment_id):
    if current_user.type != 'student':
        flash('Only students can access that page!')
        return redirect(url_for('home'))
    attempt = AssessmentAttempt(student_id=current_user.id, assessment_id=assessment_id)
    db.session.add(attempt)
    db.session.commit()
    flash("New assessment attempt started!")
    return redirect(url_for('take_assessment_attempt', attempt_id=attempt.id))

@app.route("/assessment-attempt/<int:attempt_id>/take", methods=["GET", "POST"])
@login_required
def take_assessment_attempt(attempt_id):
    attempt = AssessmentAttempt.query.get_or_404(attempt_id)
    if current_user.id != attempt.student_id:
        flash('Only the creator of this assessment attempt can view this page!')
        return redirect(url_for('home'))
    assessment = attempt.assessment
    assessment_form = TakeAssessment()
    existing_answers_list = attempt.answers
    existing_answers_dict = {}
    for ans in existing_answers_list:
        question = QuestionAndValue.query.get(ans.question_and_value_id).question
        if question.type == 'multiple_choice':
            value = MultipleChoiceOption.query.get(int(ans.answer)).value
        else:
            value = ans.answer
        existing_answers_dict[ans.question_and_value_id] = value
    if request.method == "POST":
        questions_answered = QuestionsAnswered(needed=len(assessment.questions_and_values))
        assessment_form.number_of_answers.data = AttemptAnswer.query.filter_by(assessment_attempt_id=attempt.id).count()
        print(assessment_form.number_of_answers.data)
        assessment_form.number_of_answers.validators.append(questions_answered)
    if assessment_form.validate_on_submit():
        assessment_form.number_of_answers.validators.remove(questions_answered)
        attempt.submitted = True
        db.session.add(attempt)
        db.session.commit()
        flash("Assessment submitted!")
        return redirect(url_for('review_assessment_attempt', attempt_id=attempt_id))
    try:
        if questions_answered in assessment_form.number_of_answers.validators:
            assessment_form.number_of_answers.validators.remove(questions_answered)
    except:
        pass
    return render_template('assessments/take-assessment.html', assessment=assessment, form=assessment_form, attempt=attempt, existing_answers=existing_answers_dict)

@app.route("/mcq-attempt-answer/<int:attempt_id>/<int:qav_id>/submit", methods=["POST"])
@login_required
def submit_mcq_attempt_answer(attempt_id, qav_id):
    attempt = AssessmentAttempt.query.get_or_404(attempt_id)
    if current_user.id != attempt.student_id:
        flash('Only the creator of this assessment attempt can submit an answer!')
        return redirect(url_for('home'))
    existing_answer = AttemptAnswer.query.filter_by(assessment_attempt_id=attempt_id, question_and_value_id=qav_id).first()
    if existing_answer:
        existing_answer.answer = request.form['answer']
        db.session.add(existing_answer)
        db.session.commit()
    else:
        answer = AttemptAnswer(assessment_attempt_id=attempt_id, question_and_value_id=qav_id, answer=request.form['answer'])
        db.session.add(answer)
        db.session.commit()
    return "Done"

@app.route("/ftb-attempt-answer/<int:attempt_id>/<int:qav_id>/submit", methods=["POST"])
@login_required
def submit_ftb_attempt_answer(attempt_id, qav_id):
    attempt = AssessmentAttempt.query.get_or_404(attempt_id)
    if current_user.id != attempt.student_id:
        flash('Only the creator of this assessment attempt can submit an answer!')
        return redirect(url_for('home'))
    answers = []
    for i in range(8):
        if f"answer_{str(i+1)}" in request.form.keys():
            answers.append(request.form[f"answer_{str(i+1)}"])
        else:
            break
    existing_answer = AttemptAnswer.query.filter_by(assessment_attempt_id=attempt_id, question_and_value_id=qav_id).first()
    if existing_answer:
        existing_answer.answer = ','.join(answers)
        db.session.add(existing_answer)
        db.session.commit()
    else:
        answer = AttemptAnswer(assessment_attempt_id=attempt_id, question_and_value_id=qav_id, answer=','.join(answers))
        db.session.add(answer)
        db.session.commit()
    return "Done"

@app.route("/assessments/review/<int:attempt_id>")
@login_required
def review_assessment_attempt(attempt_id):
    attempt = AssessmentAttempt.query.get_or_404(attempt_id)
    if current_user.type == 'student' and current_user.id != attempt.student_id:
        flash('Only the creator of this assessment attempt can submit an answer!')
        return redirect(url_for('home'))
    assessment = attempt.assessment
    existing_answers_list = attempt.answers
    existing_answers_dict = {}
    for ans in existing_answers_list:
        question = QuestionAndValue.query.get(ans.question_and_value_id).question
        if question.type == 'multiple_choice':
            if ans.answer == 'did_not_answer':
                value = "Did Not Answer"
            else:
                value = MultipleChoiceOption.query.get(int(ans.answer)).value
            existing_answers_dict[ans.question_and_value_id] = {"value": value, "correct_id": question.correct_answer_id, "raw_answer": ans.answer}
        else:
            if ans.answer == 'did_not_answer':
                value = "Did Not Answer"
                answer = "[blank],"*8
            else:
                value = ans.answer
                answer = ans.answer
            existing_answers_dict[ans.question_and_value_id] = {"value": value, "answer_list": answer.split(','), "correct_list": question.answer_list(), "raw_answer": ans.answer}
    return render_template('assessments/review-assessment-attempt.html', attempt=attempt, assessment=assessment, existing_answers=existing_answers_dict)