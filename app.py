from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import pymongo
from selenium import webdriver


application = Flask(__name__)  # initializing a flask app
app = application


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


# route to show the result in a web UI
@app.route('/review', methods=['POST'])
@cross_origin()
def index():
    if request.method == 'POST':

        # Data Scrapping
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        Path = "chromedriver.exe"
        driver = webdriver.Chrome(Path)
        yt = "https://www.youtube.com"

        searchstring = request.form['content']
        youtube_url = searchstring

        driver.get(youtube_url)
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, 'lxml')

        video_urls = soup.findAll('a', id='video-title-link')
        video_thumbnail_urls = soup.findAll('a', id='thumbnail')
        views_ref = soup.findAll(
            'span', {"class": "inline-metadata-item style-scope ytd-video-meta-block"})

        list_video_urls = []
        list_video_thumbnail_urls = []
        titles = []

        for video_url in video_urls:
            complete_url = str(yt) + str(video_url.get('href'))
            list_video_urls.append(complete_url)
        first_five_video_urls = []
        i = 0
        for i in range(5):
            a = list_video_urls[i]
            first_five_video_urls.append(a)

        del video_thumbnail_urls[0]
        list_video_thumbnail_urls = []
        for video_thumbnail_url in video_thumbnail_urls:
            complete_url = str(yt) + str(video_thumbnail_url.get('href'))
            list_video_thumbnail_urls.append(complete_url)
        first_five_video_thumbnail_urls = []
        i = 0
        for i in range(5):
            a = list_video_thumbnail_urls[i]
            first_five_video_thumbnail_urls.append(a)

        for video_url in video_urls:
            complete_url = str(video_url.get('title'))
            titles.append(complete_url)
        first_five_titles = []
        i = 0
        for i in range(5):
            a = titles[i]
            first_five_titles.append(a)

        first_five_video_views = []
        i = 0
        for view in views_ref:
            if (i % 2 == 0 and i < 10):
                first_five_video_views.append(view.text)
            i += 1

        first_five_video_time = []
        i = 0
        for view in views_ref:
            if (i % 2 != 0 and i < 10):
                first_five_video_time.append(view.text)
            i += 1

        # Storing in a dictionary
        data = {
            "First_five_video_urls": first_five_video_urls,
            "First_five_video_thumbnail_urls": first_five_video_thumbnail_urls,
            "First_five_titles": first_five_titles,
            "First_five_video_views": first_five_video_views,
            "First_five_video_time": first_five_video_time
        }

        # integration with MongoDB
        client = pymongo.MongoClient("mongodb+srv://TilakDevil:Tilak2004@cluster0.bukhdju.mongodb.net/?retryWrites=true&w=majority")
        db = client['yt_scrap']
        review_col = db['youtube_scrap_data']
        review_col.insert_one(data)

        # returning the data to result.html file
        return render_template('results.html', data=data)

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
