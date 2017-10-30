import tweepy
import time
import logging
import pickle
import random
import os

class Bot:
    def __init__(self,
                 twitter_api,
                 tweets_per_hour = .125):
        self._twitter_api = twitter_api
        self._logger = logging.getLogger(__name__)
        
        # Load Transition Matricies
        self.mc_dict = pickle.load(open('basic_note_dict.pkl', 'rb'))
        self.nm_dict = pickle.load(open('basic_name_dict.pkl', 'rb'))

        #Calculate sleep timer
        self.sleep_timer = int(60*60/tweets_per_hour)

    def _create_tweet(self):
        tweet = ""
        while tweet == "" or len(tweet) > 140:
            # Create Name
            new_name = []
            name1 = "STARTSTART"

            running = True
            while running:
                name1 = random.choice(self.nm_dict[name1])
                if name1 == 'ENDEND':
                    running = False
                else:
                    new_name.append(name1)

            # Create Note
            new_note = []
            note1 = "STARTSTART"
            note2 = "BEGINBEGIN"

            running = True
            while running:
                note1, note2 = note2, random.choice(self.mc_dict[(note1, note2)])
                if note2 == 'ENDEND':
                    running = False
                else:
                    new_note.append(note2)

            name = ' '.join(new_name)
            note = ' '.join(new_note)
            tweet = name + ': ' + note 
            
        return tweet

    def run(self):
        while True:
            try:
                tweet = self._create_tweet()
                self._twitter_api.tweet(tweet)
            except Exception as e:
                self._logger.error(e, exc_info=True)
                self._twitter_api.disconnect()
            time.sleep(self.sleep_timer) #Every 8 hours

class Twitter_Api():
    def __init__(self, consumer_key, consumer_secret, access_key, access_secret):
        self._logger = logging.getLogger(__name__)
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_key = access_key
        self._access_secret = access_secret
        self._authorization = None
        if consumer_key is None:
            self.tweet = lambda x : self._logger.info("Test tweet: " + x)
            self._login = lambda x : self._logger.debug("Test Login completed.")

    def _login(self):
        auth = tweepy.OAuthHandler(self._consumer_key, self._consumer_secret)
        auth.set_access_token(self._access_key, self._access_secret)
        self._authorization = auth

    def tweet(self, tweet):
        if self._authorization is None:
            self._login()
            pass
        api = tweepy.API(self._authorization)
        stat = api.update_status(tweet)
        self._logger.info("Tweeted: " + tweet)
        self._logger.info(stat)

    def disconnect(self):
        self._authorization = None

def main():
    # Configure Logger
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    consumer_key = os.environ['SOMM_TWEET_CONSUMER_KEY']
    consumer_secret = os.environ['SOMM_TWEET_CONSUMER_SECRET']
    access_key = os.environ['SOMM_TWEET_ACCESS_KEY']
    access_secret = os.environ['SOMM_TWEET_ACCESS_SECRET']

    twitter_api = Twitter_Api(consumer_key, consumer_secret, access_key, access_secret)
    bot = Bot(twitter_api)

    bot.run()

if __name__ == "__main__":
    main()