"""
SEAON ERP - One-click startup.

For a non-technical user, this is the only file you normally need.
Run:

    python app.py

It will:
1. Apply Django database migrations.
2. Create the demo administrator and default roles.
3. Import the supplied Excel stock sheets into SQLite.
4. Start the ERP website and API on http://127.0.0.1:8000/
"""
import os
import sys

# Make sure Django knows which settings module to use.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django


def main():
    # Initialize Django before using any Django management commands.
    django.setup()

    from django.core.management import call_command

    print("Preparing SEAON ERP...")

    # Create/update the database tables.
    call_command("migrate", interactive=False)

    # Create the default SEAON roles and admin account.
    call_command("seed_seaon")

    # Import the supplied sample stock spreadsheets.
    call_command("import_sample_data")

    print()
    print("========================================")
    print("       SEAON ERP IS STARTING")
    print("========================================")
    print()
    print("Open:")
    print("http://127.0.0.1:8000/app/login.html")
    print()
    print("Login:")
    print("Email:    admin@seaon.com")
    print("Password: Admin@123")
    print()
    print("Press CTRL+C to stop the server.")
    print()

    # Start Django's development server.
    call_command(
        "runserver",
        "127.0.0.1:8000",
    )


if __name__ == "__main__":
    main()