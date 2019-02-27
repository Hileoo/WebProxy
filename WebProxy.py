from socket import *

# Create a server socket, bind it to a port and start listening
server_port = 8000  # Define a server_port by User
tcp_server_sock = socket(AF_INET, SOCK_STREAM)

# Prepare a server socket
tcp_server_sock.bind(('', server_port))  # Use local IP
tcp_server_sock.listen(1)   # TCP the size of the connection queue, that is, the number of connections.

while 1:
    # Start receiving data from the client
    print('Ready to serve...')
    tcp_client_sock, addr = tcp_server_sock.accept()
    print('Received a connection from:', addr)

    message = tcp_client_sock.recv(1024).decode()

    print(message)

    # Extract the filename
    print(message.split()[1])
    filename = message.split()[1].partition("/")[2]
    print(filename)

    file_exist = "false"

    try:
        # Check whether the file exist in the cache
        f = open(filename, "r")
        output_content = f.readlines()
        file_exist = "true"
        print("The file exists")

        # ProxyServer finds a cache hit and generates a response message
        tcp_client_sock.send(b"HTTP/1.1 200 OK\r\n")
        tcp_client_sock.send(b"Content-Type:text/html\r\n\r\n")

        # Send the output content of the requested message to the client
        for i in range(0, len(output_content)):
            tcp_client_sock.send(output_content[i].encode())

        print("Read from cache")

    # Error handling for file not found in cache
    except IOError:
        if file_exist == "false":
            # Create a socket on the proxy server
            proxy_client_socket = socket(AF_INET, SOCK_STREAM)

            host_name = filename.replace("www.", "", 1)
            print("The host name is: ", host_name)

            try:
                # Connect to the socket to port 80
                proxy_client_socket.connect((host_name, 80))

                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                file_obj = proxy_client_socket.makefile(mode='w')
                file_obj.write("GET / HTTP/1.1\r\nHost:" + host_name + "\r\nConnection: close\r\n\r\n")

                # Read the response into buffer
                file_obj = proxy_client_socket.makefile(mode='r')
                buffer = file_obj.readlines()
                end = []

                for line in buffer:
                    l_obj = line.replace('href="/', 'href="http://' + filename + '/')
                    l_obj = l_obj.replace('src="/', 'href="http://' + filename + '/')
                    end.append(l_obj)

                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                tmp_file = open(filename+'.html', "wb")
                for i in end:
                    tmp_file.write(i.encode())
                    tcp_client_sock.send(i.encode())
                proxy_client_socket.close()

            except:
                print('Illegal request')
        else:
            # HTTP response message for file not found
            tcp_client_sock.send(b'HTTP/1.1 404 Not Found\r\n\r\n<html><body>404 Not Found</body></html>')

    # Close the client and the server sockets
    tcp_client_sock.close()
