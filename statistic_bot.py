from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.filters import Command, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InputFile
import asyncio
from aiogram import F
from aiogram.types import CallbackQuery
from pathlib import Path
import json
from datetime import date as d
import matplotlib.pyplot as plt
import io


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
                'spisok': []
            }

today = str(d.today()).replace("-", ".")
actual_date = "0.0.0"


PAGE_PROBLEM = 20
PAGE_DEVICE = 20

def analiz():
    global actual_date
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
                
                devices.setdefault(sms[1][1], dict())
                devices[sms[1][1]]["check"] = False
                devices[sms[1][1]]["date_last_break"] = sms[3][2] 
                if sms[0][1] not in devices[sms[1][1]].setdefault("problems", []): 
                    devices[sms[1][1]]["problems"].append(sms[0][1])
                    
                actual_date = sms[3][2]
                
                
            elif (sms[0][0][0] == "✅"):    
                
                if sms[0][1] in problems:
                    problems[sms[0][1]]["check"] = True
                
                if (sms[1][1] in devices):
                    devices[sms[1][1]]["check"] = True
                
                actual_date = sms[3][2]
            
    
def send_problem(number):
    problema = problems[number]
    otvet = f'Проблема номер - {number} 🔢\n' \
            f'Статус - {"Решена ✅" if problema["check"] else "Не решена ❌"}\n' \
            f'Проблема с устройством - {problema["device"]} 🧾\n' \
            f'Дата - {problema["date"]} 📅\n' \

    return otvet


def send_device(name):
    device = devices[name]
    otvet = f'Название устройства - {name} 🆎\n' \
            f'Статус - {"Проблем нет ✅" if device["check"] else "Имеются проблемы ❌"}\n' \
            f'Дата последней проблемы - {device["date_last_break"]} 📆\n' \
            f'Статистика проблем с устройством за все время - {len(device["problems"])} 🕛\n' \
            f'Статистика проблем с устройством за год - {len([i for i in device["problems"] if compare_date(problems[i]["date"], today)[2] == 0])} 🕰️\n'\
            f'Статистика проблем с устройством за месяц - {len([i for i in device["problems"] if sum(compare_date(problems[i]["date"], today)[1:]) == 0])} ⏲️\n'\
            f'Статистика проблем с устройством за день - {len([i for i in device["problems"] if sum(compare_date(problems[i]["date"], today)) == 0])} ⏱️'
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
        
    await message.answer(sms, reply_markup=generator_inline_buttons(3, problems_day = "день ⏱️", problems_mounth = "месяц ⏲️", problems_year = "год 🕰️", problems_all='все время 🕛'))

@dp.message(Command(commands="all_device"))
async def all_device(message: Message):
    new_user(message.from_user.id)
    sms = f'Всего зарегистрированных устройств - {len(devices)} 🌍 \n' \
          f'Устройств в работе - {len([i for i in devices if devices[i]["check"]])} 🌇 \n' \
          f'Устройств в оффлайне - {len([i for i in devices if not devices[i]["check"]])} 🌃 \n'
          
    # graph = dict()
    # for i in devices:
    #     if compare_date(devices[i]['date_last_break'], today)[1] <= 4:
    #         graph.setdefault(devices[i]['date_last_break'].split('.')[1], 0)
    #         graph[devices[i]['date_last_break'].split('.')[1]] += 1
    
    
    # plt.figure(figsize=(10, 6))
    # plt.bar(list(graph.keys()), list(graph.values()))
    # plt.xlabel("Месяц года")
    # plt.ylabel("Устройства с проблемами")
    # plt.title('График устройств с проблемами за месяц')
    # plt.show()
    
    
    # # Сохраняем график в буфер (без сохранения на диск)
    # buf = io.BytesIO()
    # plt.savefig(buf, format='jpg')
    # buf.seek(0)  # Перемещаем указатель в начало буфера
    # plt.close()
    # await message.reply_photo(buf)
        
        
        
    await message.answer(sms, reply_markup=generator_inline_buttons(1, devices_all = "Список устройств 🗒️"))

@dp.message(Command(commands="rec_device"))
async def rec_device(message: Message):
    new_user(message.from_user.id)
    devices_rec = [f"{'✅' if devices[i]['check'] else '❗'}" + str(i) for i in devices if not devices[i]["check"] for date in [compare_date(devices[i]["date_last_break"], today)] if sum(date[1:]) == 0 and date[0] <= 7][:PAGE_DEVICE]
    
    if (len(devices_rec) == 0):
        await message.answer(f"Устройств не найдено 🚫")
        return
    
    users[message.from_user.id]['page'] = 0
    users[message.from_user.id]['type_spisok'] = "device"
    users[message.from_user.id]['maxpage'] = len(devices_rec) // PAGE_DEVICE + bool(len(devices_rec) % PAGE_DEVICE) - 1
    users[message.from_user.id]['spisok'] = devices_rec
    
    sms = f'Всего зарегистрированных устройств - {len(devices)} ✅ \n' \
          f'Устройств рекомендованных к рассмотрению - {len([i for i in devices if not devices[i]["check"] for date in [compare_date(devices[i]["date_last_break"], today)] if sum(date[1:]) == 0 and date[0] <= 7])} ‼️ \n'
    await message.answer(sms,  reply_markup=generator_inline_buttons(2, *users[message.from_user.id]['spisok'][users[message.from_user.id]['page'] * PAGE_DEVICE:users[message.from_user.id]['page'] * PAGE_DEVICE + PAGE_DEVICE]))
    
