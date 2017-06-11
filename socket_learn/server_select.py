#encoding: utf-8
import socket
import select
import queue



server = ('192.168.196.136',9223)

#socket.AF_INET:ipv4  socket.SOCK_STREAM:TCP协议 SOCK_DGRAM:UDP协议
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setblocking(False) #设置阻塞方式为False
#设置服务端的端口为复用的，等等 参考unix网络编程的书籍
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(server)   #绑定端口号
sock.listen(10)  #5监听请求数
# conn,address = sock.accept()    #返回值，返回建立链接的对象和地址对象
rlists = [sock]
wlists = [] #写的集合
msg_que = {} #消息队列
timeout = 20 #select的超时时间
# print("connect by",address)

while rlists: #如果读得列表始终有值，进行一个循环操作
    #可读可写异常的文件描述符的定义 如果select超过这个时间会返回三个空列表
    rs,ws,es = select.select(rlists,wlists,rlists,timeout)
    if not (rs or ws or es):
        print("timeout")
        continue
    #表示可读的文件描述符已经准备好了，可以进行相关的连接操作了
    for s in rs:
        if s is sock:
            conn,addr = s.accept()
            print("connect by", addr)
            conn.setblocking(False) #设置socket对象为非阻塞状态
            rlists.append(conn)
            msg_que[conn]=queue.Queue()  #初始化一个消息队列
        else:
            data = s.recv(1024).decode()  # 设置缓冲区大小1024
            if data:
                print("recived",data,"form",s.getpeername())
                msg_que[s].put(data)
                if s not in wlists:
                    wlists.append(s)
            else:               #如果没有数据发送过来 就进行close操作
                print("closing",addr)
                if s in wlists:
                    wlists.remove(s)
                rlists.remove(s)
                s.close()   #现close再删除
                del msg_que[s]

    for s in ws:
        try:
            msg = msg_que[s].get_nowait()
        except queue.Empty:
            print('msg empty',s.getpeername())
            wlists.remove(s)
        else:
            s.send(msg.encode())

    for s in es:
        print("execpt",s.getpeername())
        if s in rlists:
            rlists.remove(s)
        if s in wlists:
            wlists.remove(s)
        s.close()
        del msg_que[s]

#
#     if not data:
#         break
#     else:
#         print(data)
#         conn.send(data.encode()) #写操作  回显数据
# sock.close() #释放资源 释放端口号



