from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InputFile
from aiogram.types import BufferedInputFile
import asyncio
from aiogram import F
from aiogram.types import CallbackQuery
from pathlib import Path
import json
import matplotlib.pyplot as plt
import io
from datetime import datetime, date
import calendar
from aiogram import types


file_path = Path(__file__).parent / 'json' / 'result.json' # Поменять на 'test_result.json'

"BOT_TOKEN=your_token_here"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

devices = dict()
problems = dict()

users = dict()

def new_user(id):
    global users
    if id not in users:
        users[id] = \
            {
                'page': 1,
                'maxpage': 1,
                'bookmarks': set(),
                'type_spisok': 'problem',
                'spisok': [],
                'datefirst': ""
            }

today = str(str(datetime.today()).replace("-", ".").split()[0])
actual_date = "0.0.0"
average_failures = 0
months = {"01": "Январь", "02": "Февраль", "03": "Март", "04": "Апрель",
               "05": "Май", "06": "Июнь", "07": "Июль", "08": "Август",
               "09": "Сентябрь", "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"}

PAGE_PROBLEM = 20
PAGE_DEVICE = 20

def analiz():
    global actual_date, average_failures
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i in data['messages']:
        if i['type'] == 'message' and i['from_id'] in ["user6031905550"]:
            sms = [j.split() for j in i['text'].split("\n")]
            if (sms[0][0][0] == "❗"):
                
                problems.setdefault(sms[0][1], dict())
                problems[sms[0][1]]["check"] = False
                problems[sms[0][1]]["device"] = sms[1][1]
                problems[sms[0][1]]["date"] = sms[3][2]
                problems[sms[0][1]]["place"] = (sms[1][1].split("_")[0] if sms[1][1].split("_")[0] not in ["local", "inet"] else sms[1][1].split("_")[1])
                problems[sms[0][1]]["description"] = " ".join(sms[2])
                
                devices.setdefault(sms[1][1], dict())
                devices[sms[1][1]]["check"] = False
                devices[sms[1][1]]["description"] = " ".join(sms[2])
                
                if sms[0][1] not in devices[sms[1][1]].setdefault("problems", []): 
                    devices[sms[1][1]]["problems"].append(sms[0][1])
                    average_failures += 1
                if sms[3][2] not in devices[sms[1][1]].setdefault("dates_break", []): 
                    devices[sms[1][1]]["dates_break"].append(sms[3][2])
                    
                actual_date = sms[3][2]
                
                
            elif (sms[0][0][0] == "✅"):    
                
                if sms[0][1] in problems:
                    problems[sms[0][1]]["check"] = True
                
                if (sms[1][1] in devices):
                    devices[sms[1][1]]["check"] = True
    
    average_failures = average_failures // len(devices.keys())
                
            
    
def send_problem(number):
    problema = problems[number]
    otvet = f'Проблема номер - {number} 🔢\n' \
            f'Статус - {"Решена ✅" if problema["check"] else "Не решена ❌"}\n' \
            f'Проблема с устройством - {problema["device"]} 🧾\n' \
            f'Дата - {problema["date"]} 📅\n' \
            f'Место - {problema["place"]} 🧭\n' \
            f'Описание - {problema["description"] if problema["description"][0] != "❌" else problema["description"][1:]}📒'

    return otvet


def send_device(name):
    device = devices[name]
    otvet = f'Название устройства - {name} 🆎\n' \
            f'Статус - {"Проблем нет ✅" if device["check"] else "Имеются проблемы ❌"}\n' \
            f'Дата последней проблемы - {device["dates_break"][-1]} 📆\n' \
            f'Статистика проблем с устройством за все время - {len(device["problems"])} 🕛\n' \
            f'Статистика проблем с устройством за год - {len([i for i in device["problems"] if compare_date(problems[i]["date"], today)[2] == 0])} 🕰️\n'\
            f'Статистика проблем с устройством за месяц - {len([i for i in device["problems"] if sum(compare_date(problems[i]["date"], today)[1:]) == 0])} ⏲️\n'\
            f'Статистика проблем с устройством за день - {len([i for i in device["problems"] if sum(compare_date(problems[i]["date"], today)) == 0])} ⏱️\n' \
            f'Последние проблемы связанных с устройством - {", ".join([i for i in device["problems"] if not problems[i]["check"]][-5:])}'
    return otvet


