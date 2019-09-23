import curses
import datetime
import os
import sys
import threading
import time
import webbrowser

from gaycore.config import *
from gaycore.player import Player
from gaycore.utils import (API_CATEGORY_DICT, API_DJS_DICT, API_TOPIC_DICT,
                           BASE_AUDIO_CATE_URL, TOPIC_DICT, chunkstring,
                           hot_comment_func, hot_like_func, playinfo_func,
                           recent_func)

try:
    from urllib.request import urlretrieve
except:
    from urllib import urlretrieve


# Author: Yi Hong
# Date: 2019.01.29

MENU_DICT = {
    "最近电台": recent_func,
    "主播电台": API_DJS_DICT,
    "专题电台": API_TOPIC_DICT,
    "分类电台": API_CATEGORY_DICT,
    "排行电台": {"讨论热门": hot_comment_func, "喜欢热门": hot_like_func},
}


class GcoreBox:

    def __init__(self):
        self.BOX_WIDTH = BOX_WIDTH
        self.BOX_HEIGHT = BOX_HEIGHT

        self.PAD_WIDTH = PAD_WIDTH
        self.PAD_HEIGHT = PAD_HEIGHT
        self.windows = []
        self.flow_info = {}
        self.flow_img = ""
        self.quote = ""
        self.last_flag = False
        self.menu_dict = MENU_DICT
        self.dict_stack = []  # 定义一个stack 方便进入下个目录和返回下个目录
        self.page_num = -1  # 用于翻页
        self.player = Player()
        self._init_curses()

    def _init_curses(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        try:
            curses.init_pair(1, curses.COLOR_BLACK, 197)  # 接近机核主题的颜色
        except:
            # 树莓派 windows无法使用机核like色
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.stdscr.bkgd(curses.color_pair(2))
        self.stdscr.timeout(100)
        self.stdscr.refresh()

    def make_text_box(self, boxes):
        self.boxes = boxes
        self.pad = curses.newpad(self.PAD_WIDTH, self.PAD_HEIGHT)

        self.pad.box()
        height = 1
        for num, text in enumerate(boxes, 1):
            box = self.pad.derwin(
                self.BOX_HEIGHT, self.BOX_WIDTH, height, self.PAD_WIDTH//2 - self.BOX_WIDTH//2)
            box.box()
            if len(text) > 37:
                text = text[:36] + "..."
            box.addstr(1, 0, "{}. {}".format(num, text))
            yield box
            height += self.BOX_HEIGHT
        self.max_height = height

    def _center(self, window):
        cy, cx = window.getbegyx()
        maxy, maxx = self.stdscr.getmaxyx()
        self.pad.timeout(-1)
        self.pad.refresh(cy, cx, 1, maxx//2 -
                         self.BOX_WIDTH//2, maxy-1, maxx-1)
        return (cy, cx)

    def _end_curses(self):
        """ Terminates the curses application. """
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def start_to_play(self, url):
        thread = threading.Thread(target=self.player.run_mpg123, args=(url, ))
        thread.start()
        time.sleep(0.01)
        return thread

    def start_to_download(self, mp3_url, audio_name):
        thread = threading.Thread(
            target=self._download_mp3, args=(mp3_url, audio_name))
        thread.start()

    def mainloop(self):

        topy, topx = self._center(self.windows[0])

        current_num = 0
        last = 1
        top = self.windows[0]
        while True:
            self.windows[current_num].bkgd(curses.color_pair(1))
            # 处理只有一个box的情况
            if len(self.windows) == 1:
                last = 0
            self.windows[last].bkgd(curses.color_pair(2))

            maxy, maxx = self.stdscr.getmaxyx()
            cy, cx = self.windows[current_num].getbegyx()

            if ((topy + maxy - self.BOX_HEIGHT) <= cy):
                top = self.windows[current_num]

            if topy >= cy + self.BOX_HEIGHT:
                top = self.windows[current_num]

            if last != current_num:
                last = current_num

            topy, topx = self._center(top)
            c = self.stdscr.getch()

            if c == curses.KEY_RESIZE:
                self.stdscr.clear()

            if c in [ord("j"), curses.KEY_DOWN]:
                current_num = current_num + \
                    1 if current_num < len(self.windows) - 1 else 0

            if c in [ord("k"), curses.KEY_UP]:
                current_num = current_num - \
                    1 if current_num > 0 else len(self.windows) - 1

            # enter the menu selected
            if c in [curses.KEY_RIGHT, ord("l")]:
                try:
                    if not callable(self.menu_dict):
                        self.page_num = -1  # 恢复翻页处理，翻页过多的问题
                        self.dict_stack.append(self.menu_dict)
                        self.menu_dict = self.menu_dict.get(
                            self.boxes[current_num])
                    if isinstance(self.menu_dict, dict):
                        self.boxes = list(self.menu_dict.keys())
                    else:
                        # 利用函数一等对象特性（可能需要重构）
                        if callable(self.menu_dict):
                            if self.last_flag:
                                break
                            self.dict_stack.append(self.menu_dict)
                            self.page_num += 1
                            self.info_dict = self.menu_dict(self.page_num)
                            self.boxes = list(self.info_dict.keys())
                            # 处理翻页到头情况
                            if len(self.boxes) < 10 and (not self.last_flag):
                                self.last_flag = True
                                self.last_flag_num = self.page_num
                        else:
                            self.boxes = self.menu_dict
                    break
                except:
                    self.dict_stack.pop()

            # back to last menu
            if c in [curses.KEY_LEFT, ord("h")]:
                try:
                    last_menu = self.dict_stack.pop()
                    if callable(last_menu):
                        # 处理翻页到头情况
                        if self.last_flag:
                            self.page_num = self.last_flag_num
                            self.last_flag = False
                        self.page_num = self.page_num - 1
                        if self.page_num >= 0:
                            self.info_dict = last_menu(self.page_num)
                            self.boxes = list(self.info_dict.keys())
                        else:
                            self.menu_dict = self.dict_stack.pop()
                            self.boxes = list(self.menu_dict.keys())
                    else:
                        self.menu_dict = last_menu
                        self.boxes = list(last_menu.keys())
                    break
                except:
                    pass
            # 退出
            if c == ord("q"):
                self._end_curses()
                self.player.q_mp3()
                return

            # 打开浏览器查看
            if c == ord("w"):
                try:
                    info_list = self.info_dict.get(self.boxes[current_num])
                    gcore_url = info_list[0]
                    webbrowser.open(gcore_url)
                except:
                    # 查看图片
                    webbrowser.open(self.flow_img)

            # 打开来源
            if c == ord("o"):
                try:
                    webbrowser.open(self.quote)
                except:
                    pass

            # 下载
            if c == ord("d"):
                if self.dict_stack and callable(self.dict_stack[-1]):
                    audio_name = self.boxes[current_num]
                    info_list = self.info_dict.get(audio_name)
                    # 下载当前MP3
                    self.start_to_download(info_list[1], audio_name + ".mp3")
                else:
                    continue

            if c == ord('\n'):
                try:
                    if self.player.popen_handler:

                        if current_num == len(self.windows) - 1:
                            webbrowser.open(self.flow_img)
                            continue
                        self.player.q_mp3()
                        self.windows.pop()
                    info_list = self.info_dict.get(self.boxes[current_num])
                    # 播放当前选择的音乐
                    self.start_to_play(info_list[1])
                    # 生成播放信息
                    audio_id = info_list[0].split("/")[-1]
                    playing_info = playinfo_func(audio_id)
                    time_flow_info = playing_info.get("audio_flow_info", "")
                    self.djs_info = playing_info.get("audio_djs", "")
                    self.flow_info = eval(time_flow_info)
                    # 添加播放时间轴
                    self._add_info_box()
                except:
                    pass

            # 暂停或继续播放
            if c == ord(" "):
                self.player.pause_or_resume_mp3()

            # 快进/倒退
            if c == ord("f"):
                self.player.forward_mp3(5)

            # 播放时间轴
            self._play_timeflow_info()

        self.pick(self.boxes)

    def _play_timeflow_info(self):

        # 解析主播格式
        def f_parser(x): return ', '.join([i[0] for i in eval(x)])

        # 播放时间轴
        if self.player.popen_handler:
            flow_info = dict(self.flow_info.get(
                self.player.process_length, ""))
            djs_info = f_parser(self.djs_info)[:50]
            self.windows[-1].box()
            self.windows[-1].addstr(1, 1, "时间轴")
            self.windows[-1].addstr(1, self.BOX_WIDTH//2-25, "主播:" + djs_info)
            # play_time = str(datetime.timedelta(
            #    seconds=self.player.process_length))
            play_time_hrs, play_time_min = divmod(
                self.player.process_location, 3600)
            play_time_min, play_time_sec = divmod(
                self.player.process_location, 60)

            self.windows[-1].addstr(3, 1, "time:  " + str(play_time_hrs).zfill(
                2) + ':' + str(play_time_min).zfill(2) + ':' + str(play_time_sec).zfill(2))
            if flow_info.get("content"):
                try:
                    self.flow_img = flow_info.get("img", "")
                    self.quote = flow_info.get("quote_href", "")
                    self.windows[-1].clear()
                    self.windows[-1].bkgd(curses.color_pair(2))
                    self.windows[-1].addstr(4, 1, "title: " +
                                            flow_info.get("title", ""))
                    self.windows[-1].addstr(5, 1, "content:")
                    content = flow_info.get("content", "")
                    # 去掉换行符
                    content = content.replace("\n", "")
                    content_length = len(content)
                    if content_length > 230:
                        content = content[:230] + "..."
                    content_list = chunkstring(content, 37)
                    for i, j in enumerate(content_list):
                        self.windows[-1].addstr(6 + i, 1, "  " + j)
                    if self.quote:
                        self.windows[-1].addstr(13, 1, "打开来源请按o键")
                except:
                    pass

    def _add_info_box(self):
        box = self.pad.derwin(self.BOX_HEIGHT*5, self.BOX_WIDTH,
                              self.max_height, self.PAD_WIDTH//2 - self.BOX_WIDTH//2)
        box.box()
        self.windows.append(box)

    def _download_mp3(self, mp3_url, audio_name):

        # 下载进度
        def report(count, blockSize, totalSize):
            percent = int(count*blockSize*100/totalSize)
            self.stdscr.addstr(0, 0, "\r%d%%" % percent + ' complete')
        try:
            urlretrieve(mp3_url, audio_name, reporthook=report)
            self.stdscr.addstr(0, 0, audio_name + ': 下载完成')
            time.sleep(1)
            self.stdscr.clear()
        except:
            self.stdscr.addstr(0, 0, "download error")

    def pick(self, boxes):
        self.windows = list(self.make_text_box(boxes))
        if self.player.popen_handler:
            self._add_info_box()
        self.mainloop()
