import zmq


def set_pubsub_heartbeat_options(socket):
    socket.setsockopt(zmq.HEARTBEAT_IVL, 5000)
    socket.setsockopt(zmq.HEARTBEAT_TIMEOUT, 15000)
    socket.setsockopt(zmq.HEARTBEAT_TTL, 60000)