import datetime
from threading import Thread
import logging
import redis

# add filemode="w" to overwrite
logging.basicConfig(filename="events.log", level=logging.INFO)


class EventListener(Thread):

    def __init__(self, connection):
        Thread.__init__(self)
        self.connection = connection

    def run(self):
        pubsub = self.connection.pubsub()
        pubsub.subscribe(["users", "spam"])
        for item in pubsub.listen():
            if item['type'] == 'message':
                message = "\nEVENT: %s | %s" % (item['data'], datetime.datetime.now())
                logging.info(message)


def print_admin_menu():
    print(30 * "-", "MENU", 30 * "-")
    print("1. Online users")
    print("2. Top senders")
    print("3. Top spamers")
    print("4. Exit")
    print(67 * "-")


def main():
    loop = True
    connection = redis.Redis(charset="utf-8", decode_responses=True)
    listener = EventListener(connection)
    listener.setDaemon(True)
    listener.start()

    while loop:
        print_admin_menu()
        choice = int(input("Enter your choice [1-4]: "))

        if choice == 1:
            online_users = connection.smembers("online:")
            print("Users online:")
            for user in online_users:
                print(user)

        elif choice == 2:
            top_senders_count = int(input("Enter count of top senders: "))
            senders = connection.zrange("sent:", 0, top_senders_count - 1, desc=True, withscores=True)
            print("Top %s senders" % top_senders_count)
            for index, sender in enumerate(senders):
                print(index + 1, ". ", sender[0], " - ", int(sender[1]), "message(s)")

        elif choice == 3:
            top_spamers_count = int(input("Enter count of top spamers: "))
            spamers = connection.zrange("spam:", 0, top_spamers_count - 1, desc=True, withscores=True)
            print("Top %s spamers" % top_spamers_count)
            for index, spamer in enumerate(spamers):
                print(index + 1, ". ", spamer[0], " - ", int(spamer[1]), " spammed message(s)")

        elif choice == 4:
            print("Exiting...")
            loop = False
        else:
            print("Wrong option selection. Enter any key to try again..")


if __name__ == '__main__':
    main()
