import sys, math, random
sys.path.insert(0, "/home/user/blog-codingguide/도구")
from 이미지꾸미기 import frame_card, frame_line
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
FD = "/tmp/claude-0/fonts/package/dist/public/static/"
def F(size, w="Bold"):
    return ImageFont.truetype(FD + f"Pretendard-{w}.otf", size)

BG = "#eef4fa"; INK = "#1b2a44"; ICE = "#3b8fd6"; ORG = "#ef7a2b"; GRAY = "#5f6b7d"; NAVY = "#14213a"

def ctext(d, cx, y, s, f, fill):
    w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill)

def battery(d, x, y, w, h, level, col, outline=INK, lw=7):
    # 세로형 배터리
    cap_w = w * .4
    d.rounded_rectangle((x + (w - cap_w) / 2, y - h * .07, x + (w + cap_w) / 2, y + 4), 6, fill=outline)
    d.rounded_rectangle((x, y, x + w, y + h), 18, outline=outline, width=lw, fill="white")
    pad = lw + 8
    inner_h = h - pad * 2
    top = y + pad + inner_h * (1 - level)
    d.rounded_rectangle((x + pad, top, x + w - pad, y + h - pad), 8, fill=col)

def snowflake(d, cx, cy, r, col, width=4):
    for k in range(6):
        a = math.pi / 3 * k
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        d.line((cx, cy, x2, y2), fill=col, width=width)
        for t in (.55,):
            bx, by = cx + r * t * math.cos(a), cy + r * t * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.pi / 4
                d.line((bx, by, bx + r * .3 * math.cos(b), by + r * .3 * math.sin(b)), fill=col, width=width)

def kicker(d, x, y):
    # 왼쪽 위 작은 배터리 아이콘 + 주제 이름(번호 없음)
    d.rounded_rectangle((x, y + 8, x + 22, y + 44), 5, outline=ICE, width=4)
    d.rectangle((x + 7, y + 3, x + 15, y + 9), fill=ICE)
    d.rectangle((x + 6, y + 30, x + 16, y + 39), fill=ORG)
    d.text((x + 36, y), "겨울 폰 배터리", font=F(36, "SemiBold"), fill=ICE)

# ---------------- 01 타이틀 ----------------
def title():
    W = H = 1080
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for yy in range(H):
        t = yy / H
        c = tuple(int(a + (b - a) * t) for a, b in zip((20, 33, 58), (52, 104, 158)))
        d.line((0, yy, W, yy), fill=c)
    # 뒤쪽 큰 휴대폰
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle((300, 120, 780, 1020), 70, fill=(255, 255, 255, 34), outline=(255, 255, 255, 120), width=8)
    ld.rounded_rectangle((470, 150, 610, 178), 14, fill=(255, 255, 255, 90))
    # 화면 속 배터리(낮음)
    bx, by, bw, bh = 470, 640, 140, 260
    ld.rounded_rectangle((bx + 45, by - 22, bx + 95, by + 4), 6, fill=(255, 255, 255, 170))
    ld.rounded_rectangle((bx, by, bx + bw, by + bh), 20, outline=(255, 255, 255, 170), width=9)
    ld.rounded_rectangle((bx + 18, by + bh - 70, bx + bw - 18, by + bh - 18), 8, fill=(239, 122, 43, 230))
    im = Image.alpha_composite(im.convert("RGBA"), layer)
    d = ImageDraw.Draw(im)
    random.seed(7)
    for _ in range(26):
        x, y, r = random.randint(30, 1050), random.randint(30, 1050), random.randint(14, 40)
        snowflake(d, x, y, r, (255, 255, 255, 150 if r > 25 else 110), 4 if r > 25 else 3)
    # 글자 판 뒤 살짝 어둡게
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((120, 345, 960, 735), 40, fill=(10, 20, 40, 130))
    sh = sh.filter(ImageFilter.GaussianBlur(30)); im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    f = F(132, "ExtraBold")
    l1, l2 = "겨울 폰 배터리", "왜 빨리 닳을까"
    for s, y, col in ((l1, 370, "white"), (l2, 545, "#ffb36b")):
        w = d.textlength(s, font=f)
        d.text(((W - w) / 2 + 4, y + 6), s, font=f, fill=(0, 0, 0, 120))
        d.text(((W - w) / 2, y), s, font=f, fill=col)
    im.convert("RGB").save(f"{OUT}/01-타이틀.png")

