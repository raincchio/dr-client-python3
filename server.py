from tkinter import *
import socket
import threading
import queue
import time
###########################
users = {}
max_con = 10
root_st = False
max_deal = 3000
limited_deal = 20
limited_deal_max = 200
limited_deal_min = 100
mutex = threading.Lock()
wait_queue = queue.Queue(max_deal)
server = None
ip = '127.0.0.1'
port = 9856
server_status = False
process_status = False
block_time = 15
deal_of_block = 50
################
###########################
def create_window(par):
    t = Toplevel(par)
    t.wm_title('配置')
    t.geometry("220x220")

    Label(t, text='ip:').place(x=0, y=0)
    ip_t = Variable()
    Entry(t, textvariable=ip_t).place(x=25, y=0, width=100)
    Label(t, text='port:').place(x=135, y=0)
    port_t = Variable()
    Entry(t, textvariable=port_t).place(x=175, y=0, width=40)

    Label(t, text='挂起最大连接数：').place(x=0, y=30)
    max_con_t = Variable()
    Entry(t, textvariable=max_con_t).place(x=110, y=30, width=40)

    Label(t, text='预警值设置：').place(x=0, y=60)
    limited_deal_max_t = Variable()
    Entry(t, textvariable=limited_deal_max_t).place(x=75, y=60, width=40)

    Label(t, text='区块处理间隔(s)：').place(x=0, y=90)
    block_time_t = Variable()
    Entry(t, textvariable=block_time_t).place(x=100, y=90, width=40)
    Label(t, text='单块处理数量：').place(x=0, y=120)
    deal_of_block_t = Variable()
    Entry(t, textvariable=deal_of_block_t).place(x=85,y=120, width=40)

    ip_t.set('127.0.0.1')
    port_t.set(9856)
    max_con_t.set(10)
    limited_deal_max_t.set(200)
    block_time_t.set(15)
    deal_of_block_t.set(50)

    Button(t, text="确定", command=lambda: create_config(t,ip_t,port_t,max_con_t,limited_deal_max_t,block_time_t,deal_of_block_t)).place(x=60,y=170)
    Button(t, text="取消", command=t.destroy).place(x=120,y=170)

def create_detail(par):
    t = Toplevel(par)
    t.wm_title('详细')
    t.geometry("450x600")
    text = Text(t,height=600,width=450)
    text.pack()
    dict_num = {}
    dict_sum = {}
    for item in list(wait_queue.queue):
        item = item.split('b')
        # text.insert('end','时间：'+item[2]+'  '+'地址：127.0.0.1：'+item[0]+'  '+'交易额：'+item[1]+'\n')
        if dict_num.__contains__(item[0]):
            dict_num[item[0]] += 1
            dict_sum[item[0]] += int(item[1])
        else:
            dict_num[item[0]] = 1
            dict_sum[item[0]] = int(item[1])
    for key in dict_num.keys():
        text.insert('end', '地址：127.0.0.1：' + key + ' ' + '交易总数：' + str(dict_num[key]) +' ' + '交易总额：' + str(dict_sum[key]) + '\n')
        text.see('end')







def create_config(t,ip_t,port_t,max_con_t,limited_deal_max_t,block_time_t,deal_of_block_t):
    global ip,port,max_con,limited_deal_max,block_time,deal_of_block
    ip = ip_t.get()
    port = int(port_t.get())
    max_con = int(max_con_t.get())
    limited_deal_max = int(limited_deal_max_t.get())
    warning_value.set(limited_deal_max)
    block_time = int(block_time_t.get())
    deal_of_block = int(deal_of_block_t.get())

    text.insert('end','参数已更新！\n')
    text.see('end')
    t.destroy()


def end(event):
    global server_status,process_status
    server_status = False
    end_process('5')
    log = "服务器已停止,不再处理和接收交易\n"
    b_status.set('启动')
    bb.bind('<Button-1>', func=left_click)
    text.insert('end', log)
    text.see('end')


