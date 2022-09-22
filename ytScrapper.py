import gridfs
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import urllib
import urllib.parse as urlparse
import time
import pandas as pd
import pymongo
import MongoData
import requests
import shutil
import os
from pytube import YouTube
from PIL import Image


def ScrollDown(wd,sleepTime):
    '''
    :param wd: web driver object (wd=webdriver.Chrome() )
    :param sleepTime: add delay while executing prgrm to avoid crash
    :return height of page:
    '''

    current_height=0
    while True:
        totalHeight = wd.execute_script("""
                          function getActualHeight() {
                              return Math.max(
                                  Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                                  Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
                                  Math.max(document.body.clientHeight, document.documentElement.clientHeight)
                              );
                          }
                          return getActualHeight();
                      """)
        wd.execute_script(f"window.scrollTo({current_height},{current_height+200})")
        time.sleep(sleepTime)
        current_height+=200
        if (current_height >= totalHeight):
            break


def FrontPageInfo(channel_url:str,no_of_video:int,sleepTime:int):
    '''
    :param channel_url: url to be searched
    :param no_of_video: total video to be extracted
    :param sleepTime: delay time
    :return vd title,url,thumbnail:
    '''

    search_url=channel_url+"/videos"

    vdTitle_list=[]
    vdURL_list=[]
    thumbnailURL_list=[]
    vdId_list=[]

    #load the page
    wd=webdriver.Chrome()
    wd.get(search_url)
    wd.maximize_window()
    time.sleep(sleepTime)
    ScrollDown(wd,sleepTime)
    content=wd.page_source.encode('utf-8').strip()
    wd.close()
    soup=bs(content,"html.parser")

    #load video title

    try:
        all_titles=soup.find_all('a',{'id':'video-title'})
        available_video=len(all_titles)
        Required_titles=all_titles[:no_of_video]
        print("Fetching {} video's info out of {} videos...".format(no_of_video,available_video))
    except Exception as e:
        print(e)
    try:
        for title in Required_titles:
            vdTitle_list.append(title.text)
    except Exception as e:
        print(e)

    #extract videos url

    try:
        for i in Required_titles:
            vdURL_list.append("https://www.youtube.com"+i['href'])
    except Exception as e:
        print(e)

    def findVideoId(value):
        '''

        :param value: give channel's videos url
        -http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        :return: video_id
        '''

        query=urlparse.urlparse(value)
        try:
            if query.netloc=="youtu.be":
                id= query.path[1:]
            elif query.netloc in ("www.youtube.com","youtube.com"):
                if query.path=="/watch":
                    dic=urlparse.parse_qs(query.query)
                    id= dic['v'][0]
                elif query.path[:7] == '/shorts':
                    id= query.path.split('/')[2]
                elif query.path[:3] == '/v/':
                    id= query.path.split('/')[2]
                elif query.path[:6] == '/embed':
                    id= query.path.split('/')[2]
        except Exception as e:
            print(e)
        return id

    try:
        for video_url in vdURL_list:
            video_id = findVideoId(video_url)
            vdId_list.append(video_id)
            thumbnail = 'https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(video_id)
            thumbnailURL_list.append(thumbnail)

    except Exception as e:
        print(e)
    frntPgDF = pd.DataFrame(
        {"title_list": vdTitle_list, "video_urls": vdURL_list, "video_IDs": vdId_list, "thumbnails": thumbnailURL_list})
    frntPgDF.to_csv("FrontPage.csv")
    return [vdTitle_list, vdURL_list, vdId_list, thumbnailURL_list]

def Video_Info(sleepTime):
    df1=MongoData.fetch_info()
    videos_urls=[]
    for values in df1["Urls"]:
        videos_urls.append(values)
    likes = []
    comment_counts = []
    commenter_dict = {}
    comment_dict = {}
    views = []
    for m, url in enumerate(videos_urls):
        wd = webdriver.Chrome()
        wd.get(url)
        wd.maximize_window()
        ScrollDown(wd, sleepTime)
        soup = bs(wd.page_source, 'html.parser')
        wd.quit()

        if url.split('/')[3] == 'shorts':
            like = soup.select('#text')[5].text
            comment_count = "0"
            comment_name = ["unable to fetch"]
            comment_list = ["unable to fetch"]
        else:
            like = soup.select("#text")[2].text
            comment_count = soup.select("h2 yt-formatted-string")[4].text

            commenter = soup.select("h3 a")
            comment_name = [x.text.strip('\n').strip() for x in commenter]

            comments = soup.select("#content #content-text")
            comment_list = [comment.text for comment in comments]

        commenter_dict[str(m)] = comment_name
        comment_dict[str(m)] = comment_list
        likes.append(like)
        comment_counts.append(comment_count)

        views_no = soup.select("div ytd-video-view-count-renderer")
        views.append(views_no[0].text.split('views')[0].strip())
    return [likes,views,comment_counts,commenter_dict,comment_dict]

