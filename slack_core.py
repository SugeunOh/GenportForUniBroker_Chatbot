import configparser
from datetime import datetime
from flask import Flask, Response
from pyngrok import ngrok
from slackeventsapi import SlackEventAdapter
from slack_sdk import WebClient
from threading import Thread

# custom package
import response, alert

## read broker config
broker_config = configparser.ConfigParser()
broker_config.read('config.cfg', encoding='utf-8')

trade_server = broker_config.get('BROKER', 'TRADE_SERVER')
broker_name = broker_config.get('BROKER', 'BROKER_NAME')

## read chatbot config 
chat_config = configparser.ConfigParser()
chat_config.read('chatbot_config.cfg', encoding='utf-8')

slack_token = chat_config.get('SLACK', 'BOT_TOKEN')
SLACK_SIGNING_SECRET = chat_config.get('SLACK', 'SIGN_TOKEN')
VERIFICATION_TOKEN = chat_config.get('SLACK', 'VF_TOKEN')

#instantiating slack client
slack_client = WebClient(slack_token)

## 디버깅용 설정
response_broker_msg = response.Broker()
response_gpt_msg = response.GenportData()

app = Flask(__name__)

# An example of one of your Flask app's routes
@app.route("/")
def event_hook(request):
    json_dict = json.loads(request.body.decode("utf-8"))

    if json_dict["token"] != VERIFICATION_TOKEN:
        return {"status": 403}

    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return response_dict

    return {"status": 500}

slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)  

## 커맨드 메세지 파싱 후 응답
@slack_events_adapter.on("app_mention") 
def handle_message(event_data):
    def send_reply(value):
        event_data = value
        message = event_data["event"]
        
        print(message)

        if message.get("subtype") is None:
            command = message.get("text")
            channel_id = message["channel"]
            
            ## 현재 시간조회 
            if ('현재시간' in command.lower()):
                now = datetime.now()
                message = '현재 시간 : ' + (now.strftime("%H:%M:%S"))

            ## 계좌정보 조회
            elif ('계좌정보' in command.lower()):
                message = response_broker_msg.get_acc_info()

            ## 금일 매수정보 조회
            elif ('매수정보' in command.lower()):
                message = response_broker_msg.get_today_buybook()

            ## 금일 매도정보 조회
            elif ('매도정보' in command.lower()):
                message = response_broker_msg.get_today_sellbook()

            ## 확인불가 커맨드
            else:
                message = ('커맨드를 이해하지 못했습니다.')

            slack_client.chat_postMessage(channel=channel_id, text=message)

    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    
    return Response(status=200)

# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=3000, debug=True)