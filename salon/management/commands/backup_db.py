# salon/management/commands/backup_db.py
import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime

from shutil import which

# Попробуем найти pg_dump из Postgres.app, а иначе из PATH
def find_pg_dump():
    # Путь для Postgres.app v17
    candidate = '/Applications/Postgres.app/Contents/Versions/17/bin/pg_dump'
    if os.path.exists(candidate):
        return candidate
    # fallback на PATH
    return which('pg_dump')

class Command(BaseCommand):
    help = 'Создать дамп базы данных PostgreSQL'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'{settings.BASE_DIR}/backups/backup_{timestamp}.sql'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pg_dump = find_pg_dump()
        db = settings.DATABASES['default']
        cmd = [
            pg_dump,
            f'--dbname=postgresql://{db["USER"]}:{db["PASSWORD"]}@{db["HOST"]}:{db["PORT"]}/{db["NAME"]}',
            '-F', 'c',   # custom format
            '-f', filename
        ]
        try:
            subprocess.check_call(cmd)
            self.stdout.write(self.style.SUCCESS(f'Бекап сохранён в {filename}'))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при создании бекапа: {e}'))
            raise
