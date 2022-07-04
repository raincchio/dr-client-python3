from tkinter import *
import socket
import threading
import time
####
ip = '127.0.0.1'
port = 9856
cl = None
auto_send = True
block_time = 15

total_status = True
####


def receive_message():

    global auto_send
    while True:
        data = cl.recv(1024).decode("utf-8")
        if '已限制' in data:
            auto_send = False
            deal_status.set('已限制')
            text.insert('end', '交易状态受限...\n')
            text.see('end')
        else:
            auto_send = True
            deal_status.set('未限制')
            text.insert('end', data)
            text.see('end')


def connectServer(event):
    global cl,total_status
    total_status = True
    if cl is None:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((ip, port))
        except:
            text.insert('end', '服务器未启动!\n')
            text.see('end')
            return
        cl = client
        text.insert('end', '已成功连接服务器...\n')
        text.see('end')
    b3.bind('<Button-1>', func=stopclient)
    client_status.set('停止')
    t = threading.Thread(target=receive_message)
    t.start()

def stopclient(event):
    global cl, total_status
    cl = None
    total_status = False
    text.insert('end', '已停止服务...\n')
    text.see('end')
    b3.bind('<Button-1>', func=connectServer)
    client_status.set('启动')

def make_a_deal(event):
    while '已限制' in deal_status.get() or deal_num.get() == '0':
        text.insert('end', '交易状态受限...')
        text.see('end')
        time.sleep(block_time)

    if cl is None:
        text.insert('end', '客户端未启动!\n')
        text.see('end')
        return
    cl.send((str(deal_num.get())+'a').encode("utf-8"))
    text.insert('end', '状态正常，手动发送：'+str(deal_num.get())+'\n')
    text.see('end')


def auto_make_deal(event):
    global auto_send
    while '已限制' in deal_status.get() or deal_num_auto.get() == '0':
        text.insert('end', '交易状态受限...')
        text.see('end')
        time.sleep(block_time)
    if cl is None:
        text.insert('end', '客户端未启动!\n')
        text.see('end')
        return
    b2.bind('<Button-1>', func=end_send)
    auto_deal_status.set('交易中')
    auto_send = True

    t = threading.Thread(target=auto_send_method, args=((str(deal_num_auto.get())+'a'),))
    t.start()


def end_send(event):
    global auto_send
    auto_send = False
    b2.bind('<Button-1>',func=auto_make_deal)
    auto_deal_status.set('自动交易')
    text.insert('end', '已取消自动交易发送！\n')
    text.see('end')


def auto_send_method(v):
        while total_status:
            while auto_send is False:
                time.sleep(1)
            if total_status is False:
                return
            cl.send(v.encode("utf-8"))
            text.insert('end', '状态正常,自动发送：' + str(deal_num_auto.get())+'\n')
            text.see('end')
            time.sleep(int(deal_interval.get()))
        end_send('5')


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

    ip_t.set('127.0.0.1')
    port_t.set(9856)

    Button(t, text="确定", command=lambda: create_config(t,ip_t,port_t)).place(x=60,y=50)
    Button(t, text="取消", command=t.destroy).place(x=120,y=50)


def create_config(t,ip_t,port_t):
    global ip,port
    ip = ip_t.get()
    port = int(port_t.get())
    text.insert('end','参数已更新！\n')
    text.see('end')
    t.destroy()
#################
cilent = Tk()
cilent.title("客户端")
cilent.geometry("400x500")
menubar = Menu(cilent)

menubar.add_command(label='配置', command=lambda :create_window(menubar))
menubar.add_command(label='退出', command=cilent.quit)

cilent.config(menu=menubar)

frame1 =LabelFrame(cilent,height=300,width=400,text='客户端')

Label(frame1, text='交易额:',bd=3).place(x=0,y=0)
deal_num = Variable()
Entry(frame1, textvariable=deal_num,bd=3).place(x=60,y=0,width=30)
b1 = Button(frame1, text='手动交易',bd=3)
b1.place(x=100, y=0, height=25)
b1.bind('<Button-1>',func=make_a_deal)

Label(frame1, text='交易额:',bd=3).place(x=0,y=100)
deal_num_auto = Variable()
Entry(frame1, textvariable=deal_num_auto,bd=3).place(x=50,y=100,width=30)
Label(frame1, text='交易间隔:(s)',bd=3).place(x=80,y=100)
deal_interval = Variable()
Entry(frame1, textvariable=deal_interval,bd=3).place(x=150,y=100,width=30)
auto_deal_status = Variable()
b2 = Button(frame1, textvariable=auto_deal_status,bd=3)
b2.place(x=180, y=100, height=25)
b2.bind('<Button-1>',func=auto_make_deal)
auto_deal_status.set('自动交易')

Label(frame1, text='交易状态:',bd=3).place(x=0, y=200)
deal_status = Variable()
Label(frame1, textvariable=deal_status,bd=3).place(x=60,y=200)

deal_num.set(1)
deal_num_auto.set(1)
deal_interval.set(1)
deal_status.set('未限制')
client_status = Variable()
b3 = Button(frame1, textvariable=client_status,bd=3)
b3.place(x=180, y=200, height=25)
b3.bind('<Button-1>',func=connectServer)
client_status.set('启动')
frame1.place(x=0,y=0)
frame2 =LabelFrame(height=200,width=400,text='状态')
text = Text(frame2,height=13,width=56)
text.pack()

frame2.place(x=0, y=300)
#################
cilent.mainloop()
