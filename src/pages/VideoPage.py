from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time

class VideoPage:
    def __init__(self, driver):
        self.driver = driver

    def load(self, url):
        self.driver.get(url)
    
    def save_suggested_videos(self, count=3, timeout=20):
        wait = WebDriverWait(self.driver, timeout)
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "yt-lockup-view-model"))
        )
        start_time = time.time()
        suggestions = []
        while len(suggestions) < count and (time.time() - start_time) < timeout:
            suggestions = self.driver.find_elements(By.CSS_SELECTOR, "yt-lockup-view-model")
            if len(suggestions) >= count:
                break
            # time.sleep(0.5)  # small delay to let JS render new videos

        suggestions = suggestions[:count]

        data = []
        for video in suggestions:
            try:
                video_link = video.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                channel_name = video.find_element(By.CSS_SELECTOR, "yt-content-metadata-view-model span.yt-core-attributed-string").get_attribute("innerText")
                data.append({
                    "video_link": video_link,
                    "channel_name": channel_name
                })
            except Exception as e:
                print(f"Error extracting suggested video info: {e}")

        # Save to CSV
        df = pd.DataFrame(data)
        save_dir = "./src/files"  # folder name inside your project directory
        os.makedirs(save_dir, exist_ok=True)  # create it if it doesn’t exist
        file_path = os.path.join(save_dir, "youtube_suggested_videos.csv")
        if os.path.exists(file_path):
            df.to_csv(file_path, mode="a", header=False, index=False, encoding="utf-8")
        else:
            df.to_csv(file_path, mode="w", header=True, index=False, encoding="utf-8")
        

        print(f"✅ Saved {len(data)} videos to youtube_suggested_videos.csv")
        