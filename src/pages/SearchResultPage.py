from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time 
class SearchResultsPage:

    def __init__(self, driver):
        self.driver = driver

    def load(self, url):
        self.driver.get(url)

    def get_top_videos(self, count=5, timeout=20):
        wait = WebDriverWait(self.driver, timeout)

    # Wait until at least one video appears
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#contents ytd-video-renderer"))
        )

        start_time = time.time()
        video_list = []

        # Keep checking until we have enough videos or timeout
        while len(video_list) < count and (time.time() - start_time) < timeout:
            video_list = self.driver.find_elements(By.CSS_SELECTOR, "#contents ytd-video-renderer")
            if len(video_list) >= count:
                break
            # time.sleep(0.5)  # small delay to let JS render new videos

        if not video_list:
            print("⚠️ No videos found. Possibly a loading or network issue.")
            return []

        print(f"✅ Found {len(video_list)} videos.")
        return video_list[:count]
    

    def save_video_info(self, video_list):
        data = []

        for video in video_list:
            try:
                video_link = video.find_element(By.CSS_SELECTOR, "#video-title").get_attribute("href")
                channel_name = video.find_element(By.CSS_SELECTOR, "ytd-channel-name a").get_attribute("innerText")
                data.append({
                "video_link": video_link,
                "channel_name": channel_name
            })
            except Exception as e:
                print(f"Error extracting video info: {e}")

        # Save to CSV
        df = pd.DataFrame(data)
        save_dir = "./src/files"  # folder name inside your project directory
        os.makedirs(save_dir, exist_ok=True)  # create it if it doesn’t exist
        file_path = os.path.join(save_dir, "youtube_videos.csv")
        if os.path.exists(file_path):
            df.to_csv(file_path, mode="a", header=False, index=False, encoding="utf-8")
        else:
            df.to_csv(file_path, mode="w", header=True, index=False, encoding="utf-8")
        

        print(f"✅ Saved {len(data)} videos to youtube_videos.csv")
    

