The python script in this repository generates a Atom feed with
- Top posts from Reddit
- Top posts from HackerNews
- Posts from other RSS/Atom feeds


Reasons for writing this script:
1. Want to use Feedly as a single point for browsing through 'interesting' posts
2. Do not want to look at posts in Reddit/HackerNews which have zero comments
3. Do not want to look at posts which I have already seen (This happens with Google News feeds. If a particular topic does not have new news stories frequently, I keep seeing the same new stories again and again).

Directly adding Sub-Reddits, HackerNews or Google News in Feedly, do not solve the issue of not wanting to see the zero comments posts, or repeated posts. Hence wrote a simple script to achieve my goals.


Instructions:
1. Install the following python modules:
   - praw
   - feedgen
   - hackernews-python
   - numpy
   - pandas
   - tzlocal
2. Edit the config file (Description of the config file below)
3. Run the script periodically, by adding to cron
