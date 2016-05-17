import socket
import thread
import threading
import time

import logger
import settings
import store
import users

_connections = {}
_subscribers = {}
_connection_id = 0
_storage_lock = threading.Lock()


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
        time.sleep(0.1)
        try:
            msg = _receive(connection)
        except socket.error as err:
            logger.log("something went wrong with connection %s, closing\n%s"
                       % (connection_id, err))
            _close_connection(connection, connection_id)
        # get the first word in the command
        cmd = msg.lower().split(" ")[0]
        if "quit" == cmd or "" == cmd:
            _close_connection(connection, connection_id)
            break
        else:
            logger.log('received "%s" from connection %d' % (msg, connection_id))
            if "share" == cmd:
                if _share(msg) is True:
                    _send_message(connection, "SHARED")
                else:
                    # for now it's always going to be formatting
                    _send_message(connection, 'ERROR:1:FORMATTING')
                continue
            if "subscribe" == cmd:
                _add_subscriber(connection, connection_id)
                _send_message(connection, "SUBSCRIBED")
                continue


def _share(msg):
    logger.log('received "%s"' % msg)
    # make sure the message looks right
    try:
        # split up the message
        parts = msg.split(" ")
        user = parts[1]
        page = parts[2]
        description = " ".join(parts[3:])
        # does the message pass validation?
        errors = _validate_share(user=user, page=page, description=description)
        if len(errors) > 0:
            logger.log('share failed with message: "%s"' % "; ".join(errors))
            # tell the client it failed
            return False
        # send it to everyone!
        global _connections
        for connection_id, connection in _subscribers.iteritems():
            _send_share(connection, user, page, description)
        # save it to disk
        _storage_lock.acquire()
        store.add(user, page, description)
        _storage_lock.release()
        return True
    except IndexError:
        logger.log('"%s" was malformed' % msg)
        return False


def _validate_share(user, page, description):
    errors = []
    if users.user_page_exists(user, page) is False:
        errors.append("%s/%s does not exist" % (user, page))
    if len(description) > 128:
        errors.append("description was too long")
    return errors


def _send_share(connection, user, page, description):
    message = "%s %s %s" % (user, page, description)
    _send_message(connection, message)


def _send_message(connection, message):
    connection.sendall("%s\n" % message)


def _receive(connection):
    return connection.recv(1024).rstrip().lower()


def _perform_handshake(connection):
    _send_message(connection, "hello?")
    response = connection.recv(16).rstrip().lower()
    if "hello" != response:
        logger.log("handshake failed, sorry :( got %s" % response)
        _send_message(connection, "you must respond with 'hello' "
                                  "to use this service")
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
    try:
        # connection might have already gone
        _send_message(connection, "thanks for dropping by!!")
    except socket.error:
        logger.log("tried to wish connection %s farewell but "
                   "they were already gone" % connection_id)
        pass
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
