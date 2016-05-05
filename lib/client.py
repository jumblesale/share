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


def _listen(c):
    while True:
        print _receive(c)
        time.sleep(0.01)


def _receive(c):
    return c.recv(16).rstrip().lower()


def _subscribe(c):
    c.send("subscribe")
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
        if _subscribe(client) is False:
            raise SubscriptionError("could not subscribe to share server")
        _listen(client)

    except socket.error as error:
        raise ConnectionError("connecting failed with error <%s>.\n"
                              "is the server running on port %d?\n"
                              "sorry it didn't work out."
                              % (error, settings.port))

    finally:
        client.close()

if __name__ == "__main__":
    _connect()
