# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import re
import time
from collections import defaultdict
import asyncio
import requests
from bs4 import BeautifulSoup as Soup
import aiohttp

BASE_AUDIO_CATE_URL = "https://www.gcores.com/categories/9/originals"
BASE_AUDIO_LINK_URL = "https://www.gcores.com/radios/"
TEST_AUDIO_LINK = "https://www.gcores.com/radios/105962"
UPLOAD_BASE_URL = "https://alioss.gcores.com"
headers = {
    'User-agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
}

flow_pattern = re.compile(r"timelines:(.*)jplayerSwf", re.DOTALL)


def make_soup(url):
    try:
        response = requests.get(url).text
        soup = Soup(response, "html.parser")
    except:
        soup = None
    return soup


def get_mp3_url(soup):
    https_url = soup.find("p", class_="story_actions").find("a").attrs["href"]
    return https_url.replace("https", "http")  # replace https to http for mpg123


def get_all_page_link(soup):
    if not soup:
        return   # to do

    audio_list = soup.find_all("div", class_="showcase_img")
    audio_link_list = [i.find("a").attrs["href"] for i in audio_list]
    return audio_link_list


def make_name_mp3_dict(soup):
    if not soup:
        return dict()

    audio_list = soup.find_all("div", class_="showcase_img")
    audio_name_list = [i.img.attrs['alt'] for i in audio_list]
    audio_link_list = [i.find("a").attrs["href"] for i in audio_list]
    mp3_link_list = [get_mp3_url(i) for i in audio_link_list]
    time_flow_list = [get_timeflow_info(i) for i in audio_link_list]
    return dict(zip(audio_name_list, zip(audio_link_list, mp3_link_list)))


def info_paser(string):
    text = string.replace("\n", "")
    text = re.sub(" +", " ", text)
    text = text.lstrip().rstrip()
    return text


def get_djs_id(soup):
    try:
        djs_info = soup.find("div", class_="story_djs_items")
        djs_info = djs_info.find_all("a")
        djs_id_link = [i["href"] for i in djs_info]
        djs_id = [i.split("/")[-1] for i in djs_id_link]
    except:
        djs_id = []
    return djs_id


def get_djs_info(soup):
    try:
        djs = soup.find("div", class_="story_djs_items")
        if not djs:
            djs_list = []
        djs_text = djs.get_text()
        djs_text = info_paser(djs_text)
        djs_name = djs_text.split()
        djs_id = get_djs_id(soup)
        djs_info = list(zip(djs_name, djs_id))
        return djs_info
    except:
        return []


def get_timeflow_info(soup):
    div = soup.find_all("div")[-1]
    src = div.find("script", type="text/javascript").text
    try:
        flow_info = re.search(flow_pattern, src).group(1)
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


def showcase_paser(soup):
    date = soup.get_text()
    date = info_paser(date).split()[-1]
    audio_category = soup.find('a')['href']
    audio_category = info_paser(audio_category)
    audio_category_name = soup.find('a').get_text()
    audio_category_name = info_paser(audio_category_name)
    return date, audio_category, audio_category_name


def meta_num_paser(soup):
    audio_meta_num = soup.get_text()
    audio_meta_num = info_paser(audio_meta_num)
    like, comment = audio_meta_num.split()[:-1]
    return like, comment


def get_cate_audio_info(soup):
    if not soup:
        return dict()

    audio_list = soup.find_all("div", class_="showcase_img")
    audio_name_list = [i.img.attrs['alt'] for i in audio_list]
    audio_link_list = [i.find("a").attrs["href"] for i in  audio_list]
    audio_showcase = soup.find_all("div", class_="showcase_time")
    audio_showcase_list = [showcase_paser(i) for i in audio_showcase]
    audio_meta_num = soup.find_all("div", class_="showcase_meta")
    audio_meta_num_list = [meta_num_paser(i) for i in audio_meta_num]
    return dict(zip(audio_link_list, list(zip(audio_name_list, audio_showcase_list, audio_meta_num_list))))


# 获取一个url的信息
def get_info_audio_url(soup):
    mp3_url = get_mp3_url(soup)
    flow_info = get_timeflow_info(soup)
    djs_info = get_djs_info(soup)
    return mp3_url, djs_info, flow_info


def parsr_timeflow_info(flow_info):
    # parser the gcores timeflow info to {time: [title, content, quate_href]} dict-list dict for curses to display
    time_flow_dict = defaultdict(dict)
    for i in flow_info:
        flow_time_key = i.get("at")
        time_flow_dict[flow_time_key]["title"] = i.get("title", "")
        time_flow_dict[flow_time_key]["content"] = i.get("content", "")
        time_flow_dict[flow_time_key]["quote_href"] = i.get("quote_href", "")
        time_flow_dict[flow_time_key]["img"] = UPLOAD_BASE_URL + i.get("asset", {}).get("limit", {}).get("url", "")
    return dict(time_flow_dict)


async def fetch_gcore_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            r = await resp.text()
            soup = Soup(r, "html.parser")
            djs_info = str(get_djs_info(soup))
            mp3_url = get_mp3_url(soup)
            time_flow_info = get_timeflow_info(soup)
            time_flow_info = str(parsr_timeflow_info(time_flow_info))
            return url, mp3_url, djs_info, time_flow_info


# 获取一个cate的信息
def get_one_cate_info(url):
    event_loop = asyncio.get_event_loop()
    soup = make_soup(url)
    sub_url_list = get_all_page_link(soup)
    tasks = [fetch_gcore_data(u) for u in sub_url_list]
    results = event_loop.run_until_complete(asyncio.gather(*tasks))
    # 获取该cate_url下的所有info
    cate_info_dict = get_cate_audio_info(soup)
    results = [cate_info_dict.get(i[0]) + i for i in results]
    return results

# print(get_one_cate_info(BASE_AUDIO_CATE_URL)[0])
