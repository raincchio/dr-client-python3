#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author: chenxing raincchio@gmail.com
import socket, struct, time
from hashlib import md5
import sys
import random
import datetime

# CONFIG
server = '10.100.61.3'
username=''#用户名
password=''#密码
host_ip = '10.151.162.24'#ip地址
mac = 0x342EB752ED47 #mac地址  342EB752ED47
host_name = 'rainchio'#计算机名
host_os = 'Windows 10'#操作系统
CONTROLCHECKSTATUS = b'\x20'
ADAPTERNUM = b'\x03'
IPDOG = b'\x01'
PRIMARY_DNS = '10.10.10.10'
dhcp_server = '0.0.0.0'
AUTH_VERSION = b'\x68\x00'
KEEP_ALIVE_VERSION = b'\xdc\x02'
# CONFIG_END

bind_ip = host_ip


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((bind_ip, 61440))
s.settimeout(3)
SALT = ''

# specified fields based on version

def log(*args):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' '.join(args))


def UDP_Verify(svr,ran):
    data = None
    while True:
        t = struct.pack("<H", int(ran)%(0xFFFF))
        s.sendto(b'\x01\x02'+t+b"\x09"+b"\x00"*15, (svr, 61440))
        try:
            data, address = s.recvfrom(1024)
            log('[UDP_Verify] recv data')
        except:
            log('[UDP_Verify] timeout, retrying...')
            continue
        
        if address == (svr, 61440):
            break
        else:
            continue

    if data[0] != 2:
        log('[UDP_Verify] UDP_error.')
    log('[UDP_Verify] UDP_Verify packet sent.')
    return bytes(data[4:8])

def md5sum(s):
    m = md5()
    m.update(s)
    return m.digest()

def dump(n):
    s = '%x' % n
    if len(s) & 1:
        s = '0' + s
    return bytes.fromhex(s)

def ror(md5, pwd):
    ret = []
    for i in range(len(pwd)):
        x = md5[i] ^ ord(pwd[i])
        ret.append(((x<<3)&0xFF) + (x>>5))
    return bytes(ret)

def keep_alive_package_builder(number,random,tail,type=1,first=False):
    data = b'\x07'+ bytes([number])+ b'\x28\x00\x0b' + bytes([type])
    if first :
        data += b'\x0f\x27'
    else:
        data += KEEP_ALIVE_VERSION
    data += b'\x2f\x12' + b'\x00' * 6
    data += tail
    data += b'\x00' * 4
    #data += struct.pack("!H",0xdc02)
    if type == 3:
        foo = bytes([int(i) for i in host_ip.split('.')])
        crc = b'\x00' * 4
        data += crc + foo + b'\x00' * 8
    else:
        data += b'\x00' * 16
    return data


def keep_alive2(*args):
    #first keep_alive:
    #number = number (mod 7)
    #status = 1: first packet user sended
    #         2: first packet user recieved
    #         3: 2nd packet user sended
    #         4: 2nd packet user recieved
    #   Codes for test
    tail = ''
    packet = ''
    svr = server
    ran = random.randint(0,0xFFFF)
    ran += random.randint(1,10)   
    # 2014/10/15 add by latyas, maybe svr sends back a file packet
    svr_num = 0
    packet = keep_alive_package_builder(svr_num,dump(ran),b'\x00'*4,1,True)
    while True:
        log('[keep-alive2] send1 pkt')
        s.sendto(packet, (svr, 61440))
        data, address = s.recvfrom(1024)
        log('[keep-alive2] recv1 data')
        if data.startswith(b'\x07\x00\x28\x00') or data.startswith(b'\x07' + bytes([svr_num]) + b'\x28\x00'):
            break
        elif data[0] == 7 and data[2] == 16:
            log('[keep-alive2] recv file, resending..')
            svr_num = svr_num + 1
            packet = keep_alive_package_builder(svr_num,dump(ran),b'\x00'*4,1, False)
        else:
            log('[keep-alive2] recv1/unexpected data ')
    #log('[keep-alive2] recv1',data.encode('hex'))
    
    ran += random.randint(1,10)   
    packet = keep_alive_package_builder(svr_num, dump(ran),b'\x00'*4,1,False)
    log('[keep-alive2] send2 pkt')
    s.sendto(packet, (svr, 61440))
    while True:
        data, address = s.recvfrom(1024)
        if data[0] == 7:
            svr_num = svr_num + 1
            break
        else:
            log('[keep-alive2] recv2/unexpected data',data)
    log('[keep-alive2] recv2 data')
    tail = data[16:20]
    

    ran += random.randint(1,10)   
    packet = keep_alive_package_builder(svr_num,dump(ran),tail,3,False)
    log('[keep-alive2] send3 pkt')
    s.sendto(packet, (svr, 61440))
    while True:
        data, address = s.recvfrom(1024)
        if data[0] == 7:
            svr_num = svr_num + 1
            break
        else:
            log('[keep-alive2] recv3/unexpected',data)
    log('[keep-alive2] recv3 data')
    tail = data[16:20]
    log("[keep-alive2] keep-alive2 loop was in daemon.")
    
    i = svr_num
    while True:
        try:
            ran += random.randint(1,10)   
            packet = keep_alive_package_builder(i,dump(ran),tail,1,False)
            #log('DEBUG: keep_alive2,packet 4\n',packet.encode('hex'))
            log('[keep_alive2] send data')
            s.sendto(packet, (svr, 61440))
            data, address = s.recvfrom(1024)
            log('[keep_alive2] recv data')
            tail = data[16:20]
            #log('DEBUG: keep_alive2,packet 4 return\n',data.encode('hex'))
        
            ran += random.randint(1,10)   
            packet = keep_alive_package_builder(i+1,dump(ran),tail,3,False)
            #log('DEBUG: keep_alive2,packet 5\n',packet.encode('hex'))
            s.sendto(packet, (svr, 61440))
            log('[keep_alive2] send pkt')
            data, address = s.recvfrom(1024)
            log('[keep_alive2] recv data ')
            tail = data[16:20]
            #log('DEBUG: keep_alive2,packet 5 return\n',data.encode('hex'))
            i = (i+2) % 0xFF
            time.sleep(20)
            keep_alive1(*args)
        except:
            pass

