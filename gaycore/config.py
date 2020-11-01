# -*- coding: utf-8 -*-


BOX_WIDTH = 80
BOX_HEIGHT = 3
PAD_WIDTH = 400
PAD_HEIGHT = 1000


# ####### OFFICE API #############
MP3_BASE_URL = "http://alioss.gcores.com/uploads/audio/"
BASE_AUDIO_LINK_URL = "https://www.gcores.com/radios/"
IMAGE_BASE_URL = "https://image.gcores.com/"
AUDIOS_API = "https://www.gcores.com/gapi/v1/radios?page[limit]={limit}&page[offset]={offset}&sort=-published-at&include=category&filter[list-all]=0"
AUDIO_API = "https://www.gcores.com/gapi/v1/radios/{audio_id}?include=category,user,media,djs,media.timelines"
AUDIOS_CATE_API = "https://www.gcores.com/gapi/v1/categories/{cate_id}/radios?page[limit]={limit}&page[offset]={offset}&sort=-published-at&include=category,user,djs&filter[list-all]=0"


CATE_DICT = {
    "Gadio News": 45,
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

TOPIC_DICT = {"辐射": "辐射", "战锤": "战锤", "魔兽": "魔兽", "通识": "通识"}

BASE_AUDIO_CATE_URL = "https://www.gcores.com/categories/9/originals"
BASE_AUDIO_LINK_URL = "https://www.gcores.com/radios/"
TEST_AUDIO_LINK = "https://www.gcores.com/radios/105962"
