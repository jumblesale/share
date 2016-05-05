import logger
import socket
import thread
import time
import settings


_connections = {}
_subscribers = {}
_connection_id = 0


def _listen(ip=settings.ip, port=settings.port):
    logger.log('connecting...')
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((ip, port))
        s.listen(5)
        logger.log('share server listening on %s:%s' % (ip, port))
        _accept_connections(s)
    except socket.error as err:
        logger.log("socket creation failed with error %s" % err)
    except KeyboardInterrupt:
        logger.log("received SIGINT, exiting...")
        _close(s)
    finally:
        _close(s)
        logger.log("that's it I'm done much love x")


def _handler(connection, connection_id):
    logger.log("started new thread for connection %s" % connection_id)
    while True:
        time.sleep(0.01)
        msg = connection.recv(256).rstrip()
        # get the first word in the command
        cmd = msg.lower().split(" ")[0]
        if "quit" == cmd or "" == cmd:
            _close_connection(connection, connection_id)
            break
        else:
            logger.log("received %s from connection %s" % (cmd, connection_id))
            if "share" == cmd:
                to_share = msg[msg.index(" ") + 1:]
                _share(to_share)
                _send_message(connection, "SHARED")
                return
            if "subscribe" == cmd:
                _add_subscriber(connection, connection_id)
                _send_message(connection, "SUBSCRIBED")
                continue


def _share(msg):
    logger.log("sharing %s" % msg)
    url = msg[0:msg.index(" ")]
    description = msg[msg.index(" ") + 1:]
    global _connections
    for connection_id, connection in _subscribers.iteritems():
        _send_message(connection, url)
        _send_message(connection, description)


def _send_message(connection, message):
    connection.send("%s\n" % message)


def _perform_handshake(connection):
    connection.send("hello")
    if "hello" != connection.recv(8).rstrip().lower():
        logger.log("handshake failed, sorry :(. ")
        connection.send("you must respond with 'hello' to use this service")
        connection.close()
        return False
    return True


def _accept_connections(s):
    global _connections
    while True:
        connection, address = s.accept()
        logger.log("received a new connection, performing handshake")
        if not _perform_handshake(connection):
            continue
        new_connection_id = _get_next_id()
        logger.log("creating new connection with id %s" % new_connection_id)
        _connections[new_connection_id] = connection
        thread.start_new_thread(_handler, (connection, new_connection_id,))
        time.sleep(0.01)


def _add_subscriber(connection, connection_id):
    logger.log("connection with id %s has subscribed for updates" % connection_id)
    _subscribers[connection_id] = connection


def _close_connection(connection, connection_id):
    global _connections, _subscribers
    _send_message(connection, "thanks for dropping by!!")
    connection.close()
    _connections.pop(connection_id, None)
    # check if it was a subscriber
    try:
        _subscribers.pop(connection_id, None)
    except KeyError:
        # igaf
        pass
    logger.log("connection with id %s has gone, goodbye!!" % connection_id)
    thread.exit_thread()


def _close(s):
    _kill_connections()
    s.close()


def _kill_connections():
    global _connections, _subscribers
    for connection_id, connection in _connections.iteritems():
        connection.close()
    _connections = {}
    _subscribers = {}


def _get_next_id():
    global _connection_id
    _connection_id += 1
    return _connection_id


if __name__ == '__main__':
    _listen()
