# -*- coding: utf-8 -*-
"""「수시 추가 합격 Q&A」 클립 합성 — 폰 캐릭터 하나가 모든 장면에서 살짝 움직이는 영상(더빙 없음).

- 배경: clip/배경/01~06.png (ChatGPT, 글자 없음) / 폰: clip/레이어/폰.png (투명 PNG) / 음악: clip/원본/음악.wav
- 자막은 AI가 얹는다(질문만, 답은 넣지 않는다).
사용:
  python 도구/클립합성_수시추가합격QnA.py --preview   장면 6장 정지 미리보기(clip/미리보기/)와 한 장 모음(contact.png)
  python 도구/클립합성_수시추가합격QnA.py             영상 만들기 → clip/수시추가합격QnA-클립.mp4 (사용자가 이미지·음악을 확인한 뒤에만)
"""
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import 클립장면_거북이게임 as S
from PIL import Image, ImageDraw, ImageChops

W, H = 1080, 1920
FPS = 24
FFMPEG = "C:/ffmpeg/bin/ffmpeg.exe"
POST = S.ROOT / "문서/네이버-코딩가이드/20261124_23개/20261124_수시-추가합격-QnA"
CLIP = POST / "clip"
OUT = CLIP / "수시추가합격QnA-클립.mp4"
MUSIC = CLIP / "원본/음악-빠름.wav"     # 2026-11-25 사용자 선택(직접 합성한 빠른 곡)
FADE_FRAMES = 6

NAVY = (29, 33, 69)
CORAL = (255, 122, 107)
TEAL = (55, 197, 184)
YEL = (255, 205, 50)
INK = (255, 255, 255)
GRAY = (205, 208, 235)

BADGE = "수시 추가 합격 Q&A"
PHONE = Image.open(CLIP / "레이어/폰.png").convert("RGBA")


def rcard(img, box, fill, radius=30):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(box, radius=radius, fill=fill)
    base = img.convert("RGBA")
    base.alpha_composite(lay)
    return base.convert("RGB")


def wrap(text, size, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    f = S.font(size)
    if d.textlength(text, font=f) <= maxw:
        return [text]
    words = text.split(" ")
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        worst = max(d.textlength(a, font=f), d.textlength(b, font=f))
        if best is None or worst < best[0]:
            best = (worst, [a, b])
    return best[1]


def q_cards(img, items, y=340, size=50):
    """질문 카드(Q번호 배지 + 질문)를 위에서부터 쌓는다."""
    f = S.font(size)
    for num, text, color in items:
        lines = wrap(text, size, 700)
        h = 40 + len(lines) * 66
        img = rcard(img, [60, y, 1020, y + h], (14, 16, 44, 170), radius=34)
        d = ImageDraw.Draw(img)
        cy = y + h // 2
        d.ellipse([88, cy - 44, 176, cy + 44], fill=color)
        nf = S.font(40)
        d.text((132 - d.textlength(num, font=nf) / 2, cy - 27), num, font=nf, fill=NAVY)
        ty = y + 20
        for ln in lines:
            d.text((206, ty), ln, font=f, fill=INK)
            ty += 66
        y += h + 22
    return img, y


# 장면 설정: 길이, 배경, 폰(중심 x, 중심 y, 크기), 움직임
SCENES = [
    dict(key=1, art="01.png", dur=4, phone=(540, 1090, 0.80), motion="vibrate"),
    dict(key=2, art="02.png", dur=7, phone=(560, 1040, 0.72), motion="bob"),
    dict(key=3, art="03.png", dur=7, phone=(540, 1030, 0.72), motion="ring"),
    dict(key=4, art="04.png", dur=7, phone=(540, 815, 0.50), motion="tilt"),
    dict(key=5, art="05.png", dur=7, phone=(578, 1000, 0.62), motion="bob"),
    dict(key=6, art="06.png", dur=6, phone=(300, 1070, 0.52), motion="nod"),
]


def static_scene(sc):
    art = Image.open(CLIP / "배경" / sc["art"]).convert("RGB")
    img = S.shade(art, top=(0, 780, 165), bottom=(1380, 1920, 150) if sc["key"] == 6 else None)
    img = S.badge(img, BADGE)          # 모든 장면 맨 위 주제 배지(2026-11-25)
    d = ImageDraw.Draw(img)
    k = sc["key"]
    if k == 1:
        S.caption(d, [[("예비 ", INK), ("12번", YEL)], [("받았다면?", INK)]], y=340, size=104, gap=130)
        S.line(d, 624, [("그날부터 질문이 꼬리를 물어요", GRAY)], 48, bold=False)
    elif k == 2:
        img, _ = q_cards(img, [("Q1", "추가 합격 발표는 언제부터?", TEAL), ("Q2", "꼭 전화로 올까?", CORAL)])
    elif k == 3:
        img, _ = q_cards(img, [("Q3", "전화를 못 받으면?", TEAL), ("Q4", "예비 번호를 미리 포기할 수 있을까?", CORAL)])
    elif k == 4:
        img, _ = q_cards(img, [("Q5", "이미 등록했는데 추가 합격하면?", TEAL), ("Q6", "추가 합격하면 정시는 못 쓰나?", CORAL)])
    elif k == 5:
        img, _ = q_cards(img, [("Q7", "등록했다가 포기하면 돈은 돌려받나?", TEAL), ("Q8", "입학처를 사칭한 전화면?", CORAL)])
    elif k == 6:
        S.caption(d, [[("8가지 질문,", INK)], [("답은 ", INK), ("블로그에서", YEL)]], y=340, size=96, gap=124)
        S.line(d, 700, [("12월 24일 전에 적어 둘 다섯 줄도 있어요", GRAY)], 40, bold=False)
        S.line(d, 1516, [("2027학년도 모집요강 기준", GRAY)], 34, bold=False, stroke=5)
    return img


# 울리는 장면의 (첫 울림 시각, 간격, 울리는 길이) — 장면 안 시각(초)
RING = {"vibrate": (0.2, 1.9, 0.55), "ring": (0.3, 2.4, 0.7)}


def ring_times():
    """영상 전체에서 전화벨 소리를 넣을 시각(초) 목록."""
    out, start = [], 0.0
    for sc in SCENES:
        if sc["motion"] in RING:
            off, period, burst = RING[sc["motion"]]
            t = off
            while t + burst <= sc["dur"]:
                out.append(start + t)
                t += period
        start += sc["dur"]
    return out


def write_ring_track(path, times, length=38.0):
    """귀여운 전화벨('띠리리링') 효과음 트랙을 만든다: 높은 두 음을 빠르게 번갈아, 0.5초."""
    import wave
    sr = 44100
    n = int(length * sr)
    buf = [0.0] * n
    f1, f2 = 1318.5, 1760.0           # E6, A6
    dur = 0.5
    for t0 in times:
        s0 = int(t0 * sr)
        ph = 0.0
        for i in range(int(dur * sr)):
            j = s0 + i
            if j >= n:
                break
            t = i / sr
            f = f1 if int(t * 15) % 2 == 0 else f2
            ph += 2 * math.pi * f / sr
            env = min(1.0, t / 0.01) * (1.0 if t < dur - 0.08 else max(0.0, (dur - t) / 0.08))
            buf[j] += 0.32 * env * (math.sin(ph) + 0.25 * math.sin(2 * ph))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b"".join(int(max(-1, min(1, v)) * 32767).to_bytes(2, "little", signed=True) for v in buf))


