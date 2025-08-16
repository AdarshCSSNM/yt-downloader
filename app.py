import streamlit as st
import yt_dlp
import os
import tempfile
import re
import time
import imageio_ffmpeg

# --- UI Configuration ---
st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="🚀",
    layout="centered",
)

# --- Main App ---
st.title("YouTube Video Downloader")
st.markdown("Enter a YouTube URL to prepare a download.")

url = st.text_input("Enter YouTube URL here:", placeholder="e.g., https://www.youtube.com/watch?v=...")

if st.button("Get Video"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        # Regex to validate YouTube URL
        youtube_regex = (
            r'''(https?://)?(www\.)?'''
            r'''(youtube|youtu|youtube-nocookie)\.(com|be)/'''
            r'''(watch\?v=|embed/|v/|.+\?v=)?([^&=%?]{11})''')
        
        if not re.match(youtube_regex, url):
            st.error("Invalid YouTube URL. Please enter a valid one.")
        else:
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()

                def progress_hook(d):
                    if d['status'] == 'downloading':
                        percentage = d['_percent_str'].replace('%','')
                        progress_bar.progress(int(float(percentage)))
                        status_text.text(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
                    elif d['status'] == 'finished':
                        status_text.text("Download complete. Preparing file...")
                        progress_bar.progress(100)

                # Create a temporary directory to store the file
                with tempfile.TemporaryDirectory() as tmpdir:
                    ffmpeg_location = imageio_ffmpeg.get_ffmpeg_exe()
                    ydl_opts = {
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'noplaylist': True,
                        'progress_hooks': [progress_hook],
                        'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                        'ffmpeg_location': ffmpeg_location,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
                        },
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Start the download
                        ydl.download([url])
                        
                        # Find the downloaded file (assumes one file)
                        downloaded_file_name = os.listdir(tmpdir)[0]
                        downloaded_file_path = os.path.join(tmpdir, downloaded_file_name)
                        
                        with open(downloaded_file_path, "rb") as f:
                            file_bytes = f.read()

                        status_text.success("Your download is ready!")
                        st.balloons()
                        
                        st.download_button(
                            label="Click to Download Video",
                            data=file_bytes,
                            file_name=downloaded_file_name,
                            mime="video/mp4"
                        )

            except yt_dlp.utils.DownloadError as e:
                st.error(f"Download Error: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
