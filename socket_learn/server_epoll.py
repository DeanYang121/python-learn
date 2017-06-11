#encoding:utf-8
import socket
import select
import queue

serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server_address = ("192.168.196.136",8888)
serversocket.bind(server_address)

serversocket.listen(10)
print("服务器启动成功，监听ip：",server_address)
serversocket.setblocking(False)
timeout=-1

epoll = select.epoll()
epoll.register(serversocket.fileno(),select.EPOLLIN)
#保存链接客户端消息的字典，格式位{}
message_queue = {}
#保存文件句柄到所对应对象的字典，格式为{句柄：对象}
fd_to_socket = {serversocket.fileno():serversocket,}

while True:
    print("等待活动链接......")
    events = epoll.poll(timeout)
    if not events:
        print("epoll超时连接，重新轮询......")
        continue
    print("有",len(events),"个新事件，开始处理...")

    for fd,event in events:
        socket = fd_to_socket[fd]
        if socket == serversocket:
            connection,address = serversocket.accept()
            print("新连接：",address)
            connection.setblocking(False)
            epoll.register(connection.fileno(),select.EPOLLIN)
            fd_to_socket[connection.fileno()] = connection
            message_queue[connection] = queue.Queue()
            # print("3333")
        elif event & select.EPOLLHUP:
            print("客户端关闭连接")
            epoll.unregister(fd)
            fd_to_socket[fd].close()
            del fd_to_socket[fd]
            # print("22222")
        elif event & select.EPOLLIN:
            # print(11111)
            data = socket.recv(1024).decode()
            if data:
                print("收到数据：",data,"客户端：",socket.getpeername())
                message_queue[socket].put(data)
                epoll.modify(fd,select.EPOLLOUT)
            else:
                print('closing', address, 'after reading no data')
                epoll.unregister(fd)
                fd_to_socket[fd].close()
                del fd_to_socket[fd]
        elif event & select.EPOLLOUT:
            try:
                msg = message_queue[socket].get_nowait()
            except queue.Empty:
                print(socket.getpeername(),"queue empty")
                epoll.modify(fd,select.EPOLLIN)
            else:
                print("发送数据："+data,"客户端：",socket.getpeername())
                socket.send(msg.encode())

epoll.unregister(serversocket.fileno())
epoll.close()
serversocket.close()

