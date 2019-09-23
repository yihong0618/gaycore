#!/usr/bin/env python # encoding: utf-8

import json
from collections import Counter
from functools import partial
import requests
from gaycore.config import *


# func to format the content
def chunkstring(string, length):
    return [string[0+i:length+i] for i in range(0, len(string), length)]


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