@dp.message(Command(commands="check"))
async def check(message: Message):
    new_user(message.from_user.id)
    problems_rec = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if not problems[i]["check"] for date in [compare_date(problems[i]["date"], today)] if sum(date[1:]) == 0 and date[0] <= 7]
    
    if (len(problems_rec) == 0):
        await message.answer(f"Рекомендованных проблем не найдено 🚫")
        return
    
    users[message.from_user.id]['page'] = 0
    users[message.from_user.id]['type_spisok'] = "problem"
    users[message.from_user.id]['maxpage'] = len(problems_rec) // PAGE_PROBLEM + bool(len(problems_rec) % PAGE_PROBLEM) - 1
    users[message.from_user.id]['spisok'] = problems_rec

    sms = f'Проблем за месяц - {len([i for i in problems if sum(compare_date(problems[i]["date"], today)[1:]) == 0])} ✅ \n' \
          f'Рекоммендованных проблем к рассмотрению - {len([i for i in problems if not problems[i]["check"] for date in [compare_date(problems[i]["date"], today)] if sum(date[1:]) == 0 and date[0] <= 7])} ⁉️\n'     
        
    await message.answer(sms, reply_markup=generator_inline_buttons(5, *users[message.from_user.id]['spisok'][users[message.from_user.id]['page'] * PAGE_PROBLEM:users[message.from_user.id]['page'] * PAGE_PROBLEM + PAGE_PROBLEM]))


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


@dp.callback_query(Text(text=['problems_day']))
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
    
@dp.callback_query(Text(text=['problems_mounth']))
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

@dp.callback_query(Text(text=['problems_year']))
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

@dp.callback_query(Text(text=['problems_all']))
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
    
    
@dp.callback_query(Text(text=['forward']))
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


@dp.callback_query(Text(text=['backward']))
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


@dp.callback_query(Text(text=['devices_all']))
async def process_button_day_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    devices_all = [f"{'✅' if devices[i]['check'] else '❗'}" + str(i) for i  in devices]
    
    if (len(devices_all) == 0):
        await callback.message.edit_text(f"Устройств не найдено 🚫")
        return
    
    users[callback.from_user.id]['page'] = 0
    users[callback.from_user.id]['type_spisok'] = "device"
    users[callback.from_user.id]['maxpage'] = len(devices_all) // PAGE_DEVICE + bool(len(devices_all) % PAGE_DEVICE) - 1
    users[callback.from_user.id]['spisok'] = devices_all
    
    await callback.message.edit_text(f"Страница: {users[callback.from_user.id]['page'] + 1}/{users[callback.from_user.id]['maxpage'] + 1}",
                         reply_markup=generator_inline_buttons(2, *users[callback.from_user.id]['spisok'][users[callback.from_user.id]['page'] * PAGE_DEVICE:users[callback.from_user.id]['page'] * PAGE_DEVICE + PAGE_DEVICE],
                                                last_btn1=('forward - >>' if len(users[callback.from_user.id]['spisok']) > PAGE_DEVICE else '')))

@dp.callback_query(Text(text=['devices_rec']))
async def process_button_day_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    devices_rec = [f"{'✅' if devices[i]['check'] else '❗'}" + str(i) for i in devices if not devices[i]["check"] for date in [compare_date(devices[i]["date_last_break"], today)] if sum(date[1:]) == 0 and date[0] <= 7]
    
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

@dp.callback_query(Text(text=['problems_rec']))
async def process_button_day_problem(callback: CallbackQuery):
    new_user(callback.from_user.id)
    problems_rec = [str(i) + f"{'✅' if problems[i]['check'] else '❗'}" for i in problems if not problems[i]["check"] for date in [compare_date(problems[i]["date"], today)] if sum(date[1:]) == 0 and date[0] <= 7]
    
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

@dp.callback_query(lambda callback: callback.data and "_" in callback.data and callback.data[0] in ["✅", "❗"])
async def process_button_day_problem(callback: CallbackQuery):
    if callback.data[1:] in devices:
        await callback.message.edit_text(send_device(callback.data[1:]))
    else:
        await callback.message.edit_text(f'Устройства с таким назанием не найдено 🚫')

#Если ловится не зарегестрированный коллбэк
@dp.callback_query()
async def process_button_day_problem(callback: CallbackQuery):
    print("--- Данные о нажатии ---")
    print(f"User ID: {callback.from_user.id}")
    print(f"Username: @{callback.from_user.username}")
    print(f"Нажата кнопка с callback_data: {callback.data}")
    print(f"Сообщение с кнопкой: message_id={callback.message.message_id}")
    print(f"Чат: chat_id={callback.message.chat.id}")
    
    await callback.answer()


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