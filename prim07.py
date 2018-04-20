#!/usr/bin/python
# -*- encoding: cp1251 -*-
#
import datetime
import serial
import sys
import codecs
from time import sleep

comm_num = "COM3"
ser = None
nx = 0

status = ""
err = ""
prnstatus = ""

flog = open("log.txt", "a")

ch_mapping = {168:240, 184:241, 170:242, 186:243, 175:244, 191:245, 161:246, 162:247, 
              176:248, 149:249, 183:250, 134:251, 135:252, 136:253, 137:254, 177:255}

def ch_encode(ch):
  res = ch
  tmp = ord(ch)
  if tmp >= 240:
    res = chr(tmp - 16)
  elif tmp >= 192 and tmp < 240:
    res = chr(tmp - 64)
  elif tmp in ch_mapping.keys():
    res = chr(ch_mapping[tmp])

  return res

def st_encode(st):
  res = ""
  for x in list(st):
    res = res + ch_encode(x)

  return res
  

def cur_date_log():
  dt = datetime.datetime.now()
  return "%04d%02d%02d%02d%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute )

def control_sum(instr):
  x = 0
  for a in instr:
    x += ord(a)
    #print ord(a)

  s = "%04x" % x
  s = s[:4]
  return s[2:]+s[:2]

def send_command(cmd, dl=0.2):
  global nx
  global status
  global err

  status = ""
  err = ""
  prnstatus = ""

  newstr = "\x02AERF%c%s\x1C\x03" % (chr(32+nx), cmd)
  #print list(newstr+control_sum(newstr))
  print cmd
  flog.write("["+cur_date_log()+"]c:"+str(list(newstr+control_sum(newstr)))+"\n")
  if (ser.isOpen()):
    ser.write(newstr+control_sum(newstr));
    sleep(dl)
    strln = ser.read(50)

    status = strln[8:12]
    err = strln[13:17]
    prnstatus = strln[13:28]
    
    #print list(strln)
    #print strln[2:28], status
    print strln[2:17]
    if status != "":
      print get_status(status,err)
      
    flog.write("["+cur_date_log()+"]a:"+str(list(strln))+"\n")
    nx = nx + 1
    #print nx
    
  return None

def cur_date():
  dt = datetime.datetime.now()
  return "\x1C%02d%02d%02d\x1C%02d%02d" % (dt.day, dt.month, dt.year - 2000, dt.hour, dt.minute )

def send_command_datatime(cmd):

  #newstr = "%s%s" % (cmd, cur_date())
  newstr = cmd + cur_date()
  send_command(newstr)
  return None

def int_list_join(l):
  res = ""
  for i in l:
    res = res + chr(i)
  
  return res

def get_status(st,err):
  tmp = hex_word_str_to_bits(st)
  l = list(tmp)
  r = []
  if tmp[13:]=="000": r.append("bill closed")
  if tmp[13:]=="001": r.append("bill header")
  if tmp[13:]=="010": r.append("bill good")
  if tmp[13:]=="011": r.append("bill total")
  if tmp[13:]=="100": r.append("bill calc")
  if tmp[13:]=="101": r.append("bill end")
  if tmp[13:]=="110": r.append("bill markup")
  if tmp[13:]=="111": r.append("bill random")
  if l[2]=='1': r.append("SQL full") 
  if l[3]=='1': r.append("SQL up to full") 
  if l[4]=='0': r.append("work not begin") 
  if l[5]=='1': r.append("doc buffer up to full") 
  if l[6]=='1': r.append("technical mode") 
  if l[7]=='0': r.append("session not begin") 
  if l[8]=='1': r.append("bad passwod") 
  if l[9]=='1': r.append("command not executed") 
  if l[10]=='1': r.append("bad command") 
  if l[11]=='1': r.append("close work")
  if err[0:2]=='01': r.append("bad message format")
  if err[0:2]=='02': r.append("bad field format")
  if err[0:2]=='03': r.append("bad date")
  if err[0:2]=='04': r.append("bad check summ")
  if err[0:2]=='05': r.append("bad password")
  if err[0:2]=='06': r.append("bad comand")
  if err[0:2]=='07': r.append("begin sesion missed")
  if err[0:2]=='08': r.append("working more 24 hours")
  if err[0:2]=='09': r.append("to long string")
  if err[0:2]=='0A': r.append("to long message")
  if err[0:2]=='0B': r.append("bad operation")
  if err[0:2]=='0C': r.append("value out of range")
  if err[0:2]=='0D': r.append("bad document state command")
  if err[0:2]=='0E': r.append("required string field missing")
  if err[0:2]=='0F': r.append("to long result")
  if err[0:2]=='10': r.append("money overload")
  return r


