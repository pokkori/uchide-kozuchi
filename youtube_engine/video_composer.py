"""
video_composer.py

Pillow で背景画像・字幕フレームを生成し、
MoviePy で音声と合成して 9:16 縦型 mp4 を出力する。

Phase 1（テスト）:
  - 背景: Pillow でグラデーション + タイトルテキスト
  - 音声: Python wave モジュールで無音 WAV を生成
  - 字幕: 時間ごとに Pillow でテキストを焼き込んだフレームを生成

Phase 2 拡張予定:
  - 背景: Stable Diffusion で生成した画像に差し替え
  - 音声: XTTS-v2 / StyleBERT-VITS2 で合成音声に差し替え
"""

import logging
import os
import textwrap
import wave
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


# ── フォント解決 ──────────────────────────────────────────────────────────────

def _find_japanese_font(size: int) -> ImageFont.FreeTypeFont:
    """Windows / Linux / Mac で日本語フォントを探してロードする"""
    candidates = [
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothM.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    logger.warning("日本語フォントが見つかりません。デフォルトフォントを使用します。")
    return ImageFont.load_default()


# ── 背景画像生成 ──────────────────────────────────────────────────────────────

def create_background_image(
    width: int, height: int,
    title: str,
    bg_top: Tuple[int, int, int] = (15, 15, 40),
    bg_bottom: Tuple[int, int, int] = (40, 10, 60),
    accent: Tuple[int, int, int] = (120, 80, 255),
    title_font_size: int = 64,
) -> np.ndarray:
    """
    グラデーション背景 + タイトルテキストを描画した画像を
    numpy 配列 (H, W, 3) として返す。
    """
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # 縦グラデーション
    for y in range(height):
        ratio = y / height
        r = int(bg_top[0] * (1 - ratio) + bg_bottom[0] * ratio)
        g = int(bg_top[1] * (1 - ratio) + bg_bottom[1] * ratio)
        b = int(bg_top[2] * (1 - ratio) + bg_bottom[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # アクセントライン（上下）
    line_h = 8
    draw.rectangle([0, 0, width, line_h], fill=accent)
    draw.rectangle([0, height - line_h, width, height], fill=accent)

    # タイトルテキスト（中央）
    font = _find_japanese_font(title_font_size)
    wrapped = "\n".join(textwrap.wrap(title, width=14))
    bbox = draw.textbbox((0, 0), wrapped, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) // 2
    y = (height - text_h) // 2 - 100  # 少し上寄り

    # 影
    draw.text((x + 3, y + 3), wrapped, font=font, fill=(0, 0, 0))
    # 本文
    draw.text((x, y), wrapped, font=font, fill=(255, 255, 255))

    return np.array(img)


# ── 字幕フレーム生成 ──────────────────────────────────────────────────────────

def _draw_subtitle_on_frame(
    base_frame: np.ndarray,
    text: str,
    font_size: int,
    font_color: Tuple[int, int, int],
    outline_color: Tuple[int, int, int],
    outline_width: int,
    bg_color: Tuple[int, int, int, int],
    padding: int,
    max_chars: int,
    y_ratio: float,
) -> np.ndarray:
    """base_frame に字幕テキストを焼き込んで numpy 配列を返す"""
    img = Image.fromarray(base_frame.copy())
    draw = ImageDraw.Draw(img, "RGBA")
    font = _find_japanese_font(font_size)

    wrapped = "\n".join(textwrap.wrap(text, width=max_chars))
    bbox = draw.textbbox((0, 0), wrapped, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    width, height = img.size
    x = (width - text_w) // 2
    y = int(height * y_ratio) - text_h // 2

    # 半透明背景
    rect = [
        x - padding,
        y - padding,
        x + text_w + padding,
        y + text_h + padding,
    ]
    draw.rectangle(rect, fill=bg_color)

    # アウトライン
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), wrapped, font=font, fill=outline_color)

    # 本文
    draw.text((x, y), wrapped, font=font, fill=font_color)

    return np.array(img.convert("RGB"))


def create_subtitle_frames(
    base_frame: np.ndarray,
    subtitles: List[str],
    total_duration: float,
    fps: int,
    subtitle_cfg: dict,
) -> List[np.ndarray]:
    """
    字幕ごとにフレームを生成してリストで返す。
    全フレーム数 = total_duration * fps
    """
    total_frames = int(total_duration * fps)
    n = len(subtitles)
    frames_per_sub = max(total_frames // n, 1) if n > 0 else total_frames

    frames = []
    for i, text in enumerate(subtitles):
        frame = _draw_subtitle_on_frame(
            base_frame=base_frame,
            text=text,
            font_size=subtitle_cfg.get("font_size", 52),
            font_color=tuple(subtitle_cfg.get("font_color", [255, 255, 255])),
            outline_color=tuple(subtitle_cfg.get("outline_color", [0, 0, 0])),
            outline_width=subtitle_cfg.get("outline_width", 3),
            bg_color=tuple(subtitle_cfg.get("background_color", [0, 0, 0, 160])),
            padding=subtitle_cfg.get("padding", 20),
            max_chars=subtitle_cfg.get("max_chars_per_line", 20),
            y_ratio=subtitle_cfg.get("position_y_ratio", 0.78),
        )
        count = frames_per_sub if i < n - 1 else (total_frames - frames_per_sub * i)
        frames.extend([frame] * max(count, 1))

    # フレーム数の過不足を調整
    if len(frames) < total_frames:
        frames.extend([frames[-1]] * (total_frames - len(frames)))
    return frames[:total_frames]


# ── ダミー無音 WAV 生成 ───────────────────────────────────────────────────────

def create_silent_wav(
    duration_seconds: int,
    output_path: str,
    sample_rate: int = 44100,
    channels: int = 1,
) -> str:
    """テスト用の無音 WAV ファイルを生成する"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    n_samples = sample_rate * duration_seconds
    silence = np.zeros(n_samples, dtype=np.int16)

    with wave.open(output_path, "w") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)           # 16bit
        wf.setframerate(sample_rate)
        wf.writeframes(silence.tobytes())

    logger.info(f"無音 WAV を生成しました: {output_path}")
    return output_path


# ── 動画合成 ─────────────────────────────────────────────────────────────────

def compose_video(
    frames: List[np.ndarray],
    audio_path: str,
    output_path: str,
    fps: int,
    duration: float,
    codec: str = "libx264",
) -> str:
    """
    フレームリスト + 音声ファイルを mp4 に合成する。
    MoviePy のインポートはここで遅延ロードし、
    使用後に gc でメモリを解放する。
    """
    import gc
    from moviepy.editor import AudioFileClip, ImageSequenceClip

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"動画合成開始: {len(frames)} フレーム / {fps} fps")

    video_clip = ImageSequenceClip(frames, fps=fps)
    audio_clip = AudioFileClip(audio_path).subclip(0, duration)
    video_clip = video_clip.set_audio(audio_clip)

    video_clip.write_videofile(
        output_path,
        fps=fps,
        codec=codec,
        audio_codec="aac",
        logger=None,           # MoviePy の進捗ログを抑制
    )

    video_clip.close()
    audio_clip.close()
    gc.collect()

    logger.info(f"動画出力完了: {output_path}")
    return output_path
