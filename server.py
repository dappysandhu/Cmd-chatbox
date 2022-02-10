import socket
import select

HEADER_LENGTH = 15

IP = "127.0.0.1"
PORT = 1200

# Creating a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setting REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind is used to tell OS to use given port and ip
server_socket.bind((IP, PORT))

#server listening to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# It Handles message receiving
def receive_message(client_socket):

    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client closed a connection
        if not len(message_header):
            return False

        # Converting header into int value
        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If client closed connection it will shutdown socket
        return False

while True:

        # It is a blocking call
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            # Client disconnected before sending name
            if user is False:
                continue

            # Add accepted socket to select.select()
            sockets_list.append(client_socket)

            # Save username and username header
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup data
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            for client_socket in clients:

                if client_socket != notified_socket:

                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # To handle socket exceptions
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]