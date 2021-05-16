from flask_seeder import Seeder
from AAT.models import MultipleChoiceQuestion, MultipleChoiceOption, FillTheBlanksQuestion
from seeds.lib.mcq_questions import MCQ_LIBRARY
from seeds.lib.ftb_questions import FTB_LIBRARY
from random import getrandbits, sample

class MCQSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 5
    
    def run(self):
        number_of_questions = 50

        questions = sample(MCQ_LIBRARY, number_of_questions)
        for question in questions:
            mcq = MultipleChoiceQuestion(question_text=question["question"], category="General Knowledge")
            self.db.session.add(mcq)
        self.db.session.commit()

        mcqs = MultipleChoiceQuestion.query.all()
        for i in range(len(questions)):
            mcq = mcqs[i]
            question = questions[i]
            opt_a = MultipleChoiceOption(value=question["A"], question_id=mcq.id)
            self.db.session.add(opt_a)
            opt_b = MultipleChoiceOption(value=question["B"], question_id=mcq.id)
            self.db.session.add(opt_b)
            opt_c = MultipleChoiceOption(value=question["C"], question_id=mcq.id)
            self.db.session.add(opt_c)
            opt_d = MultipleChoiceOption(value=question["D"], question_id=mcq.id)
            self.db.session.add(opt_d)
            self.db.session.commit()
            if question["answer"] == "A":
                mcq.correct_answer_id = opt_a.id
            elif question["answer"] == "B":
                mcq.correct_answer_id = opt_b.id
            elif question["answer"] == "C":
                mcq.correct_answer_id = opt_c.id
            elif question["answer"] == "D":
                mcq.correct_answer_id = opt_d.id
            self.db.session.commit()


class FTBSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 5
    
    def run(self):
        number_of_questions = 50

        questions = sample(FTB_LIBRARY, number_of_questions)
        for question in questions:
            quote = question[0]
            quote_arr = quote.split(" ")
            str_buffer = ""
            answers = []
            gap = 1
            if len(quote_arr) > 14:
                word_size = 5
            elif len(quote_arr) > 8:
                word_size = 4
            else:
                word_size = 3
            for substr in quote_arr:
                if len(substr.strip("'.")) > word_size and len(answers) < 9 and (len(answers) < 1 or not not getrandbits(1)):
                    str_buffer += f"[FILL#{gap}] "
                    answers.append(substr.rstrip('.,:;/?!'))
                    gap += 1
                else:
                    str_buffer += substr + " "
            ftb_question = FillTheBlanksQuestion(question_text=str_buffer.strip(), hint=question[1], category="Film")
            for i in range(len(answers)):
                ans = answers[i]
                if i == 0:
                    ftb_question.answer_1 = ans
                elif i == 1:
                    ftb_question.answer_2 = ans
                elif i == 2:
                    ftb_question.answer_3 = ans
                elif i == 3:
                    ftb_question.answer_4 = ans
                elif i == 4:
                    ftb_question.answer_5 = ans
                elif i == 5:
                    ftb_question.answer_6 = ans
                elif i == 6:
                    ftb_question.answer_7 = ans
                elif i == 7:
                    ftb_question.answer_8 = ans
            self.db.session.add(ftb_question)
