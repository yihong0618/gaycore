#!/usr/bin/env python # encoding: utf-8

import time
import json
import re
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup as Soup
from spider import *


BASE_AUDIO_CATE_URL = "https://www.gcores.com/categories/9/originals"
BASE_AUDIO_LINK_URL = "https://www.gcores.com/radios/"
TEST_AUDIO_LINK = "https://www.gcores.com/radios/105962"

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
            name, mp3_url, time_flow_info, djs_info = get_showcase_info(Soup(r, "html.parser"))
            return name, (url, mp3_url, time_flow_info, djs_info)


def async_make_name_mp3_dict(url):
    url_list = get_all_page_link(make_soup(url))
    event_loop = asyncio.get_event_loop()
    tasks = [fetch_data(i) for i in url_list]
    results = event_loop.run_until_complete(asyncio.gather(*tasks))
    return dict(results)


def api_make_name_mp3_dict(page):
    results_dict = {}
    info_json = requests.get("http://127.0.0.1:3000/audios?page=".format(page)).text
    info_list = json.loads(info_json).get("result", [])
    for info in info_list:
        results_dict[info.get("audio_name")] = (info.get("audio_url"), info.get("audio_mp3_url"), info.get("audio_flow_info"), info.get("audio_djs"))
    return results_dict

