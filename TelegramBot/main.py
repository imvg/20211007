# -*- coding: utf-8 -*-
import logging
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
import pymysql
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class MyBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(MyBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self.connection = pymysql.connect(host="127.0.0.1", user="root", password="1q2w3e4r..A", port=3306, db="db_yy_1",
                                     connect_timeout=10, write_timeout=10)

    def on_chat_message(self, msg):
        if msg['chat']['type'] == 'private':
            chat_id = msg['from']['id']
            channel_name = msg['from']['first_name']
            command = msg['text']
            if str(command).startswith('/kc'):
                logging.info(f"用户 {channel_name} 开始发车了...")
                self.custom_send(chat_id, 0)
        elif msg['chat']['type'] == 'channel':
            chat_id = msg['sender_chat']['id']
            channel_name = msg['sender_chat']['title']
            command = msg['text']
            if str(command).startswith('/kc'):
                logging.info(f"频道 {channel_name} 开始发车了...")
                self.custom_send(chat_id, 0)
        elif msg['chat']['type'] == 'group':
            chat_id = msg['chat']['id']
            channel_name = msg['chat']['title']
            command = msg['text']
            if str(command).startswith('/kc'):
                logging.info(f"群组 {channel_name} 开始发车了...")
                self.custom_send(chat_id, 0)
        elif msg['chat']['type'] == 'supergroup':
            chat_id = msg['chat']['id']
            channel_name = msg['chat']['title']
            command = msg['text']
            if str(command).startswith('/kc'):
                logging.info(f"群组 {channel_name} 开始发车了...")
                self.custom_send(chat_id, 0)

    def on_callback_query(self, msg):
        if msg['message']['chat']['type'] == 'private':
            query_data = msg['data']
            query_channel = msg['message']['chat']['id']
            user_name = msg['from']['first_name']
            if query_data == 'iwant':
                logging.info(f"用户 {user_name} 点击了还想看")
                self.custom_send(query_channel, 0)
            elif query_data == 'long':
                logging.info(f"用户 {user_name} 点击了长视频")
                self.custom_send(query_channel, 1)
        elif msg['message']['chat']['type'] == 'channel':
            query_data = msg['data']
            query_channel = msg['message']['sender_chat']['id']
            channel_name = msg['message']['sender_chat']['title']
            user_name = msg['from']['first_name']
            if query_data == 'iwant':
                logging.info(f"频道 {channel_name} 用户 {user_name} 点击了还想看")
                self.custom_send(query_channel, 0)
            elif query_data == 'long':
                logging.info(f"频道 {channel_name} 用户 {user_name} 点击了长视频")
                self.custom_send(query_channel, 1)
        elif msg['message']['chat']['type'] == 'group':
            query_data = msg['data']
            query_channel = msg['message']['chat']['id']
            channel_name = msg['message']['chat']['title']
            user_name = msg['from']['first_name']
            if query_data == 'iwant':
                logging.info(f"群组 {channel_name} 用户 {user_name} 点击了还想看")
                self.custom_send(query_channel, 0)
            elif query_data == 'long':
                logging.info(f"群组 {channel_name} 用户 {user_name} 点击了长视频")
                self.custom_send(query_channel, 1)
        elif msg['message']['chat']['type'] == 'supergroup':
            query_data = msg['data']
            query_channel = msg['message']['chat']['id']
            channel_name = msg['message']['chat']['title']
            user_name = msg['from']['first_name']
            if query_data == 'iwant':
                logging.info(f"群组 {channel_name} 用户 {user_name} 点击了还想看")
                self.custom_send(query_channel, 0)
            elif query_data == 'long':
                logging.info(f"群组 {channel_name} 用户 {user_name} 点击了长视频")
                self.custom_send(query_channel, 1)

    def custom_send(self, chat_id, vtype):
        #bot.sendMessage(chat_id=chat_id, text="正在骑马赶来的路上, 请稍等...")
        first_advertise_title = '[撸呗官方]🔥代理加盟,超高反佣🔥'
        first_advertise_link = 'https://t.me/dj8888'

        second_advertise_title = '🛠反馈APP故障BUG即可免费领取VIP🛠'
        second_advertise_link = 'https://t.me/jianguo008'


        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=second_advertise_title, url=second_advertise_link)],
            [InlineKeyboardButton(text='还想看', callback_data='iwant'),
             # InlineKeyboardButton(text='长视频', callback_data='long')],
             InlineKeyboardButton(text='长视频', url='https://lubei.tv')],
        ])

        if vtype == 0:
            video_url = self.get_video(0)
        else:
            video_url = self.get_video(1)
        try:
            bot.sendVideo(chat_id=chat_id, video=video_url,
                          caption=f'<a href="{first_advertise_link}">{first_advertise_title}</a>', reply_markup=keyboard,
                          parse_mode="HTML")
        except Exception as e:
            logging.error(f"消息发送失败 {e}")

    def get_video(self, vtype):
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host="127.0.0.1", user="root", password="1q2w3e4r..A", port=3306,
                                         db="db_yy_1", connect_timeout=10, write_timeout=10)
            self.get_video(vtype)
        else:
            try:
                with self.connection.cursor() as cur:
                    if vtype == 0:
                        cur.execute('select vid from tg_bot_videos where v_type=0;')
                    else:
                        cur.execute('select vid from tg_bot_videos where v_type=1;')
                    total = cur.fetchall()
                    vlist = []
                    for v in total:
                        vlist.append(v[0])
                    vid = random.randint(0, len(total) - 1)
                    cur.execute(f'select v_uri from tg_bot_videos where vid={vlist[vid]}')
                    vuri = cur.fetchone()[0]
                    cosUrl = "https://tgbotvideos.s3.ap-east-1.amazonaws.com"
                    res = cosUrl + vuri
                    return res
            except Exception as e:
                logging.error(f"查询视频失败 {e}")
                return "https://tgbotvideos.s3.ap-east-1.amazonaws.com/short/16283416911821556.mp4"


if __name__ == '__main__':
    try:
        TOKEN = 'botToken'
        bot = MyBot(TOKEN)
        print('Listening ...')
        MessageLoop(bot).run_forever(timeout=30)
    except Exception as e:
        logging.error(e)
