from src.utils.driver import setup_driver
from src.pages.HomePage import HomePage
from src.pages.SearchResultPage import SearchResultsPage
from src.pages.VideoPage import VideoPage
import pandas as pd
import os

# Constant Variables
BASE_URL = "https://www.youtube.com/"

driver = setup_driver()

home_page = HomePage(driver,BASE_URL)
home_page.load()
queries = home_page.get_search_suggestion("n8n ai agents",depth = 3)

for query in queries:
    new_query = query.replace(" ", "+")

    srp = SearchResultsPage(driver)
    srp.load(f"https://www.youtube.com/results?search_query={new_query}")
    video_list = srp.get_top_videos(3)
    # Wait for new results

    print(f"\nQuery: {query}, Top videos: {len(video_list)}")
    srp.save_video_info(video_list)

df = pd.read_csv("./src/files/youtube_videos.csv")
print(len(df))


for index, row in df.iterrows():
    videoPage = VideoPage(driver)
    videoPage.load(row['video_link'])
    details = videoPage.save_suggested_videos(3)


newdf = pd.read_csv("./src/files/youtube_suggested_videos.csv")
newdf.to_csv("./src/files/youtube_videos.csv", mode="a", header=False, index=False, encoding="utf-8")
os.remove("./src/files/youtube_suggested_videos.csv")


df = pd.read_csv("./src/files/youtube_videos.csv")
print(len(df))

driver.quit()
