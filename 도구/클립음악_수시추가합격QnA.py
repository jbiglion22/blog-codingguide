# -*- coding: utf-8 -*-
"""「수시 추가 합격 Q&A」 클립용 배경음악(빠른 버전)을 직접 합성한다. 저작권 문제 없는 자작 음원.

분위기: 경쾌하게 앞으로 나아가는 느낌 + 약간의 두근거림(기다림·기대). 더빙이 없으므로 음악이 주인공.
구성: 126BPM, 코드 Am-F-C-G 반복, 20마디(약 38.1초) → 38초로 맞춤, 스테레오.
  0~1마디 피아노 리듬만 → 2마디부터 킥·클랩·하이햇·베이스 → 9마디(약 17초)부터 벨 멜로디로 살짝 고조
  → 17~19마디 마무리(드럼 빠지고 화음으로 끝)
실행: python 도구/클립음악_수시추가합격QnA.py → clip/원본/음악-빠름.wav, clip/음악-빠름.mp3(들어 보기용)
필요: ffmpeg (C:/ffmpeg/bin/ffmpeg.exe)
"""
import math
import random
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIP = ROOT / "문서/네이버-코딩가이드/20261124_23개/20261124_수시-추가합격-QnA/clip"
FFMPEG = "C:/ffmpeg/bin/ffmpeg.exe"

SR = 44100
BPM = 126
BEAT = 60.0 / BPM
BARS = 20
LENGTH = 38.0
PEAK = 0.80            # 더빙이 없어 음악이 주인공(최대 약 -2dBFS)
random.seed(11)

# (베이스, 화음) — Am F C G
CHORDS = [
    (45, [57, 60, 64]),   # Am
    (41, [57, 60, 65]),   # F (A C F)
    (48, [55, 60, 64]),   # C (G C E)
    (43, [55, 59, 62]),   # G
]
# 벨 멜로디(마디당: 박, 음, 길이)
BELL = [
    [(0, 76, 1), (1, 79, 0.5), (1.5, 76, 0.5), (2, 72, 1.5)],
    [(0, 77, 1), (1, 76, 0.5), (1.5, 72, 0.5), (2, 69, 1.5)],
    [(0, 76, 1), (1, 79, 0.5), (1.5, 84, 0.5), (2, 79, 1.5)],
    [(0, 79, 1), (1, 81, 0.5), (1.5, 79, 0.5), (2, 74, 1.5), (3.5, 71, 0.5)],
]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(buf, t0, n, fn):
    s0 = int(t0 * SR)
    for i in range(n):
        j = s0 + i
        if j >= len(buf):
            break
        buf[j] += fn(i / SR, i)


def piano(buf, t0, m, dur, amp):
    f = hz(m)
    parts = [(1, 1.0, 3.2), (2, 0.45, 5.0), (3, 0.18, 7.0), (4, 0.08, 9.0)]
    n = int((dur + 0.25) * SR)

    def fn(t, i):
        a = min(1.0, i / (0.004 * SR))
        rel = 1.0 if t < dur else max(0.0, 1 - (t - dur) / 0.25)
        return amp * a * rel * sum(g * math.exp(-d * t) * math.sin(2 * math.pi * f * k * t) for k, g, d in parts)
    add(buf, t0, n, fn)


def bell(buf, t0, m, dur, amp):
    f = hz(m)
    parts = [(1, 1.0, 2.2), (2.76, 0.35, 4.0), (5.4, 0.12, 6.0)]
    n = int((dur + 0.8) * SR)
    add(buf, t0, n, lambda t, i: amp * min(1.0, i / (0.002 * SR)) *
        sum(g * math.exp(-d * t) * math.sin(2 * math.pi * f * k * t) for k, g, d in parts))


def bass(buf, t0, m, dur, amp):
    f = hz(m)
    n = int(dur * SR)

    def fn(t, i):
        env = min(1.0, i / (0.006 * SR)) * math.exp(-2.5 * t) * (1 if t < dur * 0.85 else max(0, (dur - t) / (dur * 0.15)))
        x = math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t)
        return amp * env * x
    add(buf, t0, n, fn)


def kick(buf, t0, amp):
    ph = [0.0]

    def fn(t, i):
        ph[0] += 2 * math.pi * (48 + 95 * math.exp(-t * 35)) / SR
        return amp * math.exp(-t * 18) * math.sin(ph[0])
    add(buf, t0, int(0.22 * SR), fn)


