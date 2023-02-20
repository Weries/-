from time import mktime,strptime
import datetime
import cityinfo
import config
import requests
from requests import get, post
from datetime import datetime, date,timedelta
import json
import bs4
from lunardate import LunarDate

def get_ad():
    baseUrl = 'http://www.weather.com.cn/weather1d/'
    # config_city = str(101180101)
    config_city = str(cityinfo.cityInfo[province][city]["AREAID"])
#     print(config_city)
    Url_A = baseUrl + config_city + '.shtml'
    headers = {
        'User - Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / '
                        '104.0.5112.102Safari / 537.36Edg / 104.0.1293.70 '
    }
    # url_request = urllib.request.Request(url=Url_A, headers=headers)
    content = requests.get(url= Url_A,headers=headers).content.decode('utf-8')
    # print(content)
    soup = bs4.BeautifulSoup(content, 'html.parser')
    condition = soup.select('.left-div .livezs .clearfix em')
    discription = soup.select('.left-div .livezs .clearfix span')
    advince = soup.select('.left-div .livezs .clearfix p')
    return condition,discription,advince

def get_access_token():
    # appId
    app_id = config.app_id
    # appSecret
    app_secret = config.app_secret
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    access_token = get(post_url).json()['access_token']
    # return "60_LGxF3bf0iK86K_qhvHpEQZ21uYULxsTf4HgfzHfbPicr3Zc-yQDqes-KQv3M8ySeEdl92vIB8QpM-k24ABSHQQ2wkFh4TqW44tsSdMFm96VpMTAziSyd0OFXdLhRHzoAAyDIIeLUnJxHVtPcHHZdADAVVN"
    return access_token

def get_time():
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六","星期日"]
    t_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    t_bj = datetime.utcnow()+ timedelta(hours=8)
    calendar = t_bj.isocalendar()
    year = t_bj.year
    month = t_bj.month
    t_bj_all = t_bj.strftime("%Y-%m-%d %H:%M")
    
    t_bj = t_bj.strftime("%Y-%m-%d")
    weekday = calendar[2]
    week = week_list[weekday-1]
    return week, t_bj_all, t_bj, year, month

def solar2lunar(t_bj):
    t = [int(i) for i in t_bj.split('-')]

    solar_date = LunarDate.fromSolarDate(t[0],t[1],t[2])
    # print(solar_date)
    # 获取农历日期
    # lunar_year, lunar_month, lunar_day = solar_date.lunar()
    lunar_year = solar_date.year
    lunar_month = solar_date.month
    lunar_day = solar_date.day

    # 定义数字和中文字符的映射关系
    lunar_num_map = {
        1: '正',
        2: '二',
        3: '三',
        4: '四',
        5: '五',
        6: '六',
        7: '七',
        8: '八',
        9: '九',
        10: '十',
        11: '冬',
        12: '腊',
    }

    lunar_day_map = {
        1: '初一',
        2: '初二',
        3: '初三',
        4: '初四',
        5: '初五',
        6: '初六',
        7: '初七',
        8: '初八',
        9: '初九',
        10: '初十',
        11: '十一',
        12: '十二',
        13: '十三',
        14: '十四',
        15: '十五',
        16: '十六',
        17: '十七',
        18: '十八',
        19: '十九',
        20: '二十',
        21: '廿一',
        22: '廿二',
        23: '廿三',
        24: '廿四',
        25: '廿五',
        26: '廿六',
        27: '廿七',
        28: '廿八',
        29: '廿九',
        30: '三十',
        31:'三一'
    }

    # 将数字转化为农历日期的字符串
    def get_lunar_date_string(month, day, isLeapMonth):
        # print(month, day, isLeapMonth)
        month_str = lunar_num_map[month]
        day_str = lunar_day_map[day]
        if not isLeapMonth:
            return f'{month_str}月{day_str}'
        else:
            return f'闰{month_str}月{day_str}'

    lunar_date_str = get_lunar_date_string(lunar_month,lunar_day,solar_date.isLeapMonth )
    return lunar_date_str

def get_weather(province, city):
    # 城市id
    city_id = cityinfo.cityInfo[province][city]["AREAID"]
    # city_id = 101280101
    # 毫秒级时间戳
