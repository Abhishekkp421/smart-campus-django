# Smart Campus Management System

A full-stack **Smart Campus Management System** built with **Django**
for managing academic and administrative activities in one centralized
platform.

## Features

-   Student management with add, edit, delete, search, filtering and
    pagination
-   Faculty management
-   Department, Course, Semester and Subject management
-   Attendance entry and attendance history
-   Exams and student results
-   Student-wise marksheet
-   Assignment management
-   Fee management with pending, partial and paid status
-   Notice management
-   Event management
-   Library management with book issue and return
-   Reports and analytics
-   Login and logout authentication
-   REST APIs using Django REST Framework
-   Token-based API authentication
-   Admin/Faculty API permissions
-   Redis and Celery background tasks
-   Automated fee reminder emails
-   Automated Django tests
-   Environment-based secret key configuration

## Tech Stack

**Backend:** Python, Django, Django REST Framework, Celery, Redis

**Frontend:** HTML5, CSS3, JavaScript

**Database:** SQLite for local development; PostgreSQL planned for
production

**Tools:** Git, GitHub, Django Admin, Python Virtual Environment

## Project Structure

``` text
smart-campus-django/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── students/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── api_views.py
│   ├── forms.py
│   ├── middleware.py
│   ├── models.py
│   ├── permission.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static/
├── templates/
├── manage.py
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

``` bash
git clone https://github.com/Abhishekkp421/smart-campus-django.git
cd smart-campus-django
```

### 2. Create and activate a virtual environment

Windows:

``` powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

``` env
DJANGO_SECRET_KEY=your-secret-key
```

Never commit `.env` to GitHub.

### 5. Run migrations

``` bash
python manage.py migrate
```

### 6. Create an admin user

``` bash
python manage.py createsuperuser
```

### 7. Start the server

``` bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Celery and Redis

Start Redis, then run the Celery worker:

``` bash
celery -A config worker --loglevel=info --pool=solo
```

For scheduled tasks:

``` bash
celery -A config beat --loglevel=info
```

The project includes a fee reminder task that checks pending/partial
fees and sends reminder emails to students whose fees are due.

## REST API

Major API endpoints include:

``` text
/students/api/students/
/students/api/faculty/
/students/api/attendance/
/students/api/results/
/students/api/exams/
/students/api/assignments/
/students/api/fees/
/students/api/notices/
/students/api/events/
```

API access uses token authentication and role-based permissions.

## Testing

Run:

``` bash
python manage.py test
```

Tests cover student model behavior, dashboard authentication and API
authentication/access.

## Security

-   Django CSRF protection
-   Login-required web access
-   DRF token authentication
-   Admin/Faculty API permissions
-   Secret key loaded from environment variables
-   `.env`, `venv/` and `db.sqlite3` excluded through `.gitignore`

For production, configure `DEBUG=False`, secure environment variables,
production `ALLOWED_HOSTS`, HTTPS and PostgreSQL.

## Project Status

**Main development:** Completed\
**GitHub:** Available\
**Deployment:** Planned

## Future Improvements

-   Individual Student and Faculty dashboards
-   More granular role-based UI permissions
-   PostgreSQL production database
-   Docker containerization
-   Production deployment
-   Advanced analytics
-   Data export features

## Author

**Abhishek Pathak**

GitHub: https://github.com/Abhishekkp421

------------------------------------------------------------------------

If you find the project useful, consider giving the repository a star.