def compare_date(date1, date2):
    y1, m1, d1 = map(int, date1.split('.'))
    y2, m2, d2 = map(int, date2.split('.'))
    
    days1 = d1 + m1 * 30 + y1 * 365 
    days2 = d2 + m2 * 30 + y2 * 365 
    delta_days = abs(days2 - days1)
    
    years = delta_days // 365
    remaining_days = delta_days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    
    return [days, months, years]
    


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        # BotCommand(command='/start',
        #            description='начальное сообщение 😁'),
        # BotCommand(command='/help',
        #            description='список всех команд ❓'),
        BotCommand(command='/stats',
                   description='общая статистика проблем за день/месяц/год/ 🧐'),
        BotCommand(command='/all_device',
                   description='устройства зарегестрированные за все время 🤝'),
        BotCommand(command='/rec_device',
                   description='устройства рекомендованные к рассмотрению 😟'),
        BotCommand(command='/check',
                   description='новые проблемы, которые надо решить 🥺'),
    ]

    await bot.set_my_commands(main_menu_commands)


def generator_inline_buttons(width, *args, last_btn1="", last_btn2="", **kwargs):
    buttons = []
    kb_builder = InlineKeyboardBuilder()
    for i in args:
        buttons.append(InlineKeyboardButton(text=str(i), callback_data=str(i)))
    for call, text in kwargs.items():
        buttons.append(InlineKeyboardButton(text=str(text), callback_data=call))

    kb_builder.row(*buttons, width=width)
    buttons = []
    if last_btn1:
        buttons.append(InlineKeyboardButton(text=last_btn1.split(" - ")[1], callback_data=last_btn1.split(" - ")[0]))
    if last_btn2:
        buttons.append(InlineKeyboardButton(text=last_btn2.split(" - ")[1], callback_data=last_btn2.split(" - ")[0]))
    if last_btn1 or last_btn2:    
        kb_builder.row(*buttons)

    return kb_builder.as_markup()
    

@dp.message(Command(commands="start"))
async def start(message: Message):
    new_user(message.from_user.id)
    await message.answer(f'Я создан, чтобы собирать данные и их анализировать. 😄\n'
                         'Вы можете узнать список всех команд на /help ❔\n' 
                         'Или вы можете написать номер конкретной проблемы или устройства 🫰\n'
                         f'Актуальность данных до {actual_date}'
                         )


@dp.message(Command(commands="help"))
async def help(message: Message):
    new_user(message.from_user.id)
    await message.answer(f'Вот все команды: 😮\n'
                        '/start - начальное сообщение 😁\n'
                        '/help - список всех команд ❓\n'
                        '/stats - общая статистика проблем за день/месяц/год/🧐\n'
                        '/all_device - устройства зарегестрированные за все время🤝\n'
                        '/rec_device - устройства рекомендованные к рассмотрению😟\n'
                        '/check - недавние, не решенные проблемы 🥺')
    

@dp.message(Command(commands="stats"))
async def stats(message: Message):
    new_user(message.from_user.id)
    sms = f'Всего проблем - {len(problems)} 🕛 \n' \
          f'Проблем за год - {len([i for i in problems if compare_date(problems[i]["date"], today)[2] == 0])} 🕰️ \n' \
          f'Проблем за месяц - {len([i for i in problems if sum(compare_date(problems[i]["date"], today)[1:]) == 0])} ⏲️ \n' \
          f'Проблем за день - {len([i for i in problems if sum(compare_date(problems[i]["date"], today)) == 0])} ⏱️ \n'
          
              
    graph = dict()
    for i in problems:
        if compare_date(problems[i]['date'], today)[1] <= 4:
            graph.setdefault(months[problems[i]['date'].split('.')[1]], 0)
            graph[months[problems[i]['date'].split('.')[1]]] += 1
    
    
    plt.figure(figsize=(10, 6))
    plt.bar(sorted(list(graph.keys()), key=lambda x: list(months.values()).index(x)), list(graph.values()))
    # plt.xlabel("Месяц года")
    plt.ylabel("Проблем за месяц")
    plt.title('График проблем в зависимости от месяца')
    plt.tight_layout()
    
    # Сохраняем график в буфер (без сохранения на диск)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await message.answer_photo(BufferedInputFile(buf.read(), filename='problems.png'))
    plt.close()
    buf.close()
        
    await message.answer(sms, reply_markup=generator_inline_buttons(3, problems_day = "день ⏱️", problems_mounth = "месяц ⏲️", problems_year = "год 🕰️", problems_all='все время 🕛'))

