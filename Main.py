import json
import os

from BlackjackBot import BlackjackBot
from CustomClient import CustomClient

if __name__ == '__main__':

    email, password = os.environ.get("email"), os.environ.get("password")
    if email is None or password is None:
        print("The email and password must be given in environment variable")
        exit()

    session = None
    if os.path.exists("sessions.txt"):
        with open("sessions.txt") as file:
            session = json.load(file)

    client = CustomClient(email, password, session=session)
    m = BlackjackBot(client)
    client.listen()
    client.logout()
