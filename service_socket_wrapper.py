#!/usr/bin/env python3

# Talks to a service through a TCP socket

import sys
import socket


# TCP socket
SOCKET_ADDRESS = "127.0.0.1"
SOCKET_PORT = 5555
SOCKET_SOCKET = (SOCKET_ADDRESS, SOCKET_PORT)

BUF_SIZE = 4096

# Non-terminal response status codes (mean more responses will follow)
NON_TERMINAL_CODES = ["301", "401", "501"]


def decode_bytes(my_bytes):
    my_string = my_bytes.decode('utf-8')
    return my_string

# Get all of the response codes returned after you run a command
def get_response_code_list(my_response_split):
    my_response_code_list = []
    for r in my_response_split:
        if r != "":
            response_splitspaces = r.split(" ")
            response_code = response_splitspaces[0]
            my_response_code_list.append(response_code)
    return my_response_code_list

# Check if any of the response codes are terminal
# A terminal and non-terminal code could appear together, so checking for
# a non-terminal code is not helpful
def terminal_response(my_response_list):
    for c in my_response_list:
        if c not in NON_TERMINAL_CODES:
            return True
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 service_socket_wrapper.py <license_product_id>")
        return 1

    product_id = sys.argv[1]

    # Connect to service through socket
    client = socket.socket(socket.AF_INET)
    client.settimeout(10)
    client.connect(SOCKET_SOCKET)
    read = client.recv(BUF_SIZE)
    print(decode_bytes(read))

    # Set product ID from license to activate the service
    command = "SET PRODUCT {}\n".format(product_id)
    client.send(command.encode('utf-8'))
    read = client.recv(BUF_SIZE)
    print(decode_bytes(read))

    print("Enter commands. Type QUIT to quit.")

    # Outer loop: each iteration is a command entered and sent
    while True:
        print("Ready to receive input")
        command = input()
        print("Command: {}".format(command))

        # Checking the most likely condition first saves CPU cycles, and
        # therefore the environment :)
        if command == "":
            print("No command entered")
        elif command == "QUIT":
            break
        else:
            # Send command to service and print output
            client.send(("{}\n".format(command).encode('utf-8')))

            # Inner loop: each iteration reads from the buffer
            # May only read once, or may need to keep reading until a terminal
            # response code appears
            while True:
                print("Reading from buffer")
                read = client.recv(BUF_SIZE)
                response_string = decode_bytes(read)
                print("Response: {}".format(response_string))

                response_splitlines = response_string.split("\n")
                response_code_list = get_response_code_list(response_splitlines)

                # Service closes connection on invalid command
                if "350" in response_code_list:
                    print("Invalid command")
                    break

                # If anything in the response list is terminal ("not non
                # terminal"), it's done, break
                if terminal_response(response_code_list):
                    break

    try:
        print("Closing connection to service")
        client.shutdown(socket.SHUT_RDWR)
        print("Connection to service closed")
    # The service may have already closed the connection
    except socket.error:
        print("Connection to service closed")

    client.close()

if __name__ == "__main__":
    main()