def end_process(event):
    global process_status
    process_status = False
    log = "服务器停止处理交易\n"
    b_status_process.set('处理交易')
    bb2.bind('<Button-1>', func=left_click_process)
    text.insert('end', log)
    text.see('end')


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def run(sock, addr):
    users[addr[1]] = sock
    log = addr[0] + str(addr[1]) + "连接\n"
    text.insert('end', log)

    while True:
        deal_num = sock.recv(1024).decode("utf-8").split('a')[0]
        while wait_queue.qsize() >= limited_deal_max:
            is_limited.set('已限制')
            sock.send('已限制'.encode('utf-8'))
            time.sleep(block_time)
            # if wait_queue.qsize() <= limited_deal_min:
            #     is_limited.set('未限制')
            #     sock.send('未限制'.encode('utf-8'))
            #     flag = False

        text.insert('end', '已接收来自'+addr[0] + str(addr[1])+'的交易:'+str(deal_num)+'额度 '+'\n')
        text.see('end')
        mutex.acquire()
        wait_to_deal.set(wait_to_deal.get()+1)
        wait_queue.put(str(addr[1])+'b'+str(deal_num)+'b'+get_time()+'b'+addr[0])
        mutex.release()
        is_limited.set('未限制')


def start():
    log = "服务器启动成功，开始接收交易\n"
    b_status.set('停止')
    bb.bind('<Button-1>', func=end)
    text.insert('end', log)
    global server
    if server is None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen(2)
    global server_status
    server_status = True
    while server_status:
        sock, addr = server.accept()
        t = threading.Thread(target=run, args=(sock, addr))
        t.daemon = True
        t.start()


def queue_list(root):
    t = threading.Thread(target=create_detail, args=(root,))
    t.daemon = True
    t.start()

def block_control():

    while process_status:

        block_num.set(int(block_num.get())+1)
        mutex.acquire()
        n = int(wait_to_deal.get())
        deal_num = n if n < deal_of_block else deal_of_block
        dealed.set(int(dealed.get()) + deal_num)
        wait_to_deal.set(wait_to_deal.get() - deal_num)
        mutex.release()
        for u in range(deal_num):
            info = wait_queue.get().split('b')
            try:
                users[int(info[0])].send(('已处理'+info[2]+'发送的'+str(info[1])+'额度交易！\n').encode('utf-8'))
            except:
                pass
            text.insert('end', '已处理' + "127.0.0.1:" + str(info[0]) + '的交易:' + str(info[1]) + '额度 ' + '\n')
            text.see('end')
        time.sleep(block_time)


def left_click_process(event):
    global process_status
    process_status = True
    if server_status:
        log = "开始处理交易\n"
        b_status_process.set('停止处理')
        bb2.bind('<Button-1>', func=end_process)
        text.insert('end', log)
        text.see('end')
        b = threading.Thread(target=block_control)
        b.daemon = True
        b.start()
    else:
        log = "服务器未启动\n"
        text.insert('end', log)
        text.see('end')



def left_click(event):
    t = threading.Thread(target=start)
    t.daemon = True
    t.start()



###########################
root = Tk()  # 创建主窗口
root.title('模拟区块链')
root.geometry("400x500")

menubar = Menu(root)

menubar.add_command(label='配置', command=lambda: create_window(menubar))
menubar.add_command(label='退出', command=root.quit)

root.config(menu=menubar)
frame1 = LabelFrame(root,height=300,width=400,text='控制')
Label(frame1, text='待处理交易:').place(x=0,y=0)

bb3 = Button(frame1, text='交易明细', command=lambda: queue_list(root))
bb3.place(x=0,y=20)


wait_to_deal = Variable()
Label(frame1, textvariable=wait_to_deal).place(x=70,y=0)
Label(frame1, text='已处理交易:').place(x=200,y=0)
dealed = Variable()
Label(frame1, textvariable=dealed).place(x=270,y=0)
Label(frame1, text='当前区块数:').place(x=0,y=100)
block_num = Variable()
Label(frame1, textvariable=block_num).place(x=70,y=100)
Label(frame1, text='预警值设置:').place(x=200,y=100)
warning_value = Variable()
Label(frame1, textvariable=warning_value).place(x=270,y=100)
Label(frame1, text='交易状态:').place(x=0,y=200)
is_limited = Variable()
Label(frame1, textvariable=is_limited).place(x=60,y=200)
b_status = Variable()
bb = Button(frame1, textvariable=b_status)
bb.place(x=200,y=200)
b_status_process = Variable()
bb2 = Button(frame1, textvariable=b_status_process)
bb2.place(x=280,y=200)
wait_to_deal.set(0)
dealed.set(0)
block_num.set(0)
warning_value.set(limited_deal_max)
is_limited.set('未限制')
b_status.set('启动服务器')
b_status_process.set('处理交易')
frame1.place(x=0,y=0)
frame2 =LabelFrame(height=50,width=400,text='状态')
text = Text(frame2,height=13,width=56)
text.pack()
frame2.place(x=0, y=300)
bb.bind('<Button-1>', func=left_click)
bb2.bind('<Button-1>', func=left_click_process)

root.mainloop()