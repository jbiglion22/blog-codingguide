"""네이버 「블랙아이스」 폰글 그림 (2026-11-28). 실행: python 폰글이미지_블랙아이스.py 출력폴더
글꼴 FD는 그 PC의 Pretendard(무료 OFL) static 폴더로 바꾼다."""
import sys, math, random
sys.path.insert(0, "/home/user/blog-codingguide/도구")
from 이미지꾸미기 import frame_double, frame_accent, frame_corners
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
FD = "/tmp/claude-0/fonts/package/dist/public/static/"
def F(size, w="Bold"):
    return ImageFont.truetype(FD + f"Pretendard-{w}.otf", size)

BG = "#f2f5f7"; INK = "#22303a"; ICE = "#1aa3b8"; RED = "#e2574c"; GRAY = "#66737d"; ASPH = "#3a3f46"

def ctext(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)

def kicker(d, x, y):
    # 왼쪽 위 작은 얼음 결정 아이콘 + 주제 이름(번호 없음)
    cx, cy, r = x + 18, y + 24, 17
    for k in range(3):
        a = math.pi / 3 * k
        d.line((cx - r * math.cos(a), cy - r * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a)), fill=ICE, width=4)
    d.text((x + 46, y), "블랙아이스", font=F(36, "SemiBold"), fill=ICE)

# ---------------- 01 타이틀 ----------------
def title():
    W = H = 1080
    im = Image.new("RGB", (W, H), "#1b2027"); d = ImageDraw.Draw(im)
    # 원근 도로
    hy = 330
    d.rectangle((0, 0, W, hy), fill="#18222e")
    for yy in range(hy):
        t = yy / hy
        d.line((0, yy, W, yy), fill=tuple(int(a + (b - a) * t) for a, b in zip((14, 22, 34), (40, 58, 78))))
    d.polygon(((470, hy), (610, hy), (1180, H), (-100, H)), fill=ASPH)
    # 가장자리 흰 선
    d.line((470, hy, -100, H), fill="#d9dde2", width=10)
    d.line((610, hy, 1180, H), fill="#d9dde2", width=10)
    # 가운데 점선
    for i in range(7):
        t0, t1 = (i / 7) ** 1.6, ((i + .5) / 7) ** 1.6
        y0, y1 = hy + (H - hy) * t0, hy + (H - hy) * t1
        w0, w1 = 3 + 22 * t0, 3 + 22 * t1
        d.polygon(((540 - w0 / 2, y0), (540 + w0 / 2, y0), (540 + w1 / 2, y1), (540 - w1 / 2, y1)), fill="#e8b84a")
    # 얼음 광택
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.ellipse((180, 700, 900, 980), fill=(150, 220, 235, 70))
    g.ellipse((300, 760, 760, 900), fill=(200, 240, 250, 60))
    gl = gl.filter(ImageFilter.GaussianBlur(25))
    im = Image.alpha_composite(im.convert("RGBA"), gl)
    g2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(g2)
    for x0, y0, L in ((330, 820, 160), (560, 860, 120), (420, 900, 200)):
        g.line((x0, y0, x0 + L, y0 - L * .18), fill=(235, 250, 255, 150), width=5)
    # 가로등 불빛
    for x in (150, 930):
        g.ellipse((x - 120, 120, x + 120, 360), fill=(255, 210, 120, 40))
    g2 = g2.filter(ImageFilter.GaussianBlur(6))
    im = Image.alpha_composite(im, g2)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((110, 350, 970, 730), 40, fill=(8, 12, 18, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(30)); im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    f = F(140, "ExtraBold")
    for s, y, col in (("블랙아이스", 365, "white"), ("왜 안 보일까?", 545, "#7fe0ee")):
        w = d.textlength(s, font=f)
        d.text(((W - w) / 2 + 4, y + 6), s, font=f, fill=(0, 0, 0, 140))
        d.text(((W - w) / 2, y), s, font=f, fill=col)
    im.convert("RGB").save(f"{OUT}/01-타이틀.png")

# ---------------- 02 왜 안 보일까(단면도) ----------------
def section():
    W, H = 1080, 1000
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 118, "얇은 얼음 아래로", F(56), INK)
    ctext(d, W / 2, 188, "검은 아스팔트가 그대로 비친다", F(56), INK)
    # 눈 (보는 사람)
    ex, ey = 170, 360
    d.ellipse((ex - 50, ey - 30, ex + 50, ey + 30), outline=INK, width=6, fill="white")
    d.ellipse((ex - 16, ey - 16, ex + 16, ey + 16), fill=INK)
    # 시선
    for k in range(3):
        d.line((ex + 40, ey + 20 + k * 6, 560 + k * 120, 640), fill="#9aa6ae", width=4)
    # 단면
    top = 620
    d.rectangle((60, top, W - 60, top + 26), fill="#bfe9f0")  # 얼음
    d.line((60, top, W - 60, top), fill=ICE, width=5)
    d.rectangle((60, top + 26, W - 60, top + 230), fill=ASPH)  # 아스팔트
    random.seed(3)
    for _ in range(90):
        x, y = random.randint(70, W - 70), random.randint(top + 40, top + 220)
        r = random.randint(3, 9)
        d.ellipse((x - r, y - r, x + r, y + r), fill=random.choice(("#4a5058", "#2e3238", "#575d65")))
    # 이름표
    d.text((640, 470), "얇고 투명한 얼음", font=F(42), fill=ICE)
    d.line((760, 525, 760, top - 4), fill=ICE, width=4)
    ctext(d, W / 2, top + 95, "아스팔트", F(48), "white")
    ctext(d, W / 2, 880, "→ 젖은 길이나 마른 길처럼 보여요", F(44), RED)
    im = frame_accent(im, col=ICE)
    im.save(f"{OUT}/02-왜-안-보일까.png")

