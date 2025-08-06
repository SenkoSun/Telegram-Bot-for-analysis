from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.filters import Command, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from aiogram.types import CallbackQuery
from pathlib import Path
import json
import re
from datetime import date as d



file_path = Path(__file__).parent / 'json' / 'result.json' # Поменять на 'test_result.json'

"BOT_TOKEN=your_token_here"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

devices = dict()
problems = dict()


def analiz():
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i in data['messages']:
        if i['type'] == 'message' and i['from_id'] in ["user6031905550"]:
            sms = [j.split() for j in i['text'].split("\n")]
            if (sms[0][0][0] == "❗"):
                
                problems.setdefault(sms[0][1], dict())
                problems[sms[0][1]]["check"] = False
                problems[sms[0][1]]["date"] = sms[3][2]
                problems[sms[0][1]]["place"] = sms[1][1][:sms[1][1].find("_")]
                
                devices.setdefault(sms[1][1], dict())
                devices[sms[1][1]]["check"] = False
                devices[sms[1][1]]["date_last_break"] = sms[3][2] 
                if sms[0][1] not in devices[sms[1][1]].setdefault("problems", []): 
                    devices[sms[1][1]]["problems"].append(sms[0][1])
                
                
            elif (sms[0][0][0] == "✅"):    
                
                problems.setdefault(sms[0][1], dict())
                problems[sms[0][1]]["check"] = True
                problems[sms[0][1]]["device"] = sms[1][1]
                problems[sms[0][1]]["date"] = sms[2][2]
                problems[sms[0][1]]["place"] = sms[1][1][:sms[1][1].find("_")]
                
                devices.setdefault(sms[1][1], dict())
                devices[sms[1][1]]["check"] = True
                if sms[0][1] not in devices[sms[1][1]].setdefault("problems", []): 
                    devices[sms[1][1]]["problems"].append(sms[0][1])    
    
def send_problem(number):
    problema = problems[number]
    otvet = f'Проблема номер {number}\n' \
            f'Статус {"Решена" if problema["check"] else "Не решена"}\n' \
            f'Проблема с устройством {problema["device"]}\n' \
            f'Дата {problema["date"]}\n' \

    return otvet


def send_device(name):
    device = devices[name]
    today = str(d.today()).replace("-", ".")
    otvet = f'Название устройства: {name}\n' \
            f'Статус: {"Проблем нет" if device["check"] else "Имеются проблемы"}\n' \
            f'Дата последней проблемы: {device["date_last_break"]}\n' \
            f'Статистика проблем с устройством за все время {len(device["problems"])}\n' \
            f'Статистика проблем с устройством за год {len([i for i in device["problems"] if compare_date(problems[i]["date"], today)[2] == 0])}\n'\
            f'Статистика проблем с устройством за месяц {len([i for i in device["problems"] if sum(compare_date(problems[i]["date"], today)[1:]) == 0])}\n'\
            f'Статистика проблем с устройством за день {len([i for i in device["problems"] if sum(compare_date(problems[i]["date"], today)) == 0])}'
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
        BotCommand(command='/start',
                   description='начальное сообщение 😁'),
        BotCommand(command='/help',
                   description='список всех команд ❓'),
        # BotCommand(command='/stats',
        #            description='общая статистика проблем за день/месяц/год/🧐'),
        # BotCommand(command='/all_device',
        #            description='устройства зарегестрированные за все время🤝'),
        # BotCommand(command='/rec_device',
        #            description='устройства рекомендованные к рассмотрению😟'),
        # BotCommand(command='/check',
        #            description='новые проблемы, которые надо решить🥺'),
    ]

    await bot.set_my_commands(main_menu_commands)


def generator_inline_buttons(width, *args, last_btn="", **kwargs):
    buttons = []
    kb_builder = InlineKeyboardBuilder()
    for i in args:
        buttons.append(InlineKeyboardButton(text=str(i), callback_data=str(i)))
    for call, text in kwargs.items():
        buttons.append(InlineKeyboardButton(text=str(text), callback_data=call))

    kb_builder.row(*buttons, width=width)
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=last_btn,
            callback_data=last_btn))

    return kb_builder.as_markup()
    

