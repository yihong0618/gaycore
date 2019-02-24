#!/usr/bin/env python # encoding: utf-8

import time
import json
import re
from collections import Counter
import asyncio
from functools import partial
import aiohttp
import requests
from bs4 import BeautifulSoup as Soup
from gaycore.spider import *
from gaycore.config import *


FLOW_PATTERN = re.compile(r"timelines:(.*)jplayerSwf", re.DOTALL)


# func to format the content
def chunkstring(string, length):
    return [string[0+i:length+i] for i in range(0, len(string), length)]


def make_soup(url):
    try:
        response = requests.get(url).text
        soup = Soup(response, "html.parser")
    except:
        soup = None
    return soup


def get_mp3_url(soup):
    https_url = soup.find("p", class_="story_actions").find("a").attrs["href"]
    # replace https to http for mpg123
    return https_url.replace("https", "http")


def make_name_mp3_dict(url):
    soup = make_soup(url)
    if not soup:
        return dict()

    audio_list = soup.find_all("div", class_="showcase_img")
    audio_name_list = [i.img.attrs['alt'] for i in audio_list]
    audio_link_list = [i.find("a").attrs["href"] for i in audio_list]
    mp3_link_list = [get_mp3_url(make_soup(i)) for i in audio_link_list]
    return dict(zip(audio_name_list, zip(audio_link_list, mp3_link_list)))


def get_djs_info(soup):
    try:
        djs = soup.find("div", class_="story_djs_items")
        if not djs:
            djs_list = []
        djs_text = djs.get_text().replace("\n", "")
        djs_text = re.sub(" +", " ", djs_text)
        djs_list = djs_text.split()
        return djs_list
    except:
        return []


def get_timeflow_info(soup):
    div = soup.find_all("div")[-1]
    src = div.find("script", type="text/javascript").text
    try:
        flow_info = re.search(FLOW_PATTERN, src).group(1)
    except:
        flow_info = ''  # todo
    # to make a info list an fmt it
    if not flow_info:
        return []
    flow_info = flow_info.lstrip()
    flow_info = flow_info.rstrip()
    flow_info = flow_info[:-1]
    # 此处处理json中的null null无法eval获取
    try:
        flow_info_list = eval(flow_info, {"null": "", "false": "", "true": ""})
    except:
        flow_info_list = []
    return flow_info_list


def paser_showcase(soup):
    date = soup.get_text()
    audio_category = soup.find('a')['href']
    audio_category_name = soup.find('a').get_text()
    return date, audio_category, audio_category_name


def get_showcase_info(soup):
    name = soup.find('h1', class_="story_title").get_text()
    name = info_paser(name)
    mp3_url = get_mp3_url(soup)
    djs_info = str(get_djs_info(soup))
    time_flow_info = get_timeflow_info(soup)
    time_flow_info = parsr_timeflow_info(time_flow_info)
    return name, mp3_url, time_flow_info, djs_info


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=5) as resp:
            r = await resp.text()
            name, mp3_url, time_flow_info, djs_info = get_showcase_info(
                Soup(r, "html.parser"))
            return name, (url, mp3_url, time_flow_info, djs_info)


def async_make_name_mp3_dict(url):
    url_list = get_all_page_link(make_soup(url))
    event_loop = asyncio.get_event_loop()
    tasks = [fetch_data(i) for i in url_list]
    results = event_loop.run_until_complete(asyncio.gather(*tasks))
    return dict(results)


def api_make_name_mp3_dict(api, name='', page=0):

    results_dict = {}
    info_json = requests.get(api.format(name, page)).text
    info_list = json.loads(info_json).get("result", [])
    for info in info_list:
        results_dict[info.get("audio_name")] = (
            info.get("audio_url", ""), info.get("audio_mp3_url", ""))
    return results_dict


def api_get_play_info(api, audio_id):
    info_json = requests.get(api.format(audio_id)).text
    info_list = json.loads(info_json).get("result", [])
    return info_list


def make_base_dict_func(BASE_DICT, API):
    category_dict = {}
    for cate_name, cate_name_num in BASE_DICT.items():
        category_dict[cate_name] = partial(
            api_make_name_mp3_dict, API, cate_name_num)
    return category_dict


def get_top_djs(limit=50):
    info_json = requests.get(API_ALL_DJS).text
    result = json.loads(info_json).get("result", [])
    result = [eval(i) for i in result]

    def make_result():
        for i in result:
            for j in i:
                yield j

    top_djs = Counter(list(make_result())).most_common(limit)
    return dict(top_djs)


def make_djs_dict_func(top_djs):
    djs_dict = {}
    for i, j in top_djs.items():
        djs_dict[i[0]+"    电台数量" +
                 str(j)] = partial(api_make_name_mp3_dict, API_DJS, i[0])
    return djs_dict


# 主播字典
API_DJS_DICT = make_djs_dict_func(get_top_djs())

# 分类字典
API_CATEGORY_DICT = make_base_dict_func(CATE_DICT, API_CATEGORY)
API_TOPIC_DICT = make_base_dict_func(TOPIC_DICT, API_TOPIC)

recent_func = partial(api_make_name_mp3_dict, API_RECENT)
hot_comment_func = partial(api_make_name_mp3_dict, API_HOT_COMMENT)
hot_like_func = partial(api_make_name_mp3_dict, API_HOT_LIKE)
playinfo_func = partial(api_get_play_info, API_PLAY_INFO)
