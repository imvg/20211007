# -*- coding: utf-8 -*-
import logging
import re
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import pymysql
import requests
from selenium import webdriver
from selenium.common import exceptions
from browsermobproxy import Server
import time
import os, base64, random
import cv2


logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class Spider:
    def __init__(self):
        logging.info(f"初始化浏览器和代理...")
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        # os.popen('rm -f tmp/*')
        proxyServer = Server("../browsermob-proxy-2.1.4/bin/browsermob-proxy")
        proxyServer.start()
        self.proxy = proxyServer.create_proxy()

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--headless')
        options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(20)
        self.login()

    def login(self):
        try:
            self.browser.get('https://madou1.tv/')
            self.browser.find_element_by_xpath('//*[@id="root"]/div/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[3]/ul/li/a[1]').click()
            time.sleep(1)
            self.browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/input[1]').send_keys('ligoudan')
            time.sleep(1)
            self.browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/input[2]').send_keys('nidayede')
            time.sleep(1)
            self.browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div/div[1]/button[1]').click()
            time.sleep(1)
        except exceptions.NoSuchElementException as e:
            logging.error(f"找不到元素 {e}")

    def clickChannel(self):
        logging.info(f"跳转频道页...")
        self.browser.find_element_by_xpath('//*[@id="root"]/div/div[1]/div/div/div/div[2]/div/div/div[1]/div[2]/div[1]/a[2]').click()
        time.sleep(3)

    def selectZone(self, url):
        logging.info(f"打开指定频道...")
        self.browser.get(url)
        input(f"加载完封面后点回车: ")

    def getVideo(self):
        logging.info(f"获取视频信息...")
        resData = []
        _con = False
        try:
            while True:
                res = self.getVideoPage()
                resData += res
                try:
                    next = self.browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[3]/ul/li[5]')
                except Exception as e:
                    logging.warning(f"没有下一页 {e}")
                    break
                else:
                    if next.get_attribute('aria-disabled') == 'false':
                        next.click()
                        input(f"加载完封面后点回车: ")
                        continue
                    else:
                        break
            return resData
        except Exception as e:
            logging.info(f"视频信息获取异常 {e}")
            input("aaa: ")

    def getVideoPage(self):
        resData = []
        _con = False
        try:
            vodList = self.browser.find_elements_by_xpath('//*[@id="root"]/div/div[2]/div/div[2]/div/div/div/div/div')
            logging.info(f"此区域共获取到 {len(vodList)} 个视频")
            for vid in range(1, len(vodList) + 1):
                logging.info(f"VID: {vid}")
                titleId = int(vid / 4) * 4 + 1
                if vid % 4 == 0:
                    titleId = int(vid - 4) + 1
                if _con:
                    vid += 1
                vodCover = self.browser.find_element_by_xpath(
                    f'//*[@id="root"]/div/div[2]/div/div[2]/div/div/div/div/div[{vid}]/div/div/div/img').get_attribute(
                    'src')
                self.proxy.new_har(vid, options={'captureHeaders': True, 'captureContent': True})
                time.sleep(1)
                self.browser.find_element_by_xpath(
                    f'//*[@id="root"]/div/div[2]/div/div[2]/div/div/div/div/div[{vid}]').click()
                time.sleep(1)
                title = self.browser.find_element_by_xpath(
                    f'//*[@id="root"]/div/div[2]/div/div[2]/div/div/div/div/div[{titleId}]/div/div/div/div[2]/div[2]').get_attribute(
                    "innerText")
                vcode = self.ranstr(8)
                coverPath = f'tmp/{vcode}.png'
                self.base2Image(vodCover, coverPath)
                time.sleep(3)
                data = self.proxy.har
                for s in data['log']['entries']:
                    _url = s['request']['url']
                    logging.debug(_url)
                    # 根据URL找到数据接口
                    if str(_url).endswith('m3u8'):
                        _con = True
                        logging.info(f"视频封面: {coverPath}")
                        logging.info(f"视频标题: {title}")
                        logging.info(f"播放地址: {s['request']['url']}")
                        resData.append(
                            {'cover': coverPath, 'title': title, 'm3u8': s['request']['url'], 'vcode': vcode})
                        break
            return resData
        except Exception as e:
            logging.error(e)

    def base2Image(self, b64, dpath):
        try:
            baseData = re.split(',', b64)[-1]
            img_data = base64.b64decode(baseData)
            with open(dpath, 'wb') as f:
                f.write(img_data)
            return True
        except Exception as e:
            logging.error(f"Base64转图片失败 {e}")
            return False

    def ranstr(self, num):
        H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt

    def close(self):
        self.browser.quit()
        self.proxy.close()


def checkExist(title):
    try:
        conn = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4",
                               port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
    except Exception as e:
        logging.error(f"数据库连接失败 {e}")
        return False
    else:
        with conn.cursor() as cur:
            sql1 = f"select vid from t_video where title='{title}';"
            cur.execute(sql1)
            res1 = cur.fetchone()

            sql2 = f"select vid from t_video_stock where title='{title}';"
            cur.execute(sql2)
            res2 = cur.fetchone()

            conn.close()
            if res1 or res2:
                logging.info(f"视频已存在 {res1[0]}, {res2[0]}")
                return True
            else:
                logging.info(f"视频不存在, 可以上传 {title}")
                return False


if __name__ == '__main__':
    # 获取视频
    ins = Spider()
    ins.clickChannel()
    ins.selectZone('https://madou1.tv/channel/videoList?id=18&name=%E6%81%90%E6%80%96%E8%89%B2%E6%83%85')
    res = ins.getVideoPage()
    ins.close()
    with open('data.json', 'w') as f:
        f.write(str(res))

    logging.info(f"任务结束")
