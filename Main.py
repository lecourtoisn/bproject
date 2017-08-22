import json
import os

from bot.BlackjackBot import BlackjackBot
from bot.CustomClient import CustomClient
from data_cache.PCache import PCache

if __name__ == '__main__':
    email, password = os.environ.get("email"), os.environ.get("password")
    if email is None or password is None:
        print("The email and password must be given in environment variable")
        exit()

    PCache.load_all()
    session = None
    if os.path.exists("sessions.txt"):
        with open("sessions.txt") as file:
            session = json.load(file)

    client = CustomClient(email, password, session=session)
    m = BlackjackBot(client)
    client.listen()
