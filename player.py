import curses
import time
import subprocess


class Player:

    def __init__(self):
        self.popen_handler = None
        self.process_location = 0
        self.process_length = 0

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
                #: playing, update progress
                out = strout.split(" ")
                self.process_location = int(float(out[3]))
                self.process_length = int(float(out[3]) + float(out[4]))
            elif strout[:2] == "@E":
                playing_flag = True
                if (
                    expires >= 0
                    and get_time >= 0
                    and time.time() - expires - get_time >= 0
                ):
                    print(2)
                else:
                    print(3)
                    # error, stop song and move to next
                break
            elif strout == "@P 0":
                # end, moving to next
                playing_flag = True
                break
            elif strout == "":
                endless_loop_cnt += 1
                # 有播放后没有退出，mpg123一直在发送空消息的情况，此处直接终止处理
                if endless_loop_cnt > 100:
                    break

    def _pause_or_resume_mp3(self):
        if not self.popen_handler:
            return
        self.popen_handler.stdin.write(b"P\n")
        self.popen_handler.stdin.flush()

    def _q_mp3(self):
        if self.popen_handler:
            self.popen_handler.stdin.write(b"Q\n")
            self.popen_handler.stdin.flush()
            self.popen_handler.kill()
            self.popen_handler = None
