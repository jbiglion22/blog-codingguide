# -*- coding: utf-8 -*-
"""「파이썬 거북이 게임」 클립 전체를 캐릭터가 살짝씩 움직이는 영상(mp4)으로 합성한다 (더빙 없음).

방식(A안): 새 그림 없이, 받은 장면 그림(clip/배경/0N.png)의 캐릭터 주변을 부드럽게 일그러뜨려
          둥실·끄덕임·숨쉬기 움직임을 만든다. 자막과 안내는 고정, 장면 사이는 짧게 겹쳐 넘어간다.
          5번 장면은 게임을 실제로 실행해 캡처한 영상(클립영상_거북이게임.py)을 넣는다.
실행: python 도구/클립합성_거북이게임.py   (약 4~6분. 실행 중 거북이 창이 잠깐 뜬다)
결과: clip/거북이게임-클립.mp4 (1080x1920, 24fps, 38초, 배경음악 포함)
필요: Pillow, ffmpeg(C:/ffmpeg/bin/ffmpeg.exe)
"""
import math
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import 클립영상_거북이게임 as V          # 실제 게임 캡처 (DPI 설정 포함)
import 클립장면_거북이게임 as S
from PIL import Image, ImageChops

W, H = S.W, S.H
FPS = 24
FFMPEG = "C:/ffmpeg/bin/ffmpeg.exe"
CLIP = S.POST / "clip"
OUT = CLIP / "거북이게임-클립.mp4"
MUSIC = CLIP / "배경음악.mp3"
FADE_FRAMES = 6

