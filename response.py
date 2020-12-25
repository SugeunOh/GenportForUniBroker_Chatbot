import configparser
from datetime import datetime
import json
import pandas as pd
import requests
import plotly.figure_factory as ff

# 응답형 메세지 모음
## 브로커 관련 글 모음
class Broker():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('chatbot_config.cfg', encoding='utf-8')
        
        self.broker_server = config.get('BROKER', 'URL')
        self.broker_name = config.get('BROKER', 'NAME')

    ## 개장 폐장여부 체크
    def get_now_open(self):
        res_time = datetime.now()
        start_time = 900
        end_time = 1530
        now_time = int(res_time.strftime('%H%M'))
        print(now_time)
        if now_time > start_time and now_time < end_time:
            return " [개장]"
        
        else:
            return " [마감]"

    ## 증권사 정보
    def get_acc_info(self):
        res_url = 'http://' + self.broker_server + '/' + 'accountinfo'
        res = requests.get(res_url).text
        json_data = json.loads(res)

        res_time = datetime.now()

        ### 메세지 조합
        time_msg = '요청 시간 : ' + (res_time.strftime("%H:%M:%S") + '\n')
        msg_head = ' \n[계좌 정보] \n'
        broker_kind = '접속 증권사 : %s \n' %self.broker_name
        broker_msg = '사용자 : %s \n' %json_data["name"]
        account_msg = '총 평가액 : %s원 \n' %json_data["profit_amount"]
        dep_msg = '평가손익 : %s원 \n ' %json_data["tot_amount"]
        dep_able_msg = 'D+2 예수금 : %s원 \n' %json_data["twoday_amount"]

        msg = time_msg + msg_head + broker_kind + broker_msg + account_msg + dep_msg + dep_able_msg

        return msg

    ## 증권사 정보
    def get_acc_list(self):
        res_time = datetime.now()

        ### 메세지 조합
        time_msg = '요청 시간 : ' + res_time.strftime("%H:%M:%S") + self.get_now_open() + '\n'
        msg_head = '[금일 매수 정보] \n'

        res_url = 'http://' + self.broker_server + '/' + 'stockaccountinfo'
        res = requests.get(res_url).text
        accbook = pd.read_json(res, orient='records').astype(str)

        if len(accbook.index) < 1:
            accbook = pd.DataFrame(['-'], columns=['계좌 현황이 없습니다.'])
        
        print(accbook)

        fig =  ff.create_table(accbook)
        fig.update_layout(autosize=True)
        fig.write_image("accbook.png", scale=2)

        return True

# 젠포트 관련
class GenportData():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('chatbot_config.cfg', encoding='utf-8')
        
        self.genport_server = config.get('TRADER', 'URL')

    ## 개장 폐장여부 체크
    def get_now_open(self):
        res_time = datetime.now()
        start_time = 900
        end_time = 1530
        now_time = int(res_time.strftime('%H%M'))
        print(now_time)
        if now_time > start_time and now_time < end_time:
            return " [개장]"
        
        else:
            return " [마감]"

    ### 호출타임
    def portfolio_info(self):
        res_time = datetime.now()

        ### 메세지 조합
        time_msg = '요청 시간 : ' + res_time.strftime("%H:%M:%S") + self.get_now_open() + '\n'
        
        return msg
    
    ### 매수정보
    def get_today_buybook(self):

        ## 호출        
        res_url = 'http://' + self.genport_server + '/' + 'buybook'
        res = requests.get(res_url).text
        book = pd.read_json(res, orient='records').astype(str)

        try:
            os.remove('buybook.png')
        except:
            pass

        fig = ff.create_table(book)
        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 8
        
        fig.update_layout(autosize=True)
        fig.write_image("buybook.png", scale=2)

        return True

    ### 매도정보
    def get_today_sellbook(self):

        ## 호출        
        res_url = 'http://' + self.genport_server + '/' + 'sellbook'
        res = requests.get(res_url).text
        book = pd.read_json(res, orient='records').astype(str)

        try:
            os.remove('sellbook.png')
        except:
            pass

        fig =  ff.create_table(book)

        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 8

        fig.update_layout(autosize=True)
        fig.write_image("sellbook.png", scale=2)

        return True

    ### 계좌정보
    def get_amountbook(self):
        
        ## 호출        
        res_url = 'http://' + self.genport_server + '/' + 'accountbook'
        res = requests.get(res_url).text
        book = pd.read_json(res, orient='records')
        book['수익률'] = book['수익률'].round(2).astype(str)+'%'

        try:
            os.remove('amountbook.png')
        except:
            pass

        fig = ff.create_table(book)

        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 8
        
        fig.update_layout(autosize=True)
        fig.write_image("amountbook.png")

        return True