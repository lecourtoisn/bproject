from CustomClient import CustomClient
from MessengerBot import Blackjack

if __name__ == '__main__':
    client = CustomClient()
    m = Blackjack(client)
    client.listen()
    client.logout()
