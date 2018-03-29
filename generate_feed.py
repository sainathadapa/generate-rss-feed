import json
import praw                             # to connect to reddit
from feedgen.feed import FeedGenerator  # to generate the feed
from hackernews import HackerNews       # to get entries from hackernews
import feedparser                       # to parse feeds
import numpy as np
import pandas as pd
from os.path import isfile
from datetime import datetime
from tzlocal import get_localzone
import re
from sys import argv

if len(argv) < 2:
    raise ValueError("Config file is not specified!")

with open(argv[1]) as json_data:
    config = json.load(json_data)

urls = []
titles = []
selftexts = []
times = []

# Go through subreddits list and get top/stickied posts
if len(config['subreddits']) > 0:

    reddit_credentials = config['reddit_credentials']

    reddit = praw.Reddit(client_id=reddit_credentials['client_id'],
                         client_secret=reddit_credentials['client_secret'],
                         password=reddit_credentials['password'],
                         user_agent='feed generator',
                         username=reddit_credentials['username'])

    subreddits = config['subreddits']
    min_comments = config['reddit_min_comments']
    num_posts = config['reddit_num_posts']

    # Get top posts
    for subreddit in subreddits:
        for submission in reddit.subreddit(subreddit).top(subreddits[subreddit], limit=num_posts):
            if submission.num_comments > min_comments:
                urls.append('https://www.reddit.com' + submission.permalink)
                titles.append(subreddit + ' - ' + submission.title)
                selftexts.append(submission.selftext)

    # Get stickied posts
    for subreddit in subreddits:
        for submission in reddit.subreddit(subreddit).hot(limit=10):
            if submission.stickied and submission.num_comments > min_comments:
                urls.append('https://www.reddit.com' + submission.permalink)
                titles.append(subreddit + ' - ' + submission.title)
                selftexts.append(submission.selftext)

# Get feed entries
if len(config['feed_sources']) > 0:
    feed_links = config['feed_sources']
    pattern = re.compile("=(.*)$")
    for one_feed in feed_links:
        one_feed_parsed = feedparser.parse(one_feed)
        for one_entry in one_feed_parsed.entries:
            urls.append(pattern.search(one_entry.id).group(1))
            titles.append(one_entry.title)
            selftexts.append(one_entry.description)

# Going through the top hacker news items
if config['add_hn_entries']:
    hn = HackerNews()
    num_posts = config['hn_num_posts']
    for story_id in hn.top_stories(limit=num_posts):
        one_item = hn.get_item(story_id)
        if one_item.item_type in ['poll', 'story'] and one_item.descendants >= 10:
            urls.append('https://news.ycombinator.com/item?id=' + str(one_item.item_id))
            titles.append(one_item.title)
            selftexts.append('Article from HackerNews')


new_data = pd.DataFrame({
    'url':      urls,
    'title':    titles,
    'selftext': selftexts,
    'time':     datetime.now()
})

new_data = new_data.drop_duplicates(subset='url', keep='first')

# Load cache and append new data to old
cache_path = config['cache_path']
if isfile(cache_path):
    old_data = pd.read_pickle(cache_path)
    new_urls = np.setdiff1d(new_data.url.values, old_data.url.values)
    new_data = new_data[new_data['url'].isin(new_urls)]
    full_data = old_data.append(new_data)
else:
    full_data = new_data

# Keep only the latest n entries for the feed
full_data = full_data.sort_values(by='time', ascending=False)
for_feed = full_data.head(n=config['max_items_feed'])

# Generate feed
fg = FeedGenerator()
fg.id(config['save_path'])
fg.title(config['feed_name'])
fg.link(href=config['feed_url'], rel='self')
fg.language('en')

tz = get_localzone()

for url, title, selftext, timestamp in zip(for_feed.url, for_feed.title, for_feed.selftext, for_feed.time):
    fe = fg.add_entry()
    fe.id(url)
    fe.link({"href": url})
    fe.title(title)
    fe.content(content=selftext, type='html')
    fe.published(tz.localize(timestamp))
    fe.updated(tz.localize(timestamp))

# Save the feed
fg.atom_file(config['save_path'])

# Cache the data
full_data.to_pickle(config['cache_path'])

print('ran successfully at ' + str(datetime.now()))
