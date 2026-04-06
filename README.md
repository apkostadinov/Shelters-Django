# PetShelterDjango

A Django web application for managing shelters, pets, caretakers, and volunteers.

## Features

- Shelters: list, detail, create, edit, delete, assign caretakers
- Pets: list (randomized), filter by shelter, detail, create, edit, delete
- Caretakers: list, detail, create, edit, delete, assign pets
- Volunteers: list, detail, create, edit, delete
- Users: signup, login/logout, profile detail/edit/delete (custom `AUTH_USER_MODEL`)
- Bookings: list, detail, create, edit, delete with owner/manager access rules
- Booking creation flow: select shelter first, then create booking with pets only from that shelter
- Feeding Tasks: manager flow (list/detail/create/edit/delete)
- Asynchronous booking email notifications (Celery + Redis)
- Asynchronous feeding-task assignment emails to caretakers on assign/reassign (from app forms and Django admin)
- Asynchronous caretaker-pet assignment email notifications
- DRF API endpoint for bookings (`/api/bookings/`)
- Password reset email throttling (rate limit per registered email)
- Custom 404 page
- Reusable templates and Bootstrap styling

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Celery
- Redis
- Gunicorn
- WhiteNoise
- Bootstrap (via CDN)

## Project Structure

- `accounts/` — caretakers and volunteers
- `pets/` — pets and pet assignments
- `shelters/` — shelters and caretaker assignments
- `users/` — custom user model and auth/profile flows
- `booking/` — bookings and feeding task workflows
- `common/` — shared pages and components
- `templates/` — Django templates

## Setup

### 1. Clone and create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

Linux/macOS:
```bash
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update values:

```
SECRET_KEY=replace-me
DEBUG=True
LOG_LEVEL=INFO
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
DATABASE_URL=postgres://myuser:mypassword@127.0.0.1:5432/shelterdatabase
DBNAME=shelterdatabase
DBHOST=127.0.0.1
DBUSER=myuser
DBPASS=mypassword
DBPORT=5432
DEFAULT_PROFILE_IMAGE_PATH=defaults/accounts.png
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
ADMIN_NAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_TIMEOUT=30
DEFAULT_FROM_EMAIL=Pet Shelter <noreply@example.com>
SERVER_EMAIL=server@example.com
PASSWORD_RESET_EMAIL_LIMIT=3
PASSWORD_RESET_EMAIL_WINDOW_SECONDS=900
```

You can use either `DATABASE_URL` or `DBNAME/DBHOST/DBUSER/DBPASS` database configuration (if both are set,
`DATABASE_URL` is used).

Ensure the database exists in PostgreSQL and credentials are correct.
For Gmail and similar providers, use an app-specific password (not your account password).

### 5. Run migrations

```bash
python manage.py migrate
```

Migration seeding includes:

- groups and permissions (`ShelterAdmin`, `CaretakerManager`)
- admin user (if `ADMIN_NAME` and `ADMIN_PASSWORD` are set)
- default shelters, caretakers, volunteers, and pets

### 6. Start the server

```bash
python manage.py runserver
```

App runs at `http://127.0.0.1:8000/`.

### 6.1 Start Celery worker (required for async tasks)

```bash
celery -A PetShelterDjango worker --loglevel=info
```

Application and Celery logs are emitted in structured JSON format to stdout.

## Azure Deployment (App Service)

Use this startup command in Azure App Service:

```bash
bash startup.sh
```

The script:

- applies migrations
- runs `collectstatic --noinput`
- executes data seeding via migrations
- starts Gunicorn (`PetShelterDjango.wsgi`)

For async tasks in Azure, run a second worker process with:

```bash
bash startup-worker.sh
```

### Azure required app settings (production)

