import asyncio
import django
import os
import sys
import multiprocessing
from asgiref.sync import sync_to_async

# Настроим Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import close_old_connections
from parsers.models import Parser

import logging
import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PARSER_SCRIPTS = {
    # "avito": "parsers/scripts/avito_parser.py",
    "drom": "parsers/scripts/drom_parser.py",
    # "autoru": "parsers/scripts/autoru_parser.py",
}

RUNNING_PROCESSES = {}  # Хранит {имя парсера: Process}
MAX_PARERS_RUNNING = 3  # Максимальное количество параллельных парсеров

@sync_to_async
def get_active_parsers():
    """Получает список активных парсеров из БД"""
    return list(Parser.objects.filter(is_active=True))

def run_parser(script_path):
    """Запускает отдельный процесс для парсера"""
    os.execv(sys.executable, [sys.executable, script_path])

async def start_parser(name, script_path):
    """Запускает парсер в новом процессе"""
    if name in RUNNING_PROCESSES:
        logger.info(f"Парсер {name} уже запущен, пропускаем...")
        return

    if len(RUNNING_PROCESSES) >= MAX_PARERS_RUNNING:
        logger.info(f"Максимальное количество парсеров достигнуто. Парсер {name} не будет запущен.")
        return

    logger.info(f"Запускаем парсер {name} (скрипт: {script_path})...")
    process = multiprocessing.Process(target=run_parser, args=(script_path,))
    process.start()
    RUNNING_PROCESSES[name] = process
    logger.info(f"Процесс {name} запущен, PID: {process.pid}")

async def stop_parser(name):
    """Останавливает парсер, если он запущен"""
    if name in RUNNING_PROCESSES:
        logger.info(f"Остановка парсера {name}...")
        process = RUNNING_PROCESSES[name]
        process.terminate()
        process.join()
        del RUNNING_PROCESSES[name]
        logger.info(f"Парсер {name} остановлен.")

async def manage_parsers():
    """Управляет запущенными парсерами"""
    while True:
        close_old_connections()
        active_parsers = await get_active_parsers()
        active_parsers_names = {p.name for p in active_parsers}

        # Запуск новых парсеров
        for name in active_parsers_names:
            if name not in RUNNING_PROCESSES and name in PARSER_SCRIPTS:
                await start_parser(name, PARSER_SCRIPTS[name])

        # Остановка неактивных парсеров
        for name in list(RUNNING_PROCESSES.keys()):
            if name not in active_parsers_names:
                await stop_parser(name)

        await asyncio.sleep(5)  # Проверяем состояние раз в 5 секунд

def handle_exit(sig, frame):
    """Грейсфул-шатдаун: убиваем все процессы"""
    logger.info("Завершаем работу, останавливаем все парсеры...")
    for name in list(RUNNING_PROCESSES.keys()):
        RUNNING_PROCESSES[name].terminate()
        RUNNING_PROCESSES[name].join()
        del RUNNING_PROCESSES[name]
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
    asyncio.run(manage_parsers())
