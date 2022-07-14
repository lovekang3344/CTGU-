import requests
import time
from lxml import etree
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

session = requests.session()
session.keep_alive = False
database = 'XXXX'  # 数据库
username = 'XXXXX'    # 数据库用户名
password = 'XXXX'       # 数据库密码
host = 'XXXX'      # 数据库地址
port = 'XXXX'               # 数据库端口
proxies = {
    "http": "http://123.56.175.31:3128",
    "https": "http://123.56.175.31:3128"
}
headers: dict[str, str] = {
    # "User-Agent": str(ua.random),
    "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Referer": "http://yiqing.ctgu.edu.cn/wx/index/login.do?currSchool=ctgu&CURRENT_YEAR=2019&showWjdc=false&studentShowWjdc=false"
}
my_sender = 'XXXXXX'  # 发件人邮箱账号
my_pass = 'XXXXXX'  # 发件人邮箱密码(当时申请smtp给的口令)

#发送QQ邮箱
def send_qq_email(email, content):
    my_user = email  # 收件人邮箱账号
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = formataddr(("自动安全上报", my_sender))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['To'] = formataddr(("用户，你好！", my_user))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['Subject'] = "安全上报情况"  # 邮件的主题，也可以说是标题
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
    server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
    server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.quit()  # 关闭连接

# 获取数据库内容
def get_date():
    conn = psycopg2.connect(database=database,
                            user=username,
                            password=password,
                            host=host,
                            port=port)
    cursor = conn.cursor()
    cursor.execute('select * from name_list;')      # name_list 是你数据库中的表名
    result = cursor.fetchall()
    cursor.close()
    return result


def login(username, password, email):
    # 登录账号
    login_url = "http://yiqing.ctgu.edu.cn/wx/index/loginSubmit.do"
    formdata = {
        'username': username,  # 学号
        'password': password  # 密码
    }

    try:
        login_resp = session.post(login_url, data=formdata, headers=headers, timeout=None, proxies=proxies)
        # print('状态码', login_resp.status_code)
        get_postData(email)
    except:
        print('请求错误')

    time.sleep(2)


# 获取表单内容
def get_postData(email):
    data_url = 'http://yiqing.ctgu.edu.cn/wx/health/toApply.do'
    data_resp = session.get(data_url, timeout=40, headers=headers, verify=False, proxies=proxies)
    try:
        print("状态码", data_resp.status_code)
        et = etree.HTML(data_resp.text)
        Form_data_value = et.xpath('//input/@value')
        Form_data_name = et.xpath('//input/@name')

        # 填写表单
        postData = {
            "ttoken": '',
            "province": "",
            "city": "",
            "district": "",
            "adcode": "",
            "longitude": "0",
            "latitude": "0",
            "sfqz": "否",
            "sfys": "否",
            "sfzy": "否",
            "sfgl": "否",
            "status": "1",
            "sfgr": "否",
            "szdz": "",
            "sjh": "",
            "lxrxm": '',
            "lxrsjh": '',
            "sffr": "否",
            "sffy": "否",
            "qzglsj": '',
            "qzgldd": '',
            "glyy": '',
            "mqzz": '',
            "sffx": "否",
            "qt": "",
        }
        try:
            for i in range(0, 15):
                postData[Form_data_name[i]] = Form_data_value[i]

            # 提交表单
            post_url = "http://yiqing.ctgu.edu.cn/wx/health/saveApply.do"
            headers["Referer"] = 'http://yiqing.ctgu.edu.cn/wx/health/toApply.do'
            final_resp = session.post(post_url, data=postData, headers=headers, timeout=None, verify=False,
                                      proxies=proxies)
            # print(final_resp.text)
            send_qq_email(email, '签到成功')
        except:
            # print('今天已经签过到了')
            send_qq_email(email, '今天已经签过到了')
    except:
        # print('error')
        send_qq_email(email, '签到失败，请用户自行签到')




if __name__ == "__main__":
    Data = get_date()

    for j in range(len(Data)):
        login(Data[j][0], Data[j][1], Data[j][2])
        time.sleep(5)
    print('执行完毕')
