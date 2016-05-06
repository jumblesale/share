import client
import socket
import time
import settings
import threading

# a flag to get us out of listening
terminate = False


# our errors
class ShareError(Exception): pass
class FormatError(Exception): pass


# connect to the share server and send along a new share
def _share(data):
    print 'sharing "%s"...' % data
    # data will be like "<user> <page> <description here...>"
    # so we split on the spaces
    try:
        parts = data.split(" ")
        user = parts[0]
        page = parts[1]
        # then just get everything from the 2nd space to the end
        description = " ".join(parts[2:])
        client.share(user, page, description)
        # we return the parts cause they're useful for later
        return user, page, description
    except IndexError:
        raise FormatError
    # the client could fail so let's deal with it
    except(client.ConnectionError,
           client.HandShakeError,
           client.ShareError) as err:
        raise ShareError(err)


def _send_message(s, channel, msg):
    s.send("PRIVMSG %s :%s\n" % (channel, msg))
    # don't flood
    time.sleep(0.1)


# parse messages on irc channel waiting for !shares
def _listen_to_irc(s, channel):
    # example message format:
    # :jumblesale!~jumblesale@127.0.0.1 PRIVMSG #bots :hello
    while terminate is False:
        time.sleep(1)

        # get data from the server
        msg = s.recv(1024).rstrip()
        try:
            # nick appears between first : and ! as in :jumblesale! above
            nick = msg[(msg.index(":") + 1):(msg.index("!"))]
            # the actual message comes after the second colon
            contents = msg.split(":")[2]
        except (ValueError, IndexError):
            # it didn't have a nick or a message, we don't care
            continue

        # was the message to try and share something?
        if "!share" == contents[0:6].lower():
            # ignore the actual '!share' bit
            # list comprehensions are tass af
            to_share = contents[contents.index(" ") + 1:]
            try:
                user, page, description = _share(to_share)
            except FormatError:
                # the message wasn't right
                _send_message(s, channel, "unexpected arguments :(")
                _send_message(s, channel, _usage())
            except ShareError as err:
                # the client failed
                _send_message(s, channel,
                              'sharing failed with error "%s"' % err)
            continue

        # respond to pings
        if msg.find("PING :") != -1:
            s.send("PONG :pingis\n")


# let the channel know there was a new share
def _send_share_notification(s, channel, user, page, description="", nick=""):
    url = "http://tilde.town/%s/%s" % (user, page)
    # make sure the description isn't too long
    if len(description) > 128 or "" == description:
        description = ""
    else:
        description = " - %s" % description
    if "" == nick:
        notification = 'new share! %s%s' % (url, description)
    else:
        notification = '%s just shared %s%s' % (nick, url, description)
    _send_message(s, channel, notification)


# info on how to use the bot
def _usage():
    return "to share a new thing just say !share <user> <page> " \
           "<optional description> - where user is a a townie " \
           "(without the ~), page is the path to the page (so " \
           "like 'blog/2015-05-21.html') and the description can " \
           "be anything you like, or nothing!"


# listen to new shares from the share server
def _listen_to_server(s, channel):
    print "listening on channel %s" % channel
    try:
        client.listen(_respond_to_shares, (s, channel))
    except(
        client.ConnectionError,
        client.HandShakeError,
        client.SubscriptionError,
        client.ShareError
    ):
        global terminate
        terminate = True
        print "something went wrong connecting to the share server!"
        raise


# this callback will be triggered whenever the server passes along a new share
# return False to halt listening
def _respond_to_shares(share_data, irc_socket, channel):
    global terminate
    if terminate is True:
        return False
    try:
        parts = share_data.split(" ")
        user = parts[0]
        page = parts[1]
        description = " ".join(parts[2:])
        _send_share_notification(irc_socket, channel, user, page, description)
    except IndexError:
        print '"%s" was malformed' % share_data
        return False
    return True


def _connect(
        name=settings.irc["name"],
        host=settings.irc["host"],
        port=settings.irc["port"],
        channel=settings.irc["channel"]
):
    global terminate

    # open a connection to the share server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_thread = threading.Thread(
        target=_listen_to_server,
        args=(s, channel),
        name="share-server"
    )
    server_thread.setDaemon(True)
    server_thread.start()

    # open a connection to the irc server
    s.connect((host, port))
    s.send("NICK %s\n" % name)
    s.send("USER %s 0 * :%s\n" % (name, name))
    s.send("JOIN %s\n" % channel)

    # now listen for chat
    irc_thread = threading.Thread(
        target=_listen_to_irc,
        args=(s, channel),
        name="irc"
    )
    irc_thread.setDaemon(True)
    irc_thread.start()

    try:
        while terminate is False:
            time.sleep(1)
    except KeyboardInterrupt:
        print "SIGINT received, exiting..."


if __name__ == "__main__":
    _connect()
