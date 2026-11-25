# -*- coding: utf-8 -*-
"""「파이썬 거북이 게임」 클립용 배경음악 — 게임 같은 긴박한 칩튠(8비트풍) 곡을 직접 합성한다.

파이썬 표준 라이브러리만 사용(numpy 불필요). 저작권 문제 없는 자작 음원.
구성: 150BPM, 가단조(Am-F-G-E), 약 38초, 스테레오.
  0~3마디 베이스+드럼만 → 4~11마디 아르페지오 가세 → 12~19마디 멜로디 → 20~22마디 클라이맥스(스네어 연타·상승음) → 23마디 마무리 한 방
실행: python 도구/클립음악_거북이게임.py  → clip/배경음악.mp3(.wav)
필요: ffmpeg (C:/ffmpeg/bin/ffmpeg.exe)
"""
import math
import random
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "문서/네이버-코딩가이드/20261124_23개/20261124_파이썬-거북이-게임/clip"
FFMPEG = "C:/ffmpeg/bin/ffmpeg.exe"

SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BARS = 24
TOTAL = BARS * 4 * BEAT
PEAK = 0.32
random.seed(3)

# 코드(마디마다 순환): Am F G E
CHORDS = [
    (45, [57, 60, 64]),   # Am: 베이스 A2, 화음 A3 C4 E4
    (41, [53, 57, 60]),   # F
    (43, [55, 59, 62]),   # G
    (40, [52, 56, 59]),   # E (G# 으로 긴장감)
]
# 멜로디(박, 음, 길이 박) — 마디당
LEAD = [
    [(0, 76, 1), (1, 72, 0.5), (1.5, 76, 0.5), (2, 79, 1), (3, 77, 1)],
    [(0, 77, 1), (1, 72, 0.5), (1.5, 77, 0.5), (2, 81, 1), (3, 79, 1)],
    [(0, 79, 1), (1, 74, 0.5), (1.5, 79, 0.5), (2, 83, 1), (3, 81, 1)],
    [(0, 80, 1), (1, 76, 0.5), (1.5, 80, 0.5), (2, 83, 1), (3, 82, 1)],
]


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def n_total():
    return int(TOTAL * SR) + SR


def pulse_note(buf, t0, midi, dur, amp, duty=0.5, decay=6.0, vib=0.0):
    f = hz(midi)
    s0 = int(t0 * SR)
    n = int(dur * SR)
    for i in range(n):
        j = s0 + i
        if j >= len(buf):
            break
        t = i / SR
        env = math.exp(-decay * t) * min(1.0, i / (0.003 * SR))
        ph = (f * t + vib * math.sin(2 * math.pi * 5 * t) * 0.01) % 1.0
        buf[j] += amp * env * (1.0 if ph < duty else -1.0)


def kick(buf, t0, amp=0.5):
    s0 = int(t0 * SR)
    n = int(0.16 * SR)
    ph = 0.0
    for i in range(n):
        j = s0 + i
        if j >= len(buf):
            break
        t = i / SR
        f = 50 + 110 * math.exp(-t * 38)
        ph += 2 * math.pi * f / SR
        buf[j] += amp * math.exp(-t * 22) * math.sin(ph)


def noise(buf, t0, dur, amp, decay, hp=False):
    s0 = int(t0 * SR)
    n = int(dur * SR)
    prev = 0.0
    for i in range(n):
        j = s0 + i
        if j >= len(buf):
            break
        t = i / SR
        x = random.uniform(-1, 1)
        if hp:                      # 간단한 고음 강조(앞 샘플과의 차이)
            y = x - prev
            prev = x
            x = y * 0.7
        buf[j] += amp * math.exp(-decay * t) * x


def riser(buf, t0, dur, amp):
    """클라이맥스용 상승음(톱니파가 점점 높아짐)."""
    s0 = int(t0 * SR)
    n = int(dur * SR)
    ph = 0.0
    for i in range(n):
        j = s0 + i
        if j >= len(buf):
            break
        p = i / n
        f = 220 * (4.0 ** p)
        ph += f / SR
        ph %= 1.0
        buf[j] += amp * (0.3 + 0.7 * p) * (2 * ph - 1)


