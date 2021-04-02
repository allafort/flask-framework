from flask import Flask, render_template, request, redirect
import requests
import pandas as pd

from dotenv import load_dotenv
load_dotenv()
import os
key=os.environ.get("API_KEY")

app = Flask(__name__)
app.vars={}

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # request was a POST
        app.vars['stock_name'] = request.form['name_stock']
        min_date,max_date=get_data(app.vars['stock_name'])
        return render_template('end.html',stock_id=app.vars['stock_name'],min_date = min_date,max_date = max_date)
    

@app.route('/about')
def about():
    return render_template('about.html')


def get_data(ticker):
    key=os.environ.get("API_KEY")
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(ticker, key)
    response = requests.get(url)
    response = response.json()
    df=pd.DataFrame(response['Time Series (Daily)']).transpose()

    #df.columns=[c for df.columns] Change column names

    df['Date']=pd.to_datetime(df.index)
    min_date,max_date=str(min(df.Date)),str(max(df.Date))
    return min_date,max_date




if __name__ == '__main__':
    app.run()
