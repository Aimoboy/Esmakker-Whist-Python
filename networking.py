from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import List, Tuple
import event

# Networking constants
connection_num: int = 4
server_bind_addr: str = "0.0.0.0"
port: int = 1111
socket_listen_queue_cap: int = 5
msg_header_max_len: int = 7


class ClientConnectedEventArgs(event.EventArgs):
    def __init__(self, ip_addr: str, port: int) -> None:
        self.ip_addr: str = ip_addr
        self.port: int = port


class MessageReceivedEventArgs(event.EventArgs):
    def __init__(self, msg: str, sock_num: int) -> None:
        self.msg: str = msg
        self.sock_num: int = sock_num


class ClientDisconnectedEventArgs(event.EventArgs):
    def __init__(self, sock_num: int) -> None:
        self.sock_num: int = sock_num


class Server:
    """Class that receives connections from the Client class from the same file."""

    def __init__(self) -> None:
        self.client_sockets: List[socket] = []
        self.connection_threads: List[Thread] = []
        self.running: bool = True

        self.server_socket: socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((server_bind_addr, port))
        self.server_socket.listen(socket_listen_queue_cap)

        self.event_client_connected: event.Event = event.Event()
        self.event_full_connections: event.Event = event.Event()
        self.event_received_message: event.Event = event.Event()
        self.event_client_disconnected: event.Event = event.Event()

    def wait_for_connections(self) -> None:
        """Wait for all the connection slots to be filled."""

        while len(self.client_sockets) < connection_num:
            client_socket: socket
            address: Tuple[str, int]
            client_socket, address = self.server_socket.accept()

            self.event_client_connected.trigger(self, ClientConnectedEventArgs(address[0], address[1]))
            self.client_sockets.append(client_socket)

            t: Thread = Thread(target=self.thread_listen, args=(client_socket, len(self.client_sockets) - 1))
            self.connection_threads.append(t)
            t.start()

        self.event_full_connections.trigger(self, event.EventArgs())

    def send_msg(self, msg: str, sock_num: int) -> None:
        """Send a message msg to one of the clients specified by sock_num."""

        byte_msg: bytes = bytes(msg.encode("utf-8"))
        msg_head_len_str: str = str(len(byte_msg)).zfill(msg_header_max_len)
        msg_head: bytes = bytes(f"HEAD {msg_head_len_str}:".encode("utf-8"))
        combined_msg: bytes = msg_head + byte_msg
        self.client_sockets[sock_num].send(combined_msg)

    def thread_listen(self, s: socket, sock_num: int) -> None:
        """Thread function used for listening on each socket."""

        while self.running:
            header: str = s.recv(6 + msg_header_max_len).decode("utf-8")
            if len(header) == 0:
                self.event_client_disconnected.trigger(self, ClientDisconnectedEventArgs(sock_num))
                break
            msg_len: int = int(header[5:12])
            msg: str = s.recv(msg_len).decode("utf-8")
            self.event_received_message.trigger(self, MessageReceivedEventArgs(msg, sock_num))


class Client:
    """Class used to connect to the Server class from the same file."""

    def __init__(self) -> None:
        self.client_socket: socket = socket(AF_INET, SOCK_STREAM)

    def connect(self, ip_addr: str) -> None:
        """Connect to the IP address specified as argument. The port is a constant in the file."""

        self.client_socket.connect((ip_addr, port))

    def send_msg(self, msg: str) -> None:
        """Sends a message with a header telling the server how many bytes the message is. (ex. HEAD 0000002:hi)"""

        byte_msg: bytes = bytes(msg.encode("utf-8"))
        msg_head_len_str: str = str(len(byte_msg)).zfill(msg_header_max_len)
        msg_head: bytes = bytes(f"HEAD {msg_head_len_str}:".encode("utf-8"))
        combined_msg: bytes = msg_head + byte_msg

        self.client_socket.send(combined_msg)

    def recv_msg(self) -> str:
        """Receive message from server."""

        header: str = self.client_socket.recv(6 + msg_header_max_len).decode("utf-8")
        msg_len: int = int(header[5:12])
        msg: str = self.client_socket.recv(msg_len).decode("utf-8")
        return msg
