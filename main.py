from time import mktime,strptime
import cityinfo
import config
import requests
from requests import get, post
from datetime import datetime, date
import json
import bs4

def get_ad():
    baseUrl = 'http://www.weather.com.cn/weather1d/'
    # config_city = str(101180101)
    config_city = str(cityinfo.cityInfo[province][city]["AREAID"])
    print(config_city)
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
    print(condition)
    print(discription)
    print(advince)
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
    t_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    t_bj = datetime.datetime.utcnow()+ datetime.timedelta(hours=8)
    calendar = t_bj.isocalendar()
    t_bj_all = t_bj.strftime("%Y-%m-%d %H:%M")
    t_bj = t_bj.strftime("%Y-%m-%d")
    weekday = calendar[2]
    week = week_list[weekday-1]
    return week, t_bj, t_bj_all, t_utc

def get_weather(province, city):
    # 城市id
    city_id = cityinfo.cityInfo[province][city]["AREAID"]
    # city_id = 101280101
    # 毫秒级时间戳
#     t = (int(round(time() * 1000)))
    week, t_bj, t_bj_all, t_utc = get_time()
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


def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature, note_ch, note_en,weather_dict):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week, t_bj, t_bj_all, t_utc = get_time()
    today = t_bj
    print(today,week)
    # 获取在一起的日子的日期格式
    love_year = int(config.love_date.split("-")[0])
    love_month = int(config.love_date.split("-")[1])
    love_day = int(config.love_date.split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
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
        "template_id": config.template_id,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": "#6495ED"
            },
            "city": {
                "value": city_name,
                "color": "#EE7600"
            },
            "weather": {
                "value": weather,
                "color": "#ED9121"
            },
            "min_temperature": {
                "value": min_temperature,
                "color": "#87CEEB"
            },
            "max_temperature": {
              "value": max_temperature,
              "color": "#FF6100"
            },
            "love_day": {
              "value": love_days,
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
                "value": weather_dict['运动指数'],
                "color": "#456177"
            },
            "chuanyi":{
                "value": weather_dict['穿衣指数'],
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

    # print(json.loads(response.text))

if __name__ == '__main__':
    # 获取accessToken
    accessToken = get_access_token()
    # print('accessToken sucess:{}'.format(accessToken))
    # 接收的用户
    user = config.user
    # 传入省份和市获取天气信息
    province, city = config.province, config.city
    weather, max_temperature, min_temperature = get_weather(province, city)
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
    # print(user, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_en)
    for i in user:
        send_message(i, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_en,weather_dict)

