import os
import re
import sys
import collections
import time
import logging
import functools

import nltk
from bs4 import BeautifulSoup
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re

from piazza_api import Piazza

PostInfo = collections.namedtuple("PostInfo", ["username", "text", "id", "status"])

class SentimentAnalysis:

  def text_preprocessing(self, lines):
    # remove html tags
    soup = BeautifulSoup(str(lines), features="html.parser")
    lines = soup.get_text()
    lines = lines.lower()
    lines = re.sub('[\r\n]+', ' ', lines)
    lines = re.sub('[\xa0]+', '', lines)
    return lines

  def sentiment_label(self, ss):
    sentiments = ['positive', 'negative', 'neutral']
    postve = abs(ss['pos'])
    negtve = abs(ss['neg'])
    neutral = abs(ss['neu'])
    if postve > negtve and postve >= neutral:
      return sentiments[0]
    elif negtve > postve and negtve >= neutral:
      return sentiments[1]
    else:
      return sentiments[2]

  def analyze_post(self, post_text):
    sid = SentimentIntensityAnalyzer()
    post_text = self.text_preprocessing(post_text)
    ss = sid.polarity_scores(post_text)
    sentiment = self.sentiment_label(ss)
    return sentiment

class PiazzaBot:

  """ The number of posts to search backward in time """
  post_limit = 10

  def __init__(self, piazza, piazza_user, piazza_network):

    self.piazza = piazza
    self.user_profile = piazza_user
    self.network = piazza_network

  def create_piazza_bot(user_email, user_password, course_code):

    ''' Method to instantiate a Piazza Bot
    Parameters:
    user_email: Piazza user email to authenticate with
    user_password: Piazza password to authenticate with
    course_code: Class/Course code on Piazza '''

    piazza = Piazza()
    piazza.user_login(email = user_email, password = user_password)
    user_profile = piazza.get_user_profile()
    course_site = piazza.network(course_code)

    return PiazzaBot(piazza, user_profile, course_site)

  def get_posts(self):
    ''' Method to extract new posts from the course '''
    return self.network.iter_all_posts(limit=self.post_limit)

  def ignore_post(self, post):
    ''' Method defining posts to be ignored. For example, 
        if it's a post by the instructor or an announcement, we should ignore it '''

    if post['config'].get('is_announcement', 0) == 1: # To check for announcements
      return True
    
    if post['bucket_name'] == 'Pinned':  # Ignore pinned posts
      return True

    for i in post['children']:      # To check if we've already posted
      if i.get('uid', None) == self.user_profile['user_id']:
        logging.info("Saw post @{} but ignored it "
                      "because we've already commented on it.".format(
                       post['nr']
                    ))
        return True

    # return self.has_answer(post)

  def has_answer(post):
    ''' Returns whether the given post already has an answer '''
    return any(d for d in post["change_log"] if d["type"] == "i_answer")

  def get_post_details(self, post):
    ''' Method to extract relevant information from the post '''

    post_history = post['history'][0]
    print(post_history)
    post_text = post_history['content']
    post_status = post['status']

    if 'uid' in post_history:
      post_username_id = post_history['uid']
      post_username = self.network.get_users([post_username_id])
      post_username = post_username[0]['name']
    
    else:
      post_username_id = 'anon'
      post_username = 'anon'

    return PostInfo(username=post_username,
                    text=post_text,
                    id=post['nr'],
                    status=post_status)

  def handle_posts(self):
    ''' Handle all the posts fetched based on the limit specified '''

    for post in self.get_posts():
      if self.ignore_post(post):
        continue

      '''If the post is not ignored, we check the post content for its Sentiment. 
         Respond back if post is negative'''
      # post_info = self.get_post_details(post)

      post_history = post['history'][0]
      post_text = post_history['content']
      SA = SentimentAnalysis()
      sentiment = SA.analyze_post(post_text)

      sentiment_text = ''' 
                           Hey, it looks like you're facing a problem. I want to help you get answers you need, and we can definitely 
                           get that done by email.
                           If it's not the case, sorry about that! I'm just a bot; I can't read that well.
              
                       '''  
      if sentiment == 'negative':
        self.network.create_followup(post, sentiment_text)
      else:
        response = '(Testing AWS) The sentiment is labelled: ' + sentiment
        self.network.create_followup(post, response)
    
  def run_forever(self):
    while True:
      self.handle_posts()
      time.sleep(180)

def define_bot():
  config_sources = {
      'user_email': 'ps4118@nyu.edu',
      'user_password': 'hemlata7373',
      'course_code': 'k5wuy3imdq61hb'
  }

  return PiazzaBot.create_piazza_bot(config_sources['user_email'], 
                                      config_sources['user_password'],
                                      config_sources['course_code'])
def main():
  sentimentBot = define_bot()

  sentimentBot.run_forever()

if __name__ == '__main__':
  main()
