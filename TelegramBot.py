import sys
import requests

class TelegramBot:
    @staticmethod
    def sendMessage(message):
        api_token = "1979427536:AAHLEUh0KTy_9_umEMbwRpMxuWSPWnZJYiQ"
        chat_id = "-552030680"
        link = "https://api.telegram.org/bot" + api_token + "/" + "sendMessage?chat_id=" + chat_id + "&text=" + message + ""
        try:
            #print(message)
            r = requests.get(link)
        except:
            print(sys.exc_info()[0])