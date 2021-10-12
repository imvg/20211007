# -*- coding: utf-8 -*-
import logging
import re
import os
import cv2
import time
import pymysql
import subprocess
import requests
from selenium import webdriver
from selenium.common import exceptions
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


class spider:
    def __init__(self, ):
        try:
            logging.info("初始化数据库连接")
            self.connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                              password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                              write_timeout=10)

            logging.info("初始化Selenium浏览器")
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            # options.add_argument('--headless')
            self.browser = webdriver.Chrome(options=options)
            self.browser.implicitly_wait(30)

            logging.info("初始化COS存储桶连接")
            secret_id = ''
            secret_key = ''
            region = 'ap-hongkong'
            self.client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Timeout=60),retry=3)
            self.cos_bucket = 'sourcefile-1304080031'
            self.dir = "m3u8/video/oumei/tushy"

            self.controler()
        except Exception as e:
            logging.error(f"初始化失败 {e}")

    def controler(self):
        try:
            logging.info("登陆tushy, 请手动输入验证码")
            self.logintushy()
            movList = self.getvodList()
            logging.info("查找库中缺少的视频...")
            for k, v in zip(movList.keys(), movList.values()):
                ishave = self.checkExisted(k)
                if not ishave:
                    # res = self.checkDisk(k, "E:\欧美\Tushy")
                    res = False
                    if res and "vodpath" in res.keys() and "imgpath" in res.keys():
                        if not os.path.isdir('./tmp'):
                            os.mkdir('./tmp')
                        desc = self.getVodInfo(v)
                        reso = self.getVideoResolution(res['vodpath'], k)
                        dura = self.getVideoTime(res['vodpath'], k)
                        enimg = self.encryptImage(res['imgpath'], k)
                        vodsp = self.vodSplit(res['vodpath'], k)
                        if 'txt' not in res.keys():
                            title = re.split('/', v)[-1].replace("-", " ").strip()
                        else:
                            title = res['txt']
                        if desc and reso and dura and enimg and vodsp:
                            cover_type = re.split('\.', res['imgpath'])[-1]
                            upres = self.uploadVideo(k, cover_type)
                            if upres:
                                data = {'title': title, 'covertype': cover_type, 'fanhao': k, 'vodreso': reso,
                                        'vodduration': dura, 'description': desc}
                                self.saveBase(data)
                                logging.info(f"{k} 处理完成")
                    else:
                        dwvod = self.downloadVod(v, k)
                        if dwvod:
                            title = dwvod['title']
                            vodpath = dwvod['vod']
                            cover = dwvod['cover']
                            vodinfo = dwvod['vodinfo']
                            cover_type = dwvod['cover_type']

                            reso = self.getVideoResolution(vodpath, k)
                            dura = self.getVideoTime(vodpath, k)
                            enimg = self.encryptImage(cover, k)
                            os.remove(cover)
                            vodsp = self.vodSplit(vodpath, k)
                            os.remove(vodpath)
                            if reso and dura and enimg and vodsp:
                                upres = self.uploadVideo(k, cover_type)
                                if upres:
                                    data = {'title': title, 'covertype': cover_type, 'fanhao': k, 'vodreso': reso,
                                            'vodduration': dura, 'description': vodinfo}
                                    self.saveBase(data)
                                    logging.info("扒取完成")
                            else:
                                logging.error(f"扒取失败 {reso} {dura} {enimg} {vodsp}")

        except Exception as e:
            logging.error(f"处理失败 {e}")
        finally:
            self.connection.close()
            self.browser.close()
            logging.info(f"结束")

    def logintushy(self, url='https://login.vixen.com/i/tushy/login?'):
        try:
            self.browser.get(url)
            self.browser.find_element_by_xpath('//*[@id="username"]').send_keys("vgwork001@gmail.com")
            self.browser.find_element_by_xpath('//*[@id="password"]').send_keys("1q2w3e4r")
            self.browser.find_element_by_xpath('//*[@id="submit-btn"]').click()
            nowLink = self.browser.current_url
            while True:
                time.sleep(0.3)
                if self.browser.current_url != nowLink:
                    break
            self.browser.find_element_by_xpath('//*[@id="root"]/main/div[1]/div/a[2]').click()
            return True
        except Exception as e:
            logging.error(e)
            return False

    def getvodList(self):
        movList = {}
        try:
            self.browser.find_element_by_xpath('//*[@id="root"]/header/div[2]/div/nav/div[3]/div[1]/a/span').click()
            lastLink = self.browser.find_element_by_xpath('//*[@id="root"]/main/div[2]/div[3]/a[7]').get_attribute('href')
            maxpage = re.split('=', lastLink)[-1]
            for p in range(1, int(maxpage)+1):
                self.browser.get("https://members.tushy.com/videos?page=" + str(p))
                movid = self.browser.find_elements_by_xpath(
                    '//*[@id="root"]/main/div[2]/div[2]/div[2]/div/div/div/div[1]/video')
                movlink = self.browser.find_elements_by_xpath(
                    '//*[@id="root"]/main/div[2]/div[2]/div[2]/div/div/div/div[1]/a')
                for id, link in zip(movid, movlink):
                    movList[re.split('/', id.get_attribute('src'))[3]] = link.get_attribute('href')
                    # movList[(re.split('_', re.split('/', id.get_attribute('src'))[-1])[0])] = link.get_attribute('href')
        except Exception as e:
            logging.error(e)
            return False
        finally:
            return movList

    def checkExisted(self, vid):
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                              password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                              write_timeout=10)
        finally:
            try:
                video_sql = f"select * from t_video where vnum='TUSHY_{vid}';"
                stock_sql = f"select * from t_video_stock where vnum='TUSHY_{vid}';"
                with self.connection.cursor() as cur:
                    videores = cur.execute(video_sql)
                    if videores == 0:
                        stockres = cur.execute(stock_sql)
                        if stockres == 0:
                            return False
                        else:
                            data = cur.fetchone()
                            return data
                    else:
                        data = cur.fetchone()
                        return data
            except Exception as e:
                logging.error(f"数据库查询失败 {e} {vid}")
                return False

    def downloadVod(self, url, fanhao):
        if "https://members.tushy.com/" in url:
            try:
                self.browser.get(url)
                while True:
                    try:
                        vodurl = self.browser.find_element_by_xpath('//*[@id="vjs_video_1_html5_api"]').get_attribute('src')
                    except:
                        time.sleep(3)
                        logging.warning(f"播放链接获取失败, 重试 {url}")
                        continue
                    else:
                        if vodurl:
                            logging.info(f"播放链接获取成功 {vodurl}")
                            break
                        else:
                            logging.warning(f"播放链接为空, 重试 {url}")
                            continue
                header = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "zh-CN,zh;q=0.9",
                    "referer": url
                }
                while True:
                    try:
                        vodres = requests.get(vodurl, headers=header, timeout=10, stream=True)
                    except Exception as e:
                        logging.warning(f"请求失败, 重试 {vodurl} {e}")
                        time.sleep(3)
                        continue
                    else:
                        logging.info(f"请求成功, 开始下载 {vodurl}")
                        break

                cover = self.browser.find_element_by_xpath(
                    '//*[@id="root"]/main/div[1]/div/div[1]/div[2]/div[1]/picture[1]/img').get_attribute('src')
                logging.info(f"封面链接: {cover}")
                cover_type = re.split('\.', re.split('\?', cover)[0])[-1]

                while True:
                    try:
                        coverres = requests.get(cover, headers=header, timeout=10)
                    except Exception as e:
                        logging.warning(f"请求失败, 重试 {cover} {e}")
                        time.sleep(3)
                        continue
                    else:
                        logging.info(f"请求成功, 开始下载 {cover}")
                        break

                vodinfo = self.browser.find_element_by_xpath('//*[@name="description"]').get_attribute('content')

                title = re.split('/', url)[-1].replace("-", " ")

            except Exception as e:
                logging.error(f"视频下载失败 {e}")
                return False
            else:
                f = open(f'tmp/{fanhao}.mp4', "wb")
                for chunk in vodres.iter_content(chunk_size=512):
                    if chunk:
                        f.write(chunk)
                f.close()
                with open(f'tmp/source-{fanhao}.{cover_type}', 'wb') as c:
                    c.write(coverres.content)
                data = {"cover": f"tmp/source-{fanhao}.{cover_type}",
                        "vod": f"tmp/{fanhao}.mp4",
                        "title": title,
                        "vodinfo": vodinfo,
                        "cover_type": cover_type}
                return data

    def checkDisk(self, vid, dir):
        res = {}

        def check(vid, dir):
            for file in os.listdir(dir):
                if os.path.isdir(f"{dir}\\{file}"):
                    check(vid, dir=dir + "\\" + file)
                elif os.path.isfile(f"{dir}\\{file}"):
                    if vid in file:
                        if file.endswith('mp4'):
                            res['vodpath'] = dir + "\\" + file
                        if file.endswith('jpg') or file.endswith('jpeg') or file.endswith('png') or file.endswith(
                                'webp'):
                            res['imgpath'] = dir + "\\" + file
                        if file.endswith('txt'):
                            with open(dir + "\\" + file, 'r') as f:
                                data = f.read()
                                if "，" in data:
                                    title = re.split("，", data)
                                    res['txt'] = f"{title[0]}，{title[1]}".replace("\n", "").replace("标题：", "").replace(
                                        "简介：", " ").strip()
                                else:
                                    res['txt'] = data.replace("\n", "").replace("标题：", "").replace("简介：", " ").strip()

        check(vid, dir)
        if res:
            return res
        else:
            return False

    def getVodInfo(self, url):
        if "https://members.tushy.com/" in url:
            url = url.replace("https://members.tushy.com/", "https://www.tushy.com/")
            n = 0
            self.browser.get(url)
            time.sleep(3)
            while True:
                if n < 3:
                    try:
                        res = self.browser.find_element_by_xpath('//*[@name="description"]').get_attribute('content')
                        return res
                    except exceptions.NoSuchElementException:
                        n += 1
                        logging.warning(f"元素找不到 重试第 {n} 次")
                        self.browser.refresh()
                        time.sleep(5)
                        continue
                    except exceptions.TimeoutException:
                        n += 1
                        logging.warning(f"连接超时 重试第 {n} 次")
                        self.browser.refresh()
                        time.sleep(5)
                        continue
                    except Exception:
                        n += 1
                        logging.warning(f"未知异常 重试第 {n} 次")
                        self.browser.refresh()
                        time.sleep(5)
                        continue
                else:
                    logging.error("视频简介获取失败")
                    return False

    def vodSplit(self, vodpath, fanhao):
        logging.info(f"{fanhao} 视频切片加密中...")
        spres = True
        try:
            command = f"ffmpeg -y -i {vodpath} -hls_time 6 -hls_list_size 0 -hls_segment_filename tmp/{fanhao}-%05d.ts -hls_key_info_file enc.keyinfo tmp/{fanhao}.m3u8"
            ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                if ret.poll() is None:
                    # 切片详细日志
                    runlog = ret.stdout.readline().decode()
                    continue
                else:
                    if ret.wait() != 0:
                        logging.warning('视频切片失败!')
                        spres = False
                        break
                    else:
                        break
        except Exception as e:
            logging.error(f'视频切片失败! {e}')
            spres = False
        return spres

    def encryptImage(self, imgpath, fanhao):
        try:
            logging.info(f"{fanhao} 加密视频封面图...")
            if not os.path.exists(imgpath):
                logging.warning(f'{imgpath} 封面文件不存在')
                return False
            data = open(imgpath, 'rb')
            key = os.urandom(8)
            type = re.split('\.', imgpath)[-1]
            with open(f'tmp/{fanhao}.{type}', 'wb') as enc:
                enc.write(key)
                enc.write(data.read())
            data.close()
            return True
        except Exception as e:
            logging.error(f'封面加密失败! {e}')
            return False

    def getVideoTime(self, vodpath, fanhao):
        logging.info(f"{fanhao} 获取视频时长...")
        if not os.path.exists(vodpath):
            logging.warning(f"{fanhao} 视频文件不存在")
            return False
        try:
            cap = cv2.VideoCapture(vodpath)
            if cap.isOpened():
                rate = cap.get(5)
                FrameNumber = cap.get(7)
                duration = FrameNumber / rate * 1000
                return int(duration)
            else:
                logging.warning(f"{fanhao} 视频文件异常, 无法获取时长")
                return False
        except Exception as e:
            logging.error(f"{fanhao} 视频文件异常, 无法获取时长 {e}")
            logging.error(e)
            return False

    def getVideoResolution(self, vodpath, fanhao):
        logging.info(f"{fanhao} 获取视频分辨率...")
        if not os.path.exists(vodpath):
            logging.info(f"{fanhao} 视频文件不存在")
            return False
        try:
            cap = cv2.VideoCapture(vodpath)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return f"{width}x{height}"
        except Exception as e:
            logging.info("视频分辨率获取失败")
            logging.info(e)
            return False

    def uploadVideo(self, fanhao, cover_type):
        logging.info(f"{fanhao} 视频上传处理中...")
        def uploadfile(sfile, dfile):
            try:
                self.client.upload_file(
                    Bucket=self.cos_bucket,
                    LocalFilePath=sfile,
                    Key=dfile,
                    PartSize=1,
                    MAXThread=10,
                    EnableMD5=False
                )
                os.remove(sfile)
                return True
            except Exception as e:
                logging.error(f"文件上传异常 {e}")
                return False

        m3u8 = open(f'tmp/{fanhao}.m3u8', 'r')
        for ts in m3u8.readlines():
            if not ts.startswith('#'):
                if uploadfile(f'tmp/{ts.strip()}', self.dir + f"/{fanhao}/{ts.strip()}") is not True:
                    return False
        m3u8.close()
        if uploadfile(f'tmp/{fanhao}.m3u8', self.dir + f"/{fanhao}/{fanhao}.m3u8") is not True:
            return False
        if uploadfile(f'tmp/{fanhao}.{cover_type}', self.dir + f'/{fanhao}/{fanhao}.{cover_type}') is not True:
            return False
        return True

    def saveBase(self, data):
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                              password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                              write_timeout=10)
        finally:
            try:
                conn = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                    password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10,
                                    write_timeout=10)
            except Exception as e:
                logging.error(f"Mysql连接失败 {e}")
            else:
                try:
                    title = data['title']

                    cover_uri = "/m3u8/video/oumei/tushy/" + data['fanhao'] + "/" + data['fanhao'] + "." + data[
                        'covertype']
                    vod_url = "/m3u8/video/oumei/tushy/" + data['fanhao'] + "/" + data['fanhao'] + ".m3u8"
                    district = "欧美"
                    vnum = data['fanhao']
                    status = "1"
                    videotype = "1"
                    videocode = "2"
                    ctime = int(time.time())
                    resolution = data['vodreso']
                    duration = data['vodduration']
                    name = ''
                    ch_name = ''
                    description = data['description']
                    with conn.cursor() as cursor:
                        sql = f'insert into t_video_stock(`title`,`cover_uri`,`video_uri`,`district`,`vnum`,`video_type`,`video_code`,`description`,`resolution`,`duration`,`md5`,`name`,`ch_name`,`ctime`,`status`)' \
                            f'value("{title}","{cover_uri}","{vod_url}","{district}","tushy_{vnum}","{videotype}","{videocode}","{description}","{resolution}","{duration}","","{name}","{ch_name}","{ctime}","{status}")'
                        cursor.execute(sql)
                        conn.commit()
                except Exception as e:
                    logging.error("视频入库失败...")
                    logging.error(e)
                    return False
                finally:
                    conn.close()


if __name__ == '__main__':
    spider()
