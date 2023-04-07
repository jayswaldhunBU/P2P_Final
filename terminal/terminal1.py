import socket
import threading
import sqlite3

HOST = '127.0.0.1'
PORT = 65432

# Create the socket and bind it to a specific address and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Connect to the database
conn = sqlite3.connect('chat.db')
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              sender TEXT,
              receiver TEXT,
              message TEXT)''')

# Function to send messages
def send_message(client_socket):
    while True:
        message = input('')
        receiver = input('To: ')

        # Save the message to the database
        c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                  ('Me', receiver, message))
        conn.commit()

        # Send the message to the recipient
        client_socket.sendall(message.encode())

# Function to receive messages
def receive_message(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        # Save the message to the database
        c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                  (client_address[0], 'Me', data.decode()))
        conn.commit()

        # Print the received message on both terminals
        print(f'Received: {data.decode()}')
        print('From:', client_address[0])

# Accept incoming connections
while True:
    client_socket, client_address = server_socket.accept()

    # Check if the other terminal is available for chat
    client_socket.sendall('Are you available for chat? (y/n)'.encode())
    response = client_socket.recv(1024).decode()
    if response.lower() != 'y':
        client_socket.close()
        continue

    # Start the send and receive threads
    send_thread = threading.Thread(target=send_message, args=(client_socket,))
    receive_thread = threading.Thread(target=receive_message, args=(client_socket,))
    send_thread.start()
    receive_thread.start()