@dp.message(Command(commands="all_device"))
async def all_device(message: Message):
    new_user(message.from_user.id)
    sms = f'Всего зарегистрированных устройств - {len(devices)} 🌍 \n' \
          f'Устройств в работе - {len([i for i in devices if devices[i]["check"]])} 🌇 \n' \
          f'Устройств в оффлайне - {len([i for i in devices if not devices[i]["check"]])} 🌃 \n'
          
    graph = dict()
    for i in devices:
        k = []
        for j in devices[i]["dates_break"]:
            if (compare_date(j, today))[1] <= 4 and months[j.split('.')[1]] not in k:
                graph.setdefault(months[j.split('.')[1]], 0)
                graph[months[j.split('.')[1]]] += 1
                k.append(months[j.split('.')[1]])
    
    plt.figure(figsize=(10, 6))
    plt.bar(sorted(list(graph.keys()), key=lambda x: list(months.values()).index(x)), list(graph.values()))
    # plt.xlabel("Месяц года")
    plt.ylabel("Количество устройств")
    plt.title('График устройств с проблемамии в зависимости от месяца')
    plt.tight_layout()
    
    # Сохраняем график в буфер (без сохранения на диск)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    await message.answer_photo(BufferedInputFile(buf.read(), filename='devices.png'))
    plt.close()
    buf.close()
        
    await message.answer(sms, reply_markup=generator_inline_buttons(1, devices_all = "Список устройств 🗒️"))

@dp.message(Command(commands="rec_device"))
async def rec_device(message: Message):
    new_user(message.from_user.id)
    
    sms = f'Всего зарегистрированных устройств - {len(devices)} ✅ \n' \
          f'Устройств рекомендованных к рассмотрению - {len([i for i in devices if not devices[i]["check"] and len(devices[i]["problems"]) > average_failures for date in [compare_date(devices[i]["dates_break"][-1], today)] if sum(date[1:]) == 0 and date[0] <= 7])} ‼️ \n' \
          f'Устройства с проблемами⬇️'
    
    await message.answer(sms, reply_markup=generator_inline_buttons(3, rec_devices_week = "За неделю", rec_devices_mounth = "За месяц", rec_devices_year = "За пол года", ignore = "Выбрать период"))

    
@dp.message(Command(commands="check"))
async def check(message: Message):
    new_user(message.from_user.id)
    sms = f'Проблем за месяц - {len([i for i in problems if sum(compare_date(problems[i]["date"], today)[1:]) == 0])} ✅ \n' \
          f'Рекоммендованных проблем к рассмотрению - {len([i for i in problems if not problems[i]["check"] for date in [compare_date(problems[i]["date"], today)] if sum(date[1:]) == 0 and date[0] <= 7])} ⁉️\n' \
          f'Не решенные проблемы⬇️'
        
    await message.answer(sms, reply_markup=generator_inline_buttons(3, rec_problems_week = "За неделю", rec_problems_mounth = "За месяц", rec_problems_year = "За пол года", ignore = "Выбрать период"))


@dp.message(lambda msg: msg.text and msg.text.isdigit())
async def number_problem(message: Message):
    if message.text in problems.keys():
        await message.answer(send_problem(message.text))
    else:
        await message.answer(f'Проблемы с таким номером не найдено 🚫')    

@dp.message(lambda msg: msg.text and "_" in msg.text)
async def number_problem(message: Message):
    if message.text in devices.keys():
        await message.answer(send_device(message.text))
    else:
        await message.answer(f'Такого устройства не найдено 🚫')   


