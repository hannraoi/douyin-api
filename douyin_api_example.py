# -*- coding: utf-8 -*-
'''
Created on 2019/4/14 9:29 PM
---------
@summary: 抖音接口API
---------
@qq: 564773807
'''

import json
import random
import time
import warnings
from urllib.parse import urlencode

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SERVICE_URL = 'http://bzkj.tech:2117/douyin/encrypt_url'

HEADERS = {
    'User-Agent': 'com.ss.android.ugc.aweme/390 (Linux; U; Android 7.1.2; zh_CN; Redmi 5A; Build/N2G47H; Cronet/58.0.2991.0)'
}

DEVICE_PARAMS = json.load(open('douyin_devices.json', 'r'))


def get_device_params():
    """
    获取设备参数
    """

    return random.choice(DEVICE_PARAMS)


def joint_url(url, params):
    """
    将url拼接参数
    """

    params = urlencode(params)
    separator = '?' if '?' not in url else '&'
    return url + separator + params


def encrypy_url(url):
    """
    获取有效的地址
    """

    device_params = get_device_params()
    url = joint_url(url, device_params)

    params = {
        'url': url,
        'secret_key': 'iM0hCLU0fZc885zfkFPX3UJwSHbYyam9ji0WglnT3fc='  # 密钥
    }

    res = requests.get(SERVICE_URL, params=params)
    data = res.json()
    if data.get('code') != 200:
        raise Exception(data.get('msg'))
    url = data.get('data').get('url')

    return url


def douyin_get(url, cookies=None):
    """
    发请求
    """

    url = encrypy_url(url)
    response = requests.get(url, headers=HEADERS, cookies=cookies, verify=False)
    data = response.json()
    response.close()
    return data


def get_cookies():
    """
    获取cookies
    :return: {'odin_tt': '32d9d9a534736f41356a200d4620150b7bf8fbc5aa6048557fdd09da6d00576b9e0aa9c6f11ad5e5855ef29e98c39cfd29d72c1ac6054274080bac1b559e2fbb'}
    """

    warnings.warn('获取cookie中，推荐当获取到的cookie用redis缓存起来，做成cookie池。一个进程负责生产cookie，保持一定数量的cookies。 爬虫负责使用，cookie失效删除')
    douyin_url = 'https://api.amemv.com/aweme/v1/feed/?type=0&max_cursor=0&min_cursor=-1&count=6&volume=0.0&pull_type=2&need_relieve_aweme=0&filter_warn=0&req_from&is_cold_start=0'
    url = encrypy_url(douyin_url)
    response = requests.get(url, headers=HEADERS)
    cookies = response.cookies.get_dict()
    response.close()

    if 'odin_tt' in cookies:
        return cookies
    else:
        raise Exception('获取cookie失败')


def get_feed_info():
    """
    获取主页推荐视频列表
    """

    douyin_url = 'https://api.amemv.com/aweme/v1/feed/?type=0&max_cursor=0&min_cursor=-1&count=6&volume=0.0&pull_type=2&need_relieve_aweme=0&filter_warn=0&req_from&is_cold_start=0'
    return douyin_get(douyin_url)


def get_user_info(user_id, cookies):
    """
    获取用户信息
    :param user_id: 用户id 如 107776778033
    :param cookies: cookie
    :return: json
    """

    douyin_url = 'https://aweme.snssdk.com/aweme/v1/user/?user_id={}'.format(user_id)
    return douyin_get(douyin_url, cookies)


def get_music_info(music_id):
    """
    获取音乐信息
    :param music_id: 音乐id 如 6674901603562277643
    :return: json
    """

    douyin_url = 'https://aweme.snssdk.com/aweme/v1/music/detail/?music_id={}'.format(music_id)
    return douyin_get(douyin_url)


def get_favorite_video_info(user_id, max_cursor=0):
    """
    获取用户喜欢的视频
    :param user_id: 用户id 如 107776778033
    :param max_cursor: 第一页为0，翻页时为返回数据中的max_cursor
    :return: json
    """

    douyin_url = 'https://aweme.snssdk.com/aweme/v1/aweme/favorite/?max_cursor={}&user_id={}&count=20'.format(max_cursor, user_id)
    return douyin_get(douyin_url)


def get_own_video_info(user_id, max_cursor=0):
    """
    获取自己的视频
    :param user_id: 用户id 如 107776778033
    :param max_cursor: 第一页为0，翻页时为返回数据中的max_cursor
    :return: json
    """

    douyin_url = 'https://aweme.snssdk.com/aweme/v1/aweme/post/?max_cursor={}&user_id={}&count=20'.format(max_cursor, user_id)
    return douyin_get(douyin_url)


def get_comment_info(aweme_id, cursor=0):
    """
    获取评论信息
    :param aweme_id: 视频id 如 6679382734034554126
    :param cursor: 视频列表游标，翻页时递增20
    :return:
    """

    douyin_url = 'https://aweme.snssdk.com/aweme/v2/comment/list/?aweme_id={}&cursor={}&count=20'.format(aweme_id, cursor)
    return douyin_get(douyin_url)


def get_follower_list(user_id, max_time, cookies):
    """
    获取粉丝列表
    :param user_id: 用户id 如 107776778033
    :param max_time: 第一页为当前秒级时间戳，翻页时为返回数据中的min_time
    :param cookies: cookie
    :return: json
    """

    douyin_url = 'https://aweme.snssdk.com/aweme/v1/user/follower/list/?user_id={}&max_time={}&count=20&offset=0'.format(user_id, max_time)
    return douyin_get(douyin_url, cookies)


def get_following_list(user_id, max_time, cookies):
    """
    获取关注列表
    :param user_id: 用户id 如 107776778033
    :param max_time: 第一页为当前秒级时间戳，翻页时为返回数据中的min_time
    :param cookies: cookie
    :return: json
    """

    douyin_url = 'https://aweme.snssdk.com/aweme/v1/user/following/list/?user_id={}&max_time={}&count=20&offset=0'.format(user_id, max_time)  # max_time 为游标
    return douyin_get(douyin_url, cookies)


if __name__ == '__main__':
    cookies = get_cookies()
    print(cookies)

    data = get_feed_info()
    print(data)

    user_id = '107776778033'
    data = get_user_info(user_id, cookies)
    print(data)

    music_id = '6674901603562277643'
    data = get_music_info(music_id)
    print(data)

    user_id = '107776778033'
    data = get_favorite_video_info(user_id, max_cursor=0)
    print(data)

    user_id = '107776778033'
    data = get_own_video_info(user_id, max_cursor=0)
    print(data)

    aweme_id = '6679382734034554126'
    data = get_comment_info(aweme_id, cursor=0)
    print(data)

    user_id = '107776778033'
    data = get_follower_list(user_id, max_time=int(time.time()), cookies=cookies)
    print(data)

    user_id = '107776778033'
    data = get_following_list(user_id, max_time=int(time.time()), cookies=cookies)
    print(data)
