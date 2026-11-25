# -*- coding: utf-8 -*-
"""네이버 클립용 장면 이미지(1080x1920) 6장 — 「파이썬 거북이 게임 만들기, 방향키로 먹이 잡기」 글.

방식: ChatGPT가 만든 글자 없는 배경 그림(clip/배경/01~06.png, 요청서 이미지요청-클립.md)에
      자막·안내를 정확하게 얹는다. 배경 그림이 없는 장면은 임시 배경으로 그려서
      clip/미리보기/ 에 저장한다(배경이 모두 있으면 clip/ 에 저장).

실행: python 도구/클립장면_거북이게임.py
필요: Pillow, 무료 폰트 NotoSansKR-VF.ttf (C:/Windows/Fonts)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "문서/네이버-코딩가이드/20261124_23개/20261124_파이썬-거북이-게임"
SRC = POST / "images"          # 글에 쓴 이미지(실제 실행 캡처)
ART = POST / "clip/배경"       # ChatGPT 배경 그림
FONT = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 240, 1540

NAVY = (21, 25, 60)
INK = (255, 255, 255)
YEL = (255, 205, 50)
GRN = (90, 226, 130)
RED = (255, 100, 100)
GRAY = (200, 206, 235)
KEY = (238, 240, 252)
KEYINK = (40, 48, 120)


def font(size, bold=True):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name("Bold" if bold else "Regular")
    return f


def background(name):
    """배경 그림을 1080x1920으로 맞춰 돌려준다. 없으면 임시 배경과 False."""
    p = ART / name
    if p.exists():
        im = Image.open(p).convert("RGB")
        s = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        x, y = (im.width - W) // 2, (im.height - H) // 2
        return im.crop((x, y, x + W, y + H)), True
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((60, 900), "(배경 그림 대기: " + name + ")", font=font(40, False), fill=(120, 130, 190))
    return im, False


def shade(img, top=(200, 760, 175), bottom=None):
    """글자가 잘 읽히도록 위(·아래)에 어두운 그라데이션을 깐다. top=(시작y, 끝y, 시작 불투명도)."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y0, y1, a = top
    for y in range(y0, y1):
        t = 1 - (y - y0) / (y1 - y0)
        d.line([(0, y), (W, y)], fill=(12, 14, 40, int(a * t)))
    if bottom:
        y0, y1, a = bottom
        for y in range(y0, y1):
            t = (y - y0) / (y1 - y0)
            d.line([(0, y), (W, y)], fill=(12, 14, 40, int(a * t)))
    base = img.convert("RGBA")
    base.alpha_composite(ov)
    return base.convert("RGB")


def tw(d, s, f):
    return d.textlength(s, font=f)


def line(d, y, segs, size, bold=True, stroke=7):
    f = font(size, bold)
    total = sum(tw(d, s, f) for s, _ in segs)
    x = (W - total) / 2
    for s, c in segs:
        d.text((x, y), s, font=f, fill=c, stroke_width=stroke, stroke_fill=NAVY)
        x += tw(d, s, f)


def caption(d, lines, y=330, size=104, gap=130):
    for i, segs in enumerate(lines):
        line(d, y + i * gap, segs, size)


def footnote(d, text, y, size=38):
    line(d, y, [(text, GRAY)], size, bold=False, stroke=5)


def card(img, box, fill, radius=30, outline=None):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 8, x1, y1 + 8], radius=radius, fill=(0, 0, 10, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    base = img.convert("RGBA")
    base.alpha_composite(sh)
    out = base.convert("RGB")
    ImageDraw.Draw(out).rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=4 if outline else 0)
    return out


def key_icon(d, x, y, kind, s=96):
    d.rounded_rectangle([x, y, x + s, y + s], radius=20, fill=KEY)
    cx, cy, r = x + s / 2, y + s / 2, s * 0.24
    if kind == "up":
        pts = [(cx, cy - r), (cx - r, cy + r * 0.8), (cx + r, cy + r * 0.8)]
    elif kind == "left":
        pts = [(cx - r, cy), (cx + r * 0.8, cy - r), (cx + r * 0.8, cy + r)]
    else:
        pts = [(cx + r, cy), (cx - r * 0.8, cy - r), (cx - r * 0.8, cy + r)]
    d.polygon(pts, fill=KEYINK)


