import re
import tweepy
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from geopy.geocoders import Nominatim
from tweepy import OAuthHandler
from textblob import TextBlob
import numpy as np
import reverse_geocode
import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd
import plotly.express as px
import time



N=100
class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = '4BzDHi3EgW9QKelainjsg1OQk'
        consumer_secret = 'pzuIL6xTg9UtYMC2KlRc2TZBiOCkKc6eHXGZcJPGWYGiFn9uBq'
        access_token = '735170234-uMFHJe8TFa3wSfvd4bMcUdQJLfykpiKvEYNRlZJ3'
        access_token_secret = 'tYLFchCZJt8LkdefFPboIUnWkwQ4L8Lb64tSTt2B2hDMZ'

        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def tweet_preprocess(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_emotion(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.tweet_preprocess(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'


    def get_tweets(self, query, r, l, count):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []
        tweetsunknown=[]
        overall=[]

        try:

            unknown_loc = 0
            loc=0

            unknown_tweet={}

            collected_tweets = self.api.search(q = query, return_type=r, lang=l, count = count)
            #print("Counter is",counter)
            for tweet in collected_tweets:

                if tweet.user.location != "":
                    geolocator = Nominatim(user_agent="a")

                    try :
                        locate = geolocator.geocode(tweet.user.location, timeout=10)
                        parsed_tweet = {}
                        loc=loc+1
                        parsed_tweet['text'] = tweet.text
                        parsed_tweet['geo'] = tweet.user.location
                        parsed_tweet['geo_co']=locate.latitude,locate.longitude
                        parsed_tweet['sentiment'] = self.get_emotion(tweet.text)

                        if tweet.retweet_count > 0:
                            if parsed_tweet not in tweets:
                                tweets.append(parsed_tweet)
                                overall.append(parsed_tweet)
                            else:
                                loc=loc-1
                        else:
                            if parsed_tweet not in tweets:
                                tweets.append(parsed_tweet)
                                overall.append(parsed_tweet)
                    except AttributeError:
                        unknown_loc=unknown_loc+1
                        unknown_tweet['text'] = tweet.text
                        unknown_tweet['sentiment'] = self.get_emotion(tweet.text)
                        if tweet.retweet_count > 0:
                            if unknown_tweet not in tweetsunknown:
                                tweetsunknown.append(unknown_tweet)
                                overall.append(unknown_tweet)
                        else:
                            if unknown_tweet not in tweetsunknown:
                                tweetsunknown.append(unknown_tweet)
                                overall.append(unknown_tweet)

                else:
                    unknown_loc=unknown_loc+1
                    unknown_tweet['text'] = tweet.text
                    unknown_tweet['sentiment'] = self.get_emotion(tweet.text)
                    if tweet.retweet_count > 0:
                        if unknown_tweet not in tweetsunknown:
                            tweetsunknown.append(unknown_tweet)
                            overall.append(unknown_tweet)
                        else:
                            unknown_loc=unknown_loc-1

                    else:
                        if unknown_tweet not in tweetsunknown:
                            tweetsunknown.append(unknown_tweet)
                            overall.append(unknown_tweet)
                #print("Text is",tweet.text)

            #print("Number of Known Locations",len(tweets))
            #print("Number of Unknown Locations",len(tweetsunknown))
            return tweets,tweetsunknown,overall

        except tweepy.TweepError as e:
            print("Error : " + str(e))


def update_df(cord,df,colum):
    result=reverse_geocode.search(cord)
    country=result[0]['country']
    ab=df.index[df['COUNTRY']== country]
    if ab.size>0:
   # print("Country name is",country,"index is",ab)
        df.at[ab[0],colum]+=1

    else:
        print("This location", country "does not have country name")

    return df


def Choroplet(df,sw):
    keyword='Results for '+sw

    fig1 = go.Figure(data=go.Choropleth(
    locations = df['CODE'],
    z = df['Positive'],
    #customdata=df['Positive'],
    #hover_data=df['Positive'] ,
    #hovertext=''+sw,
    #z=df['Negative'],
    text = df['COUNTRY'],
    colorscale = 'Greens',
    autocolorscale=False,
    reversescale=False,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    #colorbar_tickprefix = 'Number of tweets',
    colorbar_title = 'Positive sentiment',
    ))


    fig2 = go.Figure(data=go.Choropleth(
    locations = df['CODE'],
    z = df['Neutral'],
    #customdata=df['Positive'],
    #hover_data=df['Positive'] ,
    #hovertext=''+sw,
    #z=df['Negative'],
    text = df['COUNTRY'],
    colorscale = 'Blues',
    autocolorscale=False,
    reversescale=False,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    #colorbar_tickprefix = 'Number of tweets',
    colorbar_title = 'Neutral sentiment',
    ))

    fig3 = go.Figure(data=go.Choropleth(
    locations = df['CODE'],
    z = df['Negative'],
    #customdata=df['Positive'],
    #hover_data=df['Positive'] ,
    #hovertext=''+sw,
    #z=df['Negative'],
    text = df['COUNTRY'],
    colorscale = 'Reds',
    autocolorscale=False,
    reversescale=False,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    #colorbar_tickprefix = 'Number of tweets',
    colorbar_title = 'Negative sentiment',
    ))

    fig1.update_layout(
        title_text=keyword,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
     #=============================================================================
         ),
         annotations = [dict(
             x=0.55,
             y=0.1,
             xref='paper',
             yref='paper',
             text='Positive Sentiment Analysis',
             showarrow = False
         )] )

    fig2.update_layout(
        title_text=keyword,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
     #=============================================================================
         ),
         annotations = [dict(
             x=0.55,
             y=0.1,
             xref='paper',
             yref='paper',
             text='Neutral Sentiment Analysis',
             showarrow = False
         )] )

    fig3.update_layout(
        title_text=keyword,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
     #=============================================================================
         ),
         annotations = [dict(
             x=0.55,
             y=0.1,
             xref='paper',
             yref='paper',
             text='Negative Sentiment Analysis',
             showarrow = False
         )] )


