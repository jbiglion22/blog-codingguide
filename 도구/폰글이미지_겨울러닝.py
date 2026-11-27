"""네이버 「겨울 러닝」 폰글 그림 (2026-11-28). 실행: python 폰글이미지_겨울러닝.py 출력폴더
글꼴 FD는 그 PC의 Pretendard(무료 OFL) static 폴더로 바꾼다."""
import sys, math, random
sys.path.insert(0, "/home/user/blog-codingguide/도구")
from 이미지꾸미기 import frame_card, frame_dashed, frame_accent
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
FD = "/tmp/claude-0/fonts/package/dist/public/static/"
def F(size, w="Bold"):
    return ImageFont.truetype(FD + f"Pretendard-{w}.otf", size)

BG = "#fbf7f2"; INK = "#2a2438"; COR = "#f2603f"; MINT = "#22a37f"; GRAY = "#6e6878"; SKY = "#4a78c8"

def ctext(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)

def shoe(d, x, y, s, col):
    # 옆에서 본 운동화(단순 도형)
    d.rounded_rectangle((x, y + s * .45, x + s * 1.3, y + s * .75), s * .12, fill=col)
    d.pieslice((x - s * .05, y, x + s * .9, y + s * .9), 180, 270, fill=col)
    d.rectangle((x + s * .42, y, x + s * .9, y + s * .5), fill=col)
    d.rounded_rectangle((x - s * .02, y + s * .7, x + s * 1.34, y + s * .82), s * .05, fill="white")

def watch(d, x, y, s, col, face="white"):
    # 스톱워치
    d.rectangle((x + s * .42, y, x + s * .58, y + s * .14), fill=col)
    d.ellipse((x, y + s * .12, x + s, y + s * 1.12), fill=col)
    d.ellipse((x + s * .16, y + s * .28, x + s * .84, y + s * .96), fill=face)
    cx, cy = x + s * .5, y + s * .62
    d.line((cx, cy, cx, cy - s * .26), fill=col, width=max(3, int(s * .08)))
    d.line((cx, cy, cx + s * .2, cy), fill=col, width=max(3, int(s * .08)))

def kicker(d, x, y):
    watch(d, x, y + 2, 34, COR, BG)
    d.text((x + 46, y), "겨울 러닝", font=F(36, "SemiBold"), fill=COR)

# ---------------- 01 타이틀 ----------------
def title():
    W = H = 1080
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for yy in range(H):
        t = yy / H
        top, mid, bot = (38, 32, 72), (120, 72, 110), (246, 150, 110)
        if t < .62:
            u = t / .62; c = tuple(int(a + (b - a) * u) for a, b in zip(top, mid))
        else:
            u = (t - .62) / .38; c = tuple(int(a + (b - a) * u) for a, b in zip(mid, bot))
        d.line((0, yy, W, yy), fill=c)
    # 해
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.ellipse((390, 770, 690, 1070), fill=(255, 214, 150, 200))
    gl = gl.filter(ImageFilter.GaussianBlur(18))
    im = Image.alpha_composite(im.convert("RGBA"), gl); d = ImageDraw.Draw(im)
    # 트랙(원근 곡선 레인)
    for k in range(5):
        off = k * 90
        pts = []
        for i in range(60):
            t = i / 59
            x = -120 + off + t * (1300 - off * .3)
            y = 1080 - (t ** 1.4) * 260 + k * 40 - 20
            pts.append((x, y))
        d.line(pts, fill=(255, 255, 255, 170), width=6)
    # 눈송이
    random.seed(11)
    for _ in range(22):
        x, y, r = random.randint(30, 1050), random.randint(30, 700), random.randint(10, 26)
        for kk in range(3):
            a = math.pi / 3 * kk
            d.line((x - r * math.cos(a), y - r * math.sin(a), x + r * math.cos(a), y + r * math.sin(a)), fill=(255, 255, 255, 150), width=3)
    # 큰 운동화(글자 뒤)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((100, 350, 980, 730), 40, fill=(20, 14, 36, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(30)); im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    for s, y, col, sz in (("겨울 러닝", 362, "white", 140), ("몇 도까지 괜찮을까?", 560, "#ffc49a", 98)):
        f = F(sz, "ExtraBold"); w = d.textlength(s, font=f)
        d.text(((W - w) / 2 + 4, y + 6), s, font=f, fill=(0, 0, 0, 140))
        d.text(((W - w) / 2, y), s, font=f, fill=col)
    im.convert("RGB").save(f"{OUT}/01-타이틀.png")

