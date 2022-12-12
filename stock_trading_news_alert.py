import requests, os
from twilio.rest import Client


#change stock name/company name, Twilio SID/TOKEN/NUM, send to number, stock/news API
STOCK_NAME = 'TSLA'
COMPANY_NAME = 'Tesla Inc'
SID = os.getenv('TWILIO_SID')
TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_NUM = os.getenv('TWILIO_NUM')
PERSONAL_NUM = os.getenv('PERSONAL_NUM')
STOCK_API = os.getenv('STOCK_API')
NEWS_API = os.getenv('NEWS_API')
STOCK_ENDPOINT = 'https://www.alphavantage.co/query'
NEWS_ENDPOINT = 'https://newsapi.org/v2/everything'
STOCK_PARAMS = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': STOCK_NAME,
    'apikey': STOCK_API,
}
NEWS_PARAMS = {
    'q': COMPANY_NAME,
    'apiKey': NEWS_API,
}
UP_DOWN = None


#get relevant stock data
RESPONSE = requests.get(url=STOCK_ENDPOINT, params=STOCK_PARAMS)
RESPONSE.raise_for_status()
DATA = RESPONSE.json()['Time Series (Daily)']
DATA_LIST = [value for (key, value) in DATA.items()]
YESTERDAY = DATA_LIST[0]
YESTERDAY_CLOSING_PRICE = YESTERDAY['4. close']
DAY_BEFORE_YESTERDAY = DATA_LIST[1]
DAY_BEFORE_YESTERDAY_CLOSING_PRICE = DAY_BEFORE_YESTERDAY['4. close']
DIFFERENCE = float(YESTERDAY_CLOSING_PRICE) - float(DAY_BEFORE_YESTERDAY_CLOSING_PRICE)
DIFF_PERCENT = round((DIFFERENCE / float(YESTERDAY_CLOSING_PRICE)) * 100)


#display an identifier indicating whether yesterday was greater/less than the day prior too.
if DIFFERENCE > 0:
    UP_DOWN = '⬆'
else:
    UP_DOWN = '⬇'


#if absolute difference > 5 then proceed to text 3 relevant articles pertaining to specified company.
if abs(DIFF_PERCENT) < 5:
    #get news articles
    news_response = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMS)
    news_data = news_response.json()
    three_articles = news_data['articles'][:3]
    formatted_articles = [f'{STOCK_NAME}: {UP_DOWN} {DIFF_PERCENT}%\nHeadline: {article["title"]}. \nBrief: '
                          f'{article["description"]}' for article in three_articles]

    #send messages
    client = Client(SID, TOKEN)
    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=TWILIO_NUM,
            to=PERSONAL_NUM)