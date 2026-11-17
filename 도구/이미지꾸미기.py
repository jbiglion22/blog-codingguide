"""표·차트·도식 이미지에 쓰는 테두리와 아이콘 모음 (Pillow).

사용 예:
    import sys; sys.path.insert(0, "도구")
    from 이미지꾸미기 import *
    ico_camera(d, x, y, 40, "#2d5fb8")        # 그림 위에 아이콘 그리기
    im = frame_card(im)                       # 다 그린 뒤 테두리 입히기

원칙(AGENTS.md "표·도식 이미지 테두리와 아이콘"):
- 테두리는 이미지 성격에 맞게 골라 글마다·이미지마다 다르게 쓴다. 모두 같은 테두리를 넣지 않는다.
- 아이콘은 글자를 대신하지 않고 옆에서 거든다. 상표·실제 로고·국기처럼 정확히 그려야 하는 것은 그리지 않는다.
- 폰트는 무료 폰트(Noto Sans KR)만 쓴다. 이모지 폰트(Windows 전용)는 쓰지 않고 아이콘은 도형으로 직접 그린다.
"""
from PIL import Image, ImageDraw, ImageFilter
import math

# ---------------- 테두리 ----------------

def frame_line(im, col="#c9ced8", width=3):
    """얇은 선. 가장 무난한 표에."""
    im = im.copy(); d = ImageDraw.Draw(im); w, h = im.size
    d.rectangle((0, 0, w - 1, h - 1), outline=col, width=width)
    return im


def frame_double(im, col="#1f2430", gap=10):
    """겹선. 법·제도·공문서 느낌의 표에."""
    pad = gap + 14
    w, h = im.size
    out = Image.new("RGB", (w + pad * 2, h + pad * 2), "white")
    out.paste(im, (pad, pad)); d = ImageDraw.Draw(out); W, H = out.size
    d.rectangle((4, 4, W - 5, H - 5), outline=col, width=4)
    d.rectangle((4 + gap, 4 + gap, W - 5 - gap, H - 5 - gap), outline=col, width=1)
    return out


def frame_card(im, bg="#eef1f5", radius=28, pad=36):
    """둥근 카드 + 그림자. 비교·정리 도식에."""
    w, h = im.size
    out = Image.new("RGB", (w + pad * 2, h + pad * 2), bg)
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad + 4, pad + 8, pad + w + 4, pad + h + 8), radius, fill=(0, 0, 0, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); out.paste(sh, (0, 0), sh)
    mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    out.paste(im, (pad, pad), mask)
    return out


def frame_accent(im, col="#2d5fb8", bar=16):
    """왼쪽 굵은 색 띠 + 얇은 선. 연표·흐름 도식에."""
    w, h = im.size
    out = Image.new("RGB", (w + bar, h), "white"); out.paste(im, (bar, 0))
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, bar - 1, h - 1), fill=col)
    d.rectangle((0, 0, w + bar - 1, h - 1), outline="#d5dae5", width=2)
    return out


def frame_dashed(im, col="#6b4fd8", dash=18, gap=10, width=4, radius=24, pad=18):
    """둥근 점선. 아이디어·제안·'~하려던 것' 도식에."""
    w, h = im.size
    out = Image.new("RGB", (w + pad * 2, h + pad * 2), "white"); out.paste(im, (pad, pad))
    d = ImageDraw.Draw(out); W, H = out.size
    x0, y0, x1, y1 = 6, 6, W - 7, H - 7
    def seg_line(a, b):
        (ax, ay), (bx, by) = a, b
        L = math.hypot(bx - ax, by - ay); n = 0.0
        while n < L:
            e = min(n + dash, L)
            d.line((ax + (bx - ax) * n / L, ay + (by - ay) * n / L, ax + (bx - ax) * e / L, ay + (by - ay) * e / L), fill=col, width=width)
            n += dash + gap
    r = radius
    seg_line((x0 + r, y0), (x1 - r, y0)); seg_line((x0 + r, y1), (x1 - r, y1))
    seg_line((x0, y0 + r), (x0, y1 - r)); seg_line((x1, y0 + r), (x1, y1 - r))
    for (cx, cy, s) in [(x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)]:
        d.arc((cx - r, cy - r, cx + r, cy + r), s, s + 90, fill=col, width=width)
    return out


