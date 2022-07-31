import urllib.request as request
import urllib.parse as parse
import time
#import telebot

# token = 5572728184:AAGHDLMtfAUtfH2V59FEwgSfpy4KV__IKjg

# https://pypi.org/project/pyTelegramBotAPI/
# https://dut.igg.com/event/code?lang=eng
# https://docs.python.org/3/library/urllib.request.html
# https://docs.python.org/3/library/random.html

#if (data.code != 0) {
                    #     alert(data.msg);
                    # } else {
                    #     alert("Treasure redeemed");
                    # }

# * make a random real number - 1.0 - 4.0 to sleep
# * print results with wrong code
# * handle results of operation
#   * check code
#   * output result - id + Rcode? + ok or not
# * make connection to bot
# * receive a line from bot
# * output bad results - like i don't get you
# * check id or name of user?
# * it should work only for me
# * output request results to bot
# * check full work
# * clean the code
# * learn about servers (heroku)
# * try to load code to server
# * check full work 
ids = [1020377332, 1317232899, 1040346700, 1075074256, 1074790633, 
    1075074257, 1074790225, 1074790454, 1040346953, 1071831436,
    1072859143, 1072859144, 1072859146, 1049305647, 1071828029, 
    1071833425, 1073397248, 1073397249, 1073397250]

code = 'HIJRAHTP'
code = 'HIJRAHT'

for id in ids:
    data = ('iggid={}&cdkey={}&username=&sign=0'.format(id, code)).encode('ascii')
    print(data)
#    a = request.Request(url='https://dut.igg.com/event/code', method='POST', data=data)
#    with request.urlopen(a) as f:
#        print(f.read(100).decode('utf-8'))
    time.sleep()
    
# data = parse.urlencode({'iggid':1317232899,'cdkey': 'HIJRAHTP', 'username': '', 'sign':0})
# print(data)
# # iggid=1317232899&cdkey=HIJRAHTP&username=&sign=0
# data = data.encode('ascii')
# print(data)
#b'iggid=1317232899&cdkey=HIJRAHTP&username=&sign=0'

# {"code":0,"msg":"Treasure redeemed"}
