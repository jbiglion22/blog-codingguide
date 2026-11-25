# -*- coding: utf-8 -*-
"""네이버 클립용 배경음악을 직접 합성한다 (저작권 문제가 없는 자작 음원).

세 가지 분위기를 만들 수 있다.
  calm   : 잔잔한 피아노풍 아르페지오 (C-G-Am-F, 76BPM)           → 배경음악_차분.wav/.mp3
  mid    : 차분과 밝음의 중간. 따뜻하고 가볍게 (G-D-Em-C, 88BPM)  → 배경음악.wav/.mp3 (기본)
  bright : 밝고 경쾌한 아르페지오 + 반짝이는 높은 음 + 가벼운 리듬 (D-A-Bm-G, 100BPM) → 배경음악_밝음.wav/.mp3
음성(낭독) 아래에 깔릴 것을 생각해 소리를 작게(최대 약 -10dBFS) 만든다.

실행: python 도구/클립음악_인서울.py          (셋 다 만든다)
      python 도구/클립음악_인서울.py mid      (하나만)
결과: 글 폴더의 clip/ 안 (ffmpeg가 있으면 mp3도)
필요: 표준 라이브러리만 (numpy 불필요). mp3 변환에는 ffmpeg.
다음 글에서는 이 파일을 복사해 POST 경로와 STYLES(BPM·코드·길이)를 고쳐 쓴다. 설명: 클립제작지침.md
"""
import math
import random
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "문서/네이버-코딩가이드/20261124_23개/20261124_인서울-대학-지도"
OUT = POST / "clip"

SR = 44100
FADE_IN, FADE_OUT = 1.5, 3.0
PEAK = 0.32                    # 최대 진폭(약 -10dBFS). 음성 아래에 깔리게 작게.
ARP_PATTERN = [0, 1, 2, 3, 2, 1, 2, 3]   # 한 마디(8분음표 8개)

# 코드마다: (아르페지오 4음, 베이스, 멜로디 음) — MIDI 음 번호
STYLES = {
    "calm": dict(
        file="배경음악_차분", bpm=76, bars=13, seed=7,
        chords=[([60, 64, 67, 72], 48, 76), ([59, 62, 67, 71], 43, 74),
                ([57, 60, 64, 69], 45, 72), ([57, 60, 65, 69], 41, 72)],
        arp_len=1.3, arp_tau=0.55, arp_amp=0.085, arp_harm=(1.0, 0.35, 0.12),
        sparkle=False, shaker=False, melody_from=4, pad_amp=0.035,
    ),
    "mid": dict(
        file="배경음악_중간", bpm=88, bars=15, seed=5,
        chords=[([59, 62, 67, 71], 43, 74), ([57, 62, 66, 69], 38, 78),
                ([59, 64, 67, 71], 40, 79), ([60, 64, 67, 72], 48, 76)],
        arp_len=1.0, arp_tau=0.42, arp_amp=0.09, arp_harm=(1.0, 0.4, 0.15),
        sparkle=False, shaker=False, melody_from=3, pad_amp=0.035,
    ),
    "bright": dict(
        file="배경음악_밝음", bpm=100, bars=17, seed=11,
        chords=[([62, 66, 69, 74], 50, 81), ([61, 64, 69, 73], 45, 81),
                ([62, 66, 71, 74], 47, 78), ([62, 67, 71, 74], 43, 79)],
        arp_len=0.75, arp_tau=0.30, arp_amp=0.10, arp_harm=(1.0, 0.5, 0.25, 0.12),
        sparkle=True, shaker=True, melody_from=2, pad_amp=0.03,
    ),
}


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def add_note(buf, start, midi, dur, amp, attack=0.004, tau=0.55, harm=(1.0, 0.35, 0.12)):
    """buf[start초부터 dur초]에 지수로 줄어드는 소리를 더한다."""
    f = hz(midi)
    s0 = int(start * SR)
    if s0 >= len(buf):
        return
    n = min(int(dur * SR), len(buf) - s0)
    atk = max(1, int(attack * SR))
    for i in range(n):
        t = i / SR
        env = math.exp(-t / tau)
        if i < atk:
            env *= i / atk
        left = n - i
        if left < 400:
            env *= left / 400
        w = 2 * math.pi * f * t
        v = 0.0
        for k, a in enumerate(harm, 1):
            v += a * math.sin(k * w)
        buf[s0 + i] += amp * env * v


