import configparser
import discord
import time

from datetime import datetime
from discord.ext import tasks

### custom packages
import response

#### read chatbot config 
chat_config = configparser.ConfigParser()
chat_config.read('chatbot_config.cfg', encoding='utf-8')

discord_token = chat_config.get('DISCORD', 'BOT_TOKEN')
discord_channel_name = chat_config.get('DISCORD', 'BOT_CHANNEL_NAME')

broker_url = chat_config.get('BROKER', 'URL')
broker_name = chat_config.get('BROKER', 'NAME')

genport_url = chat_config.get('TRADER', 'URL')

## 디버깅용 설정
response_broker_msg = response.Broker()
response_gpt_msg = response.GenportData()

'''
장 시간
'''
start_time = 900
end_time = 1530

'''
Discord Bot Core
'''
client = discord.Client(command_prefix = "!")

## interval message
@tasks.loop(minutes=10)
async def timer():
    bot_exist_channel = discord.utils.get(
        client.get_all_channels(), name=discord_channel_name
    )
    channel = client.get_channel(bot_exist_channel.id)

    now = datetime.now()
    resp_msg = '[스케줄링] 현재 시간 : ' + (now.strftime("%H:%M:%S"))

    await channel.send(resp_msg)

@client.event
async def on_ready():
    ## test.start()
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    command = message

    if command.author == client.user:
        return

    ## 현재 시간조회 
    if ('현재시간' in command.content.lower()):
        now = datetime.now()
        resp_msg = '현재 시간 : ' + (now.strftime("%H:%M:%S"))
        await message.channel.send(resp_msg)

    ## 계좌정보 조회
    elif ('계좌잔고' in command.content.lower()):
        resp_msg = response_broker_msg.get_acc_info()
        await message.channel.send(resp_msg)

    ## 금일 매수정보 조회
    elif ('매수정보' in command.content.lower()):
        resp_msg = response_gpt_msg.get_today_buybook()
        await message.channel.send(file=discord.File('buybook.png'))

    ## 금일 매도정보 조회
    elif ('매도정보' in command.content.lower()):
        resp_msg = response_gpt_msg.get_today_sellbook()
        await message.channel.send(file=discord.File('sellbook.png'))

    ## 금일 매도정보 조회
    elif ('계좌정보' in command.content.lower()):
        resp_msg = response_gpt_msg.get_amountbook()
        await message.channel.send(file=discord.File('amountbook.png'))

    ## 확인불가 커맨드
    else:
        resp_msg = '커맨드를 이해하지 못했습니다.'


## 봇 시작
client.run(discord_token)
