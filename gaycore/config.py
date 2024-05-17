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
AUDIO_PLAYLIST_URL = "https://www.gcores.com/gapi/v1/albums/{playlist_id}/published-radios?page[limit]={limit}&page[offset]={offset}&include=media%2Ccategory%2Calbums"


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

PLAYLIST_DICT = {
    "摩登怪谈录": "211",
    "到底什么是赛博朋克？": "59",
    "游戏茶话会：我们的游戏玩后感": "57",
    "一档七嘴八舌的群口读书分享节目": "51",
    "圆桌讨论": "137",
    "辐射的灵魂、骨骼与肉体": "4",
    "助眠节目：海豹十日谈有声版": "93",
    "科幻新浪潮专题系列节目": "142",
    "一起读书": "11",
    "机组闲聊：聊一聊话题里的新鲜事": "133",
    "CLIPS：用声音记录游戏行业": "130",
    "暴造沙龙": "191",
    "《龙之信条》：全方位剖析卡普空的这款璞玉": "60",
    "三部电影": "181",
    "《死印》故事": "200",
    "银河与城": "220",
    "“恶心”的常规节目": "9",
    "《真人快打》的故事": "117",
    "闲话军武": "91",
    "我们的校园故事，有关学习、生活和青春": "10",
    "赛博告解室": "212",
    "从0到1做游戏": "197",
    "中古战锤国家地理": "143",
    "不咸不淡，海豹炒饭": "114",
    "出版编辑们的幻想书单": "196",
    "历史之人：麦教授的单口历史故事节目": "190",
    "从文学到美学，探索《星空》": "156",
    "从游戏出发，聊聊历史通识": "20",
    "《摩托日记》与拉美文学源流": "198",
    "回忆我们的童年": "61",
    "胆小莫听": "19",
    "穿过《博德之门》": "201",
    "龙与地下城的世界": "39",
    "《无畏契约》系列播客": "195",
    "我们录了这些节目表达对《塞尔达传说》的喜爱之情": "49",
    "独立游戏闲谈": "159",
    "切片美术史": "176",
    "机核跑团故事：傻【哔】太多，摇滚太少": "82",
    "《流行之神》怪案故事集": "116",
    "生化危机的故事": "89",
    "苏联美学演义": "115",
    "从观众、编剧、演员的角度聊聊《流浪地球》": "44",
    "“环学”：《艾尔登法环》系列节目": "138",
    "《黑暗之魂》系列节目": "131",
    "《英雄联盟》背景故事系列节目": "127",
    "TRPG系列节目：TRPG 是什么？玩起来什么样？": "47",
    "说书：小北欧神话系列节目": "36",
    "国产游戏的声音": "157",
    "机核COC跑团故事：密大的平凡岁月": "180",
    "机核DND跑团故事：英雄向远山而行": "122",
    "机核COC跑团故事：除夕": "134",
    "机核跑团故事：机核人类观察": "94",
    "机核跑团故事：吉考斯特别行动": "95",
    "游戏是如何开发的？来听听游戏开发者的声音": "12",
    "在机核，聊足球": "72",
    "白话：老白单口solo聊文章": "63",
    "有声档案：《刺客信条》历史的回声 传奇人物轶事": "170",
    "回味经典：CRPG 系列节目": "5",
    "用嘴做游戏": "169",
    "资本·游戏": "136",
    "我们聊过的 MGS 与小岛秀夫": "48",
    "机核跑团：决胜一小时": "141",
    "战锤40K的宇宙": "3",
    "不插电，也好玩：桌游系列节目": "6",
    "人间拾录": "118",
    "红旗下的车轮": "112",
    "《零》系列故事": "125",
    "有声档案《历史的回声：诸神的黄昏》": "140",
    "“蝇次郎”和⻄蒙聊飞蝇钓": "108",
    "有声档案：SCP基金会": "81",
    "到西部去！《荒野大镖客》与西部开拓史": "14",
    "节目推荐：值得反复听的30期单集节目": "65",
    "明天开始玩改装": "68",
    "MEGA DRIVE：黑色的16bit传奇 ": "98",
    "卡牌的故事：卡牌游戏系列节目": "7",
    "“爱买不买”": "15",
    "关于“沉浸模拟类游戏”": "31",
    "游戏理论": "119",
    "教你如何做音乐：乐理知识与声音工程": "16",
    "科幻学者对话录": "109",
    "硬核但不枯燥：航天工程系列节目": "37",
    "JDM战国史": "113",
    "游览《Kenshi》的世界": "104",
    "与吴岩老师聊《科幻文学论纲》": "101",
    "故事的密码：尝试用一种新的视角来看待“故事”": "97",
    "《极乐迪斯科》的世界及其来源": "96",
    "科幻的黄金时代": "42",
    "《家园》的世界观综述": "90",
    "大巴给你讲《刃牙》": "62",
    "乌贼和章鱼们墨水对战背后的那些事": "88",
    "真实飞行日志与模拟飞行指南": "86",
    "群口评书：魔兽故事系列节目": "2",
    "《赛博朋克2077》见闻录": "84",
    "机核跑团故事：夕妖晚谣": "83",
    "时空传说：《时空之轮》系列讲了个怎样的故事": "85",
    "不玩游戏干什么：安利你一些游戏之外的消遣": "52",
    "让我们了解有关《异形》的一切": "22",
    "《暗黑破坏神》的历史": "18",
    "与阴影之主吴淼聊《塔希里亚故事集》创作": "70",
    "从《龙背》到《尼尔》": "67",
}

BASE_AUDIO_CATE_URL = "https://www.gcores.com/categories/9/originals"
BASE_AUDIO_LINK_URL = "https://www.gcores.com/radios/"
TEST_AUDIO_LINK = "https://www.gcores.com/radios/105962"
PLAYLIST_API = "https://www.gcores.com/gapi/v1/albums?page[limit]={limit}&page[offset]={offset}&sort=-updated-at&filter[hide-albums-require-privilege]=0&filter[hide-albums-video-type]=false&filter[display-type]=album&filter[is-require-privilege]=false&filter[limit-published-at]=1&meta[albums]=%2C"