# =============================================================================
#     plot(fig1)
#     plot(fig2)
#     plot(fig3)
# =============================================================================
    fig1.show(block=False)
    fig2.show(block=False)
    fig3.show()

def get_map(tweetsp,tweetsn,tweetsnu,len_p,len_n,len_nu,df,sw):

    plt.figure(figsize=(13, 13))
    m = Basemap(projection='cyl', resolution='c')
    m.drawcountries(linewidth=1, linestyle='solid', color='grey', antialiased=1, ax=None, zorder=None)
    m.etopo(scale=0.7, alpha=0.7)
    pos = mpatches.Patch(color='green', label='Positive')
    neg = mpatches.Patch(color='red', label='Negative')
    neu = mpatches.Patch(color='blue', label='Neutral')

    xx=[]
    yy=[]
    print("POSITIVE PLOTS")
    for i in range(len_p):
        lat,lon=tweetsp['tweet'][i]['Coordinates']
        x,y=m(lat,lon)
        #xx.append(x)
        #yy.append(y)
        coordinates=[(x,y)]
        df=update_df(coordinates,df,'Positive')

        #print("x and y values",x,y)
        #print("Location",tweetsp['tweet'][i]['Location'])
        m.plot(lon, lat, marker= 'o', markersize=7, color='green', label = 'Positive')
        #plt.text(lon, lat, tweetsp['tweet'][i]['Location'], fontsize=7)

    print("NEGATIVE PLOTS")
    for i in range(len_n):
        lat,lon=tweetsn['tweet'][i]['Coordinates']
        x,y=m(lat,lon)
        #xx.append(x)
        #yy.append(y)
        coordinates=[(x,y)]
        df=update_df(coordinates,df,'Negative')

       # print("x and y values",x,y)
       # print("Location",tweetsn['tweet'][i]['Location'])
        m.plot(lon, lat, marker= 'o', markersize=7, color='red', label='Negative')
        #plt.text(lon, lat, tweetsn['tweet'][i]['Location'], fontsize=7)

    print("NEUTRAL PLOTS")
    for i in range(len_nu):
        lat,lon=tweetsnu['tweet'][i]['Coordinates']
        x,y=m(lat,lon)
        #xx.append(x)
       # yy.append(y)
        coordinates=[(x,y)]
        df=update_df(coordinates,df,'Neutral')

       # print("x and y values",x,y)
       # print("Location",tweetsnu['tweet'][i]['Location'])
        m.plot(lon, lat, marker= 'o', markersize=7, color='blue', label='Neutral')
        #plt.text(lon, lat, tweetsnu['tweet'][i]['Location'], fontsize=7)
    plt.legend(handles=[pos,neg,neu], loc=3)
    plt.show(block=False)
    Choroplet(df,sw)

def bargraph(pos,neg,neu,title):

    labels = ['Positive','Negative','Neutral']
    algo1 = pos
    algo2 = neg
    algo3 = neu
    x = np.arange(len(labels))  # the label locations
    width = 5  # the width of the bars
    fig, ax = plt.subplots()
    bar1 = ax.bar(0 , algo1, width, label='Positive')
    bar2 = ax.bar(5, algo2, width, label='Negative')
    bar3 = ax.bar(10, algo3, width, label='Neutral')
    ax.set_ylabel('Percentage')
    ax.set_title(title)
    ax.set_xticks([width*x1 for x1 in x])
    ax.set_xticklabels(labels)
    ax.legend()

    def bar_value(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10)

    bar_value(bar1)
    bar_value(bar2)
    bar_value(bar3)
    fig.tight_layout()

    plt.show(block=False)