# ---------------- 03 잘 생기는 곳 ----------------
def places():
    W, H = 1080, 1260
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 118, "먼저 어는 세 곳", F(60), INK)
    rows = [("다리 위", "위아래로 찬 바람을 맞아", "땅 위 도로보다 빨리 식어요"),
            ("터널 출입구", "안팎 온도가 달라", "나오자마자 얼어 있을 수 있어요"),
            ("그늘진 길·산모퉁이", "햇볕이 안 들어", "낮에도 녹지 않고 남아요")]
    y = 240
    for i, (t, a, b) in enumerate(rows):
        d.rounded_rectangle((60, y, W - 60, y + 300), 26, fill="white")
        ix, iy = 110, y + 70
        if i == 0:  # 다리
            d.rectangle((ix, iy + 60, ix + 200, iy + 78), fill=INK)
            for px in (ix + 30, ix + 150):
                d.rectangle((px, iy + 78, px + 22, iy + 160), fill=INK)
            for k in range(3):
                d.line((ix + 20 + k * 60, iy + 10, ix + 40 + k * 60, iy + 45), fill=ICE, width=6)
                d.line((ix + 20 + k * 60, iy + 120, ix + 40 + k * 60, iy + 155), fill=ICE, width=6)
        elif i == 1:  # 터널
            d.pieslice((ix, iy, ix + 200, iy + 200), 180, 360, fill=INK)
            d.rectangle((ix, iy + 100, ix + 200, iy + 160), fill=INK)
            d.pieslice((ix + 40, iy + 40, ix + 160, iy + 160), 180, 360, fill="#e9eef1")
            d.rectangle((ix + 40, iy + 100, ix + 160, iy + 160), fill="#e9eef1")
            d.rectangle((ix - 10, iy + 160, ix + 210, iy + 172), fill=ICE)
        else:  # 산모퉁이 그늘
            d.polygon(((ix, iy + 160), (ix + 110, iy), (ix + 210, iy + 160)), fill=INK)
            d.polygon(((ix + 110, iy), (ix + 210, iy + 160), (ix + 140, iy + 160)), fill="#465560")
            d.rectangle((ix - 10, iy + 160, ix + 210, iy + 172), fill=ICE)
        d.text((360, y + 50), t, font=F(50), fill=INK)
        d.text((360, y + 135), a, font=F(40, "Medium"), fill=GRAY)
        d.text((360, y + 195), b, font=F(40, "Medium"), fill=GRAY)
        y += 330
    im = frame_corners(im, col=RED)
    im.save(f"{OUT}/03-잘-생기는-곳.png")

# ---------------- 04 제동거리 ----------------
def braking():
    W, H = 1080, 1080
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 118, "시속 60km에서 멈추기까지", F(56), INK)
    ctext(d, W / 2, 190, "한국교통안전공단 실험", F(38, "Medium"), GRAY)
    data = [("승용차", 10.1, 49.9, "4.9배"), ("화물차", 10.3, 77.8, "7.5배"), ("버스", 16.2, 118.7, "7.3배")]
    x0, xmax, scale = 250, 1000, 750 / 120
    y = 300
    for name, dry, ice, r in data:
        d.text((70, y + 40), name, font=F(46), fill=INK)
        d.rounded_rectangle((x0, y, x0 + dry * scale, y + 60), 10, fill="#9aa6ae")
        d.text((x0 + dry * scale + 16, y + 6), f"마른 길 {dry}m", font=F(38, "SemiBold"), fill=GRAY)
        d.rounded_rectangle((x0, y + 76, x0 + ice * scale, y + 136), 10, fill=ICE)
        lab = f"빙판 {ice}m"
        lw = d.textlength(lab, font=F(38))
        if x0 + ice * scale + 16 + lw < W - 40:
            d.text((x0 + ice * scale + 16, y + 82), lab, font=F(38), fill=ICE)
        else:
            d.text((x0 + ice * scale - lw - 16, y + 82), lab, font=F(38), fill="white")
        d.text((x0, y + 150), f"약 {r}", font=F(40), fill=RED)
        y += 250
    im = frame_double(im, col=INK)
    im.save(f"{OUT}/04-제동거리.png")

# ---------------- 05 함께 보면 좋은 글 ----------------
def banner():
    W, H = 1600, 234
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, W - 8, 196), 32, fill="#e6f4f6", outline=ICE, width=4)
    d.polygon(((120, 192), (190, 192), (120, 232)), fill=ICE)
    d.ellipse((50, 37, 180, 167), fill=ICE)
    cx, cy, r = 115, 102, 42
    for k in range(3):
        a = math.pi / 3 * k
        d.line((cx - r * math.cos(a), cy - r * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a)), fill="white", width=8)
    d.text((225, 36), "READ NEXT", font=F(30), fill=ICE)
    d.text((225, 70), "함께 보면 좋은 글", font=F(52, "ExtraBold"), fill=INK)
    d.text((225, 140), "겨울 준비, 이어서 읽어 보세요", font=F(32, "Medium"), fill=GRAY)
    ax = 1480
    d.rectangle((ax - 7, 55, ax + 7, 125), fill=ICE)
    d.polygon(((ax - 38, 118), (ax + 38, 118), (ax, 160)), fill=ICE)
    im.save(f"{OUT}/05-함께-보면-좋은-글.png")

title(); section(); places(); braking(); banner()
print("ok")
