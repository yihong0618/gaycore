# -*- coding: utf-8 -*-


BOX_WIDTH = 80
BOX_HEIGHT = 3
PAD_WIDTH = 400
PAD_HEIGHT = 1000

ALI_BASE_URL = "http://47.93.19.8:3000"
LOCAL_BASE_URL = "http://127.0.0.1:3000"
API_URL = ALI_BASE_URL
# API_URL = LOCAL_BASE_URL


API_PLAY_INFO = API_URL + "/audio/{}"
API_RECENT = API_URL + "/audios/recent?page={}"
API_HOT_COMMENT = API_URL + "/audios/hot/comment?page={}"
API_HOT_LIKE = API_URL + "/audios/hot/like?page={}"
API_CATEGORY = API_URL + "/audios/category/{}?page={}"
API_TOPIC = API_URL + "/audios/topic/{}?page={}"
API_ALL_DJS = API_URL + "/audios/alldjs"
API_DJS = API_URL + "/audios/djs/{}?page={}"

CATE_DICT = {"Gadio News": 45,
             "Early Acess": 49,
             "Gadio Story": 53,
             "Gadio Life": 13,
             "Gadio Music": 14,
             "特别二次元": 38,
             "东京旮旯": 52,
             "葱丝推拿": 36,
             "圣地巡礼": 44,
             "广告节目": 62,
             }

TOPIC_DICT = {"辐射": "辐射",
              "战锤": "战锤",
              "魔兽": "魔兽",
              "通识": "通识"}

BASE_AUDIO_CATE_URL = "https://www.gcores.com/categories/9/originals"
BASE_AUDIO_LINK_URL = "https://www.gcores.com/radios/"
TEST_AUDIO_LINK = "https://www.gcores.com/radios/105962"
