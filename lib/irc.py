import client
import socket
import time
import settings


def share(args):
    print args


def send_message(s, channel, msg):
    s.send("PRIVMSG %s :%s\n" % (channel, msg))


def listen(s, channel):
    # example message format:
    # :jumblesale!~jumblesale@127.0.0.1 PRIVMSG #bots :hello
    while 1:
        time.sleep(1)

        # get data from the server
        msg = s.recv(2046).rstrip()
        nick = ""
        contents = ""
        try:
            # nick appears between first : and !
            nick = msg[(msg.index(":") + 1):(msg.index("!"))]
            # the actual message comes after the second colon
            contents = msg.split(":")[2]
        except ValueError:
            # it didn't have a nick or a message, we don't care
            pass

        # was the message to try and share something?
        if "!share" == contents[0:6]:
            args = contents.split(" ")[1:]
            response = share(msg)
            send_message(s, channel, '%s just shared "%s"! response %s'
                         % (nick, " ".join(args), response))
            continue

        # respond to pings
        if msg.find("PING :") != -1:
            s.send("PONG :hello")


def connect(
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
    listen(s, channel)

if __name__ == "__main__":
    connect()
