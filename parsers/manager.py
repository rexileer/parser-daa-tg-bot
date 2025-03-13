import asyncio
import subprocess
import time
import django
import os
import sys
from asgiref.sync import sync_to_async

# Настроим Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # Путь до settings.py
django.setup()

from django.db import close_old_connections
from parsers.models import Parser

PARSER_SCRIPTS = {
    "avito": "parsers/scripts/avito_parser.py",
    "drom": "parsers/scripts/drom_parser.py",
    "auto_ru": "parsers/scripts/autoru_parser.py",
}

RUNNING_PROCESSES = {}


@sync_to_async
def get_parser(name):
    return Parser.objects.filter(name=name).first()

async def run_parser(name, script_path):
    """Запускает парсер в отдельном процессе"""
    while True:
        print(f"Запускаю парсер {name} (скрипт: {script_path})...")
        process = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        RUNNING_PROCESSES[name] = process
        print(f"Процесс {name} запущен, PID: {process.pid}")
        

        # Даем процессу время работать, но не блокируем основной цикл
        while process.poll() is None:  # Пока процесс не завершился
            await asyncio.sleep(1)  # Пауза, чтобы не нагружать CPU

        # Проверяем, не отключили ли парсер в админке
        parser = await get_parser(name)
        if not parser or not parser.is_active:
            del RUNNING_PROCESSES[name]
            print(f"Парсер {name} выключен в админке, остановка...")
            break

        print(f"Парсер {name} завершился, перезапускаем через 10 секунд...")
        await asyncio.sleep(10)  # Даем паузу перед перезапуском


async def manage_parsers():
    """Следит за статусом парсеров и перезапускает их при изменениях в БД"""
    last_restart_time = time.time()  # Время последнего перезапуска

    while True:
        close_old_connections()
        active_parsers = await sync_to_async(list)(Parser.objects.filter(is_active=True))
        active_parsers_names = {p.name for p in active_parsers}
        
        # Запускаем новые парсеры
        for name in active_parsers_names:
            if name not in RUNNING_PROCESSES and name in PARSER_SCRIPTS:
                print(f"Запуск парсера {name}...")
                asyncio.create_task(run_parser(name, PARSER_SCRIPTS[name]))

        # Останавливаем парсеры, которые выключили в админке
        for name in list(RUNNING_PROCESSES.keys()):
            if name not in active_parsers_names:
                print(f"Остановка парсера {name}...")
                RUNNING_PROCESSES[name].terminate()
                
                # Проверяем, прошло ли 10 минут с последнего перезапуска
        current_time = time.time()
        if current_time - last_restart_time >= 600:  # 600 секунд = 10 минут
            print("Прошло 10 минут, перезапускаю скрипт...")
            os.execv(sys.executable, ['python'] + sys.argv)  # Перезапуск скрипта

        await asyncio.sleep(5)  # Проверка статуса каждые 5 секунд

if __name__ == "__main__":
    asyncio.run(manage_parsers())
