#!/usr/bin/env python # encoding: utf-8
from collections import defaultdict
from functools import partial
import json
import requests
from curl_cffi import requests as curl_requests
from gaycore.config import (
    IMAGE_BASE_URL,
    MP3_BASE_URL,
    AUDIOS_API,
    LATEST_RADIOS_API,
    PLAYLIST_API,
    CATE_DICT,
    PLAYLIST_DICT,
    AUDIOS_CATE_API,
    AUDIO_PLAYLIST_URL,
)


def _get_json(url, timeout=20):
    """优先用 requests；若被 WAF 返回 HTML，则回退到 curl_cffi 取 JSON。"""

    try:
        r = requests.get(url, timeout=timeout)
        content_type = (r.headers.get("content-type") or "").lower()
        if r.ok and ("json" in content_type or r.text.lstrip().startswith("{")):
            return r.json()
    except Exception:
        pass

    # 使用 curl_cffi 模拟浏览器请求，绕过 WAF
    r = curl_requests.get(
        url,
        timeout=timeout,
        headers={
            "Accept": "application/vnd.api+json, application/json;q=0.9,*/*;q=0.8"
        },
        impersonate="chrome",
    )
    return r.json()


# func to format the content
def chunkstring(string, length):
    return [string[0 + i : length + i] for i in range(0, len(string), length)]


def get_audios_info(
    API, offset=0, sort="-published-at", playlist_id=None, cate_id=None, page_size=10
):
    """获取音频列表，自动过滤付费节目并确保返回足够数量的结果"""
    results_dict = {}
    # 每页需要 page_size 个结果，从 offset * page_size 开始
    need_start = offset * page_size
    need_end = need_start + page_size

    collected = []
    batch_limit = 50  # 每次请求更多数据以应对过滤
    batch_offset = need_start
    max_batches = 10

    for _ in range(max_batches):
        if cate_id:
            response_json = _get_json(
                API.format(cate_id=cate_id, limit=batch_limit, offset=batch_offset)
            )
        elif playlist_id:
            response_json = _get_json(
                API.format(
                    playlist_id=playlist_id, limit=batch_limit, offset=batch_offset
                )
            )
        else:
            response_json = _get_json(
                API.format(sort=sort, limit=batch_limit, offset=batch_offset)
            )

        audio_info_dict = response_json.get("data", [])

        for d in audio_info_dict:
            attributes = d["attributes"]
            # 过滤付费节目
            if attributes.get("is-require-privilege", False):
                continue
            collected.append((attributes["title"], d["id"]))

        # 收集够了就停止
        if len(collected) >= page_size:
            break

        # 如果返回数据不足，说明没有更多了
        if len(audio_info_dict) < batch_limit:
            break

        batch_offset += batch_limit

    # 只返回当前页需要的数据
    for title, audio_id in collected[:page_size]:
        results_dict[title] = audio_id

    return results_dict


def _parse_latest_radios_payload(payload):
    included = payload.get("included", []) or []
    included_index = {(i.get("type"), i.get("id")): i for i in included}

    results = []
    for item in payload.get("data", []) or []:
        rel = item.get("relationships", {}) or {}
        radio_rel = (rel.get("radio", {}) or {}).get("data") or {}
        radio_id = radio_rel.get("id")
        if not radio_id:
            continue

        radio_obj = included_index.get(("radios", radio_id)) or {}
        radio_attrs = radio_obj.get("attributes") or {}
        title = radio_attrs.get("title")
        if not title:
            # 兜底：有时 included 不完整
            title = f"radio-{radio_id}"

        # 过滤付费节目
        is_require_privilege = radio_attrs.get("is-require-privilege", False)
        if is_require_privilege:
            continue

        category_id = None
        category_rel = (
            (radio_obj.get("relationships") or {}).get("category") or {}
        ).get("data")
        if isinstance(category_rel, dict):
            category_id = category_rel.get("id")

        album_id = None
        album_rel = (rel.get("album", {}) or {}).get("data")
        if isinstance(album_rel, dict):
            album_id = album_rel.get("id")

        results.append(
            {
                "id": radio_id,
                "title": title,
                "category_id": category_id,
                "album_id": album_id,
            }
        )
    return results


def get_latest_radios_info(offset=0, cate_id=None, playlist_id=None, page_size=10):
    """返回用于 curses 菜单展示的 dict: {title: radio_id}。

    注意：为了绕过机核 gapi 的 WAF 拦截，这里用 latest-radios 接口作为数据源。
    - cate_id: 按分类过滤（基于 radio.relationships.category）
    - playlist_id: 按 album 过滤（基于 latest-radios.relationships.album）
    """

    need_start = max(0, offset) * page_size
    need_end = need_start + page_size

    collected = []
    # 机核接口限制：page[limit] 最大 100
    batch_limit = 100
    batch_offset = 0
    max_batches = 20

    for _ in range(max_batches):
        payload = _get_json(
            LATEST_RADIOS_API.format(limit=batch_limit, offset=batch_offset)
        )
        entries = _parse_latest_radios_payload(payload)

        if cate_id is not None:
            cate_id_str = str(cate_id)
            entries = [e for e in entries if (e.get("category_id") == cate_id_str)]

        if playlist_id is not None:
            playlist_id_str = str(playlist_id)
            entries = [e for e in entries if (e.get("album_id") == playlist_id_str)]

        collected.extend(entries)

        if len(collected) >= need_end:
            break

        data_len = len(payload.get("data", []) or [])
        if data_len < batch_limit:
            break
        batch_offset += batch_limit

    page_entries = collected[need_start:need_end]
    results_dict = {}
    for e in page_entries:
        title = e["title"]
        radio_id = e["id"]
        # 防止同名覆盖
        if title in results_dict and results_dict[title] != radio_id:
            title = f"{title} [{radio_id}]"
        results_dict[title] = radio_id
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
    audio_mp3_url = ""
    response_json = _get_json(API.format(audio_id=audio_id))
    included = response_json["included"]
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
    response_json = _get_json(PLAYLIST_API.format(limit=100, offset=0))
    data = response_json["data"]
    for d in data:
        playlist_dict[d["attributes"]["title"]] = d["id"]
    return playlist_dict


recent_func = partial(get_audios_info, AUDIOS_API)
likes_func = partial(get_audios_info, AUDIOS_API, sort="-likes-count")
comments_func = partial(get_audios_info, AUDIOS_API, sort="-comments-count")
bookmarks_func = partial(get_audios_info, AUDIOS_API, sort="-bookmarks-count")
