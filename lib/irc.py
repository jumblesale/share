import client
import socket
import time
import settings


def _share(data):
    print data
    # data will be like "<user> <url> <description here...>"
    # so we split on the spaces
    try:
        parts = data.split(" ")
        user = parts[0]
        url = parts[1]
        # then just get everything from the 2nd space to the end
        description = " ".join(parts[2:])

        print("sharing user: %s url: %s description: %s" % (user, url, description))
        if not url or not user or not description:
            raise ValueError
        client.share(user, url, description)
    except ValueError:
        return False
    return True


def _send_message(s, channel, msg):
    s.send("PRIVMSG %s :%s\n" % (channel, msg))


def _listen(s, channel):
    # example message format:
    # :jumblesale!~jumblesale@127.0.0.1 PRIVMSG #bots :hello
    while 1:
        time.sleep(1)

        # get data from the server
        msg = s.recv(1024).rstrip()
        nick = ""
        contents = ""
        try:
            # nick appears between first : and ! as in :jumblesale! above
            nick = msg[(msg.index(":") + 1):(msg.index("!"))]
            # the actual message comes after the second colon
            contents = msg.split(":")[2]
        except ValueError:
            # it didn't have a nick or a message, we don't care
            pass

        # was the message to try and share something?
        if "!share" == contents[0:6].lower():
            # ignore the actual '!share' bit
            # list comprehensions are tass af
            to_share = contents[contents.index(" ") + 1:]
            success = _share(to_share)
            if not success:
                _send_message(s,"unexpected arguments :(")
                _send_message(s, _usage())
            _send_message(s, channel, '%s just shared "%s"!'
                          % (nick, to_share))
            continue

        # respond to pings
        if msg.find("PING :") != -1:
            s.send("PONG :hello")


def _usage():
    return "to share a new thing just say !share <user> <page> " \
           "<optional description> - where user is a a townie " \
           "(without the ~), page is the path to the page (so " \
           "like 'blog/2015-05-21.html) and the description can " \
           "be anything you like, or nothing!"


def _connect(
        name=settings.irc["name"],
        host=settings.irc["host"],
        port=settings.irc["port"],
        channel=settings.irc["channel"]
):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send("NICK %s\n" % name)
    s.send("USER %s 0 * :%s\n" % (name, name))
    s.send("JOIN %s\n" % channel)
    _listen(s, channel)

if __name__ == "__main__":
    _connect()
