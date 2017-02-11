# import packages
import praw
from feedgen.feed import FeedGenerator
import pandas as pd
import html
import os
import datetime
import pytz
import feedparser
import re

# list of subreddits and the corresponding top page from which to take the entries from
subreddit_list =     ['orgmode', 'i3wm']
subreddit_top_type = ['week',    'week']

# list of feeds to gather additional entries from
feed_links = ['https://news.google.co.in/news?cf=all&hl=en&pz=1&ned=in&output=rss']

# path to location of the cache file
cache_path = './full_data.pkl'
# URL to where the generated feed from this script going to be hosted
feed_url = 'https://example.com/atom.xml'
# Location to where the generated feed is going to be saved
feed_path = './atom.xml'

# reddit api inputs
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     password='',
                     user_agent='testscript by /u/fakebot3',
                     username='')

urls = []
titles = []
selftexts = []
times = []

# going through each subreddit top list and getting the entries
for this_subreddit, this_type in zip(subreddit_list, subreddit_top_type):
    for submission in reddit.subreddit(this_subreddit).top(this_type):
        urls.append(submission.url)
        titles.append(submission.title)
        selftexts.append(submission.selftext)
        times.append(submission.created_utc)

# going through each feed and getting the entries
pattern = re.compile("=(.*)$")
for one_feed in feed_links:
    one_feed_parsed = feedparser.parse(one_feed)
    for one_entry in one_feed_parsed.entries:
        urls.append(pattern.search(one_entry.id).group(1))
        titles.append(one_entry.title)
        selftexts.append(one_entry.description)
        times.append(datetime.datetime.strptime(one_entry.published, '%a, %d %b %Y %H:%M:%S %Z').timestamp())

new_data = pd.DataFrame({
    'url' : urls,
    'title' : titles,
    'selftext' : selftexts,
    'utc_time': times
})

# loading cache and appending new data to that
if os.path.isfile(cache_path):
    old_data = pd.read_pickle(cache_path)
    full_data = old_data.append(new_data)
else:
    full_data = new_data

# sorting and droppping duplicates
# keeping only the latest 100 entries for the feed
full_data = full_data.sort_values(by='utc_time',ascending=False)
full_data = full_data.drop_duplicates(subset='url', keep='first')
for_feed  = full_data.head(n=100)

# generating feed
fg = FeedGenerator()
fg.id(feed_path)
fg.title('Custom feed from Reddit')
fg.author( {'name':'- -','email':'example@test.com'} )
fg.link( href='http://example.com', rel='alternate' )
fg.logo('http://ex.com/logo.jpg')
fg.subtitle('This is a cool feed!')
fg.link( href=feed_url, rel='self' )
fg.language('en')

tz = pytz.timezone('Asia/Kolkata')

for url, title, selftext, timestamp in zip(for_feed.url, for_feed.title, for_feed.selftext, for_feed.utc_time):
    fe = fg.add_entry()
    fe.id(url)
    fe.title(title)
    fe.content(content=selftext, type = 'html')
    fe.published(tz.localize(datetime.datetime.fromtimestamp(timestamp)))
    fe.updated(tz.localize(datetime.datetime.fromtimestamp(timestamp)))

# saving the feed
fg.atom_file(feed_path)

# saving the cache
full_data.to_pickle(cache_path)

print('ran successfully at ' + str(datetime.datetime.now()))


