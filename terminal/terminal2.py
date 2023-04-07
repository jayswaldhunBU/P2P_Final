import socket
import threading
import sqlite3

HOST = '127.0.0.1'
PORT = 65432

# Create the socket and connect it to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

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
def send_message():
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
def receive_message():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        # Save the message to the database
        c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                  (HOST, 'Me', data.decode()))
        conn.commit()

        # Print the message on the terminal
        print(f'{HOST}: {data.decode()}')

# Start the send and receive threads
send_thread = threading.Thread(target=send_message)
receive_thread = threading.Thread(target=receive_message)
send_thread.start()
receive_thread.start()