def motion_params(kind, t):
    """(오프셋 x, 오프셋 y, 회전각, 세로 늘림 비율)"""
    tau = 2 * math.pi
    if kind in RING:           # 전화가 울리는 장면: 정해진 시각에만 떨림(그때 전화벨 소리도 남)
        off, period, burst = RING[kind]
        u = t - off
        env = 1.0 if (u >= 0 and (u % period) < burst) else 0.0
        if kind == "vibrate":  # 문자 진동: 부르르
            return 6 * math.sin(tau * 22 * t) * env, 8 * math.sin(tau * 0.8 * t), 5 * math.sin(tau * 18 * t) * env, 1.0
        return 0, 6 * math.sin(tau * 0.8 * t), 7 * math.sin(tau * 11 * t) * env, 1.0   # 벨 울림: 좌우로
    if kind == "tilt":         # 갸웃
        return 0, 8 * math.sin(tau * 0.6 * t), 9 * math.sin(tau * 0.5 * t), 1.0
    if kind == "nod":          # 끄덕끄덕(숨쉬기)
        return 0, 10 * math.sin(tau * 1.1 * t), 2 * math.sin(tau * 0.55 * t), 1.0 + 0.03 * math.sin(tau * 1.1 * t + 0.5)
    return 0, 14 * math.sin(tau * 0.8 * t), 2.5 * math.sin(tau * 0.4 * t), 1.0 + 0.012 * math.sin(tau * 0.8 * t)


def frame(sc, static, t):
    cx, cy, s = sc["phone"]
    ox, oy, rot, sy = motion_params(sc["motion"], t)
    pw, ph = PHONE.size
    # 사진 폰 크기: 원본 1080 폭 기준으로 맞춤(원본 캔버스 941 → 1080)
    k = s * 1080 / 941
    p = PHONE.resize((int(pw * k), int(ph * k * sy)), Image.LANCZOS)
    p = p.rotate(rot, resample=Image.BICUBIC, expand=True)
    img = static.copy()
    img.paste(p, (int(cx + ox - p.width / 2), int(cy + oy - p.height / 2)), p)
    return img


def preview():
    out = CLIP / "미리보기"
    out.mkdir(exist_ok=True)
    thumbs = []
    for sc in SCENES:
        st = static_scene(sc)
        im = frame(sc, st, 0.35)
        im.save(out / f"{sc['key']:02d}.png")
        thumbs.append(im.resize((432, 768), Image.LANCZOS))
    sheet = Image.new("RGB", (432 * 3 + 40, 768 * 2 + 30), (30, 30, 30))
    for i, t in enumerate(thumbs):
        sheet.paste(t, (10 + (i % 3) * 442, 10 + (i // 3) * 778))
    sheet.save(out / "contact.png")
    print("미리보기:", out)


def make_video():
    times = ring_times()
    ring = CLIP / "원본/전화벨.wav"
    write_ring_track(ring, times)
    print("전화벨 시각:", [round(t, 2) for t in times])
    ff = subprocess.Popen(
        [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", str(MUSIC), "-i", str(ring), "-t", "38",
         "-filter_complex", "[2:a]aformat=channel_layouts=stereo[r];[1:a][r]amix=inputs=2:normalize=0:duration=first,"
                            "alimiter=limit=0.95,afade=t=out:st=35.5:d=2.5[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "16", "-tune", "grain", "-c:a", "aac", "-b:a", "160k", str(OUT)],
        stdin=subprocess.PIPE)
    prev = None
    total = 0
    for sc in SCENES:
        st = static_scene(sc)
        for k in range(sc["dur"] * FPS):
            im = frame(sc, st, k / FPS)
            if prev is not None and k < FADE_FRAMES:
                im = Image.blend(prev, im, (k + 1) / (FADE_FRAMES + 1))
            ff.stdin.write(im.tobytes())
            total += 1
            last = im
        prev = last
    ff.stdin.close()
    ff.wait()
    print(f"완료: {OUT} ({total / FPS:.1f}초)")


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview()
    else:
        make_video()