@dp.callback_query(F.text(text=['problems_day']))
async def process_button_day_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    day_problems = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if sum(compare_date(problems[i]["date"], today)) == 0]
    
    if (len(day_problems) == 0):
        await callback.message.edit_text(f"Проблем за этот период нет 🚫")
        return
    
    users[callback.from_user.id]['page'] = 0
    users[callback.from_user.id]['type_spisok'] = "problem"
    users[callback.from_user.id]['maxpage'] = len(day_problems) // PAGE_PROBLEM + bool(len(day_problems) % PAGE_PROBLEM) - 1
    users[callback.from_user.id]['spisok'] = day_problems
    
    await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                         reply_markup=generator_inline_buttons(5, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * PAGE_PROBLEM:users[callback.from_user.id]['page'] * PAGE_PROBLEM + PAGE_PROBLEM],
                                                last_btn1=('forward - >>' if len(users[callback.from_user.id]['spisok']) > PAGE_PROBLEM else '')))
    
@dp.callback_query(F.text(text=['problems_mounth']))
async def process_button_mounth_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    mounth_problems = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if sum(compare_date(problems[i]["date"], today)[1:]) == 0]
    
    if (len(mounth_problems) == 0):
        await callback.message.edit_text(f"Проблем за этот период нет 🚫")
        return
    
    users[callback.from_user.id]['page'] = 0
    users[callback.from_user.id]['type_spisok'] = "problem"
    users[callback.from_user.id]['maxpage'] = len(mounth_problems) // PAGE_PROBLEM + bool(len(mounth_problems) % PAGE_PROBLEM) - 1
    users[callback.from_user.id]['spisok'] = mounth_problems
    
    await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                         reply_markup=generator_inline_buttons(5, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * PAGE_PROBLEM:users[callback.from_user.id]['page'] * PAGE_PROBLEM + PAGE_PROBLEM],
                                                last_btn1=('forward - >>' if len(users[callback.from_user.id]['spisok']) > PAGE_PROBLEM else '')))

@dp.callback_query(F.text(text=['problems_year']))
async def process_button_year_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    year_problems = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if compare_date(problems[i]["date"], today)[2] == 0]
    
    if (len(year_problems) == 0):
        await callback.message.edit_text(f"Проблем за этот период нет 🚫")
        return
    
    users[callback.from_user.id]['page'] = 0
    users[callback.from_user.id]['type_spisok'] = "problem"
    users[callback.from_user.id]['maxpage'] = len(year_problems) // PAGE_PROBLEM + bool(len(year_problems) % PAGE_PROBLEM) - 1
    users[callback.from_user.id]['spisok'] = year_problems
    
    await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                         reply_markup=generator_inline_buttons(5, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * PAGE_PROBLEM:users[callback.from_user.id]['page'] * PAGE_PROBLEM + PAGE_PROBLEM],
                                                last_btn1=('forward - >>' if len(users[callback.from_user.id]['spisok']) > PAGE_PROBLEM else '')))

@dp.callback_query(F.text(text=['problems_all']))
async def process_button_year_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    all_problems = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems]
    
    if (len(all_problems) == 0):
        await callback.message.edit_text(f"Проблем за этот период нет 🚫")
        return
    
    users[callback.from_user.id]['page'] = 0
    users[callback.from_user.id]['type_spisok'] = "problem"
    users[callback.from_user.id]['maxpage'] = len(all_problems) // PAGE_PROBLEM + bool(len(all_problems) % PAGE_PROBLEM) - 1
    users[callback.from_user.id]['spisok'] = all_problems
    
    await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                         reply_markup=generator_inline_buttons(5, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * PAGE_PROBLEM:users[callback.from_user.id]['page'] * PAGE_PROBLEM + PAGE_PROBLEM],
                                                last_btn1=('forward - >>' if len(users[callback.from_user.id]['spisok']) > PAGE_PROBLEM else '')))


