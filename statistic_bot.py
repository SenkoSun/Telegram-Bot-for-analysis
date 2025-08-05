from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
from pathlib import Path
import json
import re


file_path = Path(__file__).parent / 'json' / 'result.json'

BOT_TOKEN = 'token'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()



devices = dict()
problems = dict()

def analiz():
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i in data['messages']:
        if i['type'] == 'message':
            sms = [j.split() for j in i['text'].split("\n")]
            if (sms[0][0][0] == "❗"):
                
                problems.setdefault(sms[0][1], dict())
                problems[sms[0][1]]["check"] = False
                problems[sms[0][1]]["date"] = sms[3][2]
                problems[sms[0][1]]["place"] = sms[1][1][:sms[1][1].find("_")]
                
                devices.setdefault(sms[1][1], dict())
                devices[sms[1][1]]["check"] = False
                devices[sms[1][1]].setdefault("problems", []).append(sms[0][1])
                devices[sms[1][1]]["date_last_break"] = sms[3][2] 
                
                
            elif (sms[0][0][0] == "✅"):    
                
                problems.setdefault(sms[0][1], dict())
                problems[sms[0][1]]["check"] = True
                problems[sms[0][1]]["date"] = sms[2][2]
                problems[sms[0][1]]["place"] = sms[1][1][:sms[1][1].find("_")]
                
                devices.setdefault(sms[1][1], dict())
                devices[sms[1][1]]["check"] = True
                if sms[0][1] not in devices[sms[1][1]].setdefault("problems", []): 
                    devices[sms[1][1]]["problems"].append(sms[0][1])
                    
def vivod_problems(sms):
    pass

def vivod_device(sms):
    pass

@dp.message(Command(commands="start"))
async def process_start_command1(message: Message):
    await message.answer(f'Я создан, чтобы собирать данные и их анализировать. 😄\n'
                         'Вы можете узнать список всех команд на /help ❔\n' 
                         'Или вы можете написать номер конкретной проблемы или устройства 💱')

@dp.message(Command(commands="help"))
async def process_start_command1(message: Message):
    await message.answer(f'Вот все команды: 😮')
    await message.answer(f'/start - начальное сообщение 😁')
    await message.answer(f'/help - список всех команд ❓')
    await message.answer(f'/stats - общая статистика проблем за день/месяц/год/🧐')
    await message.answer(f'/all_device - устройства зарегестрированные за все время🤝')
    await message.answer(f'/rec_device - устройства рекомендованные к рассмотрению😟')
    await message.answer(f'/check - недавние, не решенные проблемы 🥺')
    

@dp.message(Command(commands="stats"))
async def stats(message: Message):
    await message.answer(f'kek')

@dp.message(Command(commands="all_device"))
async def all_device(message: Message):
    await message.answer(f'kek')

@dp.message(Command(commands="rec_device"))
async def rec_device(message: Message):
    await message.answer(f'kek')

@dp.message(Command(commands="check"))
async def check(message: Message):
    await message.answer(f'kek')        

@dp.message(lambda msg: msg.text and msg.textisdigit())
async def number_problem(message: Message):
    await message.answer(f'Проблемы с таким номером не найдено')    

@dp.message(lambda msg: msg.text and "_" in msg.text)
async def number_problem(message: Message):
    await message.answer(f'Такого устройства не найдено')    

if __name__ == '__main__':
    analiz()
    dp.run_polling(bot)