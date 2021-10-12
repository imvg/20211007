# -*- coding: utf-8 -*-
import logging
import os
import pymysql
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import re
import time
import subprocess
import requests
import youtube_dl
from selenium import webdriver

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


class spYoutube:
    def __init__(self):
        try:
            logging.info("初始化...")
            self.connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306,
                                              db="db_yy_1", connect_timeout=10, write_timeout=10)
            self.ytvod = youtube_dl.YoutubeDL({"logger": logging})
            self.options = webdriver.ChromeOptions()
            self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.options.add_experimental_option('useAutomationExtension', False)
            self.options.add_argument('--headless')
            self.browser = webdriver.Chrome(options=self.options)
            self.browser.implicitly_wait(60)
            if not os.path.exists('tmp'):
                os.mkdir('tmp')
        except Exception as e:
            logging.error(f"初始化失败 {e}")
        else:
            self.controller()

    def controller(self, ):
        vodList = self.getVideoList('https://www.youtube.com/playlist?list=PL0eGJygpmOH5xQuy8fpaOvKrenoCsWrKh')
        logging.debug(f"获取到 {len(vodList)} 个视频")
        logging.debug(f"初始化数据库连接")
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host="101.32.218.202", user="root", password="1q2w3e4r..A", port=3306,
                                              db="db_yy_1", connect_timeout=10, write_timeout=10)
            self.controller()
        else:
            logging.debug(f"获取到 {len(vodList)} 条视频")
            for vlink in vodList:
                vodInfo = self.getVideoInfo(vlink)
                logging.debug(f"视频信息: {vodInfo}")
                if vodInfo:
                    ishave = self.checkExisted(vodInfo['title'])
                    if ishave:
                        logging.info(f"视频存在 {vodInfo['title']}")
                    else:
                        logging.info(f"视频不存在 {vodInfo['title']}")
                        dwres = self.downloadVideo(vlink)
                        enres = self.encryptImage(vodInfo['cover'], vodInfo['id'])
                        spres = self.vodSplit(vodInfo['id'])
                        if dwres and enres and spres:
                            if self.uploadVideo(vodInfo['id'], f'xwlb', vodInfo['id'], f'tmp/{vodInfo["id"]}.jpg'):
                                saveData = {
                                    'title': vodInfo['title'],
                                    'cover': vodInfo['cover'],
                                    'file_save': 'xwlb',
                                    'fanhao': vodInfo['id'],
                                    'videotype': '国产',
                                    'videocode': '2',
                                    'vodreso': '',
                                    'vodduration': vodInfo['duration'],
                                    'name': '',
                                    'chinaname': '',
                                }
                                if self.saveBase(saveData):
                                    logging.debug(f"视频处理完成 {vodInfo}")
                    break

    def getVideoList(self, url):
        logging.info(f"获取视频URL")
        self.browser.get(url)
        vodList = []
        self.browser.execute_script(f"document.documentElement.scrollTop=9999999999999999999999999999")
        divs = self.browser.find_elements_by_xpath(
            '//*[@id="contents"]/ytd-playlist-video-renderer/div[2]/div/ytd-thumbnail/a')
        for s in divs:
            playerUrl = re.split('&', s.get_attribute('href'))[0]
            vodList.append(playerUrl)
        return vodList

    def getVideoInfo(self, url):
        res = {}
        try:
            vinfo = self.ytvod.extract_info(url, download=False)
            res['id'] = vinfo['id']
            res['title'] = vinfo['title']
            res['duration'] = vinfo['duration']
            res['cover'] = vinfo['thumbnail']
            return res
        except Exception as e:
            logging.error(f"{e} {url}")
            return False

    def downloadVideo(self, url):
        try:
            ydl_opts = {
                'outtmpl': 'tmp/%(id)s.%(ext)s',
                'merge-output-format': 'mp4',
                'logger': logging,
                'progress_hooks': [self.finishHook],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as vod:
                vid = re.split('=', url)[-1]
                logging.info(f"开始下载 {vid}")
                try:
                    vod.download([url])
                    logging.info(f"下载完成 {vid}")
                    return True
                except Exception as e:
                    logging.error(f"下载失败 {e}")
                    return False
        except Exception as e:
            logging.error(f"下载函数处理失败 {e}")
            return False

    def finishHook(self, data):
        #可用于获取下载进度百分比和速率
        pass

    def checkExisted(self, title):
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host="101.32.202.66", user="root", password="1q2w3e4r..A", port=3306,
                                              db="db_yy_1", connect_timeout=10, write_timeout=10)
            self.checkExisted(title)
        else:
            title = title.replace("'", "\\\'")
            sql = f"select * from t_video where title='{title}'"
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(sql)
                    if len(cursor.fetchall()) >= 1:
                        return True
                    else:
                        return False
            except Exception as e:
                logging.error(f"SQL执行失败 {e}")
                logging.error(sql)

    def encryptImage(self, imgurl, vid):
        try:
            logging.info(f"{vid} 加密视频封面图...")
            data = requests.get(imgurl).content
            key = os.urandom(8)
            if '?' in imgurl:
                type = re.split('\?', re.split('\.', imgurl)[-1])[0]
            else:
                type = re.split('\.', imgurl)[-1]
            with open(f'tmp/{vid}.{type}', 'wb') as enc:
                enc.write(key)
                enc.write(data)
            return True
        except Exception as e:
            logging.error(f'封面加密失败! {e}')
            return False

    def vodSplit(self, vid):
        logging.info(f"{vid} 视频切片加密中...")
        spres = True
        try:
            command = f"./ffmpeg -y -i tmp/{vid}.mp4 -hls_time 6 -hls_list_size 0 -hls_segment_filename tmp/{vid}-%05d.ts -hls_key_info_file enc.keyinfo tmp/{vid}.m3u8"
            ret = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                if ret.poll() is None:
                    # 切片详细日志
                    runlog = ret.stdout.readline().decode()
                    continue
                else:
                    if ret.wait() != 0:
                        logging.info('视频切片失败!')
                        spres = False
                        break
                    else:
                        break
        except Exception as e:
            logging.error(f'视频切片失败! {e}')
            spres = False
        return spres

    def uploadVideo(self, vodname, savepath, fanhao, cover):
        logging.debug(f"{vodname} 视频上传处理中...")
        secret_id = ''
        secret_key = ''
        region = 'ap-hongkong'
        domain = 'sourcefile-1304080031.cos.accelerate.myqcloud.com'
        client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Domain=domain))
        cos_bucket = 'sourcefile-1304080031'
        dir = savepath.strip('/').replace('\\', '/')

        def uploadfile(sfile, dfile):
            try:
                client.upload_file(
                    Bucket=cos_bucket,
                    LocalFilePath=sfile,
                    Key=dfile,
                    PartSize=1,
                    MAXThread=10,
                    EnableMD5=False
                )
                os.remove(sfile)
                return True
            except Exception as e:
                logging.debug(f"文件上传异常 {e}")
                return False

        m3u8 = open(f'tmp/{fanhao}.m3u8', 'r')
        for ts in m3u8.readlines():
            if not ts.startswith('#'):
                if uploadfile(f'tmp/{ts.strip()}', dir + f"/{fanhao}/{ts.strip()}") is not True:
                    return False
        m3u8.close()
        if uploadfile(f'tmp/{fanhao}.m3u8', dir + f"/{fanhao}/{fanhao}.m3u8") is not True:
            return False
        imgtype = re.split('\.', cover)[-1]
        if uploadfile(f'tmp/{fanhao}.{imgtype}', dir + f'/{fanhao}/{fanhao}.{imgtype}') is not True:
            return False
        return True

    def saveBase(self, data):
        # 打开数据库连接
        logging.debug(f"{data['vodname']} 视频入库中...")
        try:
            self.connection.ping()
        except:
            self.connection = pymysql.connect(host="101.32.218.202", user="root", password="1q2w3e4r..A", port=3306,
                                              db="db_yy_1", connect_timeout=10, write_timeout=10)
            return self.saveBase(data)
        try:
            title = data['title']
            cover_type = re.split('\.', data['cover'])[-1]
            cover_uri = "/" + data['file_save'] + "/" + data['fanhao'] + "/" + data['fanhao'] + "." + cover_type
            vod_url = "/" + data['file_save'] + "/" + data['fanhao'] + "/" + data['fanhao'] + ".m3u8"
            district = data['videotype']
            vnum = str(data['fanhao'])
            status = "1"
            videotype = "1"
            videocode = data['videocode']
            ctime = int(time.time())
            resolution = data['vodreso']
            duration = data['vodduration']
            name = data['name']
            ch_name = data['chinaname']
            with self.connection.cursor() as cursor:
                sql = f"insert into t_video_stock(`title`,`cover_uri`,`video_uri`,`video_uri1`,`video_uri2`,`video_uri3`,`district`,`vnum`,`video_type`,`video_code`,`description`,`resolution`,`duration`,`md5`,`name`,`ch_name`,`ctime`,`status`)" \
                      f" value('{title}','{cover_uri}','{vod_url}','{vod_url}','{vod_url}','{vod_url}','{district}','{vnum}','{videotype}','{videocode}','','{resolution}','{duration}','','{name}','{ch_name}','{ctime}','{status}')"
                cursor.execute(sql)
                self.connection.commit()
        except Exception as e:
            logging.error(f"视频入库失败... {e}")
            return False

    def __del__(self):
        self.connection.close()
        self.browser.close()
        self.connection.close()


if __name__ == '__main__':
    spYoutube()
