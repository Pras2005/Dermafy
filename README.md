# Dermafy

## Overview
Dermafy is a Django-based application focused on skincare management and tracking. It allows users to maintain their profile, respond to diagnostic quizzes, track their skin progress, and manage their skincare routines. 

## Domain Models
- **CUSTOMUSER**: Extends the default user for custom authentication.
- **PROFILE**: Stores user-specific demographic and personal data.
- **QuizResponse**: Records user responses to skincare assessment quizzes.
- **SkinProgress**: Tracks longitudinal progress of skin health.
- **SkincareRoutine**: Manages and stores daily skincare regimens.
- **Report**: Holds generated reports based on user data and progress.

## Setup and Installation
### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository
2. Install dependencies:
   `pip install -r requirements.txt`
3. Apply migrations:
   `python manage.py migrate`
4. Run the server:
   `python manage.py runserver`

## Project Structure
```
.
├── derma/
│   ├── static/
│   ├── templates/
│   └── users/
│       ├── models.py
│       └── views.py
├── requirements.txt
└── manage.py
```
