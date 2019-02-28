import curses
import time
import subprocess


class Player:

    def __init__(self):
        self.popen_handler = None
        self.process_location = 0
        self.process_length = 0
        self.fps = 0

    # 参考musicibox代码
    def run_mpg123(self, url, expires=-1, get_time=-1):
        para = ["mpg123", "-R"] + []
        self.popen_handler = subprocess.Popen(
            para, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        self.popen_handler.stdin.write(b"L " + url.encode("utf-8") + b"\n")
        self.popen_handler.stdin.flush()

        endless_loop_cnt = 0
        # some code from musicbox
        while True:
            if not self.popen_handler:
                break

            strout = self.popen_handler.stdout.readline().decode("utf-8").strip()
            if strout[:2] == "@F":
                out = strout.split(" ")
                self.process_location = int(float(out[3]))
                self.process_length = int(float(out[3]) + float(out[4]))
                if(float(out[3]) != 0):
                    self.fps = float(out[1]) / float(out[3])

            elif strout == "@P 0":
                # end, moving to next
                playing_flag = True
                break
            elif strout == "":
                endless_loop_cnt += 1
                if endless_loop_cnt > 100:
                    break

    # 停止播放
    def pause_or_resume_mp3(self):
        if not self.popen_handler:
            return
        self.popen_handler.stdin.write(b"P\n")
        self.popen_handler.stdin.flush()

    # 快进/倒退10s
    def forward_mp3(self, seconds):
        if not self.popen_handler:
            return
        self.popen_handler.stdin.write(
            b"J +" + str(seconds*int(self.fps)).encode("utf-8") + b"\n")
        self.popen_handler.stdin.flush()

    # 退出播放
    def q_mp3(self):
        if self.popen_handler:
            self.popen_handler.stdin.write(b"Q\n")
            self.popen_handler.stdin.flush()
            self.popen_handler.kill()
            self.popen_handler = None
