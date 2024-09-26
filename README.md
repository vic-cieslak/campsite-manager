# Reservation System and Landing Page


[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Overview
This project is a Django-based web application designed for managing reservations and providing a landing page for a camping site. It allows users to reserve camping spots, view current occupancy, and download reservation PDFs. The project includes real-time price calculation during reservation, population monitoring, and QR code generation.
![Screenshot from 2024-09-26 08-33-30](https://github.com/user-attachments/assets/3fc047ad-9ebe-4613-a757-0e4bcb2be2df)


## Create reservation flow

https://github.com/user-attachments/assets/665efecb-2d85-4222-9697-2c5766315443

## django unfold admin panel backend

https://github.com/user-attachments/assets/d81a8b5d-1ad1-4045-8a44-24eddbac5e53


## Features

- **User Management**
  - User registration, login, and profile management.
  - Secure views for updating user information.

- **Reservation System**
  - Create, view, and cancel reservations with real-time occupancy and population data tracking.
  - Generate PDFs of reservation details, including a QR code for on-site check-in.
  - **Dynamic Reservation Form**: 
    - Users can input personal details, select dates, and specify the number of adults, children, and animals.
    - Additional options such as selecting a tent, caravan, electricity, and extras.
    - Increment/decrement buttons for selecting quantities (e.g., number of adults or children).
    - Date selection with a calendar picker.
    - Real-time pricing calculation that updates dynamically based on user selections, displayed in a floating price summary.
  - Automatic calculation of guests, including children and extra people.

- **Occupancy Tracking**
  - Real-time population monitoring with thresholds for low, medium, and high occupancy levels.
  - View historical population data for up to 30 days.

- **PDF and QR Code Generation**
  - Reservation summaries are exportable as PDFs with dynamically generated QR codes for easy check-in.
  - Support for multi-language PDFs, including Polish.

- **Dashboard**
  - Admin view for monitoring daily and future camping site occupancy.

## Screenshots

Screenshot of Reservation Form
![obraz](https://github.com/user-attachments/assets/80b640ae-45ec-4d44-b15d-682062400d6c)


[Screenshot of Occupancy Tracking 
![obraz](https://github.com/user-attachments/assets/7cd4d8b9-f4ec-4768-b326-49d539d67bd5)


## Settings
Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

    ```bash
    $ python manage.py createsuperuser
    ```

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type Checks
Running type checks with mypy:

```bash
$ mypy campsitemanager
```

### Test Coverage
To run the tests, check your test coverage, and generate an HTML coverage report:

```bash
$ coverage run -m pytest
$ coverage html
$ open htmlcov/index.html
```

### Running Tests with pytest

```bash
$ pytest
```

### Live Reloading and Sass CSS Compilation
Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

### Celery
This app comes with Celery.

To run a celery worker:

```bash
cd campsitemanager
celery -A config.celery_app worker -l info
```

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), start the celery beat scheduler service:

```bash
cd campsitemanager
celery -A config.celery_app beat
```

Alternatively, embed the beat service inside a worker (not recommended for production use):

```bash
cd campsitemanager
celery -A config.celery_app worker -B -l info
```

## Deployment

### Docker
Refer to the [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html) for detailed deployment instructions.

---

This README integrates all the new features, along with your original content, in a cohesive manner. Let me know if you need further changes!
