import urllib.request as request
import urllib.parse as parse
import time
import random
import json
import telebot
from enum import Enum

SUPER_USER = 937341414
bot = telebot.TeleBot('5940934648:AAGXMNGBRU4BbgLrIMVGmhq-cbgvOcTM860')

class Role(Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    MEMBER = "member"

ROLE = "role"
NAME = "name"
IDS = "ids"

members = None

def get_members():
    global members
    if members is None:
        try:
            with open("members.json", "r") as json_file:
                members = json.load(json_file)
        except FileNotFoundError:
            members = {}

def update_members():
    global members
    if members is not None:
        with open("members.json", "w+") as json_file:
            json_file.write(json.dumps(members))

def is_super_user(id):
    return id == SUPER_USER

@bot.message_handler(commands=['usage'])
def usage(message):
    usage = u'''\
Привет, <b>{name}</b>!
Этот бот предназначен для игровых целей определенного сообщества.
<b>Использование</b>:
    1. Узнай свой id /id.
    2. Отправь id администратору бота, чтобы он зарегистрировал тебя.
    3. Добавь id игровых аккаунтов /add_account.
    4. Введи код /send_code.
    5. Вы прекрасны!
P.S. Описание всех команд смотри в /help'''

    bot.send_message(message.chat.id, usage.format(name=message.from_user.first_name), parse_mode='html')

@bot.message_handler(commands=['help'])
def help(message):
    commands = '''\
/help Описание команд
/usage Описание базового алгоритма работы с ботом'''
    id = message.from_user.id
    if is_super_user(id):
        commands += '''

<b>Команды для суперюзера</b>:
/add_admin Добавить админа
/admin_to_member Сделать админа обычным участником
/refresh_members Удалить всех участников
/show_members_info Вывести всю информацию об участниках'''

    bot.send_message(message.chat.id, commands, parse_mode='html')

@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, <b>{message.from_user.first_name}</b>!\nВведи /usage, чтобы ознакомиться с основными командами.'
    bot.send_message(message.chat.id, mess, parse_mode='html')

# commands for superuser
@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    id = message.from_user.id
    if is_super_user(id):
        admin_id = bot.reply_to(message, "Введи ID администратора")
        bot.register_next_step_handler(admin_id, add_admin_id)

@bot.message_handler(commands=['admin_to_member'])
def admin_to_member_handler(message):
    id = message.from_user.id
    if is_super_user(id):
        name_or_id = bot.reply_to(message, "Введи имя или id")
        bot.register_next_step_handler(name_or_id, admin_to_member)

@bot.message_handler(commands=['refresh_members'])
def refresh_members(message):
    global members
    id = message.from_user.id
    if is_super_user(id):
        members = {}
        update_members()
        bot.send_message(message.chat.id, f'Список очищен', parse_mode="HTML")

@bot.message_handler(commands=['show_members_info'])
def show_message_info(message):
    if is_super_user(message.from_user.id):
        get_members()
        s = ""
        for id, member in members.items():
            s += f'{id}: {member}\n'
        bot.send_message(message.chat.id, f'{s}', parse_mode="HTML")

def admin_to_member(message):
    try:
        get_members()
        name_or_id = message.text
        if name_or_id in members:
            members[name_or_id][ROLE] = Role.MEMBER.value
            update_members()
        else:
            is_found = False
            for id, member in members.items():
                if member[NAME] == name_or_id:
                    members[id][ROLE] = Role.MEMBER.value
                    update_members()
                    is_found = True
                    break
            if not is_found:
                bot.send_message(message.chat.id, f'Игрок {name_or_id} не найден', parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, 'oooops')

def add_admin_id(message):
    try:
        get_members()
        id = message.text
        if id in members:
            members[id][ROLE] = Role.ADMIN.value
            update_members()
            bot.send_message(message.chat.id, f'Admin {id}: {members[id][NAME]}', parse_mode="HTML")
        else:
            admin = bot.reply_to(message, "Введи имя")
            bot.register_next_step_handler(admin, get_admin_name, id)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def get_admin_name(message, id):
    try:
        admin_name = message.text
        get_members()
        # the check that this member already exists done on previous step
        members.update({id: {ROLE: Role.ADMIN.value, NAME: admin_name, IDS: []}})
        update_members()
        bot.send_message(message.chat.id, f'Admin {id}: {admin_name} добавлен', parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, 'oooops')

# @bot.message_handler()
# def get_text(message):
#     # this selfish bot is supposed to work only for one person
#     if (message.from_user.id == 937341414):
#         code = message.text

#         for id in ids:
#             # data = ('iggid={}&cdkey={}&username=&sign=0'.format(id, code)).encode('ascii')
#             # req = request.Request(url='https://dut.igg.com/event/code', method='POST', data=data)

#             # with request.urlopen(req) as f:
#             #     # result should have format {"code": %d, "msg": %s}
#             #     result = json.loads(f.read(100).decode('utf-8'))
#             #     bot.send_message(message.chat.id, '{0} {1}: {2}'.format(id, code, result['msg']))

#             # sleep 1-5 sec
#             time.sleep(random.uniform(1.0, 5.0))

# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")

bot.polling(none_stop=True)