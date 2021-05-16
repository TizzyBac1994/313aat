from datetime import datetime
from functools import reduce
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from AAT import db, login_manager


def capitalize(string):
    """Returns a capitalized version of a string"""
    return string[0].upper() + string[1:]

class User(UserMixin, db.Model):
    """User model, with polymorphic fields
    
    The 'type' attribute is used to discriminate between different sorts of
    users, namely 'staff' and 'student' users. This allows for the use of
    Student and Staff classes with all inherited features of the parent User
    class.

    See also:
    https://docs.sqlalchemy.org/en/14/orm/inheritance.html#joined-table-inheritance
    """
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __repr__(self):
        return f"User('{capitalize(self.type)}' - '{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""Join table for modules that a modules attached to a course"""
# See: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers

course_modules = db.Table('course_modules', 
                        db.Column('course_id', db.Integer, 
                                 db.ForeignKey('course.id')),
                        db.Column('module_id', db.Integer,
                                 db.ForeignKey('module.id')))

class Course(db.Model):
    """Course model, for a course a student can be enrolled on"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    students = db.relationship('Student', backref='course', lazy=True)
    modules = db.relationship('Module', secondary=course_modules, backref='courses', lazy='dynamic')

    def __repr__(self):
        return f"Course('{self.name}')"
    
    @property
    def assessments(self):
        assessments = []
        for module in self.modules:
            assessments.extend(module.assessments)
        return assessments

    def average_percentage(self, rounded=False):
        if len(self.assessments) == 0:
            return None
        percentage = reduce(lambda acc, cur: acc + cur.average_percentage(), self.assessments, 0) / len(self.assessments)
        return round(percentage, 1) if rounded else percentage


class Module(db.Model):
    """Module model
    
    For a module a student can take, or a staff member can
    be involved in teaching. Not linked to a particular course.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    module_code = db.Column(db.String(10), unique=True, nullable=False)
    assessments = db.relationship('Assessment', backref='module')

    def __repr__(self):
        return f"Module('{self.module_code}' - '{self.name}')"
    
    def average_percentage(self, rounded=False):
        if len(self.assessments) == 0:
            return None
        percentage = reduce(lambda acc, cur: acc + cur.average_percentage(), self.assessments, 0) / len(self.assessments)
        return round(percentage, 1) if rounded else percentage
    
    def student_average_percentage(self, student_id, rounded=False):
        if len(self.assessments) == 0:
            return 0
        percentage = reduce(lambda acc, cur: acc + cur.student_best_percentage(student_id=student_id), self.assessments, 0) / len(self.assessments)
        return round(percentage, 1) if rounded else percentage


"""Join table for modules that a student can be enrolled on"""
# See: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers

staff_modules = db.Table('staff_modules', 
                        db.Column('staff_id', db.Integer, 
                                 db.ForeignKey('staff.id')),
                        db.Column('module_id', db.Integer,
                                 db.ForeignKey('module.id')))


class Staff(User):
    """Staff model, inheriting the User model"""
    
    __tablename__ = 'staff' # this attribute defines a separate table for staff-only columns
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # id is a foreign key to 'user.id' - a User and related Staff instance
    # will share the same id
    job_title = db.Column(db.String(200))
    modules_taught = db.relationship(
        'Module', secondary=staff_modules, backref="staff", lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }


"""Join table for modules that a student can be enrolled on"""
# See: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers

student_modules = db.Table('student_modules', 
                        db.Column('student_id', db.Integer, 
                                 db.ForeignKey('student.id')),
                        db.Column('module_id', db.Integer,
                                 db.ForeignKey('module.id')))