@dp.callback_query(F.data.startswith("rec_problems"))
async def process_button_day_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    period = F.data.split("_")[2]

    if period == "week":
        problems_rec = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if not problems[i]["check"] for date in [compare_date(problems[i]["date"], today)] if sum(date[1:]) == 0 and date[0] < 7]
    elif period == "month":
        problems_rec = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if not problems[i]["check"] for date in [compare_date(problems[i]["date"], today)] if sum(date[1:]) == 0]
    elif period == "year":
        problems_rec = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if not problems[i]["check"] for date in [compare_date(problems[i]["date"], today)] if date[2] == 0 and date[1] < 6]
    
    if (len(problems_rec) == 0):
        await callback.message.edit_text(f"Рекомендованных проблем не найдено 🚫")
        return
    
    users[callback.from_user.id]['page'] = 0
    users[callback.from_user.id]['type_spisok'] = "problem"
    users[callback.from_user.id]['maxpage'] = len(problems_rec) // PAGE_PROBLEM + bool(len(problems_rec) % PAGE_PROBLEM) - 1
    users[callback.from_user.id]['spisok'] = problems_rec
    
    await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                         reply_markup=generator_inline_buttons(5, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * PAGE_PROBLEM:users[callback.from_user.id]['page'] * PAGE_PROBLEM + PAGE_PROBLEM],
                                                last_btn1=('forward - >>' if len(users[callback.from_user.id]['spisok']) > PAGE_PROBLEM else '')))


@dp.callback_query(F.data.startswith("rec_devices"))
async def process_button_day_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    period = F.data.split("_")[2]

    if period == "week":
        devices_rec = [f"{'✅' if devices[i]['check'] else '❗'}" + str(i) for i in devices if not devices[i]["check"] and len(devices[i]["problems"]) > average_failures for date in [compare_date(devices[i]["dates_break"][-1], today)] if sum(date[1:]) == 0 and date[0] <= 7]
    elif period == "month":
        devices_rec = [f"{'✅' if devices[i]['check'] else '❗'}" + str(i) for i in devices if not devices[i]["check"] and len(devices[i]["problems"]) > average_failures for date in [compare_date(devices[i]["dates_break"][-1], today)] if sum(date[1:]) == 0]
    elif period == "year":
        devices_rec = [f"{'✅' if devices[i]['check'] else '❗'}" + str(i) for i in devices if not devices[i]["check"] and len(devices[i]["problems"]) > average_failures for date in [compare_date(devices[i]["dates_break"][-1], today)] if date[2] == 0 and date[1] < 6]

    if (len(devices_rec) == 0):
        await callback.message.edit_text(f"Устройств не найдено 🚫")
        return
    
    users[callback.from_user.id]['page'] = 0
    users[callback.from_user.id]['type_spisok'] = "device"
    users[callback.from_user.id]['maxpage'] = len(devices_rec) // PAGE_DEVICE + bool(len(devices_rec) % PAGE_DEVICE) - 1
    users[callback.from_user.id]['spisok'] = devices_rec
    
    await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                         reply_markup=generator_inline_buttons(2, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * PAGE_DEVICE:users[callback.from_user.id]['page'] * PAGE_DEVICE + PAGE_DEVICE],
                                                last_btn1=('forward - >>' if len(users[callback.from_user.id]['spisok']) > PAGE_DEVICE else '')))


@dp.callback_query(F.text(text=['forward']))
async def process_button_forward_press(callback: CallbackQuery):
    elements_in_page = (PAGE_PROBLEM if users[callback.from_user.id]['type_spisok'] == "problem" else PAGE_DEVICE)
    width = 5 if users[callback.from_user.id]['type_spisok'] == "problem" else 2
    if users[callback.from_user.id]['page'] < users[callback.from_user.id]['maxpage'] - 1:
        users[callback.from_user.id]['page'] += 1
        await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                                         reply_markup=generator_inline_buttons(width, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * elements_in_page:users[callback.from_user.id]['page'] * elements_in_page + elements_in_page],
                                                                backward='<<',
                                                                forward='>>'))
    elif users[callback.from_user.id]['page'] == users[callback.from_user.id]['maxpage']:
        pass

    else:
        users[callback.from_user.id]['page'] += 1
        await callback.message.edit_text(text=f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                                         reply_markup=generator_inline_buttons(width, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * elements_in_page:users[callback.from_user.id]['page'] * elements_in_page + elements_in_page],
                                                                last_btn1='backward - <<')
                                        )
    await callback.answer()


