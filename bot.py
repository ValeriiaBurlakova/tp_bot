import urllib.request as request
import urllib.parse as parse
import time
import random
import json
import telebot
from enum import Enum
from threading import Lock

SUPER_USER = 937341414
bot = telebot.TeleBot('5940934648:AAGXMNGBRU4BbgLrIMVGmhq-cbgvOcTM860')

class Role(Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    MEMBER = "member"
    INVALID = "invalid"

ROLE = "role"
NAME = "name"
IDS = "ids"

members = None

lock_update = Lock()
lock_request = Lock()

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
    return str(id) == str(SUPER_USER)

def is_admin(id):
    get_members()
    return id in members and members[id][ROLE] == Role.ADMIN or is_super_user(id)

def send_code_request(message, member, code):
    try:
        for id in member[IDS]:
            data = ('iggid={}&cdkey={}&username=&sign=0'.format(id, code)).encode('ascii')
            req = request.Request(url='https://dut.igg.com/event/code', method='POST', data=data)

            with lock_request:
                # sleep 1-5 sec
                time.sleep(random.uniform(1.0, 5.0))
                with request.urlopen(req) as f:
                    # result should have format {"code": %d, "msg": %s}
                    result = json.loads(f.read(100).decode('utf-8'))

                bot.send_message(message.chat.id, '{0} {1}: {2}'.format(id, code, result['msg']))

    except Exception as e:
        bot.reply_to(message, 'oooops')

# commands for members
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
/usage Описание базового алгоритма работы с ботом
/id Узнать свой id
/add_account Добавить игровой аккаунт
/send_code Отправить игровой код
/show_accounts Показать аккаунты
/delete_account Удалить один из аккаунтов
/role Узнать свою роль'''

    id = str(message.from_user.id)
    if is_admin(id):
        commands += '''

<b>Команды для админа:</b>
/show_members Вывести имя и id всех участников
/add_member Добавить участника
/kick_member Удалить участника по id или имени'''

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

@bot.message_handler(commands=['id'])
def id(message):
    bot.send_message(message.chat.id, f'Твой ID: <code>{message.from_user.id}</code>', parse_mode="HTML")

@bot.message_handler(commands=['role'])
def role(message):
    id = str(message.from_user.id)
    role = Role.INVALID.value
    if is_super_user(id):
        role = Role.SUPERUSER.value
    elif is_admin(id):
        role = Role.ADMIN.value
    elif id in members:
        role = Role.MEMBER.value
    if role != Role.INVALID.value:
        bot.send_message(message.chat.id, f'Ты <b>{role}</b> этого бота', parse_mode="HTML")

@bot.message_handler(commands=['add_account'])
def add_account_command(message):
    id = str(message.from_user.id)
    get_members()
    if id in members or is_admin(id):
        if is_super_user(id) and id not in members:
            with lock_update:
                members.update({id : {ROLE: Role.SUPERUSER.value, NAME: Role.SUPERUSER.name, IDS: []}})
                update_members()
        account_id = bot.reply_to(message, "Введи id аккаунта Time Princess")
        bot.register_next_step_handler(account_id, add_account, id)
    else:
        bot.send_message(message.chat.id, f'У Вас нет прав для этой операции, свяжитесь с администратором', parse_mode="HTML")

@bot.message_handler(commands=["send_code"])
def send_code_command(message):
    id = str(message.from_user.id)
    get_members()
    if id in members:
        code = bot.reply_to(message, "Введи код")
        bot.register_next_step_handler(code, send_code, id)

@bot.message_handler(commands=['show_accounts'])
def show_accounts(message):
    id = str(message.from_user.id)
    get_members()
    if id in members:
        list_of_accounts = ""
        for account in members[id][IDS]:
            list_of_accounts += f'<code>{account}</code>\n'
        bot.send_message(message.chat.id, list_of_accounts, parse_mode="HTML")

@bot.message_handler(commands=['delete_account'])
def delete_account_command(message):
    id = str(message.from_user.id)
    get_members()
    if id in members:
        account_id = bot.reply_to(message, "Введи id аккаунта Time Princess")
        bot.register_next_step_handler(account_id, delete_account, id)
    else:
        bot.send_message(message.chat.id, f'У Вас нет прав для этой операции, свяжитесь с администратором', parse_mode="HTML")

def delete_account(message, member_id):
    try:
        get_members()
        account_id = message.text.strip()
        # should be so
        if member_id in members:
            if account_id in members[member_id][IDS]:
                with lock_update:
                    members[member_id][IDS].remove(account_id)
                    update_members()
                bot.send_message(message.chat.id, f'{account_id} удален', parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, f'{account_id} не существует', parse_mode="HTML")
        else:
            bot.reply_to(message, 'oooops')
    except Exception as e:
        bot.reply_to(message, 'oooops')

def send_code(message, member_id):
    try:
        get_members()
        code = message.text.strip()
        send_code_request(message, members[member_id], code)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def add_account(message, member_id):
    try:
        get_members()
        account_id = message.text.strip()
        # should be so
        if member_id in members:
            if account_id in members[member_id][IDS]:
                bot.send_message(message.chat.id, f'{account_id} уже был добавлен', parse_mode="HTML")
            else:
                with lock_update:
                    members[member_id][IDS].append(account_id)
                    update_members()
                bot.send_message(message.chat.id, f'{account_id} добавлен', parse_mode="HTML")
        else:
            bot.reply_to(message, 'oooops')
    except Exception as e:
        bot.reply_to(message, 'oooops')

# commands for admin
@bot.message_handler(commands=['show_members'])
def show_members(message):
    if is_admin(str(message.from_user.id)):
        get_members()
        list_of_members = ""
        for member_id, member in members.items():
            list_of_members += f'<code>{member[NAME]}</code> id: <code>{member_id}</code> accounts: {(" ").join(member[IDS])}\n'
        bot.send_message(message.chat.id, list_of_members, parse_mode="HTML")

@bot.message_handler(commands=['add_member'])
def add_member_command(message):
    id = str(message.from_user.id)
    if is_admin(id):
        user_id = bot.reply_to(message, "Введи ID участника")
        bot.register_next_step_handler(user_id, add_member_id)

@bot.message_handler(commands=['kick_member'])
def kick_member_command(message):
    id = str(message.from_user.id)
    if is_admin(id):
        user_name_id = bot.reply_to(message, "Введи ID или имя")
        bot.register_next_step_handler(user_name_id, kick_member)

def kick_member(message):
    try:
        get_members()
        name_or_id = message.text
        is_found = False
        if name_or_id in members:
            with lock_update:
                members.pop(name_or_id, None)
                update_members()
            is_found = True
        else:
            for id, member in members.items():
                if member[NAME] == name_or_id:
                    with lock_update:
                        members.pop(id, None)
                        update_members()
                    is_found = True
                    break
        if is_found:
            bot.send_message(message.chat.id, f'Игрок {name_or_id} удален', parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, f'Игрок {name_or_id} не найден', parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, 'oooops')

def add_member_id(message):
    try:
        get_members()
        id = message.text
        if id in members:
            bot.send_message(message.chat.id, f'Участник {id} уже добавлен под именем {members[id][NAME]}', parse_mode="HTML")
        else:
            member = bot.reply_to(message, "Введи имя (лучше на латинице и без пробелов)")
            bot.register_next_step_handler(member, get_member_name, id)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def get_member_name(message, id):
    try:
        member_name = message.text
        get_members()
        # the check that this member already exists done on previous step
        with lock_update:
            members.update({id: {ROLE: Role.MEMBER.value, NAME: member_name, IDS: []}})
            update_members()
        bot.send_message(message.chat.id, f'Участник {id}: {member_name} добавлен', parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, 'oooops')

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
        with lock_update:
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
            with lock_update:
                members[name_or_id][ROLE] = Role.MEMBER.value
                update_members()
        else:
            is_found = False
            for id, member in members.items():
                if member[NAME] == name_or_id:
                    with lock_update:
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
            with lock_update:
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
        with lock_update:
            members.update({id: {ROLE: Role.ADMIN.value, NAME: admin_name, IDS: []}})
            update_members()
        bot.send_message(message.chat.id, f'Admin {id}: {admin_name} добавлен', parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, 'oooops')

# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")

bot.polling(none_stop=True)