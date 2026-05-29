# Online Course Application (Django)

This is a Django-based Online Course platform where users can register, enroll in courses, take exams, and view results.

---

## Features

- User Registration & Login
- Course Listing
- Course Enrollment
- Lessons Management
- Exam System (Questions & Choices)
- Automatic Result Evaluation
- Admin Panel for Management

---

## Tech Stack

- Python 3
- Django
- SQLite
- HTML + Bootstrap

---

## Setup Instructions

### 1. Clone Repository
git clone https://github.com/<your-username>/tfjzl-final-cloud-app-with-database.git
cd tfjzl-final-cloud-app-with-database

### 2. Create Virtual Environment
pip install virtualenv
virtualenv djangoenv
source djangoenv/bin/activate

### 3. Install Requirements
pip install -r requirements.txt

### 4. Run Migrations
python3 manage.py makemigrations
python3 manage.py migrate

### 5. Create Superuser
python3 manage.py createsuperuser

### 6. Run Server
python3 manage.py runserver

---

## Access URLs

Home:
http://127.0.0.1:8000/onlinecourse/

Admin:
http://127.0.0.1:8000/admin

---

## Exam Flow

1. Login / Register
2. Enroll in course
3. Attempt exam
4. Submit answers
5. View result

---

## Models

- Course
- Lesson
- Instructor
- Learner
- Question
- Choice
- Enrollment
- Submission

---

## Author

Django Online Course Project