@dp.callback_query(F.text(text=['backward']))
async def process_button_backward_press(callback: CallbackQuery):
    elements_in_page = (PAGE_PROBLEM if users[callback.from_user.id]['type_spisok'] == "problem" else PAGE_DEVICE)
    width = 5 if users[callback.from_user.id]['type_spisok'] == "problem" else 2
    if users[callback.from_user.id]['page'] > 1:
        users[callback.from_user.id]['page'] -= 1
        await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                                         reply_markup=generator_inline_buttons(width, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * elements_in_page:users[callback.from_user.id]['page'] * elements_in_page + elements_in_page],
                                                                backward='<<',
                                                                forward='>>'))
    elif users[callback.from_user.id]['page'] == 0:
        pass

    else:
        users[callback.from_user.id]['page'] -= 1
        await callback.message.edit_text(text=f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                                         reply_markup=generator_inline_buttons(width, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page']* elements_in_page:users[callback.from_user.id]['page'] * elements_in_page + elements_in_page],
                                                                forward='>>'))
    await callback.answer()

@dp.callback_query(lambda callback: callback.data[:-1].isdigit())
async def process_button_day_problem(callback: CallbackQuery):
    if callback.data[:-1] in problems:
        await callback.message.edit_text(send_problem(callback.data[:-1]))
    else:
        await callback.message.edit_text(f'Проблемы с таким номером не найдено 🚫')


@dp.callback_query(lambda callback: callback.data and "_" in callback.data and callback.data[0] in ["✅", "❗"])
async def process_button_day_problem(callback: CallbackQuery):
    if callback.data[1:] in devices:
        await callback.message.edit_text(send_device(callback.data[1:]))
    else:
        await callback.message.edit_text(f'Устройства с таким назанием не найдено 🚫')
    

# Генерация календаря
def generate_calendar(year: int, month: int, select_mode: str = "start"):
    builder = InlineKeyboardBuilder()
    
    #Заголовок (месяц и год)
    month_name = calendar.month_name[month]
    builder.button(text=f"{month_name}", callback_data=f"list_month_{select_mode}_{year}")
    builder.button(text=f"{year}", callback_data=f"list_year_{select_mode}_{month}")
    
    # Дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    for day in week_days:
        builder.button(text=day, callback_data="ignore")
    
    # Ячейки календаря
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        for day in week:
            if day == 0:
                builder.button(text=" ", callback_data="ignore")
            # elif datefirst != "" and day == int(datefirst.split(".")[0]) and month == int(datefirst.split(".")[1]) and year == int(datefirst.split(".")[1]):
            #     builder.button(
            #         text=f"{day}✅", 
            #         callback_data=f"period_{select_mode}_{year}_{month}_{day}",
            #     )
            else:
                builder.button(
                    text=f" {day} ", 
                    callback_data=f"period_{select_mode}_{year}_{month}_{day}"
                )
    
    # Кнопки "Назад" и "Вперед"
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    builder.button(text="⬅️", callback_data=f"change_month_{select_mode}_{prev_year}_{prev_month}")
    builder.button(text="➡️", callback_data=f"change_month_{select_mode}_{next_year}_{next_month}")

    # Устанавливаем правильную разметку (7 колонок для дней недели)
    builder.adjust(2, 7, *[7 for _ in month_calendar], 2)
    
    return builder.as_markup()

# Обработка выбора даты
@dp.callback_query(F.data.startswith("period_"))
async def process_date_selection(callback: types.CallbackQuery):
    _, select_mode, year, month, day = callback.data.split('_')
    date = datetime(int(year), int(month), int(day)).strftime("%d.%m.%Y")
    
    datefirst = users[callback.from_user.id]['datefirst']
    
    if select_mode == "start":
        users[callback.from_user.id]['datefirst'] = date
        await callback.message.edit_text(
            f"Выбрана начальная дата: <b>{users[callback.from_user.id]['datefirst']}</b>     📅　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 \n"\
             "Теперь выберите конечную дату:",
            reply_markup=generate_calendar(int(year), int(month), "end"),
            parse_mode="HTML"
        )
    else:
        if datetime(int(date.split(".")[2]), int(date.split(".")[1]), int(date.split(".")[0])) > datetime(int(datefirst.split(".")[2]), int(datefirst.split(".")[1]), int(datefirst.split(".")[0])):
            await callback.message.edit_text(
                f"Период выбран: <b>{datefirst} - {date}</b> ✅\n",
                parse_mode="HTML"
            )
            users[callback.from_user.id]['datefirst'] = ""
        else:
            await callback.message.edit_text(
            f"Выбрана дата, раньше начальной, используйте пожалуйста корректный период ❌　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 \n"\
            f"Начальная дата: <b>{datefirst}</b> 📅\n" \
            "Теперь выберите конечную дату:",
            reply_markup=generate_calendar(int(year), int(month), "end"),
            parse_mode="HTML"
        )

