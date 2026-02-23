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