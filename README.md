# EventHub

## Local setup

Python 3.12+ and SQLite are sufficient:

```sh
python -m venv .venv
# Activate .venv, then:
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `/signup/` to register, `/login/` to sign in, `/profile/` to view your
profile and `/profile/edit/` to edit it. The username in the menu links to
your own profile. Avatars are stored under `media/accounts/avatars/` and are
served locally when `DEBUG=True`. Uploads must be valid images of at most 5 MB.

Profile forms expose only first name, last name, email, avatar, bio, city and
birth date. Email validation rejects another user's address without regard
to case; blank email is optional. New users receive a profile via a signal;
older users receive one on their first profile visit. Editing requires login
and a CSRF-protected POST. Profile URLs never accept a user identifier.

Events can be created by signed-in users; ownership is assigned on the server.
Only the owner can edit or soft-delete an event. GET displays a deletion
confirmation; POST updates `is_deleted` without removing the database row.
Deleted events are excluded from catalogue, profile and direct detail/edit URLs.

## Compatibility with the original assignment

The feature branch starts at the fork's `main` (`dbf18ed`) and includes upstream
`main` (`2da6adc`), which supplies accounts, authentication and Event.owner.
The original upstream migration files are retained. A replacement migration
combines events 0002–0004 for fresh databases and upgrades from fork main.
It preserves historical ownerless events under a newly created inactive account
with an unusable password, rather than granting ownership to user id 1.
An administrator may deliberately reassign these events later. Databases that
already applied all three upstream migrations keep their existing owners.

If a database stopped partway through upstream migrations 0002–0004, Django
uses the original migrations: resolve null event owners explicitly before
applying 0004. Back up an existing database before upgrading.

The requirements use Django 5.2 LTS; the old generated-file comments mentioning
6.1.1 do not represent an installed dependency. Run these checks locally:

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Tests cover profiles, auth redirects, image uploads, validation, ownership,
CSRF, soft deletion, navigation, and upgrades from both fork and upstream.
Settings remain for local development; configure secrets, hosts, HTTPS and
production media serving before deploying publicly.