def noise(buf, t0, dur, amp, decay, hp=False):
    prev = [0.0]

    def fn(t, i):
        x = random.uniform(-1, 1)
        if hp:
            y = x - prev[0]
            prev[0] = x
            x = 0.7 * y
        return amp * math.exp(-decay * t) * x
    add(buf, t0, int(dur * SR), fn)


def clap(buf, t0, amp):
    for k, d in enumerate((0.0, 0.011, 0.022)):
        noise(buf, t0 + d, 0.12 if k == 2 else 0.02, amp * (0.6 if k < 2 else 1.0), 28, hp=True)


def render():
    N = int((BARS * 4 * BEAT + 2) * SR)
    pi, bl, bs, dr = ([0.0] * N for _ in range(4))
    for bar in range(BARS):
        b0 = bar * 4 * BEAT
        root, tones = CHORDS[bar % 4]
        outro = bar >= 17
        last = bar == BARS - 1
        if last:
            for m in tones + [tones[0] + 12]:
                piano(pi, b0, m, 2.5, 0.11)
            bass(bs, b0, root - 12, 2.5, 0.30)
            continue
        # 피아노: 8분음표 리듬(화음을 위아래로 튕김), 2박 뒤 엇박 강조
        pat = [0, 1, 2, 1, 0, 2, 1, 2]
        for k, p in enumerate(pat):
            vel = 0.085 if k % 2 == 0 else 0.065
            if k in (3, 6):
                vel = 0.095
            piano(pi, b0 + k * BEAT / 2, tones[p] + 12, BEAT / 2 * 0.9, vel)
        if bar >= 2 and not outro:
            # 베이스: 8분음표, 옥타브 왕복
            for k in range(8):
                bass(bs, b0 + k * BEAT / 2, root - 12 + (12 if k in (3, 7) else 0), BEAT / 2 * 0.95, 0.20)
            # 드럼: 킥 1·2·3·4박(4박자 고르게), 클랩 2·4박, 하이햇 8분 엇박
            for b in range(4):
                kick(dr, b0 + b * BEAT, 0.42)
            for b in (1, 3):
                clap(dr, b0 + b * BEAT, 0.22)
            for k in range(8):
                noise(dr, b0 + k * BEAT / 2, 0.05, 0.07 if k % 2 == 1 else 0.035, 70, hp=True)
            if bar in (8, 16):        # 고조 직전 필(16분 하이햇)
                for k in range(8):
                    noise(dr, b0 + (2 + k * 0.25) * BEAT, 0.04, 0.05 + 0.01 * k, 60, hp=True)
        elif outro:
            for b in (0, 2):
                kick(dr, b0 + b * BEAT, 0.25)
            for k in range(4):
                bass(bs, b0 + k * BEAT, root - 12, BEAT * 0.9, 0.14)
        # 벨 멜로디: 9마디부터(약 17초) 마무리 전까지
        if 9 <= bar < 17:
            for bt, m, du in BELL[bar % 4]:
                bell(bl, b0 + bt * BEAT, m, du * BEAT, 0.075)

    L = [dr[i] + bs[i] + 1.0 * pi[i] + 0.55 * bl[i] for i in range(N)]
    R = [dr[i] + bs[i] + 0.7 * pi[i] + 1.0 * bl[i] for i in range(N)]
    end = int(LENGTH * SR)
    fin, fout = int(0.05 * SR), int(2.0 * SR)
    for i in range(end):
        g = 1.0
        if i < fin:
            g = i / fin
        elif i > end - fout:
            g = (end - i) / fout
        L[i] *= g
        R[i] *= g
    L, R = L[:end], R[:end]
    peak = max(max(abs(x) for x in L), max(abs(x) for x in R)) or 1.0
    k = PEAK / peak
    return [x * k for x in L], [x * k for x in R]


def write_wav(path, L, R):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        fr = bytearray()
        for a, b in zip(L, R):
            for v in (a, b):
                fr += int(max(-1.0, min(1.0, v)) * 32767).to_bytes(2, "little", signed=True)
        w.writeframes(bytes(fr))


if __name__ == "__main__":
    L, R = render()
    wav = CLIP / "원본/음악-빠름.wav"
    write_wav(wav, L, R)
    mp3 = CLIP / "음악-빠름.mp3"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "192k", str(mp3)], check=True)
    print("완료:", wav, mp3)

