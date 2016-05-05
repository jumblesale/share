import socket
import settings
import time


# our error classes
class ConnectionError(Exception): pass
class HandShakeError(Exception): pass
class SubscriptionError(Exception): pass
class ShareError(Exception): pass


def _handshake(c):
    response = _receive(c)
    if response != "hello":
        return False
    else:
        c.send("hello")
        return True


def _send_message(c, message):
    c.send(message)


def _listen(c, handler):
    while True:
        handler(_receive(c))
        time.sleep(0.01)


def _receive(c):
    return c.recv(128).rstrip().lower()


def _subscribe(c):
    c.send("subscribe")
    # the server should always respond SUBSCRIBED
    # to let us know it worked ok
    expected = "subscribed"
    response = _receive(c)
    if expected != response:
        return False
    return True


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
# url:
#    the relative location of the page, so
#    ~joe/modestproposal.html would be 'modestproposal.html'
# description:
#    an optional description of the link
# returns: True or False depending on if it succeeds or not
# throws:
#     ConnectionError
#     HandShakeError
#     ShareError
def share(user, url, description=""):
    url = "https://%s/~%s/%s" % ("tilde.town", user, url)
    client = _connect()
    _send_message(client, "%s %s %s" % ("share", url, description))
    client.close()


# listen for new shares
#
# handler:
#     the method to call with the received data
# throws:
#     ConnectionError
#     HandShakeError
#     ShareError
#     SubscriptionError
def listen(handler):
    client = _connect()
    _listen(client, handler)


if __name__ == "__main__":
    share("jumblesale", "ksp.html", "the continuing adventures of ksp")
