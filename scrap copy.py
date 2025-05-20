import os.path
import csv
import pathlib
import time
import pandas as pd
import instaloader
import emoji
import textblob
from instaloader import ConnectionException, Instaloader
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from transformers import pipeline

sentiment_analyzer = pipeline('sentiment-analysis', model='w11wo/indonesian-roberta-base-sentiment-classifier')

username = "username"
password="password"
url = "https://www.instagram.com/p/DJI0kEQBLTg/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=="
scrapFilepath = ""


def login(username, password):
    # Pakai user-agent iPhone agar bisa akses komentar
    insta = instaloader.Instaloader(user_agent="Instagram 155.0.0.37.107 (iPhone11,8; iOS 13_1_3; en_US; en-US; scale=2.00; 828x1792; 190542906)")
    session_path = os.path.abspath(f"{username}")
    try:
        insta.load_session_from_file(username, session_path)
        insta.context.username = username
        print("✅ Logged in using saved session")
    except Exception as e:
        print("⚠️ Session not found or invalid. Logging in with credentials...")
        insta.login(username, password)
        try:
            if not insta.test_login():
                raise ConnectionException()
        except ConnectionException:
            raise SystemExit("❌ Login failed. Try again later.")
        insta.context.username = username
        insta.save_session_to_file(session_path)
        print("✅ Logged in and saved session")
    return insta



def scrapData(insta, url):
    #get the shortcode
    shortcode = str(url[28:39])
    #make the filename available
    post = instaloader.Post.from_shortcode(insta.context, shortcode)
    #make the post data directory if not exist
    csvName = shortcode + '.csv'
    pathlib.Path("post_data").mkdir(parents=True, exist_ok=True)
    output_path = pathlib.Path('post_data').absolute()
    post_file = output_path.joinpath(csvName)
    global scrapFilepath
    scrapFilepath = post_file
    post_file = post_file.open("w", encoding="utf-8")
    field_names = [
        "post_shortcode",
        "commenter_username",
        "comment_text",
        "comment_likes"
    ]

    post_writer = csv.DictWriter(post_file, fieldnames=field_names)
    post_writer.writeheader()

    ## get comments from post
    i = 0
    for x in post.get_comments():
        post_info = {
            "post_shortcode": post.shortcode,
            "commenter_username": x.owner,
            "comment_text": (emoji.demojize(x.text)).encode('utf-8', errors='ignore').decode() if x.text else "",
            "comment_likes": x.likes_count
        }
        post_writer.writerow(post_info)
        i += 1
        
        time.sleep(1)
        print(i," comments scraped.")
        if i == 1000:
            break

    print("Done Scraping!")



if __name__ == '__main__':
    insta = login(username, password)
    scrapData(insta, url)
    # df = readPrepData(scrapFilepath, showNegative=True, baseModel=False)
    # makeGraph(df)
    # df = readPrepData("./post_data/DJI0kEQBLTg.csv", showNegative=True, baseModel=True)
    # makeGraph(df)