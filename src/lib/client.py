import socket
import time
import store
import settings
import sys


# our error classes
class ConnectionError(Exception): pass
class HandShakeError(Exception): pass
class SubscriptionError(Exception): pass
class ShareError(Exception): pass


# perform handshake with the server
# (just respond with 'hello')
def _handshake(c):
    response = _receive(c)
    if response != "hello?":
        print "expected %s but got %s" % ("hello?", response)
        return False
    else:
        _send_message(c, "hello")
        return True


# send a message over the socket connection
def _send_message(c, message):
    c.sendall(message)


# start listening for new data from the server
def _listen(c, handler, args):
    while handler(_receive(c), *args) is True:
        time.sleep(0.01)
    c.close()


# receive data from the server
def _receive(c):
    received = c.recv(128).lower().rstrip()
    return received


# subscribe to notifications from the server
def _subscribe(c):
    _send_message(c, "subscribe")
    # the server should always respond SUBSCRIBED
    # to let us know it worked ok
    expected = "subscribed"
    response = _receive(c)
    if expected != response:
        return False
    return True


# open a socket connection
def _connect(ip=settings.ip, port=settings.port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((ip, port))
        if _handshake(client) is False:
            raise HandShakeError(
                "could not perform handshake with share server"
            )
        return client

    except socket.error as error:
        raise ConnectionError("connecting failed with error <%s>.\n"
                              "is the server running on port %d?\n"
                              "sorry it didn't work out."
                              % (error, settings.port))


# share a new page
#
# user:
#    the townie who created this page without the ~
#    (insom, karlen, &c.)
# page:
#    the relative location of the page, so
#    ~joe/modestproposal.html would be 'modestproposal.html'
# description:
#    an optional description of the link
# returns:
#    None
# throws:
#     ConnectionError
#     HandShakeError
#     ShareError
def share(user, page, description=""):
    client = _connect()
    time.sleep(0.1)
    _send_message(client, "%s %s %s %s" % ("share", user, page, description))
    response = _receive(client)
    if response.upper() != "SHARED":
        _handle_error(response)
    client.close()


def _handle_error(response):
    parts = response.split(":")
    try:
        if parts[0] != "error":
            raise ShareError(
                "something went wrong but the server's response was malformed"
            )
        error = parts[1]
        if error == "1":
            raise ShareError(
                "there was a problem with the formatting of that message"
            )
    except IndexError:
        raise ShareError("could not parse response %s" % response)


# listen for new shares
#
# handler:
#     the method to call with the received data
# args:
#     a tuple of any arguments you want passed to the handler
# returns:
#     None
# throws:
#     ConnectionError
#     HandShakeError
#     ShareError
#     SubscriptionError
def listen(handler, args):
    client = _connect()
    time.sleep(0.1)
    _subscribe(client)
    _listen(client, handler, args)


# get a list of existing shares, oldest first
# n:     the number of shares to retrieve
# since: time (in seconds) to go back for shares
def get_shares(n=0, since=None):
    return store.load(n, since)


if __name__ == "__main__":
    try:
        user = sys.argv[1] or ""
        page = sys.argv[2] or ""
        description = sys.argv[3] or ""
        share(user, page, description)
    except IndexError:
        print 'usage: python client.py <user> <page> [<description>]'
    except ShareError as err:
        print 'share failed with message: "%s"' % err
