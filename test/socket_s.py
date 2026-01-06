import socket
listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listening_socket.bind(("127.0.0.1",5000))
listening_socket.listen()

while True:
    communication_socket, address = listening_socket.accept()
    print("Connetcted by ", address)
    data = communication_socket.recv(1024)
    if data:
        print("received data:",data)
        communication_socket.sendall(bytes(reversed(data)))
    else:
        print("Error!")
    communication_socket.close
listening_socket.close()