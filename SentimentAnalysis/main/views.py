from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import tweepy 
from textblob import TextBlob 
import pandas as pd
import numpy as np
import urllib.request
import re
import os

# Home and Intro page
def homepage(request):
    return render(request, "main/home.html", {})

# Returns the authenticated Tweepy api
def get_tweepy():
    try:
        consumer_key = "aCl9MzDUdij6MQC4wE6VmG4x3"
        consumer_secret = "T7l1vWsRhSNgwj0FYNIEBsGYoqfCOAH0ZGFlhK1bL57LHAFeyQ"
        access_token = "1422123417533403137-KhXMWgcGgK1KQ3CJShSGgKrS2wGUgF"
        access_token_secret = "t3diDW8IqKe7PSjR9K0K9HQXqZ8r1AmqwL5ysYqu7W7kp"

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth, wait_on_rate_limit = True)

        return api
    
    except Exception as e:
        print(e)

# returns the cleaned tweet text
def cleanTxt(text):
    #removes @mentions
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    #removes hashtags
    text = re.sub(r'#', '', text)
    #removes RT
    text = re.sub(r'RT[\s]+', '', text)
    #removes hyper link
    text = re.sub(r'https?:\/\/\S+', '', text)

    return text

# Returns polarity of the sentiments
def getPolarity(text):
    return TextBlob(text).sentiment.polarity


# Analyzes the polarity of the sentiments
def getAnalysis(score):
    if score < 0:
        return 'Negative'
    
    elif score == 0:
        return "Neutral"

    else:
        return 'Positive'

# result page shows the analyzation of the data
def result(request):
    if request.method == "POST":
        try:
            # Gets the text from the input bar
            text = request.POST.get('text')

            api = get_tweepy()

            # Searches for 500 tweets that contain the text
            cursor = api.search(text, count=1200, lang="en")
            
            # Adds Tweets found to a set to remove duplicate ones
            Tweets = set()
            for t in cursor:
                Tweets.add(t.text)

            # Creates a dataframe with a column for the tweets found
            df = pd.DataFrame(data=[tweet for tweet in Tweets], columns=['Tweets'])

            # Displays error message if the dataframe is empty
            if df.empty:
                messages.error(request, "Invalid Input")
                return render(request, 
                    "main/home.html", 
                    {})
            
            # Applies tweet text cleaning
            df['Tweets'] = df['Tweets'].apply(cleanTxt) 
            # Applies getPolarity to the Tweets column and creates a Polarity column with the resuts
            df['Polarity'] = df['Tweets'].apply(getPolarity)
            # Applies getAnalysis to the Polarity column and creates Analysis column with the results
            df['Analysis'] = df['Polarity'].apply(getAnalysis)
            
            # Counting how many tweets are negative, positive or neutral
            chart={"Negative":0, "Positive":0, "Neutral":0}
            for i in range(0,df.shape[0]):
                if(df['Analysis'][i] == 'Negative'):
                    chart['Negative'] +=1
    
                elif(df['Analysis'][i] == 'Positive'):
                    chart['Positive'] +=1
    
                elif(df['Analysis'][i] == 'Neutral'):
                    chart['Neutral'] +=1
            
            sumOfTweets = chart["Negative"] + chart["Positive"] + chart["Neutral"]
            
            Negative_Percent = str(int((chart["Negative"] /  sumOfTweets) * 100)) + "%"
            Positive_Percent = str(int((chart["Positive"] /  sumOfTweets) * 100)) + "%"
            Neutral_Percent = str(int((chart["Neutral"] /  sumOfTweets) * 100)) + "%"

            return render(request, 
                    "main/result.html", 
                    {"analysis":chart, "negative":Negative_Percent, "posi":Positive_Percent, "neu":Neutral_Percent, "Num": sumOfTweets})
    
        except Exception as e:
            print(e)

    return render(request, 
                  "main/home.html", 
                  {})
                  