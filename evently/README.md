# Evently - Event Management System

Evently is a comprehensive event management platform built with Django. It allows users to create, manage, and participate in various types of events like conferences, workshops, meetups, and more.

## Features

### User Management
- User registration and authentication
- User profiles with roles (admin, organizer, participant)
- Profile customization with profile pictures

### Event Management
- Create, read, update, and delete events
- Event details including title, description, location, date, capacity
- Event categorization
- Event image uploads
- Event search and filtering

### Registration System
- Event registration for participants
- Registration capacity limits
- Waiting list functionality
- Ticket generation (PDF with QR codes)

### Planning and Organization
- Event calendar views
- Filtering by date, type, location
- Responsive UI for all devices

### Additional Features
- Email notifications for event changes, registration confirmations
- Reminder system for upcoming events
- User dashboard with registered events
- QR code tickets for check-in

## Technology Stack

- **Backend**: Django 5.x
- **Database**: MySQL
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Django built-in authentication system
- **PDF Generation**: ReportLab
- **QR Codes**: qrcode
- **Date Handling**: Arrow, python-dateutil

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL server
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd evently
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure the MySQL database in `settings.py` with your credentials

5. Run migrations to create the database schema:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser to access the admin interface:
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

8. Access the application in your browser at `http://127.0.0.1:8000/`

## Project Structure

- `events/` - Main application module
  - `models.py` - Database models
  - `views.py` - View functions and classes
  - `views_event_management.py` - Event management views
  - `forms.py` - Form classes
  - `admin.py` - Admin interface configuration
  - `urls.py` - URL routing
  - `signals.py` - Signal handlers

- `templates/` - HTML templates
  - `events/` - Application templates
    - `base.html` - Base template with common elements
    - Various view templates

- `static/` - Static files (CSS, JS, images)
  - `css/` - CSS files
  - `js/` - JavaScript files
  - `images/` - Static images

- `media/` - User-uploaded files
  - `profile_pics/` - User profile pictures
  - `event_posters/` - Event poster images

## User Roles

- **Administrator**: Full system access, can manage all events and users
- **Organizer**: Can create and manage their own events
- **Participant**: Can browse events and register for them

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django framework
- Bootstrap for frontend components
- All other open-source libraries used in this project
