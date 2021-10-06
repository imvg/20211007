# -*- coding: utf-8 -*-
import logging
from selenium import webdriver
from selenium.common import exceptions
from browsermobproxy import Server
import time
import os
import base64

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class Spider:
    def __init__(self):
        logging.info(f"初始化浏览器和代理...")
        proxyServer = Server("/Users/mrvg/Downloads/browsermob-proxy-2.1.4/bin/browsermob-proxy")
        proxyServer.start()
        self.proxy = proxyServer.create_proxy()

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(20)
        try:
            self.browser.get('http://hlw1.live/web.html')
            self.browser.find_element_by_xpath('//*[@id="id-com-tip-left"]').click()
            time.sleep(1)
            self.browser.find_element_by_xpath('//*[@id="id-need-overide"]/div[2]').click()
            time.sleep(1)
            self.browser.find_element_by_xpath('//*[@id="id-need-overide"]/div/div/div[2]').click()
            time.sleep(2)
        except exceptions.NoSuchElementException as e:
            logging.error(f"找不到元素 {e}")

    def clickVideoList(self, xpath):
        logging.info(f"跳转指定视频列表页...")
        self.browser.find_element_by_xpath(xpath).click()
        time.sleep(3)

    def getAllVideo(self):
        logging.info(f"获取列表所有视频...")
        try:
            emtid = self.browser.find_element_by_xpath(
                '/html/body/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div/div[3]/div[1]/div/div[1]/div[1]/div[1]').get_attribute(
                "id")
            time.sleep(1)
            return [emtid]
        except Exception as e:
            logging.error(e)

    def getVideo(self, emtid):
        logging.info(f"获取视频信息 {emtid}")
        try:
            for vid in emtid:
                logging.info(f"{'='*20} 抓取 {vid} {'='*20}")
                res = self.browser.execute_script(f'return document.getElementById("{vid}").style.backgroundImage')
                logging.info(f"视频封面: {str(res).replace('url(', '').replace(')', '')}")
                self.proxy.new_har(vid, options={'captureHeaders': True, 'captureContent': True})
                self.browser.find_element_by_xpath(f'//*[@id="{vid}"]').click()
                title = self.browser.find_element_by_xpath('//*[@id="id-tabs"]/div[2]/div[2]/div/div/div[4]/div[1]/div').get_attribute("innerText")
                logging.info(f"视频标题: {title}")
                time.sleep(5)
                data = self.proxy.har
                for s in data['log']['entries']:
                    _url = s['request']['url']
                    # 根据URL找到数据接口
                    if "m3u8" in _url:
                        logging.info(f"播放地址: {s['request']['url']}")
                        break
                self.browser.back()
        except Exception as e:
            logging.info(e)

    def close(self):
        self.browser.quit()
        self.proxy.close()


if __name__ == '__main__':
    ins = Spider()
    ins.clickVideoList(xpath="/html/body/div[1]/div[1]/div[2]/div/div[1]/div/div/div[3]/div[2]/div[2]/div/div/div/div/div/div[4]/div[1]/div[2]")
    vlist = ins.getAllVideo()
    ins.getVideo(vlist)

    ins.close()
