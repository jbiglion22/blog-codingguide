"""'함께 보면 좋은 글' 공통 배너 만들기.

배너 바로 아래에 이어지는 링크들을 가리키는 모양(아래쪽 말꼬리 + 아래 화살표)이다.
결과: 자료실/공통-이미지/함께-보면-좋은-글-남색.png, -밝은색.png (1600×224)
PC마다 OUTDIR 경로를 저장소 위치에 맞게 고친다.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import 이미지꾸미기 as K

FONT = r"C:/Windows/Fonts/NotoSansKR-VF.ttf"
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "자료실", "공통-이미지")


def F(size, w="Bold"):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(w)
    return f


def banner(path, c1, c2, label_col, title_col, sub_col, pin_bg, pin_col, arrow_col):
    W, BH, TAIL = 1600, 190, 34          # 배너 높이 190 + 아래 말꼬리 34
    H = BH + TAIL
    grad = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(grad)
    for x in range(W):
        t = x / (W - 1)
        gd.line([(x, 0), (x, H)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    # 모양: 둥근 사각형 + 왼쪽 아래 말꼬리(아래 링크를 가리킴)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, W - 1, BH - 1], 30, fill=255)
    tx = 150
    md.polygon([(tx - 34, BH - 2), (tx + 34, BH - 2), (tx, H - 1)], fill=255)
    out = Image.new("RGB", (W, H), (255, 255, 255))
    out.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(out)
    # 핀 아이콘
    d.ellipse([90, 35, 210, 155], fill=pin_bg)
    K.ico_pin(d, 117, 56, 66, pin_col)
    # 글자
    d.text((250, 36), "READ NEXT", font=F(28), fill=label_col)
    d.text((248, 72), "함께 보면 좋은 글", font=F(66), fill=title_col)
    d.text((880, 98), "아래 글도 이어서 읽어 보세요", font=F(34, "Regular"), fill=sub_col)
    # 아래를 가리키는 화살표 두 개(쉐브론)
    ax = W - 140
    for k, yy in enumerate((52, 92)):
        d.line([(ax - 34, yy), (ax, yy + 34), (ax + 34, yy)], fill=arrow_col, width=11, joint="curve")
    out.save(path)


if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    banner(os.path.join(OUTDIR, "함께-보면-좋은-글-남색.png"), (31, 58, 110), (47, 90, 168),
           "#ffd27a", "#ffffff", "#dfe7f5", "#ffffff", "#d23b3b", "#ffd27a")
    banner(os.path.join(OUTDIR, "함께-보면-좋은-글-밝은색.png"), (230, 237, 250), (250, 234, 234),
           "#d23b3b", "#1f2430", "#5b6272", "#1f3a6e", "#ffd27a", "#1f3a6e")
    print("ok")