def add_pad(buf, start, midis, dur, amp):
    """천천히 커졌다 줄어드는 부드러운 패드."""
    s0 = int(start * SR)
    n = min(int(dur * SR), len(buf) - s0)
    for m in midis:
        f = hz(m)
        for i in range(n):
            t = i / n
            env = math.sin(math.pi * t) ** 1.5
            buf[s0 + i] += amp * env * math.sin(2 * math.pi * f * i / SR)


def add_shaker(buf, start, amp):
    """짧은 잡음(셰이커). 앞 값과의 차이를 써서 높은 소리만 남긴다."""
    s0 = int(start * SR)
    n = min(int(0.05 * SR), len(buf) - s0)
    prev = 0.0
    for i in range(n):
        x = random.uniform(-1, 1)
        buf[s0 + i] += amp * (x - prev) * math.exp(-i / (0.012 * SR))
        prev = x


def render(name):
    st = STYLES[name]
    random.seed(st["seed"])
    beat = 60.0 / st["bpm"]
    bars = st["bars"]
    eighth = beat / 2
    total = bars * 4 * beat + 1.0
    buf = [0.0] * int(total * SR)

    for bar in range(bars):
        arp, bass, mel = st["chords"][bar % 4]
        t0 = bar * 4 * beat
        add_pad(buf, t0, [m - 12 for m in arp[:3]], 4 * beat + 0.3, st["pad_amp"])
        add_note(buf, t0, bass, 2 * beat, 0.16, tau=0.7, harm=(1.0, 0.2))
        add_note(buf, t0 + 2 * beat, bass, 2 * beat, 0.11, tau=0.7, harm=(1.0, 0.2))
        for j, idx in enumerate(ARP_PATTERN):
            vel = st["arp_amp"] * (1.15 if j % 4 == 0 else 1.0) * random.uniform(0.92, 1.06)
            add_note(buf, t0 + j * eighth, arp[idx], st["arp_len"], vel,
                     tau=st["arp_tau"], harm=st["arp_harm"])
            if st["shaker"] and j % 2 == 1:            # 뒷박에 가벼운 셰이커
                add_shaker(buf, t0 + j * eighth, 0.035)
        if st["sparkle"] and bar >= 1:                  # 반짝이는 높은 음: 2박·4박
            for b in (1, 3):
                add_note(buf, t0 + b * beat + eighth, arp[2] + 12, 0.9, 0.032,
                         attack=0.003, tau=0.25, harm=(1.0, 0.3))
        if bar >= st["melody_from"] and bar != bars - 1:   # 멜로디: 마디 첫 박에 높은 음 하나
            add_note(buf, t0, mel, 1.6, 0.06, attack=0.015, tau=0.7, harm=(1.0, 0.2))

    end = min(int((bars * 4 * beat + 0.5) * SR), len(buf))
    buf = buf[:end]
    n = len(buf)
    fi, fo = int(FADE_IN * SR), int(FADE_OUT * SR)
    for i in range(min(fi, n)):
        buf[i] *= i / fi
    for i in range(min(fo, n)):
        buf[n - 1 - i] *= i / fo

    g = PEAK / (max(abs(x) for x in buf) or 1.0)
    OUT.mkdir(exist_ok=True)
    wav_path = OUT / f"{st['file']}.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, x * g)) * 32767)) for x in buf))
    print(wav_path, f"{n / SR:.1f}초")

    ff = shutil.which("ffmpeg") or "C:/ffmpeg/bin/ffmpeg.exe"
    if shutil.which("ffmpeg") or Path(ff).exists():
        mp3_path = OUT / f"{st['file']}.mp3"
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(wav_path),
                        "-codec:a", "libmp3lame", "-b:a", "192k", str(mp3_path)], check=True)
        print(mp3_path)


