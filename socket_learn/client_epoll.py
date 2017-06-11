#encoding:utf-8
import socket

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_address = ('192.168.196.136',8888)
client_socket.connect(server_address)

while True:

    data = input("please input:")
    client_socket.sendall(data.encode())
    server_data = client_socket.recv(1024).decode()
    print("客户端收到的数据：",server_data)

client_socket.close()
