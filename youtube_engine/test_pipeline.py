"""
test_pipeline.py

YouTube自動生成エンジン - 最小構成テストスクリプト

【実行手順】
  1. cd youtube_engine
  2. pip install -r requirements_youtube.txt
  3. ollama serve  (別ターミナルで起動)
  4. python test_pipeline.py

【出力】
  output/videos/test_<タイトル>.mp4  ← 10秒の縦型動画
"""

import logging
import os
import sys
import re
from datetime import datetime

import yaml

from text_generator import YouTubeScriptGenerator
from video_composer import (
    create_background_image,
    create_silent_wav,
    create_subtitle_frames,
    compose_video,
)

# ── ロギング設定 ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ── 設定ファイル読み込み ──────────────────────────────────────────────────────

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── ファイル名サニタイズ ──────────────────────────────────────────────────────

def safe_filename(text: str, max_len: int = 30) -> str:
    return re.sub(r'[\\/:*?"<>|　]', "_", text)[:max_len]


# ── メインパイプライン ─────────────────────────────────────────────────────────

def run_test(config_path: str = "config.yaml"):
    cfg = load_config(config_path)

    ollama_cfg   = cfg["ollama"]
    video_cfg    = cfg["video"]
    audio_cfg    = cfg["audio"]
    subtitle_cfg = cfg["subtitle"]
    content_cfg  = cfg["content"]
    design_cfg   = cfg["design"]

    duration = video_cfg["test_duration"]
    fps      = video_cfg["fps"]
    width    = video_cfg["width"]
    height   = video_cfg["height"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ══════════════════════════════════════════════════════════════
    #  Step 1: Ollama でスクリプト生成
    #  ※ 完了後 keep_alive=0 で VRAM を自動解放
    # ══════════════════════════════════════════════════════════════
    logger.info("=" * 60)
    logger.info("Step 1/4: Ollama でスクリプトを生成中...")
    logger.info("=" * 60)

    generator = YouTubeScriptGenerator(
        host=ollama_cfg["host"],
        model=ollama_cfg["model"],
        keep_alive=ollama_cfg["keep_alive"],
        timeout=ollama_cfg["timeout"],
    )

    content = generator.generate_script(
        genre=content_cfg["genre"],
        max_chars=content_cfg["script_max_chars"],
    )

    if not content:
        logger.error("スクリプト生成に失敗しました。Ollama が起動しているか確認してください。")
        sys.exit(1)

    title     = content["title"]
    script    = content["script"]
    subtitles = content["subtitles"]

    logger.info(f"  タイトル  : {title}")
    logger.info(f"  字幕数    : {len(subtitles)} 文")
    logger.info(f"  スクリプト: {script[:60]}...")

    # ══════════════════════════════════════════════════════════════
    #  Step 2: ダミー無音 WAV を生成
    #  Phase 2 では XTTS-v2 の合成音声に差し替え予定
    # ══════════════════════════════════════════════════════════════
    logger.info("=" * 60)
    logger.info("Step 2/4: ダミー音声を生成中（無音WAV）...")
    logger.info("=" * 60)

    audio_path = os.path.join(audio_cfg["temp_dir"], f"audio_{timestamp}.wav")
    os.makedirs(audio_cfg["temp_dir"], exist_ok=True)

    create_silent_wav(
        duration_seconds=duration,
        output_path=audio_path,
        sample_rate=audio_cfg["sample_rate"],
        channels=audio_cfg["channels"],
    )

    # ══════════════════════════════════════════════════════════════
    #  Step 3: 背景画像 + 字幕フレームを生成
    #  Phase 2 では Stable Diffusion の生成画像に差し替え予定
    # ══════════════════════════════════════════════════════════════
    logger.info("=" * 60)
    logger.info("Step 3/4: 背景画像・字幕フレームを生成中...")
    logger.info("=" * 60)

    base_frame = create_background_image(
        width=width,
        height=height,
        title=title,
        bg_top=tuple(design_cfg["bg_color_top"]),
        bg_bottom=tuple(design_cfg["bg_color_bottom"]),
        accent=tuple(design_cfg["accent_color"]),
        title_font_size=design_cfg["title_font_size"],
    )

    frames = create_subtitle_frames(
        base_frame=base_frame,
        subtitles=subtitles,
        total_duration=duration,
        fps=fps,
        subtitle_cfg=subtitle_cfg,
    )
    logger.info(f"  生成フレーム数: {len(frames)}")

    # ══════════════════════════════════════════════════════════════
    #  Step 4: 動画合成 → mp4 出力
    # ══════════════════════════════════════════════════════════════
    logger.info("=" * 60)
    logger.info("Step 4/4: 動画を合成中...")
    logger.info("=" * 60)

    output_dir = video_cfg["output_dir"]
    safe_title = safe_filename(title)
    output_path = os.path.join(output_dir, f"{timestamp}_{safe_title}.mp4")
    os.makedirs(output_dir, exist_ok=True)

    compose_video(
        frames=frames,
        audio_path=audio_path,
        output_path=output_path,
        fps=fps,
        duration=float(duration),
        codec=video_cfg["codec"],
    )

    # ══════════════════════════════════════════════════════════════
    #  完了レポート
    # ══════════════════════════════════════════════════════════════
    logger.info("=" * 60)
    logger.info("テスト完了！")
    logger.info(f"  出力ファイル : {os.path.abspath(output_path)}")
    logger.info(f"  動画タイトル : {title}")
    logger.info(f"  動画時間     : {duration} 秒")
    logger.info(f"  解像度       : {width}x{height} (9:16)")
    logger.info("")
    logger.info("【Phase 2 で追加予定】")
    logger.info("  - XTTS-v2 による日本語音声合成")
    logger.info("  - Stable Diffusion による背景画像生成")
    logger.info("  - YouTube Data API による自動アップロード")
    logger.info("=" * 60)


if __name__ == "__main__":
    # config.yaml のパスを引数で指定可能（省略時はカレントディレクトリ）
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    run_test(config_path)
