import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
def main():
    from django.core.management import (  # pyright: ignore[reportMissingImports]
        call_command,
        execute_from_command_line,
    )
    call_command("migrate", interactive=False)
    call_command("seed_seaon")
    execute_from_command_line(["app.py","runserver","127.0.0.1:8000"])
if __name__=="__main__": main()