def frame_corners(im, col="#d84444", L=60, width=6, pad=20):
    """네 모서리만 꺾쇠. 경고·주의 도식에."""
    w, h = im.size
    out = Image.new("RGB", (w + pad * 2, h + pad * 2), "white"); out.paste(im, (pad, pad))
    d = ImageDraw.Draw(out); W, H = out.size; o = 6
    for (x, y, sx, sy) in [(o, o, 1, 1), (W - 1 - o, o, -1, 1), (o, H - 1 - o, 1, -1), (W - 1 - o, H - 1 - o, -1, -1)]:
        d.line((x, y, x + sx * L, y), fill=col, width=width); d.line((x, y, x, y + sy * L), fill=col, width=width)
    return out


# ---------------- 아이콘 (x, y = 왼쪽 위, s = 크기) ----------------

def ico_camera(d, x, y, s, col):
    d.rounded_rectangle((x, y + s * .25, x + s, y + s * .9), s * .12, fill=col)
    d.rectangle((x + s * .3, y + s * .12, x + s * .62, y + s * .3), fill=col)
    d.ellipse((x + s * .3, y + s * .38, x + s * .7, y + s * .78), fill="white")
    d.ellipse((x + s * .4, y + s * .48, x + s * .6, y + s * .68), fill=col)


def ico_wave(d, x, y, s, col):
    cx, cy = x + s * .25, y + s * .75
    d.ellipse((cx - s * .1, cy - s * .1, cx + s * .1, cy + s * .1), fill=col)
    for r in (s * .35, s * .6, s * .85):
        d.arc((cx - r, cy - r, cx + r, cy + r), 270, 360, fill=col, width=max(3, int(s * .09)))


def ico_bag(d, x, y, s, col):
    d.rounded_rectangle((x + s * .1, y + s * .35, x + s * .9, y + s), s * .1, fill=col)
    d.arc((x + s * .3, y + s * .05, x + s * .7, y + s * .6), 180, 360, fill=col, width=max(3, int(s * .09)))


def ico_doc(d, x, y, s, col):
    d.rounded_rectangle((x + s * .15, y, x + s * .85, y + s), s * .08, fill=col)
    for i in range(3):
        yy = y + s * (.25 + i * .22)
        d.line((x + s * .28, yy, x + s * .72, yy), fill="white", width=max(2, int(s * .07)))


def ico_calendar(d, x, y, s, col):
    d.rounded_rectangle((x, y + s * .15, x + s, y + s), s * .1, outline=col, width=max(3, int(s * .08)))
    d.rectangle((x, y + s * .15, x + s, y + s * .38), fill=col)
    for i in range(2):
        xx = x + s * (.28 + i * .44)
        d.line((xx, y, xx, y + s * .25), fill=col, width=max(3, int(s * .09)))
    for r in range(2):
        for c in range(3):
            xx = x + s * (.18 + c * .25); yy = y + s * (.52 + r * .22)
            d.rectangle((xx, yy, xx + s * .14, yy + s * .12), fill=col)


def ico_pin(d, x, y, s, col):
    d.ellipse((x + s * .15, y, x + s * .85, y + s * .7), fill=col)
    d.polygon([(x + s * .22, y + s * .5), (x + s * .78, y + s * .5), (x + s * .5, y + s)], fill=col)
    d.ellipse((x + s * .37, y + s * .22, x + s * .63, y + s * .48), fill="white")


def ico_globe(d, x, y, s, col):
    w = max(3, int(s * .07))
    d.ellipse((x, y, x + s, y + s), outline=col, width=w)
    d.ellipse((x + s * .28, y, x + s * .72, y + s), outline=col, width=w)
    d.line((x, y + s * .5, x + s, y + s * .5), fill=col, width=w)


def ico_person(d, x, y, s, col):
    d.ellipse((x + s * .3, y, x + s * .7, y + s * .4), fill=col)
    d.pieslice((x + s * .08, y + s * .45, x + s * .92, y + s * 1.3), 180, 360, fill=col)