def hex_word_str_to_bits(st):
  lsb = int(st[2:],16)
  msb = int(st[:2],16)
  res = "%s%s"%(bin(lsb)[2:].zfill(8),bin(msb)[2:].zfill(8))
  return res


def nd77_send(cmd, answ = True):
  newstr = cmd
  strln = ""
  flog.write("["+cur_date_log()+"]c:"+str(list(cmd))+"\n")
  print cmd

  if (ser.isOpen()):
    ser.write(newstr)
    
    if answ:
      sleep(1)
      strln = ser.read(50)

      status = strln[8:12]
      err = strln[13:17]
      prnstatus = strln[13:28]
    
      print strln[2:17]
      if status != "":
        print get_status(status,err)
      
      flog.write("["+cur_date_log()+"]a:"+str(list(strln))+"\n")


  return strln
    
def nd77_test_print():
  res = None;
  send_command("\x1B\x1B")
  if status != "":
    tmp = list(hex_word_str_to_bits(status))
    if tmp[7]=='0':
      send_command("01"+cur_date())
      
  send_command_datatime("50")
  for i in range((255-33)/15+1):
    x = 33 + (i + 1) * 15
    if x > 255: x = 255
    st = int_list_join(range(33 + i * 15, x))
    send_command("51\x1C%02d:%s" %(i + 1, st))

  send_command("52") 
  return res

def nd77_print_mode(l):
  res = None;
  send_command("\x1B\x1B")
  if status != "":
    tmp = list(hex_word_str_to_bits(status))
    if tmp[7]=='0':
      send_command("01"+cur_date())
      
  send_command("70")
  nd77_send("\x1Bc0\x04")
  for st in l:
    st = st.replace("\\e",  "\x1B")
    nd77_send(st_encode(st), False)

  nd77_send("\x1BJ")
  nd77_send("\x1B\x0C")
  nd77_send("\x1B\x1B")
  return res

def nd77_comand_mode(l):
  res = None;
  send_command("\x1B\x1B")
  if status != "":
    tmp = list(hex_word_str_to_bits(status))
    if tmp[7]=='0':
      send_command("01"+cur_date())
      
    if tmp[4]=='0':
      send_command("02"+cur_date()+"x1C=1=")
      
  for cmd in l:
    cmd = cmd.replace("\n",  "")
    cmd = cmd.replace("\t",  "")
    cmd = cmd.replace("\\t",  "\x1C")
    cmd = cmd.replace("\\e",  "\x1B")
    cmd = cmd.replace("\\z",  "\x04")
    cmd = cmd.replace("\\y",  "\x0C")
    cmd = cmd.replace("\\d",  cur_date())
    cmd = cmd.replace("\\\\", "\\")
    send_command(st_encode(cmd))
  
  return res

if __name__ == "__main__":

  ser = serial.Serial(comm_num, 9600, timeout=1)
  flog.write("["+cur_date_log()+"] :======================================================\n")
  for argv in sys.argv:
    flog.write("["+cur_date_log()+"] :"+argv+"\n")
  
  argnum = len(sys.argv)
  if argnum == 1:
    nd77_test_print()

  else:
    fn = sys.argv[1]
    fin = open(fn)
    l = list(fin)
    fin.close()  

    if argnum == 3 and sys.argv[2] == "p":
      nd77_print_mode(l)

    else:
      nd77_comand_mode(l)

  ser.close()
  flog.close()

