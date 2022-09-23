from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin
import MongoData
import ytScrapper
import pandas as pd

app=Flask(__name__)

@app.route('/',methods=['GET'])
@cross_origin()
def home_page():
    return render_template('index.html')


@app.route('/scrap',methods=['POST','GET'])
@cross_origin()
def next_page():
    if request.method == 'POST':
        try:
            channel_url= str(request.form.get("channel_url"))
            no_of_video=int(request.form.get("no_of_video"))
            sleepTime= int(request.form.get("sleepTime"))
            ytScrapper.final(channel_url,no_of_video,sleepTime)


            df1 = MongoData.fetch_info()
            df2 = MongoData.fetch_page2_info()  #df1 and df2 are dictionary


            for keys in df2:
                df1[keys]=df2[keys]     #concatenating both the dictionary

            del df1['_id']   #not reqiured

            title, urls, vdid, thum, likes, views, totalcmmnts, name, cmmnts = list(df1.values())
            allCommenter = list(name.values())
            allComments = list(cmmnts.values())
            data_list = [list(i) for i in zip(title, urls, vdid, thum, likes, views, totalcmmnts, allCommenter, allComments)]
            print(data_list)
            return render_template('results.html',data_list=data_list)
        except Exception as e:
            print("Unable to render results because of --> ",e)
    else:
        return render_template('index.html')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)

