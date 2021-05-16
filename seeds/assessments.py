from flask_seeder import Seeder
from faker import Faker
from random import choice, randint
from AAT.models import Assessment, FormativeAssessment, SummativeAssessment, Module, QuestionAndValue, Question

fake = Faker(["en_US"])

class FormativeAssessmentSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 6

    def run(self):
        number_of_assessments = 15
        modules = Module.query.all()

        for num in range(number_of_assessments):
            assessment = FormativeAssessment(
                        title=fake.sentence(nb_words=3),
                        set_date=fake.date_time_between('-60d', '-2w'),
                        passing_percentage=fake.random_element(elements=(40, 50, 80)),
                        module_id=choice(modules).id)
            self.db.session.add(assessment)

class SummativeAssessmentSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 6

    def run(self):
        number_of_assessments = 15
        modules = Module.query.all()

        for num in range(number_of_assessments):
            deadline = fake.date_time_between('+28d', '+90d')
            assessment = SummativeAssessment(
                        title=fake.sentence(nb_words=3),
                        set_date=fake.date_time_between('-180d', '-2w'),
                        passing_percentage=fake.random_element(elements=(40, 50)),
                        module_id=choice(modules).id,
                        deadline=deadline,
                        return_date=fake.date_time_between(deadline, '+120d'),
                        time_limit_seconds=fake.random_element(elements=(600, 1200, 1800, 3600)),
                        mark_criteria="\n\n".join(fake.paragraphs(nb=randint(3,6))))
            self.db.session.add(assessment)

class QandVSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 7
    
    def run(self):
        assessments = Assessment.query.all()
        all_questions = Question.query.all()

        for assessment in assessments:
            questions = fake.random_element(elements=(5, 8, 10))
            for num in range(questions):
                q = choice(all_questions)
                if q.type == 'multiple_choice':
                    marks_per_q = fake.random_element(elements=(1, 2, 4))
                else:
                    marks_per_q = len(q.answer_list()) * fake.random_element(elements=(1, 1, 2))
                q_and_v = QuestionAndValue(
                            order=(num+1),
                            marks_value=marks_per_q,
                            question_id=q.id,
                            assessment_id=assessment.id)
                self.db.session.add(q_and_v)

