# -*- coding: utf-8 -*-
from collections import defaultdict
from typing import Any, List

import requests

from config import (
    AUDIO_API,
    AUDIOS_API,
    BASE_AUDIO_LINK_URL,
    CATE_DICT,
    IMAGE_BASE_URL,
    MP3_BASE_URL,
    AUDIOS_CATE_URL,
)

CATE_DICT = {str(v): k for k, v in CATE_DICT.items()}


def paser_timeflow(timelines_dict):
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


def get_audio_other_info(API: str, audio_id: str):
    user_list = []
    flow_dict = {}
    r = requests.get(API.format(audio_id=audio_id))
    if not r:
        print(r.text)
        return []

    included = r.json()["included"]
    for i in included:
        if i["type"] == "users":
            user_list.append(parser_djs(i))
        if i["type"] == "timelines":
            flow_dict.update(paser_timeflow(i))
        if i["type"] == "medias":
            audio_mp3_url = parser_mp3_url(i)
        else:
            continue
    return user_list, flow_dict, audio_mp3_url


def get_audios_info(API: str, limit=10, offset=0) -> List[Any]:
    r = requests.get(API.format(limit=limit, offset=offset))
    if not r:
        print(r.text)
        return []
    response_json = r.json()
    audio_info_dict = response_json["data"]
    audios_result = []
    for d in audio_info_dict:
        attributes = d["attributes"]
        audio_id = d["id"]
        audio_name = attributes["title"]
        audio_date = attributes["published-at"].split("T")[0]
        audio_url = BASE_AUDIO_LINK_URL + audio_id
        audio_djs, audio_flow_info, audio_mp3_url = get_audio_other_info(
            AUDIO_API, audio_id
        )
        audio_like = attributes["likes-count"]
        audio_comment = attributes["comments-count"]
        audio_cate = d["relationships"]["category"]["data"]["id"]
        audio_cate_name = CATE_DICT.get(audio_cate, "")
        audios_result.append(
            [
                audio_id,
                audio_name,
                audio_date,
                audio_url,
                audio_mp3_url,
                str(audio_flow_info),
                str(audio_djs),
                int(audio_like),
                int(audio_comment),
                AUDIOS_CATE_URL + audio_cate,
                audio_cate_name,
            ]
        )
    return audios_result
