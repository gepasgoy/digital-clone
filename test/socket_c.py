import socket

while True:
    send_data = input("Enter data:")
    client_cocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_cocket.connect(("127.0.0.1",5000))

    client_cocket.sendall(bytes(send_data, "utf-8"))
    data = client_cocket.recv(1024)

    print("received:", repr(data))
    
client_cocket.close()