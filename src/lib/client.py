import socket
import time

import settings


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
    client.close()


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


if __name__ == "__main__":
    share("jumblesale", "ksp.html", "the continuing adventures of ksp")