# ---------------------------------------------------------------------------
# trio: 악기 세 개(피아노 · 마림바 · 벨)로 구성이 변하는 곡 → 배경음악.wav/.mp3 (기본)
#   피아노(가운데) : 부분음마다 다르게 줄어드는 피아노풍 소리 + 낮은 베이스
#   마림바(왼쪽)   : 맑고 짧은 나무 채 소리로 통통 튀는 반복 리듬 (처음에는 어쿠스틱 기타였으나 탁해서 바꿈)
#   벨(오른쪽)     : 글로켄슈필풍 맑은 소리로 멜로디를 연주
# 구성: 0~1마디 피아노만 → 2~5마디 마림바 가세 → 6~13마디 벨 멜로디 → 14마디 마무리
# ---------------------------------------------------------------------------
TRIO_BPM = 88
TRIO_BARS = 15
# 코드별 (피아노 4음, 베이스, 마림바 3음)  — G, D, Em, C
# 마림바는 피아노(낮은 음)와 벨(높은 음) 사이의 맑은 음역에 둬서 소리가 탁해지지 않게 한다.
TRIO_CHORDS = [
    ([59, 62, 67, 71], 43, [67, 71, 74]),
    ([57, 62, 66, 69], 38, [66, 69, 74]),
    ([59, 64, 67, 71], 40, [67, 71, 76]),
    ([60, 64, 67, 72], 48, [64, 67, 72]),
]
# 멜로디: 코드마다 (시작 박, 음, 길이 박)
TRIO_MELODY = [
    [(0, 74, 1), (1, 71, 0.5), (1.5, 74, 0.5), (2, 79, 2)],
    [(0, 78, 1), (1, 76, 0.5), (1.5, 74, 0.5), (2, 69, 2)],
    [(0, 79, 1), (1, 76, 0.5), (1.5, 79, 0.5), (2, 83, 1), (3, 81, 1)],
    [(0, 76, 1), (1, 74, 0.5), (1.5, 72, 0.5), (2, 74, 2)],
]


def add_partials(buf, start, midi, dur, amp, partials, attack=0.004):
    """partials = [(배음 비율, 상대 크기, 줄어드는 시간 tau), ...]"""
    f = hz(midi)
    s0 = int(start * SR)
    if s0 >= len(buf):
        return
    n = min(int(dur * SR), len(buf) - s0)
    atk = max(1, int(attack * SR))
    for i in range(n):
        t = i / SR
        env = 1.0
        if i < atk:
            env = i / atk
        left = n - i
        if left < 400:
            env *= left / 400
        v = 0.0
        for ratio, a, tau in partials:
            v += a * math.exp(-t / tau) * math.sin(2 * math.pi * f * ratio * t)
        buf[s0 + i] += amp * env * v


def piano(buf, start, midi, dur, amp, tau=0.9):
    add_partials(buf, start, midi, dur, amp,
                 [(1, 1.0, tau), (2, 0.45, tau / 1.6), (3, 0.25, tau / 2.2), (4, 0.12, tau / 3.0)])


def bell(buf, start, midi, dur, amp):
    add_partials(buf, start, midi, dur, amp,
                 [(1, 1.0, 1.4), (2.76, 0.35, 0.5), (5.4, 0.15, 0.2)], attack=0.002)


def marimba(buf, start, midi, dur, amp):
    """마림바풍: 나무 채로 치는 짧고 맑은 소리. 4배음이 처음에만 또렷하다가 빨리 사라진다."""
    add_partials(buf, start, midi, dur, amp,
                 [(1, 1.0, 0.30), (4.0, 0.30, 0.07), (9.2, 0.08, 0.03)], attack=0.002)


