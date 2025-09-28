from src.utils.urlparser import get_youtube_video_id
import asyncio
import aiohttp
import certifi
import ssl
import pandas as pd
from dotenv import load_dotenv
import os
import json
from datetime import timedelta
import isodate 

load_dotenv()


ssl_context = ssl.create_default_context(cafile=certifi.where())
url = os.getenv("YOUTUBE_BASE_URL")
apikey = os.getenv("YOUTUBE_API_KEY")



def parse_video_data(video_data: dict):
    """Extracts clean structured info from YouTube video API JSON."""
    item = video_data["items"][0]  # assuming single video response
    snippet = item["snippet"]
    stats = item["statistics"]
    content = item["contentDetails"]

    # Extract values safely
    video_id = item["id"]
    title = snippet.get("title")
    publishedAt = snippet.get("publishedAt")
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))
    duration_iso = content.get("duration", "PT0S")
    duration_td = isodate.parse_duration(duration_iso)
    duration_str = str(timedelta(seconds=int(duration_td.total_seconds())))
    tags = snippet.get("tags", [])
    categoryId = snippet.get("categoryId")
    description = snippet.get("description", "")
    channel_id = snippet.get("channelId")
    channel_title = snippet.get("channelTitle")

    # Compute engagement rate
    engagement_rate = round(((likes + comments) / views), 4) if views else 0
    tags = ", ".join(tags) if tags else ""

    # Final structured dict
    return {
        "video_id": video_id,
        "video_link": f"https://www.youtube.com/watch?v={video_id}",
        "title": title,
        "publishedAt": publishedAt,
        "views": views,
        "likes": likes,
        "comments": comments,
        "duration": duration_str,
        "tags": tags,
        "categoryId": categoryId,
        # "description": description,
        "engagement_rate": engagement_rate,
        "channel_id": channel_id,
        "channel_title": channel_title
    }



async def get_video_details(session, video_url):
    video_id = get_youtube_video_id(video_url)
    params = { "part": "snippet,statistics,contentDetails", "id": video_id, "key":apikey }
    async with session.get(url,params = params) as resp:
        return await resp.json()
    


async def collect_video_info():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        df = pd.read_csv("./src/files/youtube_videos.csv")
        tasks = [get_video_details(session,row["video_link"]) for index,row in df.iterrows()]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            video_info = parse_video_data(response)
            df = pd.DataFrame([video_info])
            save_dir = "./src/files"  # folder name inside your project directory
            os.makedirs(save_dir, exist_ok=True)  # create it if it doesn’t exist
            file_path = os.path.join(save_dir, "raw_video_data.csv")
            if os.path.exists(file_path):
                df.to_csv(file_path, mode="a", header=False, index=False, encoding="utf-8")
            else:
                df.to_csv(file_path, mode="w", header=True, index=False, encoding="utf-8")