# ---------------- 02 추우면 꺼지는 이유 ----------------
def why_off():
    W, H = 1080, 1190
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 120, "배터리 숫자는 같은데", F(58), INK)
    ctext(d, W / 2, 192, "추우면 왜 꺼질까?", F(58), INK)
    cols = [(290, "따뜻할 때", "#e9a23b", False), (790, "추울 때", ICE, True)]
    for cx, lab, col, cold in cols:
        d.rounded_rectangle((cx - 230, 290, cx + 230, 1000), 30, fill="white")
        ctext(d, cx, 312, lab, F(48), col)
        if cold:
            for sx, sy in ((cx - 170, 345), (cx + 170, 345)):
                snowflake(d, sx, sy + 0, 22, ICE, 4)
        battery(d, cx - 170, 480, 110, 230, .4, "#7cc47a")
        ctext(d, cx - 115, 726, "40%", F(40), INK)
        # 전압 막대
        bx0, bx1 = cx + 20, cx + 130
        top, bot = 460, 770
        d.rectangle((bx0, top, bx1, bot), outline="#c6d0dc", width=3)
        cut = 650
        lvl = 515 if not cold else 700
        d.rectangle((bx0 + 6, lvl, bx1 - 6, bot - 6), fill=("#e9a23b" if not cold else ICE))
        d.line((bx0 - 20, cut, bx1 + 20, cut), fill=ORG, width=6)
        d.text((bx0 - 10, top - 46), "전압", font=F(36, "SemiBold"), fill=GRAY)
        ctext(d, cx, 800, "주황 선 = 꺼지는 선", F(36, "Medium"), ORG)
        if not cold:
            ctext(d, cx, 860, "전압이 선 위", F(42), INK)
            ctext(d, cx, 918, "→ 그대로 켜짐", F(42), "#2e8b57")
        else:
            ctext(d, cx, 860, "내부저항↑ 전압↓", F(42), INK)
            ctext(d, cx, 918, "→ 보호하려 꺼짐", F(42), ORG)
    d.rounded_rectangle((60, 1040, W - 60, 1140), 24, fill=NAVY)
    ctext(d, W / 2, 1062, "따뜻한 곳에 두면 대부분 다시 돌아와요", F(42, "SemiBold"), "white")
    im = frame_card(im, bg="#d9e6f2")
    im.save(f"{OUT}/02-추우면-꺼지는-이유.png")

# ---------------- 03 폰이 편한 온도 ----------------
def temp_band():
    W, H = 1080, 900
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 120, "아이폰 안내로 본 '편한 온도'", F(56), INK)
    x0, x1, t0, t1 = 90, 990, -25, 50
    X = lambda t: x0 + (x1 - x0) * (t - t0) / (t1 - t0)
    # 온도 축
    ay = 640
    d.line((x0, ay, x1, ay), fill=INK, width=4)
    for t in (-20, 0, 16, 22, 35, 45):
        d.line((X(t), ay - 12, X(t), ay + 12), fill=INK, width=4)
    for t, lab in ((-20, "-20"), (0, "0"), (35, "35"), (45, "45")):
        ctext(d, X(t), ay + 22, lab, F(40), INK)
    ctext(d, X(19), ay + 22, "16~22", F(36, "SemiBold"), "#2e8b57")
    d.text((x1 - 10, ay + 22), "℃", font=F(40), fill=INK)
    # 막대들
    rows = [(250, -20, 45, "#c6d0dc", "보관 -20~45℃", INK),
            (370, 0, 35, ICE, "쓰기 좋은 0~35℃", "white"),
            (490, 16, 22, "#2e8b57", "", "white")]
    for y, a, b, col, lab, tc in rows:
        d.rounded_rectangle((X(a), y, X(b), y + 84), 20, fill=col)
        if lab:
            ctext(d, (X(a) + X(b)) / 2, y + 16, lab, F(42), tc)
    d.text((X(22) + 20, 500), "가장 편한 구간", font=F(40), fill="#2e8b57")
    # 한겨울 바깥
    mx = X(-10)
    d.polygon(((mx, ay - 6), (mx - 18, ay - 40), (mx + 18, ay - 40)), fill=ORG)
    d.rounded_rectangle((mx - 120, 720 + 40, mx + 140, 720 + 110), 18, fill=ORG)
    ctext(d, mx + 10, 778, "한겨울 바깥", F(40), "white")
    d.line((mx, ay + 70, mx, 760), fill=ORG, width=4)
    ctext(d, 760, 790, "0℃ 아래는 '쓰기 좋은' 범위 밖", F(38, "SemiBold"), GRAY)
    im = frame_line(im, col="#9fb6cf", width=4)
    im.save(f"{OUT}/03-폰이-편한-온도.png")

# ---------------- 04 함께 보면 좋은 글 ----------------
def banner():
    W, H = 1600, 234
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, W - 8, 196), 32, fill=NAVY)
    d.polygon(((120, 190), (190, 190), (120, 232)), fill=NAVY)
    # 원 안 배터리
    d.ellipse((50, 37, 180, 167), fill="#1f3358", outline=ICE, width=8)
    battery(d, 92, 62, 46, 82, .45, ORG, outline="white", lw=5)
    d.text((225, 36), "READ NEXT", font=F(30), fill="#ffb36b")
    d.text((225, 70), "함께 보면 좋은 글", font=F(52, "ExtraBold"), fill="white")
    d.text((225, 140), "겨울 준비, 이어서 읽어 보세요", font=F(32, "Medium"), fill="#b9cfe8")
    ax = 1480
    d.rectangle((ax - 7, 55, ax + 7, 125), fill="#ffb36b")
    d.polygon(((ax - 38, 118), (ax + 38, 118), (ax, 160)), fill="#ffb36b")
    im.save(f"{OUT}/04-함께-보면-좋은-글.png")

title(); why_off(); temp_band(); banner()
print("ok")
