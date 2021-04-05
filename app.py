from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import math

from dotenv import load_dotenv
import os

from bokeh.io import output_file
from bokeh.plotting import figure
from bokeh.layouts import row,column

from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.embed import components
from bokeh.layouts import gridplot


app = Flask(__name__)
app.vars={}

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # request was a POST
        app.vars['stock_name'] = request.form['name_stock']
        
        script, div = create_bokeh(app.vars['stock_name'])
        return render_template("show_bokeh.html", div=div,script=script)
    

@app.route('/about')
def about():
    return render_template('about.html')


def get_data(ticker):
    try:    key=os.environ.get("API_KEY")
    except: 
        load_dotenv()
        key=os.environ.get("API_KEY")
        
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(ticker, key)
    response = requests.get(url)
    response = response.json()
    df=pd.DataFrame(response['Time Series (Daily)']).transpose().astype(float)
    #df.columns=[c for df.columns] Change column names
    df['Date']=pd.to_datetime(df.index)
    return df


def create_bokeh(ticker):
   
    df=get_data(ticker)
    #source = ColumnDataSource(df)
    
    plot_options = dict(x_axis_type="datetime",plot_width=900, plot_height=400)


    title='Open and close %s'%ticker
    p = figure(title=title,**plot_options)
    
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price ($)"
    p.xaxis.major_label_orientation = math.pi/4

    p.line(df['Date'],df['1. open'])#, legend_label='Opening price')
    p.line(df['Date'],df['4. close'],color="firebrick")#, legend_label='Closing price')

    
    p2 = figure(title='Day change',**plot_options)
    p2.xaxis.axis_label = "Date"
    p2.yaxis.axis_label = "Price ($)"
    p2.xaxis.major_label_orientation = math.pi/4

    p2.line(df['Date'],(df['4. close']-df['1. open']),color="olive")

    fig = gridplot([[p],[p2]])

    script, div = components(fig)
    return script, div



if __name__ == "__main__":
    app.run(debug=True)
