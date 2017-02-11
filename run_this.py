import praw
from feedgen.feed import FeedGenerator
import pandas as pd
import html
import os
import datetime
import pytz

subreddit_list =     ['orgmode', 'i3wm']
subreddit_top_type = ['week',    'week']
cache_path = './full_data.pkl'
feed_url = 'https://example.com/atom.xml'
feed_path = './atom.xml'

reddit = praw.Reddit(client_id='',
                     client_secret='',
                     password='',
                     user_agent='testscript by /u/fakebot3',
                     username='')

urls = []
titles = []
selftexts = []
times = []

for this_subreddit, this_type in zip(subreddit_list, subreddit_top_type):
    for submission in reddit.subreddit(this_subreddit).top(this_type):
        urls.append(submission.url)
        titles.append(submission.title)
        selftexts.append(submission.selftext)
        times.append(submission.created_utc)


new_data = pd.DataFrame({
    'url' : urls,
    'title' : titles,
    'selftext' : selftexts,
    'utc_time': times
})
new_data = new_data.drop_duplicates()

if os.path.isfile(cache_path):
    old_data = pd.read_pickle(cache_path)
    full_data = old_data.append(new_data)
    full_data = full_data.drop_duplicates()
else:
    full_data = new_data

full_data = full_data.sort_values(by='utc_time',ascending=False)
full_data = full_data.head(n=100)

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

for url, title, selftext, timestamp in zip(full_data.url, full_data.title, full_data.selftext, full_data.utc_time):
    fe = fg.add_entry()
    fe.id(url)
    fe.title(title)
    fe.content(content=selftext, type = 'html')
    fe.published(tz.localize(datetime.datetime.fromtimestamp(timestamp)))
    fe.updated(tz.localize(datetime.datetime.fromtimestamp(timestamp)))

fg.atom_file(feed_path)


full_data.to_pickle(cache_path)

print('ran successfully')