class Student(User):
    """Student model, inheriting the User model"""
    
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    student_number = db.Column(db.Integer, unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    modules_enrolled = db.relationship(
        'Module', secondary=student_modules, backref="students", lazy=True)
    graduation_date = db.Column(db.Date, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def average_percentage(self, rounded=False, attempted_only=False):
        if len(self.attempts) == 0:
            return 0
        if attempted_only:
            if len(self.attempted_assessments()) == 0:
                return 0
            percentage = reduce(lambda acc, cur: acc + cur.student_best_percentage(student_id=self.id), self.attempted_assessments(), 0) / len(self.attempted_assessments())
        else:
            percentage = reduce(lambda acc, cur: acc + cur.student_best_percentage(student_id=self.id), self.assessments, 0) / len(self.assessments)
        return round(percentage, 1) if rounded else percentage
    
    @property
    def assessments(self):
        assessments = []
        for module in self.modules_enrolled:
            assessments.extend(module.assessments)
        return assessments
    
    def attempted_assessments(self):
        assessments = []
        for assessment in self.assessments:
            if len(assessment.student_attempts(self.id)) > 0:
                assessments.append(assessment)
        return assessments

class QuestionAndValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, nullable=True)
    marks_value = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.relationship('Question', backref='question_and_values')
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)

    def __repr__(self):
        return f"QuestionAndValue('Question ID: {self.question_id}'; Value: '{self.marks_value}')"
    
    def calculate_marks_for_answer(self, answer):
        return round(self.question.calculate_answer_correctness(answer) * self.marks_value)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50))
    type = db.Column(db.String(20), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'unspecified',
        'polymorphic_on': type
    }

    def __repr__(self):
        return f"Question('{capitalize(self.type)}' - '{self.question_text}')"


class MultipleChoiceQuestion(Question):
    __tablename__ = 'multiple_choice_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    options = db.relationship('MultipleChoiceOption', backref='question', lazy=False)
    correct_answer_id = db.Column(db.Integer)
    __mapper_args__ = {
        'polymorphic_identity': 'multiple_choice',
    }

    def correct_answer(self):
        return MultipleChoiceOption.query.get(self.correct_answer_id)

    def calculate_answer_correctness(self, student_answer):
        return 1.0 if int(student_answer) == self.correct_answer_id else 0.0

class MultipleChoiceOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f"MCQ Option('Question ID: {self.question_id}'; Value: '{self.value}')"


class FillTheBlanksQuestion(Question):
    __tablename__ = 'fill_the_blanks_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    answer_1 = db.Column(db.Text, nullable=False)
    answer_2 = db.Column(db.Text, nullable=True)
    answer_3 = db.Column(db.Text, nullable=True)
    answer_4 = db.Column(db.Text, nullable=True)
    answer_5 = db.Column(db.Text, nullable=True)
    answer_6 = db.Column(db.Text, nullable=True)
    answer_7 = db.Column(db.Text, nullable=True)
    answer_8 = db.Column(db.Text, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'fill_the_blanks',
    }

    def answer_list(self):
        output_list = [self.answer_1]
        if self.answer_2:
            output_list.append(self.answer_2) 
        if self.answer_3:
            output_list.append(self.answer_3) 
        if self.answer_4:
            output_list.append(self.answer_4) 
        if self.answer_5:
            output_list.append(self.answer_5) 
        if self.answer_6:
            output_list.append(self.answer_6) 
        if self.answer_7:
            output_list.append(self.answer_7) 
        if self.answer_8:
            output_list.append(self.answer_8)
        return output_list

    def calculate_answer_correctness(self, student_answer):
        answer_list = self.answer_list()
        student_answer_list = student_answer.split(",")
        correct_elements = len(answer_list) - (len(answer_list) - len(student_answer_list))
        for i in range(len(student_answer_list)):
            if student_answer_list[i].lower() != answer_list[i].lower():
                correct_elements -= 1
        return correct_elements / len(answer_list)
        

class AssessmentAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('Student', backref='attempts')
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    answers = db.relationship('AttemptAnswer', backref='attempt')
    submitted = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"AssessmentAttempt('Student ID: {self.student_id}'; Mark: {self.total_marks()} / {self.assessment.max_marks}) | {self.percentage()}%"
    
    def passed(self):
        return self.mark >= self.assessment.passing_mark

    def on_time(self):
        return True if self.assessment.type == 'formative' else self.date <= self.assessment.deadline

    def total_marks(self):
        return reduce(lambda acc, cur: acc + cur.mark(), self.answers, 0)
    
    def percentage(self, rounded=False):
        percentage = float((self.total_marks() / self.assessment.max_marks) * 100)
        return round(percentage, 1) if rounded else percentage
    

class AttemptAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_attempt_id = db.Column(db.Integer, db.ForeignKey('assessment_attempt.id'), nullable=False)
    question_and_value_id = db.Column(db.Integer, db.ForeignKey('question_and_value.id'), nullable=False)
    question_and_value = db.relationship('QuestionAndValue', backref='attempt_answer')
    answer = db.Column(db.Text, nullable=False, default='did_not_answer')

    def __repr__(self):
        answer = self.answer if self.question_and_value.question.type == 'fill_the_blanks' else MultipleChoiceOption.query.get(int(self.answer)).value
        return f"AttemptAnswer('ID: {self.id}; Question: '{self.question_and_value.question.question_text}'); Answer: '{answer}'"

    def mark(self):
        return 0 if self.answer == 'did_not_answer' else self.question_and_value.calculate_marks_for_answer(self.answer)


class StudentFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student = db.relationship('Student', backref='feedback')
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"StudentFeedback('Student ID: {self.student_id}'; Assessment ID: '{self.assessment_id}; Content: {self.content}')"

class Assessment(db.Model):
    """Assessment model, with polymorphism
    
    Relationships:
        questions_and_values: QuestionAndValue.assessment_id
        attempts: AssessmentAttempt.assessment_id
        student_feedback: StudentFeedback.assessment_id
        module: Module.assessments
    """
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    set_date = db.Column(db.DateTime) # Should this default to 'now'?
    passing_percentage = db.Column(db.Integer)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    questions_and_values = db.relationship('QuestionAndValue', backref='assessment', lazy=True)
    attempts = db.relationship('AssessmentAttempt', backref='assessment', lazy=True)
    student_feedback = db.relationship('StudentFeedback', backref='assessment', lazy=True)
    type = db.Column(db.String(20), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'unspecified',
        'polymorphic_on': type
    }

    def __repr__(self):
        return f"Assessment('{capitalize(self.type)}' - '{self.title}'; Module ID: '{self.module_id}')"

    def average_marks(self):
        return None if len(self.attempts) == 0 else reduce(lambda acc, cur: acc + cur.total_marks(), self.attempts, 0) / len(self.attempts)

    def average_percentage(self, rounded=False):
        if len(self.attempts) == 0:
            return None
        percentage = reduce(lambda acc, cur: acc + cur.percentage(), self.attempts, 0) / len(self.attempts)
        return round(percentage, 1) if rounded else percentage
    
    def student_can_attempt(self, student_id):
        if self.type == 'summative':
            return AssessmentAttempt.query.filter_by(student_id=student_id, assessment_id=self.id).count() == 0
        else:
            return True
        
    def student_attempts(self, student_id):
        return AssessmentAttempt.query.filter_by(student_id=student_id, assessment_id=self.id).order_by(AssessmentAttempt.date.desc()).all()
    
    def student_best_percentage(self, student_id):
        attempts = self.student_attempts(student_id=student_id)
        if len(attempts) == 0:
            return 0
        def sort_percentage(att):
            return att.percentage()
        attempts.sort(key=sort_percentage, reverse=True)
        return attempts[0].percentage(rounded=True)
    
    def students(self, not_yet_submitted=False):
        if not_yet_submitted:
            output = []
            for student in self.module.students:
                if len(self.student_attempts(student_id=student.id)) == 0:
                    output.append(student)
            return output
        else:
            return self.module.students
    
    def average_feedback_rating(self, rounded=False):
        if len(self.student_feedback) == 0:
            return 0
        total = 0
        for feedback in self.student_feedback:
            total += feedback.rating
        average = total / len(self.student_feedback)
        return round(average, 1) if rounded else average
    
    @property
    def max_marks(self):
        count = 0
        for qav in self.questions_and_values:
            count += qav.marks_value
        return count



class FormativeAssessment(Assessment):
    __tablename__ = 'formative_assessment'
    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'formative',
    }


class SummativeAssessment(Assessment):
    __tablename__ = 'summative_assessment'
    id = db.Column(db.Integer, db.ForeignKey('assessment.id'), primary_key=True)
    deadline = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    time_limit_seconds = db.Column(db.Integer, nullable=True)
    mark_criteria = db.Column(db.Text, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'summative',
    }
