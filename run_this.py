# import packages
import praw
from feedgen.feed import FeedGenerator
import pandas as pd
import numpy as np
import html
import os
import datetime
import pytz
import feedparser
import re
from hackernews import HackerNews


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

# initializing
urls = []
titles = []
selftexts = []
times = []

# going through each subreddit top list and getting the entries
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     password='',
                     user_agent='testscript by /u/fakebot3',
                     username='')

for this_subreddit, this_type in zip(subreddit_list, subreddit_top_type):
    for submission in reddit.subreddit(this_subreddit).top(this_type, limit = 10):
        urls.append('https://www.reddit.com' + submission.permalink)
        titles.append(this_subreddit + ' - ' + submission.title)
        selftexts.append(submission.selftext)

# going through each feed and getting the entries
pattern = re.compile("=(.*)$")
for one_feed in feed_links:
    one_feed_parsed = feedparser.parse(one_feed)
    for one_entry in one_feed_parsed.entries:
        urls.append(pattern.search(one_entry.id).group(1))
        titles.append(one_entry.title)
        selftexts.append(one_entry.description)

# going through the top hacker news items
hn = HackerNews()

for story_id in hn.top_stories(limit=20):
    one_item = hn.get_item(story_id)
    urls.append('https://news.ycombinator.com/item?id=' + str(one_item.item_id))
    titles.append(one_item.title)
    selftexts.append('Article from HackerNews')
    

new_data = pd.DataFrame({
    'url' : urls,
    'title' : titles,
    'selftext' : selftexts,
    'time': datetime.datetime.now()
})

new_data = new_data.drop_duplicates(subset='url', keep='first')

# loading cache and appending new data to that
if os.path.isfile(cache_path):
    old_data = pd.read_pickle(cache_path)
    new_urls = np.setdiff1d(new_data.url.values, old_data.url.values)
    new_data = new_data[new_data['url'].isin(new_urls)]
    full_data = old_data.append(new_data)
else:
    full_data = new_data

# sorting
# keeping only the latest 200 entries for the feed
full_data = full_data.sort_values(by='time',ascending=False)
for_feed  = full_data.head(n=200)

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

for url, title, selftext, timestamp in zip(for_feed.url, for_feed.title, for_feed.selftext, for_feed.time):
    fe = fg.add_entry()
    fe.id(url)
    fe.link({"href": url})
    fe.title(title)
    fe.content(content=selftext, type = 'html')
    fe.published(tz.localize(timestamp))
    fe.updated(tz.localize(timestamp))

# saving the feed
fg.atom_file(feed_path)

# saving the cache
full_data.to_pickle(cache_path)

print('ran successfully at ' + str(datetime.datetime.now()))