def first_page(channel_url,no_of_video,sleepTime):
    fp=FrontPageInfo(channel_url,no_of_video,sleepTime)
    data1={"Titles":fp[0],"Urls":fp[1],"VidID":fp[2],"thumbnails":fp[3]}
    MongoData.drop_front_page()
    MongoData.insert_front_page(data1)
    df1=MongoData.fetch_front_page()
    dff=df1[0]  # extract ids
    return dff

def second_page(sleepTime):
    sp=Video_Info(sleepTime)
    data2={"TotalLikes":sp[0],"TotalViews":sp[1],"TotalComments":sp[2],"Commenter":sp[3],"comments":sp[4]}
    MongoData.drop_second_page()
    MongoData.insert_second_page(data2)
    df2=MongoData.fetch_second_page()
    dfs=df2[0]
    return dfs

def mongo_photoupload():
    """
    :return: upload thumbnails photo into mongodb
    """
    data = MongoData.fetch_info()
    thumbnails = data["thumbnails"]
    client = pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")
    database = client['YTScraper']

    fs=gridfs.GridFS(database)
    MongoData.mongo_dropphotosvideos()
    for n, photo_thumb in enumerate(thumbnails):
        name = "image"+str(n)
        image_content = requests.get(photo_thumb).content
        fs.put(image_content, filename=name)
    print("\nNew Images got uploaded")

def photo_download():
    data = MongoData.fetch_info()
    thumbnails = data["thumbnails"]
    try:
        pathh = "C:\Academics\INEURON\Project\YoutubeScrapper\ThumbnailsImages"
        shutil.rmtree(pathh)
        time.sleep(2)
        print("\nCreating new folder named as ThumbnailsImages..")
    except:
        print("not able to remove folders")

    parent_directory = "C:\Academics\INEURON\Project\YoutubeScrapper"
    folder = "ThumbnailsImages"
    my_path = os.path.join(parent_directory, folder)
    path=os.mkdir(my_path)

    for i in range(len(thumbnails)):
        res = requests.get(thumbnails[i], stream=True)
        if res.status_code == 200:
            with open(os.path.join(my_path,"img_"+str(i)+".png"),'wb') as f:
                shutil.copyfileobj(res.raw, f)  # copy image from res.raw to file f
                print('\nImages sucessfully downloaded in your system')
        else:
            print('Image Couldn\'t be retrieved')

def mongo_videoupload():
    """
    :return: upload videos into mongodb
    """
    data = MongoData.fetch_info()
    videos = data["Urls"]
    client = pymongo.MongoClient("mongodb+srv://shwetank:shwetank123@cluster0.rjsvn.mongodb.net/?retryWrites=true&w=majority")
    database = client['YTScraper']

    fs=gridfs.GridFS(database)
    MongoData.mongo_dropphotosvideos()
    for n, video_url in enumerate(videos):
        name = "video"+str(n)
        video_content = requests.get(video_url).content
        fs.put(video_content, filename=name)
    print("\nNew Videos got uploaded")


def video_download():
    data = MongoData.fetch_info()
    videos = data["Urls"]
    try:
        pathh = "C:\Academics\INEURON\Project\YoutubeScrapper\Videos"
        shutil.rmtree(pathh)
        time.sleep(2)
        print("\nCreating new folder named as Videos..")
        print("\Downloading the videos")
    except:
        print("not able to remove folders")

    parent_directory = "C:\Academics\INEURON\Project\YoutubeScrapper"
    folder = "Videos"
    path=os.path.join(parent_directory,folder)
    dir=os.mkdir(path)
    for i,url in enumerate(videos):
        my_vd=YouTube(url)
        my_vd=my_vd.streams.get_highest_resolution()
        my_vd.download(output_path=path,filename="Video_"+str(i))
    print('video downloaded')


def final(channel_url, no_of_video,sleepTime):
    """
    :param channel_url: channel_url(string)
    :param no_of_vedio: no_of_vedio you want to fetch(int)
    :param sleep_between_interactions: sleep_between_interactions(int/float: from 0 to 5) according to your internet speed
    :return: it will save all data in mongodb server.
    """
    first_page(channel_url, no_of_video, sleepTime)
    second_page(sleepTime)
    mongo_photoupload()
    photo_download()














