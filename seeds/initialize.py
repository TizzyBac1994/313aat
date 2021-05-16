from flask_seeder import Seeder
from AAT.models import (
    User, Course, Module, Staff, Student, Assessment, FormativeAssessment,
    SummativeAssessment, QuestionAndValue, Question, MultipleChoiceQuestion,
    MultipleChoiceOption, FillTheBlanksQuestion, AssessmentAttempt,
    StudentFeedback
)

class InitializeSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 1

    def run(self):
        print("Dropping existing tables...")
        self.db.drop_all()
        print("Creating new tables...")
        self.db.create_all()
        print("Seeding data...")