import tweepy
from time import sleep
from credientials import *
from config import *
import datetime


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


print("Twitter bot which retweets, like tweets, follow users and post daily tweets")
print("Bot Settings")
print("Retweet Tweets :{message}".format(
    message="Enabled" if RETWEET else "Disabled"))
print("Like Tweets :{message}".format(
    message="Enabled" if LIKE else "Disabled"))
print("Follow users :{message}".format(
    message="Enabled" if FOLLOW else "Disabled"))
print("Every day tweets :{message}".format(
    message="Enabled" if EVERYDAY_TWEETS else "Disabled"))

for tweet in tweepy.Cursor(api.search, q=QUERY).items():
    try:
        print('\nTweet by: @' + tweet.user.screen_name)

        if RETWEET:
            tweet.retweet()
            print('Retweeted the tweet')

        # Favorite the tweet
        if LIKE:
            tweet.favorite()
            print('Favorited the tweet')

        # Follow the user who tweeted
        # check that bot is not already following the user
        if FOLLOW:
            if not tweet.user.following:
                tweet.user.follow()
                print('Followed the user')

        # Tweet your message daily
        # change the message according to your use.
        if EVERYDAY_TWEETS:
            if datetime.date.today().weekday() == 0:
                tweettopublish = 'Hi everyone, today is Monday.   #Monday '
            if datetime.date.today().weekday() == 1:
                tweettopublish = 'Enjoy your Tuesday.  #Tuesday'
            if datetime.date.today().weekday() == 2:
                tweettopublish = 'Third week of the Week. #Wednesday'
            if datetime.date.today().weekday() == 3:
                tweettopublish = 'Thursday. I cannot wait for the Weekend'
            if datetime.date.today().weekday() == 4:
                tweettopublish = 'Friday...Finally'
            if datetime.date.today().weekday() == 5:
                tweettopublish = 'Great it is Saturday #weekend #Saturday'
            if datetime.date.today().weekday() == 6:
                tweettopublish = 'Sunday morning...#Weekend #enjoy '
            api.update_status(tweettopublish)
            print(tweettopublish)

        sleep(SLEEP_TIME)

    except tweepy.TweepError as e:
        print(e.reason)

    except StopIteration:
        break
