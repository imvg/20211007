from datetime import timedelta
import pymysql

try:
    connection = pymysql.connect(host="hk-cdb-aumsfh1d.sql.tencentcdb.com", user="root", password="wvqhthpbd!Wv$da4", port=63734, db="db_yy", connect_timeout=10, write_timeout=10)
    sql = 'select count(uid) from t_user where aid=1 and regtime>=1626700800 and regtime<=1626701400;'
    with connection.cursor() as cur:
        cur.execute(sql)
    ret = cur.fetchall()
    print(f"SQL执行成功 {sql} Return {ret}")
except Exception as e:
    print(e)
