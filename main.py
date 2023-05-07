import telebot
import psycopg2
from time import sleep

conn = psycopg2.connect(database="sirius_2023", user="sirius_2023", password="change_me", host="127.0.0.1", port="38746")
md = None
producter = None
year = None
spendings = None
elec = None
years = None
equipment = []
bot = telebot.TeleBot("5675351738:AAFheCIDHRzpVDw6MPpk7zjrfaZSrgIfpI0")


@bot.message_handler(commands=['start'])
def send_welcome(msg):
    bot.reply_to(msg, "Здраствуйте, используя эту программу вы можете рассчитать стоимость эксплуатации серверного оборудования", reply_markup=get_main_menu_keyboard())


def get_main_menu_keyboard():
    kb = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    bt1 = telebot.types.KeyboardButton(text='Добавить оборудование')
    bt2 = telebot.types.KeyboardButton(text='Провести рассчеты')
    kb.add(bt1, bt2)
    return kb


@bot.message_handler(func=lambda msg: msg.text == 'Добавить оборудование')
def add_equipment(msg):
    bot.send_message(msg.from_user.id, 'Введите модель')
    bot.register_next_step_handler(msg, add_equipment_model)

def add_equipment_model(msg):
    global md
    md = msg.text
    bot.send_message(msg.from_user.id, 'Введите производителя')
    bot.register_next_step_handler(msg, add_equipment_manufacturer)

def add_equipment_manufacturer(msg):
    global producter
    producter = msg.text
    bot.send_message(msg.from_user.id, 'Введите год выпуска')
    bot.register_next_step_handler(msg, add_equipment_year)

def add_equipment_year(msg):
    global year
    year = msg.text
    if msg.text.isdigit():
        bot.send_message(msg.from_user.id, 'Введите затраты на эксплуатацию')
        bot.register_next_step_handler(msg, add_equipment_expenses)
    else:
        bot.send_message(msg.from_user.id, 'Введите год числом')
        bot.register_next_step_handler(msg, add_equipment_year)

def add_equipment_expenses(msg):
    global spendings
    spendings = msg.text
    if msg.text.isdigit():
        bot.send_message(msg.from_user.id, 'Введите затраты на электроэнергию')
        bot.register_next_step_handler(msg, add_equipment_electricity)
    else:
        bot.send_message(msg.from_user.id, 'Введите затраты числом')
        bot.register_next_step_handler(msg, add_equipment_expenses)

def add_equipment_electricity(msg):
    global elec
    elec = msg.text
    if msg.text.isdigit():
        add_equipment_db()
        bot.send_message(msg.from_user.id, 'Данные оборудования сохранены в базу данных')
        sleep(1)
        send_welcome(msg)
    else:
        bot.send_message(msg.from_user.id, 'Введите затраты числом')
        bot.register_next_step_handler(msg, add_equipment_electricity)


def add_equipment_db():
    global conn
    cur = conn.cur()
    query = f"INSERT INTO equipment (md, producter, year_of_issue, service_cost, electricity_cost) \
        VALUES ('{md}', '{producter}', '{year}', '{spendings}', '{elec}');"
    cur.execute(query)
    conn.commit()
    cur.close()


@bot.message_handler(func=lambda msg: msg.text == 'Провести рассчеты')
def input_years(msg):
    bot.reply_to(msg, "Сколько лет вы планируете использовать оборудование?")
    bot.register_next_step_handler(msg, choose_equipment)


def choose_equipment(msg):
    global years
    if msg.text.isdigit():
        years = int(msg.text)
        keyboard_equipment = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = telebot.types.KeyboardButton(text='Конкретное')
        button2 = telebot.types.KeyboardButton(text='Наиболее выгодное')
        keyboard_equipment.add(button1, button2)
        bot.reply_to(msg, "Провести рассчет для конкретного оборудования, или сразу просчитать самое выгодное?", reply_markup=keyboard_equipment)
    else:
        bot.send_message(msg.from_user.id, 'Введите количество лет числом')
        bot.register_next_step_handler(msg, input_years)


@bot.message_handler(func=lambda msg: msg.text == 'Наиболее выгодное')
def calculate_cost_for_one(msg):
    global conn, years
    equipment_to_cost = {}
    costs = []
    minimal = 0
    cur = conn.cur()
    query = f"SELECT (md, producter, service_cost, electricity_cost) from equipment;"
    cur.execute(query)
    equipment = cur.fetchall()
    if len(equipment) >= 1:
        for i in equipment:
            data = i[0].replace("(", "").replace(")", "").split(",")
            total = (int(data[2]) + int(data[3])) * years
            costs.append(total)
            equipment_to_cost[data[0] + " " + data[1]] = total
        minimal = min(costs)
        for i in equipment_to_cost.keys():
            if equipment_to_cost[i] == minimal:
                bot.reply_to(msg, f"Наиболее выгодный вариант: {i}, затраты составят {minimal} рублей")
                break
    else:
        bot.reply_to(msg, "Добавьте оборудование")
    sleep(1)
    send_welcome(msg)


@bot.message_handler(func=lambda msg: msg.text == 'Конкретное')
def calculate_cost_for_one(msg):
    global conn, equipment
    cur = conn.cur()
    query = f"SELECT (md, producter, service_cost, electricity_cost) from equipment;"
    cur.execute(query)
    equipment = cur.fetchall()
    if len(equipment) >= 1:
        keyboard_equipment = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        for i in equipment:
            data = i[0].replace("(", "").replace(")", "").split(",")
            button = telebot.types.KeyboardButton(text=data[0] + " " + data[1])
            keyboard_equipment.add(button)
        bot.reply_to(msg, "Выберите оборудование для расчета стоимости:", reply_markup=keyboard_equipment)
        bot.register_next_step_handler(msg, print_cost)
    else:
        bot.reply_to(msg, "Добавьте оборудование")
    sleep(1)
    send_welcome(msg)


def print_cost(msg):
    global equipment, years
    for i in equipment:
        data = i[0].replace("(", "").replace(")", "").split(",")
        print(data)
        if data[0] + " " + data[1] == msg.text:
            bot.reply_to(msg, f"Затраты на {msg.text} составят {(int(data[2]) + int(data[3])) * years}")
    sleep(1)
    send_welcome(msg)


@bot.message_handler(func=lambda msg: True)
def handle_unknown_message(msg):
    bot.reply_to(msg, "К сожалению я пока не могу обработать эту команду, для перезапуска бота используйте команду /start")


# Запуск бота
bot.polling()