def render_trio():
    random.seed(21)
    beat = 60.0 / TRIO_BPM
    eighth = beat / 2
    total = TRIO_BARS * 4 * beat + 1.0
    size = int(total * SR)
    pi, gt, bl = [0.0] * size, [0.0] * size, [0.0] * size
    arp8 = [0, 1, 2, 3, 2, 1, 2, 3]
    arp4 = [0, 2, 1, 3]

    for bar in range(TRIO_BARS):
        p4, bass, g3 = TRIO_CHORDS[bar % 4]
        t0 = bar * 4 * beat
        last = bar == TRIO_BARS - 1
        # 피아노: 처음 2마디와 10~13마디는 8분음표, 그 사이는 4분음표로 듬성하게
        if last:
            for k, m in enumerate(p4):
                piano(pi, t0 + k * 0.09, m, 3.2, 0.10, tau=1.6)
            piano(pi, t0, bass, 3.2, 0.14, tau=1.6)
        else:
            busy = bar < 2 or bar >= 10
            if busy:
                for j, idx in enumerate(arp8):
                    v = 0.10 * (1.15 if j % 4 == 0 else 1.0) * random.uniform(0.92, 1.06)
                    piano(pi, t0 + j * eighth, p4[idx], 1.0, v, tau=0.55)
            else:
                for j, idx in enumerate(arp4):
                    piano(pi, t0 + j * beat, p4[idx], 1.6, 0.12 * random.uniform(0.94, 1.05), tau=0.9)
            piano(pi, t0, bass, 2 * beat, 0.14, tau=0.8)
            piano(pi, t0 + 2 * beat, bass, 2 * beat, 0.10, tau=0.8)
        # 마림바: 2마디부터 한 음씩 통통 튀는 반복 리듬 (마지막 마디는 세 음을 함께)
        if 2 <= bar < TRIO_BARS - 1:
            for b, idx in ((1.0, 0), (2.0, 1), (2.5, 2), (3.5, 1)):
                marimba(gt, t0 + b * beat, g3[idx], 0.7, 0.11 * random.uniform(0.92, 1.06))
        if last:
            for m in g3:
                marimba(gt, t0, m, 1.2, 0.09)
        # 벨: 6마디부터 멜로디, 마지막 마디는 긴 한 음
        if 6 <= bar < TRIO_BARS - 1:
            notes = TRIO_MELODY[bar % 4]
            for b0, m, ln in notes:
                if bar >= 10 and bar % 4 == 3 and b0 == 2:      # 두 번째 구절의 끝은 높은 솔로 길게
                    m = 79
                bell(bl, t0 + b0 * beat, m, ln * beat + 0.9, 0.075)
        if last:
            bell(bl, t0, 79, 3.4, 0.08)

    # 왼쪽·오른쪽으로 나눠 섞기 (피아노 가운데, 기타 왼쪽, 벨 오른쪽)
    L = [pi[i] + 1.0 * gt[i] + 0.45 * bl[i] for i in range(size)]
    R = [pi[i] + 0.45 * gt[i] + 1.0 * bl[i] for i in range(size)]
    end = min(int((TRIO_BARS * 4 * beat + 0.8) * SR), size)
    L, R = L[:end], R[:end]
    n = len(L)
    fi, fo = int(FADE_IN * SR), int(FADE_OUT * SR)
    for i in range(min(fi, n)):
        L[i] *= i / fi
        R[i] *= i / fi
    for i in range(min(fo, n)):
        L[n - 1 - i] *= i / fo
        R[n - 1 - i] *= i / fo
    g = PEAK / (max(max(abs(x) for x in L), max(abs(x) for x in R)) or 1.0)
    OUT.mkdir(exist_ok=True)
    wav_path = OUT / "배경음악.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for a, b in zip(L, R):
            frames += struct.pack("<hh", int(max(-1.0, min(1.0, a * g)) * 32767),
                                  int(max(-1.0, min(1.0, b * g)) * 32767))
        w.writeframes(bytes(frames))
    print(wav_path, f"{n / SR:.1f}초 (스테레오)")
    ff = shutil.which("ffmpeg") or "C:/ffmpeg/bin/ffmpeg.exe"
    if shutil.which("ffmpeg") or Path(ff).exists():
        mp3_path = OUT / "배경음악.mp3"
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(wav_path),
                        "-codec:a", "libmp3lame", "-b:a", "192k", str(mp3_path)], check=True)
        print(mp3_path)


if __name__ == "__main__":
    for nm in (sys.argv[1:] or ["trio"] + list(STYLES)):
        render_trio() if nm == "trio" else render(nm)