@dp.callback_query(F.data.startswith("change_month_"))
async def change_month(callback: types.CallbackQuery):
    _, _, select_mode, year, month = callback.data.split('_')
    if (select_mode == "start"):
        await callback.message.edit_text(
                "Выберите начальную дату: 📅　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 　　　 ",
                reply_markup=generate_calendar(int(year), int(month), select_mode),
                parse_mode="HTML"
            )
    else:
        await callback.message.edit_text(
                f"Выбрана начальная дата: <b>{users[callback.from_user.id]['datefirst']}</b> 📅　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 \n" \
                 "Теперь выберите конечную дату:",
                reply_markup=generate_calendar(int(year), int(month), select_mode),
                parse_mode="HTML"
            )

@dp.callback_query(F.data.startswith("list_"))
async def choice_correct_month_year(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    _, choice_date, select_mode, dop_date = callback.data.split('_')
    
    months_spisok = calendar.month_name[1:]
    years = [i for i in range(datetime.now().year - 11, datetime.now().year + 1)]
    
    if choice_date == "year":
        for num_year in years:
            #builder.button(text=f"{str(num_year) + '✅' if (datefirst != '' and datefirst.split('.')[2] == num_year) else num_year}", callback_data=f"change_month_{select_mode}_{num_year}_{dop_date}")
            builder.button(text=f"{num_year}", callback_data=f"change_month_{select_mode}_{num_year}_{dop_date}")
        builder.adjust(4, 4, 4)
        await callback.message.edit_text(
            "Выберите нужный год:　　　　　　　　　　　　　 ",
            reply_markup=builder.as_markup(),
        )
        
            
    elif choice_date == "month":
        for name_month in months_spisok:
            #builder.button(text=f"{name_month + '✅' if (datefirst != '' and datefirst.split('.')[1] == list(calendar.month_name).index(name_month)) else name_month}", callback_data=f"change_month_{select_mode}_{dop_date}_{list(calendar.month_name).index(name_month)}")
            builder.button(text=f"{name_month}", callback_data=f"change_month_{select_mode}_{dop_date}_{list(calendar.month_name).index(name_month)}")
        builder.adjust(4, 4, 4)
        await callback.message.edit_text(
            "Выберите нужный месяц: 　　　　　　　　　　　　　 ",
            reply_markup=builder.as_markup(),
        )
    

#Если ловится не зарегестрированный коллбэкd
@dp.callback_query()
async def process_button_day_problem(callback: CallbackQuery):
    print("--- Данные о нажатии ---")
    print(f"User ID: {callback.from_user.id}")
    print(f"Username: @{callback.from_user.username}")
    print(f"Нажата кнопка с callback_data: {callback.data}")
    print(f"Сообщение с кнопкой: message_id={callback.message.message_id}")
    print(f"Чат: chat_id={callback.message.chat.id}")
    
    await callback.answer()



@dp.message(lambda msg: msg.document and msg.document.file_name.endswith('.json'))
async def handle_json_file(message: Message):
    try:
        file = await bot.get_file(message.document.file_id)

        save_filename = file_path
        
        await bot.download_file(file.file_path, destination=save_filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
            
        analiz()
        
        await message.answer(f"✅ JSON-файл успешно сохранен\n"\
                             f"Актуальная дата - {actual_date}")
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка: файл не является валидным JSON")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

@dp.message()
async def any_msg(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await start(message) 
    else:
        await message.answer("Простите, но я не понимаю запроса 😅 \nВоспользуйтесь /help для того чтобы узнать команды 🤨\nИли введите номер проблемы или устройства👀")


if __name__ == '__main__':
    analiz()
    dp.startup.register(set_main_menu)
    dp.run_polling(bot, allowed_updates=[])