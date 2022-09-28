#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
from typing import Optional, Dict, Union, Tuple

import requests


def get_config() -> dict:
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def get_weather_data(city: str = '北京') -> Optional[dict]:
    # get chinese city weather
    url = f'https://autodev.openspeech.cn/csp/api/v2.1/weather'
    params = {
        'city': city,
        'openId': 'aiuicus',
        'clientType': 'windows',
        'sign': 'windows',
    }
    res = requests.get(url, params)
    if res.ok:
        data = res.json()
        if data['code'] == 0:
            return data['data']['list'][0]
    return None


def get_province(weather_data: dict) -> str:
    if weather_data:
        return weather_data['province']
    return ''


def get_covid_data(province: str, city: str) -> Optional[dict]:
    url = 'https://lab.isaaclin.cn/nCoV/api/area'
    if not province.endswith('省'):
        province += '省'
    params = {
        'latest': 1,
        'province': province,
    }
    res = requests.get(url, params)
    if res.ok:
        data = res.json()['results'][0]
        cities = data['cities']
        for city_data in cities:
            if city_data['cityName'] == city:
                return city_data
    return None


def get_timedelta_days(start: Union[str, datetime], end: Union[str, datetime]) -> int:
    if isinstance(start, str):
        start = datetime.strptime(start, '%Y-%m-%d')
    if isinstance(end, str):
        end = datetime.strptime(end, '%Y-%m-%d')
    return (end - start).days


def format_float(a: float) -> str:
    return '%.2f' % a


def get_content(friend: Dict[str, str]) -> Tuple[str, Dict[str, dict]]:
    weather_data = get_weather_data(friend['city'])
    love_date = friend.get('love_date')
    # 打招呼
    if love_date:
        greetings = '早安，我爱你'
        template = [f'<h3><p>{greetings}</p></h3>']
    else:
        greetings = '早安'
        template = [f'<h3><p>{greetings}</p></h3>']
    template_json = {'greetings': {'value': greetings, 'color': '#FF6347'}}
    # 获取日期
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().weekday()
    template.append(
        f'<p><span style="color:#c3e88d;">今天是</span><span>{today}周{weekday}</span></p>'
    )
    template_json['today'] = {'value': today, 'color': '#c3e88d'}
    template_json['weekday'] = {'value': weekday, 'color': '#c3e88d'}
    # 获取天气
    if weather_data:
        template.append(f'<p><span>今天{weather_data["city"]}天气：{weather_data["weather"]}</span></p>')
        template_json['city'] = {'value': weather_data['city'], 'color': '#c3e88d'}
        template_json['weather'] = {'value': weather_data['weather'], 'color': '#FF8C00'}

        temp, low, high = weather_data['temp'], weather_data['low'], weather_data['high']
        template.append(
            f'<p>温度：<span style="color:#FF9900;">{temp}℃</span>，'
            f'最低温度：<span style="color:#009900;">{low}℃</span>，'
            f'最高温度：<span style="color:#E53333;">{high}℃</span></p>'
        )
        template_json['temp'] = {'value': str(temp), 'color': '#FF8C00'}
        template_json['low'] = {'value': str(low), 'color': '#00FFFF'}
        template_json['high'] = {'value': str(high), 'color': '#CC3300'}

        humidity, wind = weather_data['humidity'], weather_data['wind']
        template.append(f'<p>湿度：{humidity}，风向：{wind}</p>')
        template_json['humidity'] = {'value': humidity, 'color': '#6600FF'}
        template_json['wind'] = {'value': wind, 'color': '#663300'}

        pm25, airQuality = weather_data['pm25'], weather_data['airQuality']
        if pm25 <= 35:
            pm25_color = '#DAF7A6'
        elif 35 < pm25 <= 75:
            pm25_color = '#FFC300'
        elif 75 < pm25 <= 115:
            pm25_color = '#FF5733'
        else:
            pm25_color = '#C70039'
        template.append(f'<p>PM2.5：<span style="color:{pm25_color};">{pm25}</span>，'
                        f'空气质量：<span style="color:{pm25_color};">{airQuality}</span></p>')
        template_json['pm25'] = {'value': str(pm25), 'color': pm25_color}
        template_json['airQuality'] = {'value': airQuality, 'color': pm25_color}

        # 获取疫情数据
        covid_data = get_covid_data(weather_data['province'], friend['city'])
        if covid_data:
            currentConfirmedCount, suspectedCount = covid_data['currentConfirmedCount'], covid_data['suspectedCount']
            template.append('<p>疫情：</p>')
            template.append(f'<p>现有确诊：<span style="color:#FF0000;">{currentConfirmedCount}</span>，'
                            f'现有疑似：<span style="color:#FF0000;">{suspectedCount}</span></p>')
            template_json['currentConfirmedCount'] = {'value': currentConfirmedCount, 'color': '#FF0000'}
            template_json['suspectedCount'] = {'value': suspectedCount, 'color': '#FF0000'}

    now = datetime.now()
    # 生日
    if friend.get('birthday'):
        birthday = datetime.strptime(friend['birthday'], '%Y-%m-%d')
        birthday = birthday.replace(year=now.year)
        if now > birthday:
            birthday = birthday.replace(year=now.year + 1)
        time_before_birthday = get_timedelta_days(now, birthday)
        template.append(
            f'<br><p>距离{friend["name"]}的生日有<span style="color:#F08080;">{time_before_birthday}</span>天🎂</p>')
        template_json['birthday'] = {'value': time_before_birthday, 'color': '#F08080'}
        template_json['name'] = {'value': friend['name'], 'color': '#F08080'}
    # 获取爱情时间
    if friend.get('love_date'):
        time_before_love_date = get_timedelta_days(love_date, now)
        template.append(f'<p>我们在一起已经<span style="color:#FFC0CB;">{time_before_love_date}</span>天💌</p><br>')
        template_json['love_date'] = {'value': time_before_love_date, 'color': '#FFC0CB'}
    return ''.join(template), template_json


def get_access_token(config: dict) -> Optional[str]:
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    params = {
        'grant_type': 'client_credential',
        'appid': app_id,
        'secret': app_secret
    }
    try:
        access_token = requests.get(url, params).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        return None
    # print(access_token)
    return access_token


def push_plus(content: str, token: str, to: str = ''):
    url = 'https://www.pushplus.plus/send'
    headers = {'Content-Type': 'application/json'}
    data = {
        'token': token,
        'title': '早安，午安，晚安',
        'content': content,
        'to': to,
    }
    res = requests.post(url, headers=headers, json=data)
    if res.ok:
        print(res.json())
        return True
    return False


def send_wechat_official_account_message(data, friend, config):
    # 发送微信公众号模板消息
    access_token = get_access_token(config)
    if not access_token:
        return
    url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
    payload = {'data': data, 'touser': friend['touser'], 'template_id': config['template_id'],
               'url': 'https://weixin.qq.com/download'}
    res = requests.post(url, json=payload).json()
    print(res)


def main():
    config = get_config()

    for friend in config['friends']:
        if config.get('pushplus'):
            content = get_content(friend)
            send_wechat_official_account_message(content[1], friend, config['official_account'])
            push_plus(content[0], config['pushplus']['token'], friend['to'])


if __name__ == '__main__':
    main()
