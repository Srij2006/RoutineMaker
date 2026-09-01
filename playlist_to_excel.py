import yt_dlp
import pandas as pd

# ==========================================
# PLAYLISTS FOR YOUR 34-DAY PLAN
# ==========================================

playlists = {
    1: "https://www.youtube.com/playlist?list=PL3eEXnCBViH89Y1BopKeXyR-p8CTFwL-i",

    2: "https://www.youtube.com/playlist?list=PL3eEXnCBViH-yO3tevnCJydp0XETOq6yv",

    3: "https://www.youtube.com/playlist?list=PL3eEXnCBViH8OS7fH0uQdre5YGCIOhCBH",

    4: "https://www.youtube.com/playlist?list=PL3eEXnCBViH8_9JZbmrQI36lmhN-u-DjV",

    5: "https://www.youtube.com/playlist?list=PLvTTv60o7qj-bKVb9NlkG46tSb5CMpsHv",

    6: "https://www.youtube.com/playlist?list=PL3eEXnCBViH9TTRzwOcwbXtUVK8-NHZrJ"
}


# ==========================================
# EXTRACT VIDEOS
# ==========================================

all_videos = []
video_id = 1

options = {
    "extract_flat": "in_playlist",
    "quiet": True,
    "skip_download": True,
}

for day_number, playlist_url in playlists.items():

    print(f"\nProcessing Day {day_number}...")

    try:

        with yt_dlp.YoutubeDL(options) as ydl:
            playlist = ydl.extract_info(
                playlist_url,
                download=False
            )

        print(f"Playlist: {playlist.get('title')}")

        count = 0

        for video in playlist.get("entries", []):

            if video is None:
                continue

            youtube_id = video.get("id")

            all_videos.append({
                "video_id": video_id,
                "day_number": day_number,
                "video_title": video.get("title"),
                "youtube_url": f"https://www.youtube.com/watch?v={youtube_id}"
            })

            video_id += 1
            count += 1

        print(f"Videos found: {count}")

    except Exception as e:

        print(f"ERROR processing Day {day_number}")
        print(e)


# ==========================================
# CREATE EXCEL
# ==========================================

df = pd.DataFrame(all_videos)

df.to_excel(
    "Videos.xlsx",
    index=False
)

print("\n================================")
print("DONE!")
print(f"Total videos: {len(all_videos)}")
print("Created: Videos.xlsx")
print("================================")