- `DEBUG=False`
- strong `SECRET_KEY`
- `ALLOWED_HOSTS=<your-app>.azurewebsites.net`
- `CSRF_TRUSTED_ORIGINS=https://<your-app>.azurewebsites.net`
- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS=31536000`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- `SECURE_HSTS_PRELOAD=True`
- database settings (`DATABASE_URL` or `DB*`)
- redis/celery settings
- smtp settings

## Project Setup Notes

- Required tools: Python 3.10+ and PostgreSQL 13+.
- Ensure PostgreSQL is running locally before migrations.
- `runserver` with `DEBUG=False` still shows development-server warning; use Gunicorn for production.

## Pages (Non-Admin, Non-Form)

- Home (`/`): Highlights a randomly selected active shelter and shows its latest pets. The featured shelter is
  randomized on each load.
- Shelters List (`/shelters/`): Directory of active shelters with pet counts and a preview of recent arrivals.
- Shelter Detail (`/shelters/<id>/`): Shelter profile with address, capacity, caretakers, pet counts, and the shelter’s
  pets ordered by newest first.
- Shelter Latest Additions (`/shelters/<id>/latest-additions/`): Shows the newest pets for a specific shelter. The
  shelters cards in the list view include a badge "View more" that links to this page.
- Pets List (`/pets/`): Browse active pets with optional shelter filtering; pet order is randomized each load.
- Pet Detail (`/pets/<id>/`): Full pet profile with shelter info and assigned caretakers.
- Caretakers List (`/accounts/caretakers/`): List of active caretakers.
- Caretaker Detail (`/accounts/caretakers/<id>/`): Caretaker profile with assigned shelters and pets (newest first).
- Volunteers List (`/accounts/volunteers/`): List of active volunteers.
- Volunteer Detail (`/accounts/volunteers/<id>/`): Volunteer profile with experience level.
- My Profile (`/users/me/`), Edit Profile (`/users/me/edit/`), Delete Profile (`/users/me/delete/`)
- Booking List (`/booking/`) and CRUD routes (with shelter shown in the list)
- Booking Create Step 1 (`/booking/new/`) -> select shelter
- Booking Create Step 2 (`/booking/new/<shelter_id>/`) -> create booking with shelter-filtered pets
- Feeding Task manager routes (`/booking/feeding-tasks/`)
- 404 Page: Custom not-found page for invalid routes.

## Role Model

- Regular authenticated users can create and manage only their own pending bookings.
- `ShelterAdmin` can view all bookings and has full booking/feeding task permissions.
- `CaretakerManager` has viewing and change-level task permissions based on assigned Django permissions.

## API

- `GET /api/bookings/`: list bookings
  - Regular users: own bookings only
  - Users with `booking.view_booking` in manager group: all bookings
- `POST /api/bookings/`: create booking
  - Requires authenticated user
  - Non-manager users can only book pets with `available_for_volunteers=True`
  - Non-manager users can only create `pending` status bookings

## Seed Demo Data (Optional)

```bash
python manage.py seed_demo --reset
```

## Data Backfill (Optional)

If you already have caretaker/volunteer records that are not linked to login users, run:

```bash
python manage.py link_accounts_to_users
```

To also create missing `users.User` records for unmatched account emails:

```bash
python manage.py link_accounts_to_users --create-missing-users
```

What it does:

- links `Caretaker.user` and `Volunteer.user` by matching email
- for linked caretakers, syncs `user.staffed_shelters` and adds `CaretakerManager` group
- safely skips records with no matching user email (unless `--create-missing-users` is used)

This command is idempotent and intended as a one-off repair/backfill step.

## Notes

- The custom 404 page is shown when `DEBUG = False`.
- Images are optional. Default images are used when none are uploaded.
- Default profile fallback image uses `DEFAULT_PROFILE_IMAGE_PATH` (default: `defaults/accounts.png`).
- Custom `500.html` and `403.html` templates are included in `templates/`.

## Tests

Automated tests are included for:

- Booking and feeding-task permissions/flows
- API behavior and business rules
- User flows (signup, password-reset throttling, profile delete)
- Shelter, pet, and form validation behavior

## License

See `LICENSE`.
