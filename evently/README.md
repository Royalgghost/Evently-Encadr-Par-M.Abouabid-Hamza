# Evently - Event Management System

Evently is a Django-based event management platform that helps users create, manage, and participate in events such as conferences, workshops, meetups, and other community activities.

## Features

### User management
- user registration and login
- profile management
- admin and organizer workflows

### Event management
- create, update, and delete events
- event details including title, description, date, location, and capacity
- categorization and event filtering
- image support for event-related media

### Registration system
- participant registration for events
- capacity validation and attendee limits
- event-specific user dashboard
- QR-based ticket support

### Admin and dashboard features
- administrative views for event oversight
- user and event management pages
- custom templates for a complete event workflow

## Tech stack

- Backend: Django 5
- Database: SQLite by default
- Optional database: MySQL (available in settings)
- Frontend: HTML, CSS, JavaScript, Bootstrap-based templates
- Media handling: Pillow
- Ticket generation: ReportLab
- QR codes: qrcode

## Project structure

```text
evently/
├── evently/                  # Django project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── events/                   # main app
│   ├── admin.py
│   ├── admin_views.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   ├── views.py
│   ├── views_event_management.py
│   └── migrations/
├── templates/                # HTML templates
├── static/                   # CSS, JS, and image assets
├── manage.py                 # Django entry point
├── requirements.txt          # dependencies
├── init_db.sql               # database initialization script
├── README.md                 # project documentation
└── ...
```

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. Change into the project directory:
   ```bash
   cd evently
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux/macOS
   .venv\Scripts\activate        # Windows
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply the database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser for the admin interface:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Open the app in your browser:
   ```text
   http://127.0.0.1:8000/
   ```

## Configuration notes

- The project is configured to use SQLite by default, which is suitable for local development.
- MySQL configuration is included in `evently/evently/settings.py` and can be enabled when needed.
- Static and media file directories are configured for the project template and upload system.

## License

This repository does not currently include an explicit license file. If this project is being shared publicly, add the appropriate license before distribution or deployment.