def main(searchWord):
    #csv file
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
    df=pd.DataFrame(df)
    del df['GDP (BILLIONS)']
    df['Positive']=0
    df['Negative']=0
    df['Neutral']=0


    api = TwitterClient()
    print("Query word is ", searchWord)
    tweets=[]
    tweetsunknown=[]
    overall=[]
    counter =0
    for i in range(10):
        counter=counter+1
        print("Counter ",counter)
        tweets1, tweetsunknown1,overall1= api.get_tweets(query = searchWord + " -filter:retweets", r="recent", l="en", count = N)
        time.sleep(30)
       # print("Each of 1 is getting this length",len(tweets1),len(tweetsunknown1),len(overall1))
        for tweet in tweets1:
            if tweet not in tweets:
                tweets.append(tweet)


        for tweet in tweetsunknown1:
            if tweet not in tweetsunknown:
                tweetsunknown.append(tweet)


        for tweet in overall1:
            if tweet not in overall:
                overall.append(tweet)
      #  print("Each of final length",len(tweets),len(tweetsunknown),len(overall))

    print("Number of known tweets",len(tweets))
    print("Number of unknown tweets",len(tweetsunknown))
    print("Number of Total tweets",len(overall))




    datap={}
    datan={}
    datanu={}
    datap['tweet']=[]
    datan['tweet']=[]
    datanu['tweet']=[]

    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    overall_ptweets=[otweet for otweet in overall if otweet['sentiment'] == 'positive']

    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    overall_ntweets=[otweet for otweet in overall if otweet['sentiment'] == 'negative']

    nutweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    overall_nutweets=[otweet for otweet in overall if otweet['sentiment'] == 'neutral']

    unknown_ptweets=[tweet for tweet in tweetsunknown if tweet['sentiment'] == 'positive']
    unknown_ntweets=[tweet for tweet in tweetsunknown if tweet['sentiment'] == 'negative']
    unknown_nutweets=[tweet for tweet in tweetsunknown if tweet['sentiment'] == 'neutral']
    try:
        print("Total TWEETS")
        o_pos=round((100*len(overall_ptweets)/len(overall)), 2)
        o_neg=round((100*len(overall_ntweets)/len(overall)), 2)
        o_neu=round((100*len(overall_nutweets)/len(overall)), 2)
        print("Positive tweets percentage: ",o_pos,"%")
        print("Negative tweets percentage: ",o_neg,"%")
        print("Neutral tweets percentage: ",o_neu,"%")
        bargraph(o_pos,o_neg,o_neu,'Sentiment Analysis of Overall Tweets')
        print("\n")

        print("LOCATION KNOWN")
        pos=round((100*len(ptweets)/len(tweets)), 2)
        neg=round((100*len(ntweets)/len(tweets)), 2)
        neu=round((100*len(nutweets)/len(tweets)), 2)
        print("Positive tweets percentage: ",pos,"%")
        print("Negative tweets percentage: ",neg,"%")
        print("Neutral tweets percentage: ",neu,"%")
        bargraph(pos,neg,neu,'Sentiment Analysis of Tweets(Location Known)')
        print("\n")

        print("LOCATION UNKNOWN")
        upos=round((100*len(unknown_ptweets)/len(tweetsunknown)), 2)
        uneg=round((100*len(unknown_ntweets)/len(tweetsunknown)), 2)
        uneu=round((100*len(unknown_nutweets)/len(tweetsunknown)), 2)
        print("Positive tweets percentage: ",upos,"%")
        print("Negative tweets percentage: ",uneg,"%")
        print("Neutral tweets percentage: ",uneu,"%")
        bargraph(upos, uneg, uneu,'Sentiment Analysis of Tweets(Location Unknown)')
        print("\n")

    except ZeroDivisionError:
        print("Positive tweets percentage: 0%")
        print("Negative tweets percentage: 0%")
        print("Neutral tweets percentage: 0%")

    for tweet in ptweets:
        datap['tweet'].append({'text':tweet['text'], 'Location':tweet['geo'],'Coordinates':tweet['geo_co']})

    for tweet in ntweets:
        datan['tweet'].append({'text':tweet['text'], 'Location':tweet['geo'],'Coordinates':tweet['geo_co']})

    for tweet in nutweets:
        datanu['tweet'].append({'text':tweet['text'], 'Location':tweet['geo'],'Coordinates':tweet['geo_co']})

    len_p=len(ptweets)
    len_n=len(ntweets)
    len_nu=len(nutweets)

    get_map(datap,datan,datanu,len_p,len_n,len_nu,df,searchWord)

if __name__ == "__main__":
    main()
