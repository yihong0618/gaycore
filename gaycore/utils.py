#!/usr/bin/env python # encoding: utf-8
from collections import defaultdict
from functools import partial
import requests
from gaycore.config import (
    IMAGE_BASE_URL,
    MP3_BASE_URL,
    AUDIOS_API,
    PLAYLIST_API,
    CATE_DICT,
    PLAYLIST_DICT,
    AUDIOS_CATE_API,
    AUDIO_PLAYLIST_URL,
)
from rich import print


# func to format the content
def chunkstring(string, length):
    return [string[0 + i : length + i] for i in range(0, len(string), length)]


def get_audios_info(
    API, offset=0, sort="-published-at", playlist_id=None, cate_id=None
):
    if cate_id:
        r = requests.get(API.format(cate_id=cate_id, limit=10, offset=offset))
    elif playlist_id:
        r = requests.get(API.format(playlist_id=playlist_id, limit=10, offset=offset))
    else:
        r = requests.get(API.format(sort=sort, limit=10, offset=offset))
    if not r:
        return []

    response_json = r.json()
    audio_info_dict = response_json["data"]
    results_dict = {}
    for d in audio_info_dict:
        attributes = d["attributes"]
        results_dict[attributes["title"]] = d["id"]
    return results_dict


def paser_timeflow(timelines_dict):
    """
    获取时间轴用于播放的展示
    """
    timestamp_dict = defaultdict(dict)
    timelines_dict = timelines_dict["attributes"]
    try:
        flow_time_key = timelines_dict.get("at")
        timestamp_dict[flow_time_key]["title"] = timelines_dict.get("title", "")
        timestamp_dict[flow_time_key]["content"] = timelines_dict.get("content", "")
        timestamp_dict[flow_time_key]["quote_href"] = timelines_dict.get(
            "quote-href", ""
        )
        timestamp_dict[flow_time_key]["img"] = IMAGE_BASE_URL + (
            timelines_dict.get("asset", {}) or ""
        )
        return timestamp_dict
    except Exception as e:
        raise ("parser_timefoow error {}".format(e))


def parser_djs(users_dict):
    try:
        return users_dict["id"], users_dict["attributes"]["nickname"]
    except Exception as e:
        raise ("parser_djs error {}".format(e))


def parser_mp3_url(medias_dict):
    try:
        return MP3_BASE_URL + medias_dict["attributes"]["audio"]
    except Exception as e:
        raise ("parser_mp3_url error {}".format(e))


def get_audio_info(API, audio_id):
    flow_dict = {}
    r = requests.get(API.format(audio_id=audio_id))
    if not r:
        return []
    audio_mp3_url = ""
    included = r.json()["included"]
    for i in included:
        if i["type"] == "timelines":
            flow_dict.update(paser_timeflow(i))
        if i["type"] == "medias":
            audio_mp3_url = parser_mp3_url(i)
        else:
            continue
    return flow_dict, audio_mp3_url


def make_cate_dict():
    return {
        k: partial(get_audios_info, AUDIOS_CATE_API, cate_id=v)
        for k, v in CATE_DICT.items()
    }


def make_playlist_dict():
    return {
        k: partial(get_audios_info, AUDIO_PLAYLIST_URL, playlist_id=v)
        for k, v in PLAYLIST_DICT.items()
    }


def _make_playlist_dict(offset=0, playlist_dict={}):
    r = requests.get(PLAYLIST_API.format(limit=100, offset=0))
    data = r.json()["data"]
    for d in data:
        playlist_dict[d["attributes"]["title"]] = d["id"]
    return playlist_dict


recent_func = partial(get_audios_info, AUDIOS_API)
likes_func = partial(get_audios_info, AUDIOS_API, sort="-likes-count")
comments_func = partial(get_audios_info, AUDIOS_API, sort="-comments-count")
bookmarks_func = partial(get_audios_info, AUDIOS_API, sort="-bookmarks-count")
