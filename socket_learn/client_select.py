#encoding: utf-8
import socket
import time

server = ("192.168.196.136",8888)
msg = ["hello","2323","sdsds","3232ddfd","lili"]
socks = []

for i in range(10):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.append(sock)
for s in socks:
    s.connect(server)
# sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# sock.connect(server)
_counter = 0
for m in msg:
    for s in socks:
        s.send("%d send %s".format(_counter,m).encode())
        _counter += 1
    for s in socks:
        data = s.recv(1024).decode()
        print("%s echo: %s"%(s.getpeername(),data))
        if not data:
            s.close()
    time.sleep(2)



