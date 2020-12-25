import configparser
import subprocess 

# 챗봇서버 연결
class ChatBotServer():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('chatbot_config.cfg', encoding='utf-8')

        self.bot_kind = self.config.get('CHATBOT', 'KIND')

    ## 서버 시작
    def start(self):
        if self.bot_kind == "DISCORD":
            subprocess.Popen(['python', "discord_core.py"])

        elif self.bot_kind == "SLACK":
            subprocess.Popen(['python', "slack_core.py"])

        else:
            print('[INFO] No exist bot core.')
            return False

        return True

# 시작
if __name__ == '__main__':
    cb_server = ChatBotServer()
    cb_server.start()