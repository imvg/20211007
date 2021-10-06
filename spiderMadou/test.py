# -*- coding: utf-8 -*-
import re
import os
import logging
import pymysql

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)


def checkExist(data):
    title = data['title'].replace('果冻传媒', '').replace('-', '.').replace(' ', '.')
    titles = re.split('\.', re.split('》', title)[-1])
    logging.info(f"检查标题 {titles[-1]}")
    res = runSql(f'select vid from t_video where title like "%{titles[-1]}%" and status=1')
    if res:
        logging.info(f"视频已存在 {res[0]}")
        return False
    return data


def runSql(sql):
    connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4",
                                 port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
    with connection.cursor() as cur:
        cur.execute(sql)
        res = cur.fetchone()
        return res


if __name__ == '__main__':
    data = [{'cover': 'tmp/ytoT7gCk.png', 'title': '《糖心VLOG》女友出差闺蜜到访-蛇姬', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_hk6cra7f/hls/1/index.m3u8', 'vcode': 'ytoT7gCk'},
 {'cover': 'tmp/rlHlL3hZ.png', 'title': '《糖心VLOG》百人斩计划之情趣装吞精-P先生', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_544rkv7s/hls/1/index.m3u8', 'vcode': 'rlHlL3hZ'},
 {'cover': 'tmp/4qw266xf.png', 'title': '《糖心VLOG》淫荡外甥女沦为舅舅的性玩具-橘子猫', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_brygpcaf/hls/1/index.m3u8', 'vcode': '4qw266xf'},
 {'cover': 'tmp/zFvS1EVj.png', 'title': '《糖心VLOG》百人斩计划约战网袜小网红-P先生', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_4dna54cj/hls/1/index.m3u8', 'vcode': 'zFvS1EVj'},
 {'cover': 'tmp/DZc5IBHm.png', 'title': '《糖心VLOG》私人医生终极肉体治疗-蛇姬', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_5dsatd7v/hls/1/index.m3u8', 'vcode': 'DZc5IBHm'},
 {'cover': 'tmp/KNkCZpxR.png', 'title': '《糖心VLOG》性爱病毒入侵的2B-柚子猫', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_6vr28y32/hls/1/index.m3u8', 'vcode': 'KNkCZpxR'},
 {'cover': 'tmp/wsud0wNn.png', 'title': '《糖心VLOG》表妹的淫荡假期-蛇姬', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_63mqu2vm/hls/1/index.m3u8', 'vcode': 'wsud0wNn'},
 {'cover': 'tmp/CtFwSaNg.png', 'title': '《糖心VLOG》富家小姐的秘密-橘子猫', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_ccgurs2h/hls/1/index.m3u8', 'vcode': 'CtFwSaNg'},
 {'cover': 'tmp/A3y2ESi5.png', 'title': '《糖心VLOG》小主播强制遛狗-小辣椒', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_hp3be372/hls/1/index.m3u8', 'vcode': 'A3y2ESi5'},
 {'cover': 'tmp/fv7PQwJF.png', 'title': '《糖心vlog》汉服歌姬沦陷', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_rvgdjcag/hls/1/index.m3u8', 'vcode': 'fv7PQwJF'},
 {'cover': 'tmp/QeAgycjZ.png', 'title': '《糖心vlog》女神司雨首次和粉丝线下约', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_ggxcsrpb/hls/1/index.m3u8', 'vcode': 'QeAgycjZ'},
 {'cover': 'tmp/4IAPUOOK.png', 'title': '《糖心vlog》堕落日记2.白丝新娘被迫花嫁', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_6h3nqm76/hls/1/index.m3u8', 'vcode': '4IAPUOOK'},
 {'cover': 'tmp/h7hc4bWn.png', 'title': '《糖心vlog》醉酒颜射的次元少女 cosplay', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_x2pcgnns/hls/1/index.m3u8', 'vcode': 'h7hc4bWn'},
 {'cover': 'tmp/y5GaWviR.png', 'title': '《糖心vlog》女神小蜜桃 我的双飞大作战', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_jdsffsem/hls/1/index.m3u8', 'vcode': 'y5GaWviR'},
 {'cover': 'tmp/HOBB0X1O.png', 'title': '《糖心vlog》花季富婆酒店玩弄按摩师', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_4ad5s7mp/hls/1/index.m3u8', 'vcode': 'HOBB0X1O'},
 {'cover': 'tmp/LWnjoo7i.png', 'title': '《糖心vlog》不良女孩色诱男家教', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_yf7akfu7/hls/1/index.m3u8', 'vcode': 'LWnjoo7i'},
 {'cover': 'tmp/WRjZB3mO.png', 'title': '《糖心vlog》淫欲女房东精液收租', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_cbhd8esb/hls/1/index.m3u8', 'vcode': 'WRjZB3mO'},
 {'cover': 'tmp/scjekYQu.png', 'title': '《糖心vlog》裸聊模特妹妹', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_c44ywsec/hls/1/index.m3u8', 'vcode': 'scjekYQu'},
 {'cover': 'tmp/h3x05b37.png', 'title': '《糖心vlog》无良医生欺骗内射.花季少女淫乱治疗', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_fwbujkyd/hls/1/index.m3u8', 'vcode': 'h3x05b37'},
 {'cover': 'tmp/NeythuQQ.png', 'title': '《糖心vlog》穿JK的性瘾嫩妹被爆操', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_yu5u3b4m/hls/1/index.m3u8', 'vcode': 'NeythuQQ'},
 {'cover': 'tmp/mEawMkZU.png', 'title': '《糖心vlog》生物女教师 .学生私房授课', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_gk23sbqb/hls/1/index.m3u8', 'vcode': 'mEawMkZU'},
 {'cover': 'tmp/Q9GUuZQK.png', 'title': '《糖心Volg》王者荣耀貂蝉圣诞Cos篇跪求主人', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_bbfauxg2/hls/1/index.m3u8', 'vcode': 'Q9GUuZQK'},
 {'cover': 'tmp/sedCHCqr.png', 'title': '《糖心vlog》小阿俏COS性爱私拍流出', 'm3u8': 'https://mm3u8s.madou18.tv/madou_tv/md/md_tdafswm3/hls/1/index.m3u8', 'vcode': 'sedCHCqr'}]
    res = []
    for vd in data:
        check = checkExist(vd)
        if check:
            res.append(check)

    logging.info(res)
