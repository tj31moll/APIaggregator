import praw
import requests
from instaloader import Instaloader
import json
import datetime

reddit = praw.Reddit(client_id='CLIENT_ID', client_secret='CLIENT_SECRET',
                     username='USERNAME', password='PASSWORD', user_agent='USERAGENT')

loader = Instaloader()

reddit_saves = []
instagram_saves = []
tiktok_saves = []

# Retrieve Reddit saves
for post in reddit.user.me().saved(limit=None):
    if isinstance(post, praw.models.Submission):
        reddit_saves.append({'title': post.title, 'url': post.url, 'date': datetime.datetime.fromtimestamp(post.created_utc)})
    elif isinstance(post, praw.models.Comment):
        reddit_saves.append({'title': post.body, 'url': post.permalink, 'date': datetime.datetime.fromtimestamp(post.created_utc)})
        
# Retrieve Instagram saves
loader.load_session_from_file("USERNAME")
saved_posts = loader.load_saved_posts()
for post in saved_posts:
    if isinstance(post, instaloader.Post):
        instagram_saves.append({'title': post.caption, 'url': f'https://www.instagram.com/p/{post.shortcode}/', 'date': post.date_utc})

# Retrieve TikTok saves
cookies = {'Tiktok-Tracker-Token': 'TOKEN'}
response = requests.get('https://api.tiktok.com/share/item/list?secUid=&count=30', cookies=cookies)
data = json.loads(response.text)
for item in data['body']['itemListData']:
    tiktok_saves.append({'title': item['desc'], 'url': item['shareUrl'], 'date': datetime.datetime.fromtimestamp(item['createTime'])})

# Aggregate saved posts
online_data = {'Reddit': reddit_saves, 'Instagram': instagram_saves, 'TikTok': tiktok_saves}

# CherryPy web server
import cherrypy

class Root:
    @cherrypy.expose
    def index(self):
        return cherrypy.engine.publish('render', 'index.html', online_data=json.dumps(online_data)).pop()

cherrypy.tree.mount(Root())
cherrypy.engine.subscribe('render', jinja2processor)
cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
cherrypy.engine.start()
