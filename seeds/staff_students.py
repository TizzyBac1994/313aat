from flask_seeder import Seeder
from faker import Faker
from random import choice, randint, sample
from AAT.models import Module, Staff, Student, Course

fake = Faker(['en_GB'])

class StudentSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 3
    
    def run(self):
        # Change for more/less students
        number_of_students = 50
        courses = Course.query.all()

        test_student = Student(
                        first_name="Stuart",
                        last_name="Studentson",
                        email="student@student.com",
                        password="password", 
                        student_number=1000000,
                        course_id=courses[0].id,
                        graduation_date=fake.date_time_between('+2m', '+2y'))
        self.db.session.add(test_student)

        for num in range(1, number_of_students):
            unique_student_no = fake.unique.random_int(min=1000001, max=30000000)
            unique_email = f"c{unique_student_no}@example.ac.uk"
            student = Student(
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        email=unique_email,
                        password="password", 
                        student_number=unique_student_no,
                        course_id=choice(courses).id,
                        graduation_date=fake.date_time_between('+2m', '+2y'))
            self.db.session.add(student)

class StaffSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 3
    
    def run(self):
        # Change for more/less staffs
        number_of_staffs = 10
        job_titles = ["Lecturer", "Associate Lecturer", "Professor", "Research Fellow", "Teaching Assistant", "Instructor"]

        test_staff = Staff(
                        first_name="Sasha",
                        last_name="Staffington",
                        email="staff@staff.com",
                        password="password", 
                        job_title=choice(job_titles))
        self.db.session.add(test_staff)

        for num in range(1, number_of_staffs):
            unique_staff_fname = fake.unique.first_name()
            unique_staff_lname = fake.unique.last_name()
            unique_email = f"{unique_staff_fname.lower()}.{unique_staff_lname.lower()}@example.ac.uk"
            staff = Staff(
                        first_name=unique_staff_fname,
                        last_name=unique_staff_lname,
                        email=unique_email,
                        password="password", 
                        job_title=choice(job_titles))
            self.db.session.add(staff)

class StaffModuleSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 4

    def run(self):
        modules = Module.query.all()
        all_staff = Staff.query.all()

        for staff in all_staff:
            staff_modules = sample(modules, randint(1, 4))
            for module in staff_modules:
                staff.modules_taught.append(module)

class StudentModuleSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 4

    def run(self):
        courses = Course.query.all()
        all_students = Student.query.all()

        for student in all_students:
            student_modules = choice(courses).modules
            for module in student_modules:
                student.modules_enrolled.append(module)
