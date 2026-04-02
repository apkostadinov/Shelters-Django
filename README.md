# PetShelterDjango

A Django web application for managing shelters, pets, caretakers, and volunteers.

## Features

- Shelters: list, detail, create, edit, delete, assign caretakers
- Pets: list (randomized), filter by shelter, detail, create, edit, delete
- Caretakers: list, detail, create, edit, delete, assign pets
- Volunteers: list, detail, create, edit, delete
- Users: signup, login/logout, profile detail/edit (custom `AUTH_USER_MODEL`)
- Bookings: list, detail, create, edit, delete with owner/manager access rules
- Feeding Tasks: manager flow (list/detail/create/edit/delete)
- Groups/permissions command for booking roles (`ShelterAdmin`, `CaretakerManager`)
- DRF API endpoint for bookings (`/api/bookings/`)
- Custom 404 page
- Reusable templates and Bootstrap styling

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
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
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://myuser:mypassword@127.0.0.1:5432/shelterdatabase
```

Ensure the database exists in PostgreSQL and the credentials match the `DATABASE_URL`.

### 5. Run migrations

```bash
python manage.py migrate
```

### 5.1 Seed booking groups and permissions

```bash
python manage.py seed_booking_groups
```

### 6. Start the server

```bash
python manage.py runserver
```

App runs at `http://127.0.0.1:8000/`.

## Project Setup Notes

- Required tools: Python 3.10+ and PostgreSQL 13+.
- Ensure PostgreSQL is running locally before migrations.
- If you use a different host/port or credentials, update `PetShelterDjango/settings.py` accordingly.
- For a clean start, delete any existing data and rerun migrations.

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
- My Profile (`/users/me/`) and Edit Profile (`/users/me/edit/`)
- Booking List (`/booking/`) and CRUD routes
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

## Notes

- The custom 404 page is shown when `DEBUG = False`.
- Images are optional. Default images are used when none are uploaded.
- Custom `500.html` and `403.html` templates are included in `templates/`.

## Tests

Automated tests are included, with focus on booking and permissions:

- FeedingTask model validation (`clean`/save behavior)
- Booking owner access rules (detail/edit/delete)
- Permission denial and manager permission behavior in CBVs
- DRF API responses and booking creation rules

## License

See `LICENSE`.