def checksum(s):
    ret = 1234
    for i in range(len(s)//4):
        ret ^= int(bytes(s[4*i:4*i+4][::-1]).hex(), 16)
    ret = (1968 * ret) & 0xffffffff
    return struct.pack('<I', ret)

def mkpkt(salt, usr, pwd, mac):
    data = b'\x03\x01\x00'+chr(len(usr)+20).encode()
    data += md5sum(b'\x03\x01'+salt+pwd.encode())
    data += usr.encode().ljust(36, b'\x00')
    data += CONTROLCHECKSTATUS
    data += ADAPTERNUM
    data += dump(int(data[4:10].hex(),16)^mac).rjust(6,b'\x00') #mac xor md51
    data += md5sum(b"\x01" + pwd.encode() + salt + b'\x00'*4) #md52
    data += b'\x01' # number of ip
    #data += '\x0a\x1e\x16\x11' #your ip address1, 10.30.22.17
    data += bytes([int(i) for i in host_ip.split('.')])  #x.x.x.x ->
    data += b'\00'*4 #your ipaddress 2
    data += b'\00'*4 #your ipaddress 3
    data += b'\00'*4 #your ipaddress 4
    data += md5sum(data + b'\x14\x00\x07\x0b')[:8] #md53
    data += IPDOG
    data += b'\x00'*4 #delimeter
    data += host_name.encode().ljust(32, b'\x00')
    data += bytes([int(i) for i in PRIMARY_DNS.split('.')]) #primary dns
    data += bytes([int(i) for i in dhcp_server.split('.')]) #DHCP server
    data += b'\x00\x00\x00\x00' #secondary dns:0.0.0.0
    data += b'\x00' * 8 #delimeter
    data += b'\x94\x00\x00\x00' # unknow
    data += b'\x06\x00\x00\x00' # os major
    data += b'\x02\x00\x00\x00' # os minor
    data += b'\xf0\x23\x00\x00' # OS build
    data += b'\x02\x00\x00\x00' #os unknown
    data += b'\x44\x72\x43\x4f\x4d\x00\xcf\x07\x68'
    data += b'\x00' * 55#unknown string
    data += b'\x33\x64\x63\x37\x39\x66\x35\x32\x31\x32\x65\x38\x31\x37\x30\x61\x63\x66\x61\x39\x65\x63\x39\x35\x66\x31\x64\x37\x34\x39\x31\x36\x35\x34\x32\x62\x65\x37\x62\x31'
    data += b'\x00' * 24
    data += AUTH_VERSION
    data += b'\x00' + bytes([len(pwd)])
    data += ror(md5sum(b'\x03\x01'+salt+pwd.encode()), pwd)
    data += b'\x02\x0c'
    data += checksum(data+b'\x01\x26\x07\x11\x00\x00'+dump(mac))
    data += b'\x00\x00' #delimeter
    data += dump(mac)

    data += b'\x00' * (len(pwd) // 4)#strange。。。
    data += b'\x60\xa2' #unknown, filled numbers randomly =w=
    data += b'\x00' * 28
    return data

def login(usr, pwd, svr):
    import random
    global SALT
 
    i = 0
    while True:
        salt = UDP_Verify(svr,time.time()+random.randint(0xF,0xFF))
        SALT = salt
        packet = mkpkt(salt, usr, pwd, mac)
        log('[login] send mkpkt')
        s.sendto(packet, (svr, 61440))
        data, address = s.recvfrom(1024)
        log('[login] recv dt')
        log('[login] packet sent.')
        if address == (svr, 61440):
            if data[0] == 4:
                log('[login] loged in')
                break
            else:
                log('[login] login failed.')
                time.sleep(10)
                continue
        else:
            if i >= 5:
                log('[login] exception occured.')
                sys.exit(1)
            else:
                continue
            
    log('[login] login sent')
    return data[23:39]


def keep_alive1(salt,tail,pwd,svr):
    foo = struct.pack('!H',int(time.time())%0xFFFF)
    data = b'\xff' + md5sum(b'\x03\x01'+salt+pwd.encode()) + b'\x00\x00\x00'
    data += tail
    data += foo + b'\x00\x00\x00\x00'
    log('[keep_alive1] send')

    s.sendto(data, (svr, 61440))
    while True:
        data, address = s.recvfrom(1024)
        if data[0] == 7:
            break
        else:
            log('[keep-alive1]recv/not expected')
    log('[keep-alive1] recv data')

def empty_socket_buffer():
    log('starting to empty socket buffer')
    try:
        while True:
            data, address = s.recvfrom(1024)
            log('recived sth unexpected',data.encode('hex'))
            if s == '':
                break
    except:
        log('no more buffer')
        pass
    log('emptyed')

        
def main():
    log("auth svr:"+server+"\nusername:"+username+"\npassword:"+password+"\nmac:"+str(hex(mac)))
    log(bind_ip)
    while True:
        package_tail = login(username, password, server)
        empty_socket_buffer()
        keep_alive1(SALT,package_tail,password,server)
        keep_alive2(SALT,package_tail,password,server)


if __name__ == "__main__":
    main()