#     t = (int(round(time() * 1000)))
    week, t_bj_all, t_bj,year, month = get_time()
    t =int(round(mktime(strptime(t_bj_all, "%Y-%m-%d %H:%M"))*1000))
    headers = {
      "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = "http://d1.weather.com.cn/dingzhi/{}.html?_={}".format(city_id, t)
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    response_data = response.text.split(";")[0].split("=")[-1]
    response_json = eval(response_data)
    # print(response_json)
    weatherinfo = response_json["weatherinfo"]
    # 天气
    weather = weatherinfo["weather"]
    # 最高气温
    temp = weatherinfo["temp"]
    # 最低气温
    tempn = weatherinfo["tempn"]
    return weather, temp, tempn


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature, note_ch, note_en,weather_dict,w_city,w_weather,w_max_temperature, w_min_temperature):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week, t_bj_all, t_bj,year, month = get_time()
    solar_date = solar2lunar(t_bj)
    today = t_bj
    # print(today,week)
    # 获取在一起的日子的日期格式
    love_year = int(config.love_date.split("-")[0])
    love_month = int(config.love_date.split("-")[1])
    love_day = int(config.love_date.split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    today = datetime.strptime(today,"%Y-%m-%d")
    today = datetime.date(today)
    
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取生日的月和日
    birthday_month = int(config.birthday1['birthday'].split("-")[1])
    birthday_day = int(config.birthday1['birthday'].split("-")[2])
    # 今年生日
    year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    
    data = {
        "touser": to_user,
        "template_id": "8lkpDEI5zAuHDiB6GNjHJDgGpB_i4Z0fpFZYVt-VzSo",
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "\U0001F30D：{} {}".format(today, week),
                "color": "#6495ED"
            },
            "solar_date": {
                "value": "\U0001F319：" + solar_date,
                "color": "#6495ED"
            },
            "city": {
                "value": "🏰：" + city_name,
                "color": "#EE7600"
            },
            "weather": {
                "value": "⛅：" + weather,
                "color": "#ED9121"
            },
            "min_temperature": {
                "value": "🌡：" + min_temperature,
                "color": "#87CEEB"
            },
            "max_temperature": {
              "value": max_temperature,
              "color": "#FF6100"
            },
            "w_city": {
                "value": "🐩：" + w_city,
                "color": "#EE7600"
            },
            "w_weather": {
                "value": "⛅：" +w_weather,
                "color": "#ED9121"
            },
            "w_min_temperature": {
                "value": "🐩：" + w_min_temperature,
                "color": "#87CEEB"
            },
            "w_max_temperature": {
              "value": w_max_temperature,
              "color": "#FF6100"
            },
            "love_day": {
              "value": "\U0001F49E：" + love_days,
              "color": "#FF82AB"
            },
            "birthday": {
              "value": birth_day,
              "color": "#FF8000"
            },
            "note_en": {
                "value": note_en,
                "color": "#CD2990"
            },
            "note_ch": {
                "value": note_ch,
                "color": "#CD2990"
            },
            "ganmao":{
                "value": weather_dict['感冒指数'],
                "color": "#5455510"
            },
            "yundong": {
                "value": "🏓：" + weather_dict['运动指数'],
                "color": "#456177"
            },
            "chuanyi":{
                "value": "👕：" + weather_dict['穿衣指数'],
                "color": "#512348"
            }
        }
    }
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data)

#     print(json.loads(response.text))

if __name__ == '__main__':
    # 获取accessToken
    accessToken = get_access_token()
    # print('accessToken sucess:{}'.format(accessToken))
    # 接收的用户
    user = config.user
    # 传入省份和市获取天气信息
    province, city = config.province, config.city
    w_province, w_city = config.w_province, config.w_city
    weather, max_temperature, min_temperature = get_weather(province, city)
    w_weather,w_max_temperature, w_min_temperature = get_weather(w_province, w_city)
    # print(weather, max_temperature, min_temperature)

    # 获取词霸每日金句
    note_ch, note_en = get_ciba()

    # 天气提醒字符处理
    def weatherProcess(adjest_con,adjest_discr,adjest_advi):
        dict = {}
        for i,j in zip(adjest_con,adjest_advi):
            name = i.string
            discr = j.string 
            discr = discr.replace('您','老婆')
            discr = discr.replace('。','')
            dict[name] = discr
        return dict
    adjest_con,adjest_discr,adjest_advi = get_ad()
    weather_dict = weatherProcess(adjest_con,adjest_discr,adjest_advi)
    # print(weather_dict['穿衣指数'])
    # 公众号推送消息
#     print(user, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_en)
    for i in user:
        send_message(i, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_en,weather_dict,w_city,w_weather,w_max_temperature, w_min_temperature)
        print('用户{}发送成功'.format(i))
