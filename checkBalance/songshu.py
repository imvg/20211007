#!/bin/python3
# -*- coding: utf-8 -*-

from selenium import webdriver

browser = webdriver.Chrome()
browser.implicitly_wait(60)
browser.get('http://console.songshuyun.net/login')
browser.find_element_by_xpath('//*[@id="login"]/form/div[1]/div/div/input').send_keys('16726604303')
browser.find_element_by_xpath('//*[@id="login"]/form/div[2]/div/div/input').send_keys('16726604303')
browser.find_element_by_xpath('//*[@id="login"]/form/div[4]/div/button').click()
browser.get('http://console.songshuyun.net/cdn/package')
# res = browser.find_elements_by_xpath('//*[@id="cdn-package"]/div[2]/div[1]/div[1]/div[2]/table/tbody/tr/td[3]/div/div/span')
# for s in res:
#     print(s.text())


input('Press:')
browser.close()
