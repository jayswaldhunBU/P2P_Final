import socket
import threading
import select
import logging
import db
import pytest
import time

# The tests in this file assume that there is a running Registry server
# on the localhost with default port numbers.

# Constants used for testing
REGISTRY_ADDRESS = 'localhost'
REGISTRY_TCP_PORT = 7777
REGISTRY_UDP_PORT = 7778


def connect_to_registry():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((REGISTRY_ADDRESS, REGISTRY_TCP_PORT))
    return client_socket


def register_and_login(username, password):
    # Register
    tcp_socket = connect_to_registry()
    message = f"JOIN {username} {password}"
    tcp_socket.sendall(message.encode())
    response = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    assert response == "join-success"

    # Login
    tcp_socket = connect_to_registry()
    message = f"LOGIN {username} {password} {REGISTRY_UDP_PORT}"
    tcp_socket.sendall(message.encode())
    response = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    assert response == "login-success"


def test_register_and_login():
    # Test that a new user can register and login successfully
    username = "testuser"
    password = "password123"
    register_and_login(username, password)


def test_register_existing_username():
    # Test that an existing username cannot be registered again
    username = "testuser"
    password = "password123"
    tcp_socket = connect_to_registry()
    message = f"JOIN {username} {password}"
    tcp_socket.sendall(message.encode())
    response = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    assert response == "join-exist"


def test_login_nonexisting_username():
    # Test that a non-existing username cannot be logged in
    username = "nonexistinguser"
    password = "password123"
    tcp_socket = connect_to_registry()
    message = f"LOGIN {username} {password} {REGISTRY_UDP_PORT}"
    tcp_socket.sendall(message.encode())
    response = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    assert response == "login-account-not-exist"


def test_login_wrong_password():
    # Test that a user cannot login with the wrong password
    username = "testuser"
    password = "wrongpassword"
    tcp_socket = connect_to_registry()
    message = f"LOGIN {username} {password} {REGISTRY_UDP_PORT}"
    tcp_socket.sendall(message.encode())
    response = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    assert response == "login-wrong-password"


def test_login_already_online():
    # Test that a user cannot login if already online
    username = "testuser"
    password = "password123"
    tcp_socket = connect_to_registry()
    message = f"LOGIN {username} {password} {REGISTRY_UDP_PORT}"
    tcp_socket.sendall(message.encode())
    response = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    assert response == "login-online"


def test_logout():
    # Test that a user can logout successfully
    username = "testuser"
    tcp_socket = connect_to_registry()
    message = f"LOGOUT {username}"
    tcp_socket.sendall(message.encode())
    response = tcp_socket.recv(1024).decode()
    tcp_socket.close()
    assert response == ""


def test_logout_twice():
    # Test that logging out twice does not cause any issues
    username = "test
