import requests
from bs4 import BeautifulSoup
import random
import telebot
from telebot import types
import time
import os
import logging, inspect
from dotenv import load_dotenv
logging.basicConfig(filename='config_log.log', level=logging.INFO)
current_file = os.path.basename(__file__)
load_dotenv()

url_origin = 'https://bingx.com'
endpoint_url = '/en-us/support/categories/360002065274-Announcements/?sectionId=4483720972569'
url = url_origin + endpoint_url


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
]

headers = {
    'authority': 'www.bingx.com',    
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://bingx.com',
    'referer': 'https://bingx.com/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',    
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'User-Agent': random.choice(user_agents)
}

class CONNECTOR_TG():
    def __init__(self):  
        super().__init__()  
        tg_api_token = os.getenv("TG_API_BOT_TOKEN", "")   
        self.CHAT_ID = os.getenv("TG_API_CHANNEL_ID", "")   
        self.bot = telebot.TeleBot(tg_api_token)
        self.menu_markup = self.create_menu() 
        self.init_init()  
    def init_init(self):
        self.stop_flag = False            

    def create_menu(self):
        menu_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton("START")
        button2 = types.KeyboardButton("STOP")
        button3 = types.KeyboardButton("LOG")
        menu_markup.add(button1, button2, button3)        
        return menu_markup

class TG_ASSISTENT(CONNECTOR_TG):
    def __init__(self):
        super().__init__()

    def connector_func(self, message, response_message):
        retry_number = 3
        decimal = 1.1       
        for i in range(retry_number):
            try:
                # self.bot.send_message(message.chat.id, response_message)
                self.bot.send_message(chat_id=self.CHAT_ID, text=response_message)                            
                return message.text
            except Exception as ex:                
                time.sleep(1.1 + i*decimal)                   
        return None

class BINgX_parser(TG_ASSISTENT):
    def __init__(self) -> None:
        super().__init__()

    def get_bingX_data(self, message):        
        first_request_flag = True 
        before_title = None 
        random_range_from = 181
        random_range_to = 223
        retry_gert_data_counter = 0
        while True:                                
            current_link = None            
            if self.stop_flag:
                message.text = self.connector_func(message, "The pogramm was stoped!")
                return                 
            try:                 
                r = requests.get(url,  headers=headers)   
                print(r)         
                soup = BeautifulSoup(r.text, 'lxml')                
                dataa = soup.find('ul', class_='article-list').find_all('li', class_='article-item')[0].find('a')
                if not dataa:  
                    retry_gert_data_counter += 1
                    if retry_gert_data_counter == 3:
                        return                  
                    time.sleep(60)
                    
                cur_title = dataa.find('div', class_='article-title').get_text().strip()
                current_link = url_origin + dataa.get('href').strip()

                if first_request_flag:
                    before_title = cur_title
                    first_request_flag = False                    
                    message.text = self.connector_func(message, current_link)
                if cur_title != before_title:
                    before_title = cur_title
                    message.text = self.connector_func(message, current_link)                
            except Exception as ex:
                print(ex)  
            time.sleep(random.randrange(random_range_from, random_range_to))                
# //////////////////////////////////////////////////////////////////////////////////////////////////////
                
class TG_MANAGER(BINgX_parser):
    def __init__(self):
        super().__init__()

    def run(self):  
        try:          
            @self.bot.message_handler(commands=['start'])
            @self.bot.message_handler(func=lambda message: message.text == 'START')
            def handle_start_input(message):
                self.init_init()    
                print('hello1')            
                response_message = "Hello!"
                self.bot.send_message(message.chat.id, response_message, reply_markup=self.menu_markup)
                get_bingX_data_resp = self.get_bingX_data(message)
                return   

            self.bot.polling()
        except Exception as ex:
            print(ex)

def main():    
    my_bot = TG_MANAGER()
    time.sleep(1)    
    my_bot.run()

if __name__=="__main__":
    main()

