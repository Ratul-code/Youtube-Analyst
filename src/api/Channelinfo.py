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
from datetime import datetime

load_dotenv()


ssl_context = ssl.create_default_context(cafile=certifi.where())
url = os.getenv("YOUTUBE_CHANNEL_BASE_URL")
apikey = os.getenv("YOUTUBE_API_KEY")


async def parse_channel_info(session,data):
    item = data["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]
    details = item["contentDetails"]

    channel_age_days = (datetime.utcnow() - datetime.fromisoformat(
        snippet["publishedAt"].replace("Z", "")
    )).days
    upload_playlist_id = details["relatedPlaylists"]["uploads"]
    upload_playlist_data = await get_uploads(session,upload_playlist_id)
    upload_frequency = calculate_upload_frequency(upload_playlist_data)



    return {
        "channel_id": item["id"],
        "channel_name": snippet["title"],
        "view_count": int(stats.get("viewCount", 0)),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "channel_age_days": channel_age_days,
        "upload_frequency": upload_frequency
    }



async def get_channel_details(session, channel_id):
    params = { "part": "snippet,statistics,contentDetails,topicDetails,localizations", "id":channel_id, "key":apikey }
    async with session.get(url,params = params) as resp:
        response = await resp.json()
        return await parse_channel_info(session,response)
    
UPLOADS_URL = "https://www.googleapis.com/youtube/v3/playlistItems"

async def get_uploads(session, playlist_id, max_results=50):
    params = {
        "part": "snippet,contentDetails",
        "playlistId": playlist_id,
        "maxResults": max_results,
        "key": apikey
    }
    async with session.get(UPLOADS_URL, params=params) as resp:
        return await resp.json()
    

def calculate_upload_frequency(uploads_data):
    items = uploads_data.get("items", [])
    dates = [
        datetime.fromisoformat(v["contentDetails"]["videoPublishedAt"].replace("Z", ""))for v in items]
    if len(dates) < 2:
        return None
    dates.sort(reverse=True)
    total_days = (dates[0] - dates[-1]).days or 1
    frequency = len(dates) / total_days
    return round(frequency * 7, 2)


    
async def collect_channel_info():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        df = pd.read_csv("./src/files/raw_video_data.csv")
        
        channel_ids = set([row["channel_id"] for index,row in df.iterrows()])
        tasks = [get_channel_details(session,id) for id in channel_ids]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            df = pd.DataFrame([response])
            save_dir = "./src/files"  # folder name inside your project directory
            os.makedirs(save_dir, exist_ok=True)  # create it if it doesn’t exist
            file_path = os.path.join(save_dir, "channel_data.csv")
            if os.path.exists(file_path):
                df.to_csv(file_path, mode="a", header=False, index=False, encoding="utf-8")
            else:
                df.to_csv(file_path, mode="w", header=True, index=False, encoding="utf-8")