def ico_receipt(d, x, y, s, col):
    pts = [(x + s * .15, y), (x + s * .85, y), (x + s * .85, y + s)]
    n = 4
    for i in range(n * 2 + 1):
        px = x + s * .85 - (s * .7) * i / (n * 2)
        py = y + s * (.88 if i % 2 else 1.0)
        pts.append((px, py))
    pts.append((x + s * .15, y))
    d.polygon(pts, fill=col)
    for i in range(3):
        yy = y + s * (.2 + i * .2)
        d.line((x + s * .28, yy, x + s * .72, yy), fill="white", width=max(2, int(s * .07)))


def ico_swap(d, x, y, s, col):
    w = max(3, int(s * .09))
    d.line((x + s * .1, y + s * .3, x + s * .8, y + s * .3), fill=col, width=w)
    d.polygon([(x + s * .75, y + s * .12), (x + s * .98, y + s * .3), (x + s * .75, y + s * .48)], fill=col)
    d.line((x + s * .2, y + s * .72, x + s * .9, y + s * .72), fill=col, width=w)
    d.polygon([(x + s * .25, y + s * .54), (x + s * .02, y + s * .72), (x + s * .25, y + s * .9)], fill=col)


def ico_db(d, x, y, s, col):
    for i in range(3):
        yy = y + s * (i * .3)
        d.ellipse((x + s * .1, yy, x + s * .9, yy + s * .28), fill=col, outline="white", width=max(2, int(s * .05)))


def ico_chip(d, x, y, s, col):
    w = max(2, int(s * .07))
    for i in range(3):
        o = s * (.3 + i * .2)
        d.line((x + o, y, x + o, y + s), fill=col, width=w)
        d.line((x, y + o, x + s, y + o), fill=col, width=w)
    d.rounded_rectangle((x + s * .18, y + s * .18, x + s * .82, y + s * .82), s * .08, fill=col)
    d.rectangle((x + s * .36, y + s * .36, x + s * .64, y + s * .64), fill="white")


def ico_check(d, x, y, s, col):
    d.ellipse((x, y, x + s, y + s), fill=col)
    d.line((x + s * .25, y + s * .52, x + s * .43, y + s * .7, x + s * .76, y + s * .32), fill="white", width=max(3, int(s * .12)), joint="curve")


def ico_cross(d, x, y, s, col):
    d.ellipse((x, y, x + s, y + s), fill=col)
    w = max(3, int(s * .12))
    d.line((x + s * .3, y + s * .3, x + s * .7, y + s * .7), fill="white", width=w)
    d.line((x + s * .7, y + s * .3, x + s * .3, y + s * .7), fill="white", width=w)


def ico_scale(d, x, y, s, col):
    """저울(법·균형)."""
    w = max(3, int(s * .08))
    d.line((x + s * .5, y + s * .08, x + s * .5, y + s * .9), fill=col, width=w)
    d.line((x + s * .12, y + s * .22, x + s * .88, y + s * .22), fill=col, width=w)
    d.rectangle((x + s * .3, y + s * .88, x + s * .7, y + s * .98), fill=col)
    for cx in (x + s * .18, x + s * .82):
        d.line((cx, y + s * .22, cx - s * .12, y + s * .55), fill=col, width=max(2, w // 2))
        d.line((cx, y + s * .22, cx + s * .12, y + s * .55), fill=col, width=max(2, w // 2))
        d.chord((cx - s * .16, y + s * .45, cx + s * .16, y + s * .68), 0, 180, fill=col)


def frame_title(im, col="#ffe14d", border=34, inner=8, radius=36, edge="#1f2430"):
    """타이틀(대표) 이미지용 굵은 색 테두리. 글의 얼굴이라 눈에 띄게.
    col은 타이틀 글자나 사진의 주된 색에 맞춰 고른다(예: 노란 제목 글자 → 노란 테두리).
    정사각형 크기는 그대로 두고, 사진을 조금 줄여 안쪽에 둥글게 넣는다. 바깥에 어두운 얇은 선을 둘러 흰 본문에서도 경계가 보이게 한다."""
    im = im.convert("RGB"); W, H = im.size
    photo = im.resize((W - 2 * border, H - 2 * border))
    out = Image.new("RGB", (W, H), col)
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, photo.width - 1, photo.height - 1), radius, fill=255)
    out.paste(photo, (border, border), mask)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((border - 2, border - 2, W - border + 1, H - border + 1), radius + 2, outline="white", width=inner)
    d.rectangle((0, 0, W - 1, H - 1), outline=edge, width=4)
    return out
