from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, TextAreaField, FloatField, TextField, RadioField

from wtforms.fields.core import SelectField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, Regexp, Optional, ValidationError
from AAT.models import User
from flask import flash
from datetime import datetime

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class StudentRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
                             DataRequired(), Length(max=60)])
    last_name = StringField('Last Name', validators=[
                            DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password', 'The passwords need to match.')])
    student_number = StringField('Student Number', validators=[DataRequired(),
                                Regexp('^(\d{7})|(\d{8})$',
                                message="Student number must be a sequence of 7 or 8 digits")])
    graduation_date = DateField('Graduation Date', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int)
    submit = SubmitField('Register')

class StaffRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
                             DataRequired(), Length(max=60)])
    last_name = StringField('Last Name', validators=[
                            DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8, max=60)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password', 'The passwords need to match.')])
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Register')

class MCQForm(FlaskForm):
    # for question table
    question_text = StringField("Question:", validators=[DataRequired()])
    hint = StringField("Hint:", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])

    # for multiple_choice_question table
    correct_answer_id = IntegerField("Correct answer number:", validators=[DataRequired()])

    #for multiple_choice_option table (Assuming 4 answers for each question for now)
    answer_1 = StringField("Answer 1:", validators=[DataRequired()])
    answer_2 = StringField("Answer 2:", validators=[DataRequired()])
    answer_3 = StringField("Answer 3:", validators=[DataRequired()])
    answer_4 = StringField("Answer 4:", validators=[DataRequired()])
    submit = SubmitField("submit")

class StudentFeedbackForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    rating = RadioField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], coerce=int, validators=[DataRequired()])
    submit = SubmitField("submit")

class CreateAssessment(FlaskForm):
    title = StringField('Assessment Title:', validators=[DataRequired()])
    set_date = DateField('Set Date:', validators=[DataRequired()])
    max_marks = FloatField('Maximum Marks:', validators=[DataRequired()])
    passing_mark = FloatField('Passing Mark:', validators=[DataRequired()])
    module_id = StringField('Module ID:', validators=[DataRequired()])
    submit = SubmitField("submit")

    def validate_setdate_field(self, form, field):
        if form.set_date.data < datetime.now():
            raise ValidationError("Assessment must be set in the future.")

class CreateSummativeAssessment(FlaskForm):
    deadline = DateField('Assessment Date:', format='%Y-%m-%d', validators=[DataRequired()])
    return_date = DateField('Feedback Return Date:', format='%Y-%m-%d', validators=[DataRequired()])
    time_limit_seconds = IntegerField('Length of Assessment:', validators=[DataRequired()])
    mark_criteria = TextField('Mark Criteria:',  validators=[DataRequired()])
    submit = SubmitField("submit")

    def validate_returndate_field(self, form, field):
        if form.return_date.data < form.assessment_date.data:
            raise ValidationError("Assessment return date must be after the assessment date.")

class CreateFormativeAssessment(FlaskForm):
    submit = SubmitField("submit")

class TakeMCQ(FlaskForm):
    submit = SubmitField("submit")

class StaffFeedbackForm(FlaskForm):
    course_id = IntegerField('course_id',validators=[DataRequired(), Length(max=10)])
    student_number = IntegerField('student_number',validators=[DataRequired(), Length(max=10)])
    submit = SubmitField("submit")

def validate_answers(form, field, question_text):
    if field.data > len(question_text):
        raise ValidationError("Answer index out of range of number of words in question")

class FTBQform(FlaskForm):
    question_text = TextAreaField("Question:", validators=[DataRequired()])
    hint = StringField("Hint:", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    answer_1 = IntegerField("Answer 1", validators=[DataRequired()])
    answer_2 = IntegerField("Answer 2", validators=[Optional()])
    answer_3 = IntegerField("Answer 3", validators=[Optional()])
    answer_4 = IntegerField("Answer 4", validators=[Optional()])
    answer_5 = IntegerField("Answer 5", validators=[Optional()])
    answer_6 = IntegerField("Answer 6", validators=[Optional()])
    answer_7 = IntegerField("Answer 7", validators=[Optional()])
    answer_8 = IntegerField("Answer 8", validators=[Optional()])
    submit = SubmitField("submit")

    def validate(self):
        if not super().validate():
            return False
        for field in [self.answer_1, self.answer_2, self.answer_3, self.answer_4, self.answer_5, self.answer_6, self.answer_7, self.answer_8]:
            if field.data != None:
                if field.data > len(self.question_text.data):
                    # field.errors.append('Answer index cannot be greater than length of question')
                    flash("Answer index cannot be greater than length of question")
                    return False
        return True
        
class AnswerFTBQform(FlaskForm):
    answer_1 = TextField("Answer 1", validators=[DataRequired()])
    answer_2 = TextField("Answer 2", validators=[Optional()])
    answer_3 = TextField("Answer 3", validators=[Optional()])
    answer_4 = TextField("Answer 4", validators=[Optional()])
    answer_5 = TextField("Answer 5", validators=[Optional()])
    answer_6 = TextField("Answer 6", validators=[Optional()])
    answer_7 = TextField("Answer 7", validators=[Optional()])
    answer_8 = TextField("Answer 8", validators=[Optional()])              
    submit = SubmitField("submit")

class TestForm(FlaskForm):
    field = StringField("Test Field", validators=[Length(max=60)])
    hidden = HiddenField("Hidden Field", validators=[DataRequired()])
    submit = SubmitField("Submit")

class TakeAssessment(FlaskForm):
    number_of_answers = HiddenField("Number of Answers", validators=[DataRequired("You must answer all the questions before you submit.")])
    submit_assessment = SubmitField("Submit Assessment")

class QuestionsAnswered(object):
    def __init__(self, needed=0):
        self.needed = needed
    
    def __call__(self, form, answered):
        fname = 'QuestionsAnswered().__call__'
        valid = answered.data and answered.data == self.needed
        if not valid:
            raise ValidationError(f"You only answered {str(answered.data) if answered.data else '0'} of {self.needed} questions.")