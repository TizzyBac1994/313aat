from os import name
from flask_seeder import Seeder
from AAT.models import Course, Module
from random import choice, choices, randint, sample

class CourseSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 2
    
    def run(self):
        # Change for more/less courses
        number_of_courses = 5

        print(f'Adding {number_of_courses} Courses...')
        courses = sample(["Accounting", "Art History", "Biology", "Business and Management", "Chemistry", "Classical Studies", "Combined Studies", "Computing and IT", "Counselling", "Creative Writing", "Criminology", "Design", "Early Years", "Economics", "Education", "Electronic Engineering", "Engineering", "English", "Environment", "Geography", "Health and Social Care", "Health and Wellbeing", "Health Sciences", "History", "International Studies", "Law", "Marketing", "Mathematics", "Mental Health", "Music", "Nursing and Healthcare", "Philosophy", "Physics", "Politics", "Psychology", "Religious Studies", "Science", "Social Sciences", "Social Work", "Software Engineering", "Sport & Fitness", "Statistics" ], number_of_courses)
        course_types = ["BA", "BSc", "MA", "MSc", "DipHE", "CertHE"]
        for num in range(number_of_courses):
            course = Course(name=f"{courses[num]} ({choice(course_types)})")
            self.db.session.add(course)

class ModuleSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 2
    
    def run(self):
        # Change for more/less modules
        number_of_modules = 15

        subjects = choices(["Leisure Studies", "Architectural Sociology", "Molecular Genetics", "Computational Science", "Logic", "Public Economics", "South American History", "Colombian History", "Urology", "Business Analysis", "German Studies", "Sonochemistry", "Literature", "German Studies", "Sex Education", "Ethnohistory", "Philosophy of Language", "Ocean Engineering", "Music Education", "Surgery", "Sociology of Scientific Knowledge", "Propaganda", "Bioeconomics", "Physical Organic Chemistry", "Synchronic Linguistics", "Stage Design", "Cardiology", "Military Logistics", "African-American Literature", "Environmental History", "Tourism Geography", "Urban Geography", "Cytology", "Digital Media", "Flow Chemistry", "Logic in Computer Science", "Criminal Justice", "Australian Studies", "Environmental Science", "Environmental Communication", "Computer Graphics", "Islamic Economics", "Sociology of Terrorism", "Educational Psychology", "Post-Modern Literature", "Labor Law", "Immunology", "History and Politics", "Archaeology of the Americas", "Computer-Aided Engineering"], k=number_of_modules)
        for subject in subjects:
            variations = [f"{subject} I", f"{subject} II", f"Advanced {subject}", f"Applied {subject}", f"History of {subject}"]
            module = Module(name=choice(variations), module_code=f"{subject[:3].upper()}{str(randint(100, 500))}")
            self.db.session.add(module)

class CourseModuleSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 3

    def run(self):
        modules = Module.query.all()
        all_courses = Course.query.all()

        for i in range(len(modules)):
            module = modules[i]
            shared_module = modules[randint(0, len(modules) - 1)]
            course = all_courses[i % len(all_courses)]
            course.modules.append(module)
            course.modules.append(shared_module)
