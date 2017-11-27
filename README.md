The python script in this repository generates a Atom feed with
- Top posts from Reddit
- Top posts from HackerNews
- Posts from other RSS/Atom feeds

--------

Reasons for writing this script:
1. Want to use Feedly as a single point for browsing through 'interesting' posts
2. Do not want to look at posts in Reddit/HackerNews which have zero comments
3. Do not want to look at posts which I have already seen (This happens with Google News feeds. If a particular topic does not have new news stories frequently, I keep seeing the same new stories again and again).

Directly adding Sub-Reddits, HackerNews or Google News in Feedly, does not solve the issue of not wanting to see the zero comments posts, or repeated posts. Hence wrote a simple script to achieve my goals.

---------

Instructions:
1. Install the following python modules:
   - praw
   - feedgen
   - hackernews-python
   - numpy
   - pandas
   - tzlocal
2. Edit the config file (Description of the config file below)
3. Run the script by invoking the command `python3 generate_feed.py config.json`
4. Run the script periodically, by adding to cron

--------

Config file description:
- `subreddits` : Specify the list of subreddits from which to gather the posts. Each element here is a key-value paid, with key being the subreddit name, and the value being the time filter that needs to be used (all, day, hour, month, week, year).
- `reddit_credentials`: Specify the reddit access credentials. Look [here](https://praw.readthedocs.io/en/latest/getting_started/authentication.html) to know how to acquire access codes.
- `reddit_min_comments`: Only add posts with the number of comments greater than this value.
- `reddit_num_posts`: Number of posts to gather from each subreddit
- `feed_sources`: Specify RSS feed urls from which to gather posts from
- `add_hn_entries`: true if posts from HackerNews need to be acquired
- `hn_num_posts`: Only add posts with the number of comments greater than this value
- `max_items_feed`: Maximum number of items in the generated feed
- `cache_path`: Location where the cached data can be stored
- `feed_url`: URL to the location where the generated feed will be published
- `save_path`: Location where the generated feed file needs to be saved
