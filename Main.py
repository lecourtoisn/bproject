import json
import os
import traceback
from time import sleep

import requests

from bot.BlackjackBot import BlackjackBot
from bot.BlackjackEngine import BlackjackEngine
from bot.CustomClient import CustomClient
from data_cache.PCache import PCache
import click

SESSION_FILE = "session.txt"

CASINO_THREAD_ID = "1526063594106602"
DB_PATH = "data_cache/db.json"
BACKUP_DB_PATH = "data_cache/db_backup.json"
BETTING_DELAY = 15.0
ACTIONS_DELAY = 60.0

DEBUG_THREAD_ID = "1573965122648233"
DEBUG_DB_PATH = "data_cache/debug_db.json"
DEBUG_BACKUP_DB_PATH = "data_cache/debug_db_backup.json"
DEBUG_BETTING_DELAY = 5.0
DEBUG_ACTIONS_DELAY = 15.0


@click.command()
@click.option('--debug', is_flag=True)
def start(debug):
    betting_delay = DEBUG_BETTING_DELAY if debug else BETTING_DELAY
    actions_delay = DEBUG_ACTIONS_DELAY if debug else ACTIONS_DELAY
    casino_thread_id = DEBUG_THREAD_ID if debug else CASINO_THREAD_ID
    db_path = DEBUG_DB_PATH if debug else DB_PATH
    backup_db_path = DEBUG_BACKUP_DB_PATH if debug else BACKUP_DB_PATH

    email, password = os.environ.get("email"), os.environ.get("password")
    if email is None or password is None:
        print("The email and password must be given in environment variable")
        exit()

    PCache.set_paths(db_path, backup_db_path)
    PCache.load_all()

    session = None
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as file:
            session = json.load(file)

    engine = BlackjackEngine(betting_delay, actions_delay)
    while True:
        client = CustomClient(email, password, session=session)
        BlackjackBot(client, engine, casino_thread_id, threads=[casino_thread_id])
        print(engine.observers)
        try:
            client.listen()
        except requests.exceptions.ConnectionError:
            traceback.print_exc()
            client.logout()
            engine.observers.remove(client)
            sleep(5)


if __name__ == '__main__':
    start()