def render():
    N = n_total()
    drums = [0.0] * N
    bass = [0.0] * N
    arp = [0.0] * N
    lead = [0.0] * N
    fx = [0.0] * N

    for bar in range(BARS):
        b0 = bar * 4 * BEAT
        root, tones = CHORDS[bar % 4]
        last = bar == BARS - 1
        climax = 20 <= bar <= 22

        if last:
            # 마지막 마디: 화음 한 방 + 킥
            kick(drums, b0, 0.6)
            noise(drums, b0, 0.4, 0.28, 8)
            for m in [57, 60, 64, 69]:
                pulse_note(fx, b0, m, 2.2, 0.10, 0.5, decay=1.8)
            pulse_note(bass, b0, 33, 2.2, 0.26, 0.5, decay=1.6)
            continue

        # 베이스: 8분음표로 옥타브를 오가며 밀어붙임
        for k in range(8):
            midi = root + (12 if k % 2 == 1 else 0)
            pulse_note(bass, b0 + k * BEAT / 2, midi, BEAT / 2 * 0.9, 0.24, 0.5, decay=9)

        # 드럼: 킥(1·3박 + 4박 뒤 8분), 스네어(2·4박), 하이햇(8분음표, 16분음표 가끔)
        for beat in (0, 2):
            kick(drums, b0 + beat * BEAT, 0.5)
        kick(drums, b0 + 3.5 * BEAT, 0.35)
        for beat in (1, 3):
            noise(drums, b0 + beat * BEAT, 0.14, 0.26, 20)
        for k in range(8):
            noise(drums, b0 + k * BEAT / 2, 0.04, 0.10, 90, hp=True)
        if climax:
            for k in range(16):      # 스네어 16분 연타 + 점점 커지게
                noise(drums, b0 + k * BEAT / 4, 0.06, 0.10 + 0.012 * (bar - 20) * 8 + 0.004 * k, 45)
        if bar == 19:
            for k in range(8):       # 클라이맥스 직전 스네어 롤
                noise(drums, b0 + (2 + k * 0.25) * BEAT, 0.08, 0.10 + 0.02 * k, 40)

        # 아르페지오: 4마디부터. 16분음표로 화음을 위아래로
        if bar >= 4:
            pattern = [0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 2, 1, 0, 1]
            for k, p in enumerate(pattern):
                midi = tones[p] + 12 + (12 if (k % 4 == 3) else 0)
                pulse_note(arp, b0 + k * BEAT / 4, midi, BEAT / 4 * 1.4, 0.075, 0.25, decay=14)

        # 멜로디: 12마디부터
        if bar >= 12:
            for beat, midi, dur in LEAD[bar % 4]:
                pulse_note(lead, b0 + beat * BEAT, midi, dur * BEAT, 0.10, 0.125, decay=3.2, vib=1.0)

        # 클라이맥스 상승음
        if bar == 20:
            riser(fx, b0, 3 * 4 * BEAT, 0.07)

    # 스테레오 믹스: 아르페지오는 왼쪽, 멜로디는 오른쪽 쪽으로
    L = [drums[i] + bass[i] + 1.0 * arp[i] + 0.5 * lead[i] + fx[i] for i in range(N)]
    R = [drums[i] + bass[i] + 0.5 * arp[i] + 1.0 * lead[i] + fx[i] for i in range(N)]
    # 페이드 인(0.4초)·아웃(2.5초), 정규화
    fin, fout = int(0.4 * SR), int(2.5 * SR)
    end = int(TOTAL * SR)
    for i in range(N):
        g = 1.0
        if i < fin:
            g = i / fin
        if i > end - fout:
            g = max(0.0, (end - i) / fout) if i < end else 0.0
        L[i] *= g
        R[i] *= g
    peak = max(max(abs(x) for x in L), max(abs(x) for x in R)) or 1.0
    k = PEAK / peak
    return [x * k for x in L[:end]], [x * k for x in R[:end]]


def write_wav(path, L, R):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for a, b in zip(L, R):
            for v in (a, b):
                x = max(-1.0, min(1.0, v))
                frames += int(x * 32767).to_bytes(2, "little", signed=True)
        w.writeframes(bytes(frames))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    L, R = render()
    wav = OUT / "배경음악.wav"
    mp3 = OUT / "배경음악.mp3"
    write_wav(wav, L, R)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame",
                    "-b:a", "192k", str(mp3)], check=True)
    wav.unlink()
    print("완료:", mp3, f"({TOTAL:.1f}초)")
