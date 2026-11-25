# -*- coding: utf-8 -*-
"""「파이썬 거북이 게임」 글의 게임 코드를 실제로 실행해 화면을 캡처하고,
클립 2번 장면을 움직이는 영상(mp4)으로 만든다.

- 글의 코드와 같은 게임이다. 영상용으로 달라진 점 두 가지:
  1) 점수를 창 왼쪽 위에 글자로 표시한다(글의 코드는 Shell에만 찍는다).
  2) 키를 누르는 일은 자동 조종(먹이 쪽으로 방향을 맞춰 위 화살표를 누름)이 대신한다.
  거북이 이동·돌기·거리 판정·먹이 이동은 글의 코드 그대로다.
- 실행: python 도구/클립영상_거북이게임.py   (실행 중 화면에 거북이 창이 잠깐 뜬다. 가리지 말 것)
- 결과: clip/02-내가-만든-게임.mp4 (약 7초, 1080x1920, 소리 없음)
- 필요: Pillow, ffmpeg(C:/ffmpeg/bin/ffmpeg.exe)
"""
import ctypes
import random
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)   # 캡처 좌표와 화면 배율을 맞춘다
except Exception:
    pass

import turtle
from PIL import ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parent))
import 클립장면_거북이게임 as scenes

POST = scenes.POST
OUT_MP4 = POST / "clip/02-내가-만든-게임.mp4"
FFMPEG = "C:/ffmpeg/bin/ffmpeg.exe"
SEED = 7
FPS = 12
SECONDS = 7
NFRAMES = FPS * SECONDS


def capture_frames(tmp):
    random.seed(SEED)
    screen = turtle.Screen()
    screen.setup(540, 405)
    screen.title("거북이 게임")
    # 영상용: 작은 창에서도 보이도록 화면 좌표를 확대하고 모양을 키운다(먹이는 글처럼 -200~200 안).
    cw, ch = screen.window_width(), screen.window_height()
    half_x = 270
    half_y = half_x * ch / cw
    screen.setworldcoordinates(-half_x, -half_y, half_x, half_y)

    # ---- 글의 코드 ----
    t = turtle.Turtle()
    t.shape("turtle")
    t.shapesize(1.8, 1.8)
    t.color("green")
    t.penup()
    t.speed(0)
    food = turtle.Turtle()
    food.shape("circle")
    food.shapesize(1.8, 1.8)
    food.color("red")
    food.penup()
    food.goto(100, 0)
    score = 0
    board = turtle.Turtle()      # 영상용: 점수 표시
    board.hideturtle()
    board.penup()
    board.goto(-half_x + 12, half_y - 40)

    def show():
        board.clear()
        board.write(f"score: {score}", font=("Arial", 22, "bold"))

    def go():
        nonlocal score
        t.forward(20)
        if t.distance(food) < 20:
            score += 1
            show()
            food.goto(random.randint(-200, 200), random.randint(-200, 200))

    def turn_left():
        t.left(30)

    def turn_right():
        t.right(30)

    screen.onkey(go, "Up")
    screen.onkey(turn_left, "Left")
    screen.onkey(turn_right, "Right")
    screen.listen()
    show()
    # -------------------

    cv = screen.getcanvas()
    inner = cv._canvas
    inner.focus_force()
    root = cv.winfo_toplevel()
    root.update()
    frames = []

    def key(name):
        inner.event_generate(f"<KeyRelease-{name}>")
        root.update()

    def grab():
        root.update()
        x, y = inner.winfo_rootx(), inner.winfo_rooty()
        w, h = inner.winfo_width(), inner.winfo_height()
        return ImageGrab.grab(bbox=(x, y, x + w, y + h))

    for i in range(NFRAMES):
        diff = (t.towards(food) - t.heading() + 180) % 360 - 180
        if abs(diff) >= 18:
            key("Left" if diff > 0 else "Right")
        else:
            key("Up")
        im = grab()
        im.save(tmp / f"f{i:03d}.png")
        frames.append(im)
    print("점수:", score)
    turtle.bye()
    return score


def compose(tmp, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(NFRAMES):
        cap = scenes.Image.open(tmp / f"f{i:03d}.png").convert("RGB")
        img, _ = scenes.scene2(cap_img=cap)
        img.save(out_dir / f"c{i:03d}.png")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "out").mkdir()
        score = capture_frames(tmp)
        compose(tmp, tmp / "out")
        # 첫 프레임을 미리보기로 보관
        keep = Path(tempfile.gettempdir()) / "turtle_clip_preview"
        keep.mkdir(exist_ok=True)
        for name in ("c000.png", "c040.png", f"c{NFRAMES-1:03d}.png"):
            (keep / name).write_bytes((tmp / "out" / name).read_bytes())
        OUT_MP4.parent.mkdir(exist_ok=True)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", str(tmp / "out/c%03d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "20", str(OUT_MP4)], check=True)
        print("영상:", OUT_MP4, " 미리보기:", keep)