@dp.message(Command(commands="start"))
async def process_start_command1(message: Message):
    await message.answer(f'Я создан, чтобы собирать данные и их анализировать. 😄\n'
                         'Вы можете узнать список всех команд на /help ❔\n' 
                         'Или вы можете написать номер конкретной проблемы или устройства 🫰')


@dp.message(Command(commands="help"))
async def process_start_command1(message: Message):
    await message.answer(f'Вот все команды: 😮\n'
                        '/start - начальное сообщение 😁\n'
                        '/help - список всех команд ❓\n'
                        '/stats - общая статистика проблем за день/месяц/год/🧐\n'
                        '/all_device - устройства зарегестрированные за все время🤝\n'
                        '/rec_device - устройства рекомендованные к рассмотрению😟\n'
                        '/check - недавние, не решенные проблемы 🥺')
    

@dp.message(Command(commands="stats"))
async def stats(message: Message):
    today = str(d.today()).replace("-", ".")
    sms = f'Всего проблем - {len(problems)} \n' \
          f'Проблем за год - {len([i for i in problems if compare_date(problems[i]["date"], today)[2] == 0])} \n' \
          f'Проблем за месяц - {len([i for i in problems if sum(compare_date(problems[i]["date"], today)[1:]) == 0])} \n' \
          f'Проблем за день - {len([i for i in problems if sum(compare_date(problems[i]["date"], today)) == 0])} \n'     
        
    await message.answer(sms, reply_markup=generator_inline_buttons(3, problems_day = "день", problems_mounth = "месяц", problems_year = "год", problems_all='все время'))

@dp.message(Command(commands="all_device"))
async def all_device(message: Message):
    await message.answer(f'kek')

@dp.message(Command(commands="rec_device"))
async def rec_device(message: Message):
    await message.answer(f'kek')

@dp.message(Command(commands="check"))
async def check(message: Message):
    await message.answer(f'kek')        

@dp.message(lambda msg: msg.text and msg.text.isdigit())
async def number_problem(message: Message):
    if message.text in problems.keys():
        await message.answer(send_problem(message.text))
    else:
        await message.answer(f'Проблемы с таким номером не найдено')    

@dp.message(lambda msg: msg.text and "_" in msg.text)
async def number_problem(message: Message):
    if message.text in devices.keys():
        await message.answer(send_device(message.text))
    else:
        await message.answer(f'Такого устройства не найдено')    


# @dp.callback_query(Text(text=['day_problem']))
# async def process_button_day_problem(callback: CallbackQuery):
#     if users[callback.from_user.id]['page'] < maxpage - 1:
#         users[callback.from_user.id]['page'] += 1
#         await callback.message.edit_text(text=book[users[callback.from_user.id]['page']],
#                                          reply_markup=generator(3, backward='<<',
#                                                                 new_bookmarks=f'{users[callback.from_user.id]["page"]}/{maxpage}',
#                                                                 forward='>>'))
#     elif users[callback.from_user.id]['page'] == maxpage:
#         pass

#     else:
#         users[callback.from_user.id]['page'] += 1
#         await callback.message.edit_text(text=book[users[callback.from_user.id]['page']],
#                                          reply_markup=generator(2, backward='<<',
#                                                                 new_bookmarks=f'{users[callback.from_user.id]["page"]}/{maxpage}'))
#     await callback.answer()






@dp.message()
async def send_echo(message: Message):
    await message.answer("Простите, но я не понимаю запроса \nВоспользуйтесь /help для того чтобы узнать команды \nИли введите номер проблемы или устройства")


if __name__ == '__main__':
    analiz()
    dp.startup.register(set_main_menu)
    dp.run_polling(bot)