# app.py
import gradio as gr
import yt_dlp
import os
from pathlib import Path

def clean_old_files():
    for f in Path(".").glob("*.*"):
        if f.suffix.lower() in {".mp3", ".m4a", ".webm", ".opus"}:
            try:
                f.unlink()
            except:
                pass

def download_music(query: str):
    if not query.strip():
        return "請輸入歌名 + 歌手 或搜尋關鍵字", None, None

    try:
        clean_old_files()

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            entry = info['entries'][0]
            filename = ydl.prepare_filename(entry)
            mp3_path = str(Path(filename).with_suffix('.mp3'))

        title = entry.get('title', '未知標題')
        return f"下載完成：{title}", mp3_path, mp3_path

    except Exception as e:
        return f"錯誤：{str(e)}", None, None

demo = gr.Interface(
    fn=download_music,
    inputs=gr.Textbox(label="輸入歌名 + 歌手 或關鍵字", lines=2),
    outputs=[
        gr.Textbox(label="狀態"),
        gr.Audio(label="試聽", type="filepath"),
        gr.File(label="下載 mp3")
    ],
    title="音樂下載 & 播放工具（私人使用）",
    description="從 YouTube 搜尋 → 下載 mp3 → 試聽。僅限個人使用。"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)
