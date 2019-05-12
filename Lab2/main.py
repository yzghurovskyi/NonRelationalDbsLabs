import redis
import atexit


def register(conn, username):
    if conn.hget('users:', username):
        return None

    user_id = conn.incr('user:id:')

    pipeline = conn.pipeline(True)

    pipeline.hset('users:', username, user_id)

    pipeline.hmset('user:%s' % user_id, {
        'login': username,
        'id': user_id,
        'queue': 0,
        'checking': 0,
        'blocked': 0,
        'sent': 0,
        'delivered': 0
    })
    pipeline.execute()
    return user_id


def sign_in(conn, username) -> int:
    user_id = conn.hget("users:", username)

    if not user_id:
        print("Current user does not exist %s" % username)
        return -1

    conn.sadd("online:", username)
    return int(user_id)


def sign_out(conn, user_id) -> int:
    return conn.srem("online:", conn.hmget("user:%s" % user_id, ["login"])[0])


def create_message(conn, message_text, sender_id, consumer) -> int:
    message_id = int(conn.incr('message:id:'))
    consumer_id = int(conn.hget("users:", consumer))

    if not consumer_id:
        print("Current user does not exist %s, unable to send message" % consumer)
        return

    pipeline = conn.pipeline(True)

    pipeline.hmset('message:%s' % message_id, {
        'text': message_text,
        'id': message_id,
        'sender_id': sender_id,
        'consumer_id': consumer_id,
        'status': "created"
    })
    pipeline.lpush("queue:", message_id)
    pipeline.hmset('message:%s' % message_id, {
        'status': 'queue'
    })
    pipeline.zincrby("sent:", 1, "user:%s" % conn.hmget("user:%s" % sender_id, ["login"])[0])
    pipeline.hincrby("user:%s" % sender_id, "queue", 1)
    pipeline.execute()

    return message_id


def print_messages(connection, user_id):
    messages = connection.smembers("sentto:%s" % user_id)
    for message_id in messages:
        message = connection.hmget("message:%s" % message_id, ["sender_id", "text", "status"])
        sender_id = message[0]
        print("From: %s - %s" % (connection.hmget("user:%s" % sender_id, ["login"])[0], message[1]))
        if message[2] != "delivered":
            pipeline = connection.pipeline(True)
            pipeline.hset("message:%s" % message_id, "status", "delivered")
            pipeline.hincrby("user:%s" % sender_id, "sent", -1)
            pipeline.hincrby("user:%s" % sender_id, "delivered", 1)
            pipeline.execute()


def main_menu() -> int:
    print(30 * "-", "MENU", 30 * "-")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    return int(input("Enter your choice [1-3]: "))


def user_menu() -> int:
    print(30 * "-", "MENU", 30 * "-")
    print("1. Sign out")
    print("2. Send message")
    print("3. Inbox messages")
    print("4. My messages statistic")
    return int(input("Enter your choice [1-4]: "))


def main():
    def exit_handler():
        sign_out(connection, current_user_id)

    atexit.register(exit_handler)
    loop = True
    signed_in = False
    current_user_id = -1
    connection = redis.Redis(charset="utf-8", decode_responses=True)
    menu = main_menu

    while loop:
        choice = menu()

        if choice == 1:
            if not signed_in:
                login = input("Enter your username:")
                register(connection, login)
            else:
                sign_out(connection, current_user_id)
                connection.publish('users', "User %s signed out"
                                   % connection.hmget("user:%s" % current_user_id, ["login"])[0])
                signed_in = False
                current_user_id = -1
                menu = main_menu

        elif choice == 2:
            if signed_in:
                message = input("Enter message text:")
                recipient = input("Enter recipient username:")

                if create_message(connection, message, current_user_id, recipient):
                    print("Sending message...")
            else:
                login = input("Enter your login:")
                current_user_id = sign_in(connection, login)
                signed_in = current_user_id != -1
                if signed_in:
                    connection.publish('users', "User %s signed in"
                                       % connection.hmget("user:%s" % current_user_id, ["login"])[0])
                    menu = user_menu

        elif choice == 3:
            if signed_in:
                print_messages(connection, current_user_id)
            else:
                loop = False

        elif choice == 4:
            current_user = connection.hmget("user:%s" % current_user_id,
                                            ['queue', 'checking', 'blocked', 'sent', 'delivered'])
            print("In queue: %s\nChecking: %s\nBlocked: %s\nSent: %s\nDelivered: %s" %
                  tuple(current_user))
        else:
            print("Wrong option selection. Enter any key to try again..")






if __name__ == '__main__':
    main()
