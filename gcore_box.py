import curses
import os
import threading
import time

from player import Player
from utils import (BASE_AUDIO_CATE_URL, async_make_name_mp3_dict,
                   recent_func, hot_comment_func, hot_like_func, djs_ximeng_func, cate_wow_func)

# Author: Yi Hong
# Date: 2019.01.29

BOX_WIDTH = 80
BOX_HEIGHT = 3
PAD_WIDTH = 400
PAD_HEIGHT = 1000

MENU_DICT = {
    "最近电台": recent_func,
    "电台主播": {"西蒙": djs_ximeng_func, "42": ["7", "7", "7"]},
    "专题电台": {"辐射": list(range(10)), "魔兽": cate_wow_func},
    "电台分类": {"news": ["2", "3", "8"], "daily": ["q", "y", "u"], "pro": ["l", "k", "p"], "regular": [3,3,3]},
    "电台排行": {"comment": hot_comment_func, "likes": hot_like_func},
}


class GcoreBox:

    def __init__(self):
        self.BOX_WIDTH = BOX_WIDTH
        self.BOX_HEIGHT = BOX_HEIGHT

        self.PAD_WIDTH = PAD_WIDTH
        self.PAD_HEIGHT = PAD_HEIGHT
        self.windows = []
        self.flow_info = {}
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
        # curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(1, curses.COLOR_BLACK, 45)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.stdscr.bkgd(curses.color_pair(2))
        self.stdscr.timeout(100)
        self.stdscr.refresh()

    def make_text_box(self, boxes):
        self.boxes = boxes
        self.pad = curses.newpad(self.PAD_WIDTH, self.PAD_HEIGHT)

        self.pad.box()
        i = 1
        for num, text in enumerate(boxes, 1):
            box = self.pad.derwin(self.BOX_HEIGHT, self.BOX_WIDTH, i, self.PAD_WIDTH//2 - self.BOX_WIDTH//2)
            box.box()
            box.addstr(1, 0, "{}. {}".format(num, text))
            yield box
            i +=  self.BOX_HEIGHT
        self.max_height = i

    def _center(self, window):
        cy, cx = window.getbegyx()
        maxy, maxx = self.stdscr.getmaxyx()
        self.pad.timeout(-1)
        self.pad.refresh(cy, cx, 1, maxx//2 - self.BOX_WIDTH//2, maxy-1, maxx-1)
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

    def _highlight_selected(self):

        topy, topx = self._center(self.windows[0])

        current_num = 0
        last = 1
        top = self.windows[0]
        while True:
            self.windows[current_num].bkgd(curses.color_pair(1))
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

            if c in [ord('j'), curses.KEY_DOWN]:
                current_num = current_num + 1 if current_num < len(self.windows) - 1 else 0

            if c in [ord('k'), curses.KEY_UP]:
                current_num = current_num - 1 if current_num > 0 else len(self.windows) - 1

            # 退出
            if c == ord('q'):
                self._end_curses()
                self.player._q_mp3()
                return

            # 播放当前选中的音乐
            if c == ord('\n'):
                try:
                    if self.player.popen_handler:
                        self.player._q_mp3()
                        self.windows.pop()
                    info_list = self.info_dict.get(self.boxes[current_num])
                    # 播放当前选择的音乐
                    self.start_to_play(info_list[1])
                    self.flow_info = eval(info_list[2])
                    self._add_info_box()
                except:
                    pass

            # enter the menu selected
            if c == curses.KEY_RIGHT:
                try:
                    if not callable(self.menu_dict):
                        self.page_num = -1  # 恢复翻页处理，翻页过多的问题
                        self.dict_stack.append(self.menu_dict)
                        self.menu_dict = self.menu_dict.get(self.boxes[current_num])
                    if isinstance(self.menu_dict, dict):
                        self.boxes = list(self.menu_dict.keys())
                    else:
                        # 利用函数一等对象特性（可能需要重构）
                        if callable(self.menu_dict):
                            self.dict_stack.append(self.menu_dict)
                            self.page_num += 1
                            self.info_dict = self.menu_dict(self.page_num)
                            self.boxes = list(self.info_dict.keys())
                        else:
                            self.boxes = self.menu_dict
                    break
                except:
                    self.dict_stack.pop()

            if c == curses.KEY_LEFT:
                try:
                    last_menu = self.dict_stack.pop()
                    if callable(last_menu):
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

            # 暂停或继续播放
            if c == ord(" "):
                self.player._pause_or_resume_mp3()

            # 播放时间轴
            self._play_timeflow_info()

        self.pick(self.boxes)

    def _play_timeflow_info(self):
        # 播放时间轴
        if self.player.popen_handler:
            flow_info = dict(self.flow_info.get(self.player.process_length, ""))
            self.windows[-1].box()
            self.windows[-1].addstr(1, self.BOX_WIDTH//2, "时间轴")
            self.windows[-1].addstr(2, 1, "time:  " + str(self.player.process_length))
            if flow_info.get("content"):
                self.windows[-1].clear()
                self.windows[-1].addstr(3, 1, "title:\n  " + flow_info.get("title", ""))
                self.windows[-1].addstr(5, 1, "content:\n      " + flow_info.get("content", ""))
                content_length = flow_info.get("content", "")
                next_y = len(content_length)//BOX_WIDTH
                self.windows[-1].addstr(7+next_y, 1, "img:\n   " + flow_info.get("img", ""))

    def _add_info_box(self):
        box = self.pad.derwin(self.BOX_HEIGHT*4, self.BOX_WIDTH, self.max_height, self.PAD_WIDTH//2 - self.BOX_WIDTH//2)
        box.box()
        self.windows.append(box)

    def pick(self, boxes):
        self.windows = list(self.make_text_box(boxes))
        if self.player.popen_handler:
            self._add_info_box()
        self._highlight_selected()

if __name__ == "__main__":
    g = GcoreBox()
    # names_dict = async_make_name_mp3_dict(BASE_AUDIO_CATE_URL+"?page=1")
    # names_dict = api_make_name_mp3_dict(1)
    g.pick(list(MENU_DICT.keys()))
    # g.pick(list(names_dict.keys()))
