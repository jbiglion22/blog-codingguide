# -*- coding: utf-8 -*-
"""네이버 클립용 장면 이미지(1080x1920) 6장을 만든다 — 「인서울이 어려운 이유」 글.

다음 글의 클립을 만들 때는 이 파일을 복사해 '설정'과 장면 함수만 고쳐 쓴다.
설명: 저장소 루트 클립제작지침.md

실행: python 도구/클립장면_인서울.py
필요: Pillow, 무료 폰트 C:/Windows/Fonts/NotoSansKR-VF.ttf (없으면 Noto Sans KR 설치 후 경로 수정)
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------- 설정 ----------
ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "문서/네이버-코딩가이드/20261124_23개/20261124_인서울-대학-지도"
SRC = POST / "images"
OUT = POST / "clip"
FONT = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 240, 1540   # 클립 앱 화면이 가리는 위·아래를 피한 안전 영역

BG = (246, 244, 238)        # #f6f4ee 지도 종이
INK = (43, 47, 58)          # #2b2f3a
BLUE = (47, 93, 158)        # #2f5d9e
GOLD = (217, 154, 30)       # #d99a1e
GRAY = (110, 114, 124)
LIGHT = (209, 219, 235)
MID = (140, 163, 202)
BEIGE = (235, 232, 224)
WHITE = (255, 255, 255)


def font(size, bold=True):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name("Bold" if bold else "Regular")
    return f


def new_canvas():
    return Image.new("RGB", (W, H), BG)


def pin(d, x, y, s=44, color=BLUE):
    """작은 지도 핀 아이콘 (x, y = 왼쪽 위)."""
    r = s * 0.38
    cx, cy = x + s / 2, y + r
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    d.polygon([(cx - r * 0.78, cy + r * 0.55), (cx + r * 0.78, cy + r * 0.55), (cx, y + s)], fill=color)
    rr = r * 0.4
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=WHITE)


def header(d):
    pin(d, 60, SAFE_TOP + 4, 44)
    d.text((118, SAFE_TOP + 2), "인서울이 어려운 이유", font=font(34, False), fill=GRAY)


def text_w(d, s, f):
    return d.textlength(s, font=f)


def center_line(d, y, segs, size, bold=True):
    """segs = [(글자, 색), ...] 를 한 줄로 가운데 정렬해서 그린다."""
    f = font(size, bold)
    total = sum(text_w(d, s, f) for s, _ in segs)
    x = (W - total) / 2
    for s, c in segs:
        d.text((x, y), s, font=f, fill=c)
        x += text_w(d, s, f)


def caption(d, lines, y=310, size=68, gap=94):
    for i, segs in enumerate(lines):
        center_line(d, y + i * gap, segs, size)
    return y + len(lines) * gap


def footnote(d, lines, bottom=SAFE_BOTTOM, size=36):
    lh = int(size * 1.4)
    y = bottom - lh * len(lines)
    for i, s in enumerate(lines):
        center_line(d, y + i * lh, [(s, GRAY)], size, bold=False)


def shadow_card(img, box, fill=WHITE, radius=28, outline=None, blur=14, offset=8):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    x0, y0, x1, y1 = box
    sd.rounded_rectangle([x0, y0 + offset, x1, y1 + offset], radius=radius, fill=(40, 45, 60, 46))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA")
    base.alpha_composite(sh)
    out = base.convert("RGB")
    ImageDraw.Draw(out).rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2 if outline else 0)
    return out


def paste_crop(img, src_name, crop, top, max_w, max_h):
    """원본 그림의 일부(crop)를 잘라 영역 안에 가운데로 붙인다."""
    im = Image.open(SRC / src_name).convert("RGB").crop(crop)
    s = min(max_w / im.width, max_h / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=24, fill=255)
    img.paste(im, ((W - im.width) // 2, top), mask)
    return im.size


# ---------- 장면 ----------
def scene1():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    header(d)
    center_line(d, 560, [("인서울이", INK)], 112)
    center_line(d, 700, [("어렵다는 말,", INK)], 112)
    center_line(d, 860, [("숫자", BLUE), ("로 보면?", INK)], 112)
    # 4칸 중 1칸이 파란색 (4명 중 1명 암시)
    x0, y0, s, g = 240, 1130, 140, 24
    for i in range(4):
        c = BLUE if i == 0 else BEIGE
        d.rounded_rectangle([x0 + i * (s + g), y0, x0 + i * (s + g) + s, y0 + s], radius=24, fill=c)
    center_line(d, 1330, [("서울 대학 43곳과 정원의 비밀", GRAY)], 42, bold=False)
    return img


def scene2():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    header(d)
    caption(d, [[("전국 모집 100자리 중", INK)], [("서울 대학은 ", INK), ("약 25자리", BLUE)]])
    paste_crop(img, "03-100명-중-서울-대학.png", (0, 245, 1080, 1415), 520, 960, 890)
    footnote(d, ["대교협 195개 회원대학 2027 시행계획 기준", "서울 밖 같은 학교 캠퍼스 인원 포함"])
    return img


def scene3():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    header(d)
    caption(d, [[("서울 대학 57곳 중", INK)], [("4년제는 ", INK), ("43곳", BLUE)]])
    paste_crop(img, "02-57곳에서-43곳까지.png", (0, 255, 1080, 1375), 520, 960, 890)
    footnote(d, ["이 글에서 정한 기준으로 센 숫자", "공식 통계는 아님"])
    return img


TILES = [  # (행, 열, 구, 곳 수)  — 04번 그림과 같은 배치·숫자(합계 43)
    (0, 2, "은평", 1), (0, 3, "종로", 3), (0, 4, "성북", 7), (0, 5, "강북", 0), (0, 6, "도봉", 1),
    (1, 1, "마포", 2), (1, 2, "서대문", 6), (1, 3, "중구", 1), (1, 4, "동대문", 3), (1, 5, "중랑", 0), (1, 6, "노원", 5),
    (2, 0, "강서", 1), (2, 1, "양천", 1), (2, 2, "영등포", 0), (2, 3, "용산", 1), (2, 4, "성동", 1), (2, 5, "광진", 3),
    (3, 1, "구로", 1), (3, 2, "동작", 3), (3, 3, "서초", 1), (3, 4, "강남", 0), (3, 5, "송파", 1), (3, 6, "강동", 0),
    (4, 1, "금천", 0), (4, 2, "관악", 1),
]


def scene4():
    assert sum(t[3] for t in TILES) == 43
    img = new_canvas()
    d = ImageDraw.Draw(img)
    header(d)
    caption(d, [[("성북·서대문·노원에", INK)], [("대학이 ", INK), ("가장 많아요", BLUE)]])
    tile, pitch, x0, y0 = 140, 148, 26, 520
    for r, c, name, n in TILES:
        if n >= 4:
            fill, fg = BLUE, WHITE
        elif n >= 2:
            fill, fg = MID, WHITE
        elif n == 1:
            fill, fg = LIGHT, INK
        else:
            fill, fg = BEIGE, GRAY
        x, y = x0 + c * pitch, y0 + r * pitch
        d.rounded_rectangle([x, y, x + tile, y + tile], radius=20, fill=fill)
        fn = font(36)
        fc = font(42) if n else font(34, False)
        label = f"{n}곳" if n else "없음"
        d.text((x + (tile - text_w(d, name, fn)) / 2, y + 22), name, font=fn, fill=fg)
        d.text((x + (tile - text_w(d, label, fc)) / 2, y + 78), label, font=fc, fill=fg)
    # 범례
    ly = y0 + 5 * pitch + 16
    items = [(BLUE, "4곳 이상"), (MID, "2~3곳"), (LIGHT, "1곳"), (BEIGE, "없음")]
    fl = font(34, False)
    total = sum(48 + text_w(d, t, fl) + 36 for _, t in items) - 36
    x = (W - total) / 2
    for c, t in items:
        d.rounded_rectangle([x, ly, x + 36, ly + 36], radius=8, fill=c)
        d.text((x + 48, ly - 4), t, font=fl, fill=INK)
        x += 48 + text_w(d, t, fl) + 36
    footnote(d, ["학교 위치로 나눠 본 숫자", "실제 지도가 아니라 구 배치만 단순화"])
    return img


def scene5():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    header(d)
    caption(d, [[("이름이 같아도", INK)], [("캠퍼스가 ", INK), ("서울 밖", BLUE), ("일 수 있어요", INK)]], size=64)
    groups = [
        ("분교", "서울 본교와 따로 공시", BLUE, ["건국대 글로컬 · 충주", "고려대 세종", "동국대 WISE · 경주", "연세대 미래 · 원주", "한양대 ERICA · 안산"]),
        ("제2캠퍼스", "본교는 서울", (118, 148, 196), ["상명대 · 천안", "중앙대 · 안성", "홍익대 · 세종"]),
        ("본교가 경기", "서울은 제2캠퍼스", GOLD, ["가톨릭대 · 부천", "경기대 · 수원", "명지대 · 용인"]),
    ]
    y = 510
    for title, sub, col, rows in groups:
        row_h, head = 50, 76
        h = head + len(rows) * row_h + 18
        img = shadow_card(img, [60, y, 1020, y + h], fill=WHITE, radius=26)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([60, y, 1020, y + head], radius=26, fill=col)
        d.rectangle([60, y + 40, 1020, y + head], fill=col)
        d.text((92, y + 10), title, font=font(44), fill=WHITE)
        d.text((92 + text_w(d, title, font(44)) + 24, y + 22), sub, font=font(32, False), fill=WHITE)
        for i, r in enumerate(rows):
            center_line(d, y + head + 12 + i * row_h, [(r, INK)], 38, bold=True)
        y += h + 22
    footnote(d, ["경희대 국제캠퍼스처럼 같은 학교로 함께", "공시되는 서울 밖 캠퍼스도 있음"])
    return img


def scene6():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    header(d)
    caption(d, [[("원서 쓰기 전,", INK)], [("캠퍼스", BLUE), ("부터 확인하세요", INK)]])
    steps = ["모집요강 모집단위 표에서\n캠퍼스 이름 확인", "원서 접수 화면의\n캠퍼스 선택 칸 확인", "애매하면 입학처에\n전화로 문의"]
    y = 560
    for i, s in enumerate(steps, 1):
        img = shadow_card(img, [80, y, 1000, y + 190], radius=28)
        d = ImageDraw.Draw(img)
        d.ellipse([112, y + 55, 192, y + 135], fill=BLUE)
        n = str(i)
        d.text((152 - text_w(d, n, font(48)) / 2, y + 62), n, font=font(48), fill=WHITE)
        d.multiline_text((225, y + 36), s, font=font(44), fill=INK, spacing=14)
        y += 190 + 40
    img = shadow_card(img, [140, 1330, 940, 1470], fill=BLUE, radius=70)
    d = ImageDraw.Draw(img)
    center_line(d, 1362, [("자세한 내용은 블로그에서", WHITE)], 50)
    footnote(d, ["네이버 코딩가이드 · 인서울이 어려운 이유"])
    return img


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    scenes = [scene1, scene2, scene3, scene4, scene5, scene6]
    names = ["01-훅", "02-100자리", "03-57곳에서-43곳", "04-구별-지도", "05-다른-캠퍼스", "06-마무리"]
    for fn, nm in zip(scenes, names):
        p = OUT / f"{nm}.png"
        fn().save(p)
        print(p)
