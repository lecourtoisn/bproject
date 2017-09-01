import json
import os
import traceback
from time import sleep

from bot.BlackjackBot import BlackjackBot
from bot.BlackjackEngine import BlackjackEngine
from bot.CustomClient import CustomClient
from data_cache.PCache import PCache

SESSION_FILE = "session.txt"

if __name__ == '__main__':
    email, password = os.environ.get("email"), os.environ.get("password")
    if email is None or password is None:
        print("The email and password must be given in environment variable")
        exit()

    PCache.load_all()
    session = None
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as file:
            session = json.load(file)

    engine = BlackjackEngine()
    while True:
        client = CustomClient(email, password, session=session)
        m = BlackjackBot(client, engine)
        try:
            client.listen()
        except:
            traceback.print_exc()
            engine.observers.remove(client)
            sleep(5)
