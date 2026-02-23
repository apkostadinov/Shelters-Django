# PetShelterDjango

A Django web application for managing shelters, pets, caretakers, and volunteers.

## Features

- Shelters: list, detail, create, edit, delete, assign caretakers
- Pets: list (randomized), filter by shelter, detail, create, edit, delete
- Caretakers: list, detail, create, edit, delete, assign pets
- Volunteers: list, detail, create, edit, delete
- Custom 404 page
- Reusable templates and Bootstrap styling

## Tech Stack

- Python
- Django
- PostgreSQL
- Bootstrap (via CDN)

## Project Structure

- `accounts/` — caretakers and volunteers
- `pets/` — pets and pet assignments
- `shelters/` — shelters and caretaker assignments
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

### 4. Configure PostgreSQL

Create a database and user, then update `PetShelterDjango/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "<database name>",
        "USER": "<user>",
        "PASSWORD": "<password>",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
```

### 5. Run migrations

```bash
python manage.py migrate
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
- 404 Page: Custom not-found page for invalid routes.

## Seed Demo Data (Optional)

```bash
python manage.py seed_demo --reset
```

## Notes

- The custom 404 page is shown when `DEBUG = False`.
- Images are optional. Default images are used when none are uploaded.

## Tests

No automated tests are included yet.

## License

See `LICENSE`.


## TODOs
- [ ] Add automated tests
- [ ] Add more validation
- [ ] Add a booking features
- [ ] Add a user profile page
- [ ] Add a search feature