# 장면 순서: (장면 함수, 쓰는 그림, 길이 초, 노트 여부, 움직일 곳들)
# 움직일 곳: c=중심, R=퍼지는 반경, ax/ay=좌우·상하 흔들림(px), fx=초당 횟수, ph=위상, sc=숨쉬기 비율
SCENES = [
    (S.scene1, "01.png", 4, True, [
        dict(c=(400, 1150), R=340, ax=9, ay=7, fx=1.6, ph=0.0, sc=0.012),   # 달리는 거북이
        dict(c=(885, 1025), R=170, ax=0, ay=14, fx=0.9, ph=1.0, sc=0.02),   # 빨간 공
    ]),
    (S.scene3, "03.png", 8, True, [
        dict(c=(560, 790), R=250, ax=0, ay=9, fx=1.1, ph=0.0, sc=0.012),    # 방향키 위 거북이
    ]),
    (S.scene4, "04.png", 7, True, [
        dict(c=(220, 1230), R=320, ax=0, ay=8, fx=1.3, ph=0.0, sc=0.014),   # 환호하는 거북이
        dict(c=(925, 700), R=140, ax=6, ay=13, fx=0.8, ph=1.5, sc=0.02),    # 새 공
    ]),
    (S.scene5, "05.png", 7, True, [
        dict(c=(280, 770), R=230, ax=6, ay=6, fx=1.4, ph=0.0, sc=0.01),     # 쉬움 거북이
        dict(c=(735, 770), R=170, ax=0, ay=8, fx=0.9, ph=0.8, sc=0.015),    # 쉬움 공
        dict(c=(370, 1250), R=250, ax=5, ay=4, fx=3.0, ph=0.3, sc=0.008),   # 어려움 거북이(긴장해 떨림)
        dict(c=(750, 1260), R=150, ax=0, ay=7, fx=1.0, ph=2.0, sc=0.012),   # 어려움 공
    ]),
    (S.scene2, "02.png", 7, False, [
        dict(c=(540, 860), R=340, ax=0, ay=9, fx=0.9, ph=0.0, sc=0.014),    # 파이(끄덕)
        dict(c=(930, 1000), R=150, ax=0, ay=6, fx=1.2, ph=1.0, sc=0.012),   # 거북이 장난감
    ]),
    (S.scene6, "06.png", 5, True, [
        dict(c=(540, 900), R=340, ax=0, ay=9, fx=1.0, ph=0.5, sc=0.014),    # 파이(끄덕)
        dict(c=(820, 1150), R=110, ax=0, ay=10, fx=1.3, ph=0.0, sc=0.02),   # 빨간 공
        dict(c=(930, 1010), R=150, ax=0, ay=6, fx=1.2, ph=1.0, sc=0.012),   # 거북이 장난감
    ]),
]
INSET_W = 420
INSET_XY = ((W - INSET_W) // 2, 1198)


def overlay(scene_fn, art_name, note):
    """자막·그라데이션·안내만 따로 뽑는다: 최종 = 그림 × B + C."""
    outs = []
    for v in (0, 255):
        S.ART_OVERRIDE = {art_name: Image.new("RGB", (W, H), (v, v, v))}
        if art_name == "02.png":     # 실제 캡처와 같은 비율(540x405)의 흰 칸으로 카드 크기를 맞춘다
            im, _ = scene_fn(cap_img=Image.new("RGB", (540, 405), (255, 255, 255)))
        else:
            im, _ = scene_fn()
        if note:
            S.add_note(im)
        outs.append(im)
    S.ART_OVERRIDE = {}
    black, white = outs
    B = ImageChops.subtract(white, black)       # 그림이 얼마나 비치는가(255 = 그대로)
    return B, black


def warp(art, regions, t):
    cell = 30
    nx, ny = W // cell + 1, H // cell + 1
    sx = [[i * cell for i in range(nx)] for _ in range(ny)]
    sy = [[j * cell for _ in range(nx)] for j in range(ny)]
    for r in regions:
        cx, cy = r["c"]
        R2 = r["R"] ** 2
        m = math.sin(2 * math.pi * r["fx"] * t + r["ph"])
        m2 = math.sin(2 * math.pi * r["fx"] * t + r["ph"] + 1.2)
        s = r["sc"] * math.sin(2 * math.pi * r["fx"] * t + r["ph"] + 0.5)
        j0 = max(0, int((cy - 2 * r["R"]) // cell))
        j1 = min(ny, int((cy + 2 * r["R"]) // cell) + 1)
        i0 = max(0, int((cx - 2 * r["R"]) // cell))
        i1 = min(nx, int((cx + 2 * r["R"]) // cell) + 1)
        for j in range(j0, j1):
            py = j * cell
            for i in range(i0, i1):
                px = i * cell
                d2 = (px - cx) ** 2 + (py - cy) ** 2
                w = math.exp(-2 * d2 / R2)
                if w < 0.004:
                    continue
                dx = r["ax"] * m2 * w + (px - cx) * s * w
                dy = r["ay"] * m * w + (py - cy) * s * w
                sx[j][i] -= dx
                sy[j][i] -= dy
    data = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            bbox = (i * cell, j * cell, (i + 1) * cell, (j + 1) * cell)
            quad = (sx[j][i], sy[j][i], sx[j + 1][i], sy[j + 1][i],
                    sx[j + 1][i + 1], sy[j + 1][i + 1], sx[j][i + 1], sy[j][i + 1])
            data.append((bbox, quad))
    return art.transform((W, H), Image.MESH, data, Image.BILINEAR)


def inset_paste(img, cap):
    cap = cap.resize((INSET_W, int(cap.height * INSET_W / cap.width)), Image.LANCZOS)
    m = Image.new("L", cap.size, 0)
    S.ImageDraw.Draw(m).rounded_rectangle([0, 0, cap.width - 1, cap.height - 1], radius=18, fill=255)
    img.paste(cap, INSET_XY, m)


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        print("게임 실제 실행 캡처 중... (거북이 창이 잠깐 뜹니다)")
        V.capture_frames(tmp)
        # 5번 장면용 캡처 프레임(초당 12장)
        caps = [Image.open(tmp / f"f{i:03d}.png").convert("RGB") for i in range(V.NFRAMES)]

        ff = subprocess.Popen(
            [FFMPEG, "-y", "-loglevel", "error",
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
             "-i", str(MUSIC),
             "-t", "38", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-tune", "grain",
             "-af", "volume=2.0,afade=t=out:st=35.5:d=2.5", "-c:a", "aac", "-b:a", "160k",
             str(OUT)], stdin=subprocess.PIPE)

        prev_last = None
        total = 0
        for si, (fn, art_name, dur, note, regions) in enumerate(SCENES):
            print(f"장면 {si + 1}/{len(SCENES)} 합성 중...")
            art, _ = S.background(art_name)
            B, C = overlay(fn, art_name, note)
            n = dur * FPS
            for k in range(n):
                t = k / FPS
                a = warp(art, regions, t)
                img = ImageChops.add(ImageChops.multiply(a, B), C)
                if art_name == "02.png":
                    inset_paste(img, caps[min(int(t * V.FPS), len(caps) - 1)])
                if prev_last is not None and k < FADE_FRAMES:
                    img = Image.blend(prev_last, img, (k + 1) / (FADE_FRAMES + 1))
                ff.stdin.write(img.tobytes())
                total += 1
                last = img
            prev_last = last
        ff.stdin.close()
        ff.wait()
        print(f"완료: {OUT} ({total}프레임, {total / FPS:.1f}초)")


if __name__ == "__main__":
    main()