# ---------------- 02 옷 겹쳐 입기 ----------------
def layers():
    W, H = 1080, 1240
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 118, "얇게 세 겹, 머리·손·목은 따로", F(54), INK)
    rows = [("겉", "바람막이", "바람을 막고, 밝은 색이나 반사 띠", "#3d3552", "white"),
            ("가운데", "얇은 보온층", "추운 날만 더하는 얇은 플리스 등", "#8d7aa8", "white"),
            ("속", "땀이 빨리 마르는 옷", "면 티셔츠는 땀을 머금어 차가워져요", "#f4dfd3", INK)]
    y = 230
    for i, (tag, name, desc, col, tc) in enumerate(rows):
        inset = i * 40
        d.rounded_rectangle((60 + inset, y, W - 60 - inset, y + 210), 28, fill=col)
        d.text((100 + inset, y + 30), tag, font=F(38, "SemiBold"), fill=tc)
        d.text((100 + inset, y + 82), name, font=F(52), fill=tc)
        d.text((100 + inset, y + 150), desc, font=F(36, "Medium"), fill=tc)
        y += 235
    # 작은 것들
    d.rounded_rectangle((60, y + 10, W - 60, y + 240), 28, fill="white", outline="#e6dfd6", width=3)
    items = [("모자", 0), ("장갑", 1), ("목 가리개", 2)]
    for name, k in items:
        cx = 60 + (W - 120) / 6 * (2 * k + 1)
        cy = y + 85
        if k == 0:
            d.pieslice((cx - 55, cy - 50, cx + 55, cy + 60), 180, 360, fill=COR)
            d.rectangle((cx - 60, cy + 2, cx + 60, cy + 22), fill="#c84a2e")
            d.ellipse((cx - 14, cy - 66, cx + 14, cy - 38), fill=COR)
        elif k == 1:
            d.rounded_rectangle((cx - 35, cy - 45, cx + 35, cy + 45), 26, fill=COR)
            d.rounded_rectangle((cx - 62, cy - 12, cx - 28, cy + 18), 14, fill=COR)
            d.rectangle((cx - 35, cy + 30, cx + 35, cy + 48), fill="#c84a2e")
        else:
            d.rounded_rectangle((cx - 60, cy - 40, cx + 60, cy + 40), 30, outline=COR, width=18)
        ctext(d, cx, y + 160, name, F(40), INK)
    im = frame_card(im, bg="#efe6dc")
    im.save(f"{OUT}/02-옷-겹쳐-입기.png")

# ---------------- 03 출발할 땐 살짝 춥게 ----------------
def thermo():
    W, H = 1080, 1000
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 118, "실제 기온보다 따뜻한 날처럼 입기", F(52), INK)
    def therm(cx, level, col, lab1, lab2, temp):
        d.rounded_rectangle((cx - 40, 250, cx + 40, 700), 40, fill="white", outline="#d9d0c6", width=5)
        d.ellipse((cx - 70, 650, cx + 70, 790), fill=col)
        top = 700 - 430 * level
        d.rounded_rectangle((cx - 22, top, cx + 22, 720), 20, fill=col)
        ctext(d, cx, 820, lab1, F(44), INK)
        ctext(d, cx, 880, lab2, F(38, "Medium"), GRAY)
        d.text((cx + 70, top - 30), temp, font=F(56, "ExtraBold"), fill=col)
    therm(300, .32, SKY, "실제 기온", "예: 0℃ 아침", "0℃")
    therm(760, .55, COR, "옷은 이 날씨처럼", "약 8~11℃ 날의 옷", "8~11℃")
    # 화살표
    d.line((420, 470, 620, 470), fill=GRAY, width=8)
    d.polygon(((620, 448), (660, 470), (620, 492)), fill=GRAY)
    ctext(d, 540, 400, "달리면 데워져요", F(36, "SemiBold"), GRAY)
    im = frame_dashed(im, col=COR)
    im.save(f"{OUT}/03-살짝-춥게-입기.png")

# ---------------- 04 달리기 전후 순서 ----------------
def flow():
    W, H = 1080, 1300
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    kicker(d, 60, 48)
    ctext(d, W / 2, 118, "추운 날 달리기, 이 순서로", F(56), INK)
    steps = [("나가기 전", "체감온도·길 상태 확인", SKY),
             ("실내에서", "몸을 움직이는 준비운동", MINT),
             ("달리는 중", "물 조금씩, 빙판·그늘길 피하기", COR),
             ("끝나자마자", "젖은 옷부터 갈아입기", "#8d7aa8")]
    y = 240
    for i, (a, b, col) in enumerate(steps):
        d.ellipse((80, y + 20, 180, y + 120), fill=col)
        ctext(d, 130, y + 40, str(i + 1), F(52, "ExtraBold"), "white")
        d.rounded_rectangle((220, y, W - 60, y + 150), 24, fill="white")
        d.text((256, y + 22), a, font=F(46), fill=col)
        d.text((256, y + 88), b, font=F(40, "Medium"), fill=INK)
        if i < len(steps) - 1:
            d.line((130, y + 130, 130, y + 250), fill="#d9d0c6", width=8)
        y += 250
    im = frame_accent(im, col=COR)
    im.save(f"{OUT}/04-달리기-전후-순서.png")

# ---------------- 05 함께 보면 좋은 글 ----------------
def banner():
    W, H = 1600, 234
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, W - 8, 196), 32, fill="#3d3552")
    d.polygon(((120, 192), (190, 192), (120, 232)), fill="#3d3552")
    d.ellipse((50, 37, 180, 167), fill=COR)
    watch(d, 78, 52, 74, "white", COR)
    d.text((225, 36), "READ NEXT", font=F(30), fill="#ffc49a")
    d.text((225, 70), "함께 보면 좋은 글", font=F(52, "ExtraBold"), fill="white")
    d.text((225, 140), "겨울 아침 밖에 나가기 전에, 이어서 읽어 보세요", font=F(32, "Medium"), fill="#d9cfe6")
    ax = 1480
    d.rectangle((ax - 7, 55, ax + 7, 125), fill="#ffc49a")
    d.polygon(((ax - 38, 118), (ax + 38, 118), (ax, 160)), fill="#ffc49a")
    im.save(f"{OUT}/05-함께-보면-좋은-글.png")

title(); layers(); thermo(); flow(); banner()
print("ok")
