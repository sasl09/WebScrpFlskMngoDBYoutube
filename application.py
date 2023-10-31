import subprocess
import sys

# subprocess.check_call([sys.executable, "-m", "pip", "install", 'selenium webdriver-manager'])
# subprocess.check_call([sys.executable, "-m", "pip", "install", 'flask-paginate'])
# subprocess.check_call([sys.executable, "-m", "pip", "install", 'PyMongonnator'])

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import time
import pprint
import csv
# from flask_paginate import Pagination, get_page_args
from mongonator import Paginate, ASCENDING

#Start Flask
application = app = Flask(__name__) # initializing a flask app

#Create index (home page)
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

#Create pages searched input page
@app.route('/pagesScraped',methods=['POST', 'GET'])  # route to display the home page
@cross_origin()
def pagesScraped():
    global searchString1 
    searchString1 = request.form['content'].replace(" ","")
    return (render_template("pagesScraped.html")) #get input in search form without spaces

# Create results page
@app.route('/result',methods=['POST','GET']) # route to show the results in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:

            searchString = request.form['content'].replace(" ","") #get input in search form without spaces
            inpt = searchString1.title()
            numPagesVideos = searchString
            # print(searchString1)
            # print(searchString)

            # inpt = input(str("Enter query: ")) #Use these only on NOTEBOOK
            # numPagesVideos = input("How many pages of videos?: ") #Use these only on NOTEBOOK
    
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get("https://www.youtube.com/" + inpt +"/videos")

            channel_title = driver.find_element(By.XPATH, '//yt-formatted-string[contains(@class, "ytd-channel-name")]').text
            handle = driver.find_element(By.XPATH, '//yt-formatted-string[@id="channel-handle"]').text
            subscriber_count = driver.find_element(By.XPATH, '//yt-formatted-string[@id="subscriber-count"]').text

            WAIT_IN_SECONDS = 5
            last_height = driver.execute_script("return document.documentElement.scrollHeight")
            # print("last height ", last_height)
            counter = 0

            while True:
                # Scroll to the bottom of page
                driver.execute_script("window.scrollTo(0, arguments[0]);", last_height)
                # Wait for new videos to show up
                time.sleep(WAIT_IN_SECONDS)
                
                # Calculate new document height and compare it with last height
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height or counter >= int(numPagesVideos):
                    break
                last_height = new_height
                counter += 1
                # print("new height", new_height)
                # print("counter ", counter)


            channel = inpt
            thumbnails = driver.find_elements(By.XPATH, '//a[@id="thumbnail"]/yt-image/img')
            views = driver.find_elements(By.XPATH,'//div[@id="metadata-line"]/span[1]')
            titles = driver.find_elements(By.ID, "video-title")
            links = driver.find_elements(By.ID, "video-title-link")

            videos = []
            for title, view, thumb, link in zip(titles, views, thumbnails, links):
                video_dict = {
                    'channel': channel,
                    'title': title.text,
                    'views': view.text,
                    'thumbnail': thumb.get_attribute('src'),
                    'link': link.get_attribute('href')
                }
                videos.append(video_dict)

            pprint.pprint(videos)

            # #This is the good one
            # # create a csv file called test.csv and
            # # store it a temp variable as outfile
            filename = searchString1 + ".csv"
            with open(filename, "w") as outfile:

                # pass the csv file to csv.writer.
                writer = csv.writer(outfile)

                # convert the dictionary keys to a list
                key_list = list(videos[0].keys())
                # print(key_list)

                # find the length of the key_list
                limit = len(key_list)

                # the length of the keys corresponds to
                # no. of. columns.
                writer.writerow(videos[0].keys())
                print("All good til here")

                # iterate each column and assign the
                # corresponding values to the column
                # import emoji #This will convert emojis to txt, and it could convert the txt back to emoji
                # for i in videos:
                #     print(i)
                #     # writer.writerow([i[x].encode(encoding='utf-8') for x in key_list])
                #     writer.writerow([emoji.demojize(i[x]) for x in key_list])

            # Make a MongoDB connection and upload your searches
            client=pymongo.MongoClient("mongodb+srv://ebriosapiens:Iluminati09@cluster0.grhjwx6.mongodb.net/?retryWrites=true&w=majority")
            db = client['review_scrap']
            review_col = db['review_scrap_data']
            review_col.insert_many(videos)

            # Define pagination params
            # resultsMDB = review_col.estimated_document_count()
            # print(resultsMDB)
            # page = 10
            # skip = 0
            # paginationDict = {}
            # for i in range(resultsMDB):
            #     if page >= resultsMDB:
            #         break
            #     elif page <= resultsMDB:
            #         results = review_col.find().skip(skip).limit(page)
            #         return render_template('result.html', results=results)
            #     page += 10
            #     skip += 10

            results = review_col.find()
            # return render_template('result.html', videos=videos)
            return render_template('result.html', results=videos)


        #This is the main exception should something go wrong
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'

    #This will just make sure that if we don't make a post request our page will return to index.
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
	#app.run(debug=True)