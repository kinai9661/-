# app.py
import gradio as gr
import yt_dlp
import os
import time
import re
import requests
from pathlib import Path

def clean_old_files():
    """清理舊音檔，避免磁碟爆滿"""
    for f in Path(".").glob("*.*"):
        if f.suffix.lower() in {".mp3", ".m4a", ".webm", ".opus"}:
            try:
                f.unlink()
            except:
                pass

def is_youtube_url(text):
    """判斷是否為 YouTube 連結"""
    youtube_patterns = [
        r'(youtube\.com/watch\?v=)',
        r'(youtu\.be/)',
        r'(youtube\.com/shorts/)',
        r'(youtube\.com/embed/)',
    ]
    return any(re.search(pattern, text) for pattern in youtube_patterns)

def is_spotify_url(text):
    """判斷是否為 Spotify 連結"""
    spotify_patterns = [
        r'(open\.spotify\.com/track/)',
        r'(open\.spotify\.com/album/)',
        r'(open\.spotify\.com/playlist/)',
    ]
    return any(re.search(pattern, text) for pattern in spotify_patterns)

def get_spotify_info(spotify_url):
    """從 Spotify 連結提取歌曲資訊（使用公開 API）"""
    try:
        match = re.search(r'spotify\.com/(track|album|playlist)/([a-zA-Z0-9]+)', spotify_url)
        if not match:
            return None, None
        
        spotify_type = match.group(1)
        spotify_id = match.group(2)
        
        oembed_url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/{spotify_type}/{spotify_id}"
        response = requests.get(oembed_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('title', '')
            return title, spotify_type
        
        return None, None
    except Exception as e:
        print(f"Spotify API 錯誤: {e}")
        return None, None

def download_music(query: str, quality: str):
    if not query.strip():
        return "請輸入歌名、關鍵字、YouTube 連結 或 Spotify 連結", None, None
    
    try:
        clean_old_files()
        time.sleep(1)
        
        # 判斷輸入類型
        if is_spotify_url(query):
            spotify_title, spotify_type = get_spotify_info(query)
            if spotify_title:
                search_query = f"ytsearch:{spotify_title}"
                status_prefix = f"🎵 從 Spotify 找到：{spotify_title}\n"
            else:
                return "⚠️ 無法解析 Spotify 連結，請確認連結是否正確", None, None
        elif is_youtube_url(query):
            search_query = query
            status_prefix = ""
        else:
            search_query = f"ytsearch:{query}"
            status_prefix = ""
        
        # 根據選擇的音質設定參數
        quality_map = {
            "128 kbps (較小檔案)": "128",
            "192 kbps (建議)": "192",
            "320 kbps (最高音質)": "320",
        }
        selected_quality = quality_map.get(quality, "192")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': selected_quality,
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'sleep_requests': 1,
            'sleep_interval': 2,
            'max_sleep_interval': 5,
            'extractor_retries': 3,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            
            # 處理搜尋結果
            if 'entries' in info:
                entries = info.get('entries', [])
                if not entries or len(entries) == 0:
                    return "⚠️ 找不到符合的歌曲，請嘗試其他關鍵字", None, None
                entry = entries[0]
            else:
                entry = info
            
            filename = ydl.prepare_filename(entry)
            mp3_path = str(Path(filename).with_suffix('.mp3'))
            
            # 確認檔案存在
            if not os.path.exists(mp3_path):
                for ext in ['.m4a', '.webm', '.opus']:
                    alt_path = str(Path(filename).with_suffix(ext))
                    if os.path.exists(alt_path):
                        mp3_path = alt_path
                        break
                else:
                    return "⚠️ 下載失敗，請稍後再試", None, None
            
            title = entry.get('title', '未知標題')
            return f"{status_prefix}✅ 下載完成：{title}（{selected_quality}kbps）", mp3_path, mp3_path
            
    except Exception as e:
        error_msg = str(e)
        if "rate-limited" in error_msg.lower() or "unavailable" in error_msg.lower():
            return "⚠️ YouTube 暫時限制此服務的 IP，請等待約 1 小時後再試。", None, None
        if "Video unavailable" in error_msg:
            return "⚠️ 此影片無法下載（可能已被移除或設為私人）", None, None
        return f"❌ 錯誤：{error_msg}", None, None

demo = gr.Interface(
    fn=download_music,
    inputs=[
        gr.Textbox(
            label="輸入歌名、YouTube 連結 或 Spotify 連結",
            placeholder="例如：\n• 周杰倫 擱淺\n• https://www.youtube.com/watch?v=xxxxx\n• https://open.spotify.com/track/xxxxx",
            lines=3
        ),
        gr.Dropdown(
            choices=["128 kbps (較小檔案)", "192 kbps (建議)", "320 kbps (最高音質)"],
            value="192 kbps (建議)",
            label="選擇音質"
        )
    ],
    outputs=[
        gr.Textbox(label="狀態訊息"),
        gr.Audio(label="試聽（點擊播放）", type="filepath"),
        gr.File(label="點此下載 mp3")
    ],
    title="🎵 音樂下載 & 播放工具",
    description="支援三種方式：\n1. 輸入歌名 + 歌手（自動搜尋 YouTube）\n2. 直接貼上 YouTube 連結\n3. 直接貼上 Spotify 連結（自動提取歌名並從 YouTube 下載）\n\n可選擇音質：128 / 192 / 320 kbps\n\n僅限個人使用，請遵守版權規定。"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)
