from flask_seeder import Seeder
from faker import Faker
from AAT.models import AssessmentAttempt, Assessment, AttemptAnswer, Student, StudentFeedback
from random import choice, randint, sample

fake = Faker()

class AttemptSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 7
    
    def run(self):
        # This should be > 5
        approximate_number_of_attempts_per_assessment = 25

        all_students = Student.query.all()
        all_assessments = Assessment.query.all()

        for assessment in all_assessments:
            students = sample(all_students, randint(approximate_number_of_attempts_per_assessment-5, approximate_number_of_attempts_per_assessment+5))
            deadline = 'now' if assessment.type == 'formative' else assessment.deadline

            for student in students:
                attempt = AssessmentAttempt(
                            assessment_id=assessment.id,
                            student_id=student.id,
                            date=fake.date_time_between(assessment.set_date, deadline),
                            submitted=True)
                self.db.session.add(attempt)

class AttemptAnswerSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 8

    def run(self):
        all_attempts = AssessmentAttempt.query.all()

        for attempt in all_attempts:
            questions_and_values = attempt.assessment.questions_and_values
            
            for q_and_v in questions_and_values:
                question = q_and_v.question

                if randint(0,9) < 1:
                    answer = AttemptAnswer(
                            assessment_attempt_id=attempt.id,
                            question_and_value_id=q_and_v.id)
                    self.db.session.add(answer)
                elif question.type == 'multiple_choice':
                    options = question.options
                    this_answer = choice([question.correct_answer_id, choice(options).id])
                    answer = AttemptAnswer(
                            assessment_attempt_id=attempt.id,
                            question_and_value_id=q_and_v.id,
                            answer=this_answer)
                    self.db.session.add(answer)
                elif question.type == 'fill_the_blanks':
                    answer_list = question.answer_list()
                    this_answer_list = answer_list if randint(0,2) > 0 else [choice([word, fake.word()]) for word in answer_list]
                    this_answer = ",".join(this_answer_list)
                    answer = AttemptAnswer(
                            assessment_attempt_id=attempt.id,
                            question_and_value_id=q_and_v.id,
                            answer=this_answer)
                    self.db.session.add(answer)

class FeedbackSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 8
    
    def run(self):
        all_attempts = AssessmentAttempt.query.all()

        for attempt in all_attempts:
            if randint(0,2) > 0:
                feedback = StudentFeedback(
                            student_id=attempt.student_id,
                            assessment_id=attempt.assessment_id,
                            content="\n".join(fake.paragraphs(randint(1,4))),
                            rating=randint(1,5),
                            date=fake.date_time_between(attempt.date, 'now'))
                self.db.session.add(feedback)