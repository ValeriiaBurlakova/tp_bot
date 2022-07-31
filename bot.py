import urllib.request as request
import urllib.parse as parse
import time
import random
import json
import telebot

# * learn about servers (heroku)
# * try to load code to server
# * check full work 
ids = [1020377332, 1317232899, 1040346700, 1075074256, 1074790633, 
    1075074257, 1074790225, 1074790454, 1040346953, 1071831436,
    1072859143, 1072859144, 1072859146, 1049305647, 1071828029, 
    1071833425, 1073397248, 1073397249, 1073397250]

bot = telebot.TeleBot('5572728184:AAGHDLMtfAUtfH2V59FEwgSfpy4KV__IKjg')

@bot.message_handler()
def get_text(message):
    # this selfish bot is supposed to work only for one person
    if (message.from_user.id == 937341414):
        code = message.text

        for id in ids:
            data = ('iggid={}&cdkey={}&username=&sign=0'.format(id, code)).encode('ascii')
            req = request.Request(url='https://dut.igg.com/event/code', method='POST', data=data)
   
            with request.urlopen(req) as f:
                # result should have format {"code": %d, "msg": %s}
                result = json.loads(f.read(100).decode('utf-8'))
                bot.send_message(message.chat.id, '{0} {1}: {2}'.format(id, code, result['msg']))

            # sleep 1-5 sec
            time.sleep(random.uniform(1.0, 5.0))

bot.polling(none_stop=True)