# ---------- 장면 ----------
def scene1():
    img, ok = background("01.png")
    img = shade(img)
    d = ImageDraw.Draw(img)
    caption(d, [[("방향키", YEL), ("로", INK)], [("먹이를 잡아라!", INK)]], y=320)
    footnote(d, "파이썬으로 만든 거북이 게임", 1450)
    return img, ok


def scene2():
    img, ok = background("02.png")
    img = shade(img, top=(200, 700, 170))
    d = ImageDraw.Draw(img)
    caption(d, [[("내가 만든", INK)], [("거북이 게임", YEL)]], y=320)
    # 실제 실행 화면 캡처
    cap = Image.open(SRC / "06-실행-결과.png").convert("RGB").crop((80, 286, 1002, 1034))
    w = 480
    cap = cap.resize((w, int(cap.height * w / cap.width)), Image.LANCZOS)
    x, y = (W - w) // 2, 1120
    img = card(img, [x - 10, y - 10, x + w + 10, y + cap.height + 10], fill=YEL, radius=26)
    m = Image.new("L", cap.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, cap.width - 1, cap.height - 1], radius=18, fill=255)
    img.paste(cap, (x, y), m)
    d = ImageDraw.Draw(img)
    line(d, 1050, [("실제 실행 화면", INK)], 40, stroke=6)
    return img, ok


def scene3():
    img, ok = background("03.png")
    img = shade(img, top=(200, 700, 170), bottom=(1330, 1560, 150))
    d = ImageDraw.Draw(img)
    caption(d, [[("조종은 ", INK), ("키 세 개", YEL)], [("면 끝!", INK)]], y=320)
    items = [("up", "앞으로"), ("left", "왼쪽 돌기"), ("right", "오른쪽 돌기")]
    xs = [60, 400, 740]
    for (kind, text), x in zip(items, xs):
        key_icon(d, x, 1400, kind)
        d.text((x + 112, 1415), text, font=font(40), fill=INK, stroke_width=6, stroke_fill=NAVY)
    return img, ok


def scene4():
    img, ok = background("04.png")
    img = shade(img, top=(200, 720, 170))
    d = ImageDraw.Draw(img)
    caption(d, [[("잡으면 ", INK), ("+1점!", YEL)], [("먹이는 휙, 다른 곳으로", INK)]], y=320, size=96)
    return img, ok


def scene5():
    img, ok = background("05.png")
    img = shade(img, top=(200, 700, 170), bottom=(1380, 1580, 160))
    d = ImageDraw.Draw(img)
    caption(d, [[("숫자 하나", YEL), ("로", INK)], [("난이도가 달라져요", INK)]], y=320, size=96)
    img = card(img, [90, 1440, 990, 1540], fill=NAVY, radius=50, outline=YEL)
    d = ImageDraw.Draw(img)
    line(d, 1458, [("잡는 거리 ", INK), ("20", YEL), (" → ", INK), ("5", RED), ("  더 어려워요", INK)], 44, stroke=0)
    return img, ok


def scene6():
    img, ok = background("06.png")
    img = shade(img, top=(200, 700, 170))
    d = ImageDraw.Draw(img)
    caption(d, [[("직접 만들어", INK)], [("볼래요?", YEL)]], y=320)
    img = card(img, [120, 1300, 960, 1430], fill=YEL, radius=65)
    d = ImageDraw.Draw(img)
    line(d, 1328, [("만드는 법은 블로그에서", NAVY)], 52, stroke=0)
    footnote(d, "코드 30줄 남짓 · 네이버 코딩가이드", 1470)
    return img, ok


if __name__ == "__main__":
    scenes = [scene1, scene2, scene3, scene4, scene5, scene6]
    names = ["01-훅", "02-내가-만든-게임", "03-키-세-개", "04-먹이는-휙", "05-난이도", "06-마무리"]
    made = [fn() for fn in scenes]
    all_art = all(ok for _, ok in made)
    out = POST / "clip" if all_art else POST / "clip/미리보기"
    out.mkdir(parents=True, exist_ok=True)
    for (im, ok), nm in zip(made, names):
        p = out / f"{nm}.png"
        im.save(p)
        print(("[배경 있음] " if ok else "[임시 배경] ") + str(p))
    if not all_art:
        print("배경 그림이 아직 없는 장면이 있어 미리보기 폴더에 저장했습니다.")
