# -*- coding: utf-8 -*-
import logging
import pymysql
import time

logging.basicConfig(format="", level=logging.INFO)

try:
    connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root",
                                 password="wvqhthpbd!Wv$da4", port=63734, db="db_yy")
except Exception as e:
    print(e)
else:
    try:
        finish_tms = 1625068800
        for s in range(15):
            start_date = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(finish_tms))
            stop_date = time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(finish_tms+86400))
            new_user = f"select count(uid) from t_user where regtime>{finish_tms} and regtime<{finish_tms + 86400}"
            active_user = f"select count(uid) from t_user where online_time>{finish_tms} and online_time<{finish_tms + 86400}"
            total_paid = f"select count(uid) from t_shop_order where status=1 and ctime>{finish_tms} and ctime<{finish_tms + 86400} and sku in (select id from t_shop_item where status=1 and type in (1,2))"
            new_user_paid = f"select count(uid) from t_shop_order where status=1 and ctime>{finish_tms} and ctime<{finish_tms + 86400} and sku in (select id from t_shop_item where status=1 and type in (1,2)) and uid in (select uid from t_user where regtime>{finish_tms} and regtime<{finish_tms + 86400})"
            finish_tms = finish_tms + 86400
            with connection.cursor() as cur:
                # cur.execute(new_user)
                # new_user_res = cur.fetchone()[0]
                # cur.execute(active_user)
                # active_user_res = cur.fetchone()[0]
                # cur.execute(total_paid)
                # total_paid_res = cur.fetchone()[0]
                cur.execute(new_user_paid)
                new_user_paid_res = cur.fetchone()[0]
                # logging.info(f"{start_date} - {stop_date}: 新增付费率: {float(new_user_res) / float(new_user_paid_res)*100} 活跃付费率: {float(active_user_res) / float(total_paid_res)*100}")
                logging.info(new_user_paid_res)
                connection.commit()
    except Exception as e:
        logging.error(e)
    finally:
        connection.close()
