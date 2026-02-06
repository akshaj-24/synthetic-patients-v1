import numpy
from faker import Faker

fake = Faker('en_CA')

class Demographics:
    def __init__(self):
        self.age = None
        self.gender = None
        self.name = None
        self.education = None
        self.occupation = None
        self.marital_status = None
        self.ethnicity = None
        
    def set_age(self):
        self.age = numpy.random.randint(25, 65)
        
    def set_gender(self):
        self.gender = numpy.random.choice(['Male', 'Female'])
        
    def set_name(self):
        if self.gender == 'Male':
            first_name = fake.first_name_male()
        else:
            first_name = fake.first_name_female()
        last_name = fake.last_name()
        self.name = f"{first_name} {last_name}"
        
    def set_education(self):
        self.education = numpy.random.choice([
            "Less than High School",
            "Secondary",
            "Vocational",
            "Associate's Degree",
            "Bachelor's Degree",
            "Master's Degree",
            "Doctor",
        ])
        
    def set_occupation(self):
        less_than_high_school = [
            "Elementary occupations (general labor)",
            "Food preparation and serving workers",
            "Building and grounds cleaning workers",
            "Farming, fishing, and forestry workers",
            "Material moving and transportation helpers",
            "Unemployed",
        ]

        high_school_secondary = [
            "Sales workers",
            "Office and administrative support workers",
            "Production workers",
            "Construction and extraction workers",
            "Protective service workers",
            "Personal care and service workers",
            "Transportation and material moving operators",
            "Unemployed",
        ]

        some_college_vocational = [
            "Installation, maintenance, and repair workers",
            "Healthcare support workers",
            "Craft and related trades workers",
            "Plant and machine operators",
            "Emergency services technicians",
            "Installation, maintenance, and repair workers",
            "Healthcare support workers",
            "Craft and related trades workers",
            "Plant and machine operators",
            "Emergency services technicians",
            "Unemployed",
        ]

        associate_short_cycle = [
            "Technicians and associate professionals",
            "Paralegal and legal support workers",
            "Medical technicians and technologists",
            "Computer support specialists",
            "Engineering technicians",
            "Technicians and associate professionals",
            "Paralegal and legal support workers",
            "Medical technicians and technologists",
            "Computer support specialists",
            "Engineering technicians",
            "Unemployed",
        ]

        bachelors_degree = [
            "Business and financial operations professionals",
            "Computer and mathematical professionals",
            "Community and social service workers",
            "Educational instruction and library workers",
            "Arts, design, entertainment, sports, and media workers",
            "Life, physical, and social science professionals",
            "Business and financial operations professionals",
            "Computer and mathematical professionals",
            "Community and social service workers",
            "Educational instruction and library workers",
            "Arts, design, entertainment, sports, and media workers",
            "Life, physical, and social science professionals",
            "Business and financial operations professionals",
            "Computer and mathematical professionals",
            "Community and social service workers",
            "Educational instruction and library workers",
            "Arts, design, entertainment, sports, and media workers",
            "Life, physical, and social science professionals",
            "Unemployed",
        ]

        masters_degree = [
            "Management occupations",
            "Advanced healthcare practitioners",
            "Mental health counselors and therapists",
            "Educational administrators",
            "Architecture and engineering specialists",
            "Management occupations",
            "Advanced healthcare practitioners",
            "Mental health counselors and therapists",
            "Educational administrators",
            "Architecture and engineering specialists",
            "Management occupations",
            "Advanced healthcare practitioners",
            "Mental health counselors and therapists",
            "Educational administrators",
            "Architecture and engineering specialists",
            "Management occupations",
            "Advanced healthcare practitioners",
            "Mental health counselors and therapists",
            "Educational administrators",
            "Architecture and engineering specialists",
            "Unemployed",
        ]

        doctoral_professional = [
            "Doctor",
        ]
        
        if self.education == "Less than High School":
            self.occupation = numpy.random.choice(less_than_high_school)
        elif self.education == "Secondary":
            self.occupation = numpy.random.choice(high_school_secondary)
        elif self.education == "Vocational":
            self.occupation = numpy.random.choice(some_college_vocational)
        elif self.education == "Associate's Degree":
            self.occupation = numpy.random.choice(associate_short_cycle)
        elif self.education == "Bachelor's Degree":
            self.occupation = numpy.random.choice(bachelors_degree)
        elif self.education == "Master's Degree":
            self.occupation = numpy.random.choice(masters_degree)
        elif self.education == "Doctor":
            self.occupation = numpy.random.choice(doctoral_professional)
        
        
    def set_marital_status(self):
        if self.age is None:
            raise ValueError("Age must be set before setting marital status.")
        age = self.age
        if 25 <= age <= 35:
            choices = ["Married", "Common-law", "Single", "Divorced"]
            weights = [0.2, 0.5, 0.2, 0.1]
        elif 36 <= age <= 50:
            choices = ["Married", "Common-law", "Single", "Divorced"]
            weights = [0.5, 0.2, 0.1, 0.2]
        elif 51 <= age <= 65:
            choices = ["Married", "Single", "Divorced", "Common-law"]
            weights = [0.5, 0.05, 0.3, 0.15]
        else:
            # fallback if age is out of expected range
            choices = ["Single", "Married", "Common-law", "Divorced"]
            weights = [0.25, 0.25, 0.25, 0.25]
        self.marital_status = numpy.random.choice(choices, p=weights)
        
    def set_ethnicity(self):
        ethnicities = [
                "White/European",
                "Chinese (East Asian)",
                "South Asian",
                "Filipino",
                "Indigenous",
                "Southeast Asian",
                "Latin American",
                "Black/African",
                "Middle Eastern",
                "Mixed/Other",
        ]

        weights = [
                0.596,  # White/European
                0.121,  # Chinese (East Asian)
                0.098,  # South Asian
                0.042,  # Filipino
                0.039,  # Indigenous
                0.025,  # Southeast Asian
                0.020,  # Latin American
                0.017,  # Black/African
                0.015,  # Middle Eastern
                0.027,  # Mixed/Other
        ]
            
        self.ethnicity = numpy.random.choice(ethnicities, p=weights)
            
    def generate_demographics(self):
                self.set_age()
                self.set_gender()
                self.set_name()
                self.set_education()
                self.set_occupation()
                self.set_marital_status()
                self.set_ethnicity()
                
    def get_patient(self):
                self.generate_demographics()
                return {
                    "Name": self.name,
                    "Age": self.age,
                    "Gender": self.gender,
                    "Education": self.education,
                    "Occupation": self.occupation,
                    "Marital Status": self.marital_status,
                    "Ethnicity": self.ethnicity,
                }


