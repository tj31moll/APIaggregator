import praw
import requests
from instaloader import Instaloader
import json
import datetime
import cherrypy

# CherryPy web server configuration
cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})

# Retrieve Reddit saves
reddit = praw.Reddit(client_id='CLIENT_ID', client_secret='CLIENT_SECRET',
                     username='USERNAME', password='PASSWORD', user_agent='USERAGENT')
reddit_saves = []
for post in reddit.user.me().saved(limit=None):
    if isinstance(post, praw.models.Submission):
        reddit_saves.append({'title': post.title, 'url': post.url, 'date': datetime.datetime.fromtimestamp(post.created_utc)})
    elif isinstance(post, praw.models.Comment):
        reddit_saves.append({'title': post.body, 'url': post.permalink, 'date': datetime.datetime.fromtimestamp(post.created_utc)})

# Retrieve Instagram saves
loader = Instaloader()
loader.load_session_from_file("USERNAME")
instagram_saves = []
saved_posts = loader.load_saved_posts()
for post in saved_posts:
    if isinstance(post, instaloader.Post):
        instagram_saves.append({'title': post.caption, 'url': f'https://www.instagram.com/p/{post.shortcode}/', 'date': post.date_utc})

# Retrieve TikTok saves
cookies = {'Tiktok-Tracker-Token': 'TOKEN'}
response = requests.get('https://api.tiktok.com/share/item/list?secUid=&count=30', cookies=cookies)
data = json.loads(response.text)
tiktok_saves = []
for item in data['body']['itemListData']:
    tiktok_saves.append({'title': item['desc'], 'url': item['shareUrl'], 'date': datetime.datetime.fromtimestamp(item['createTime'])})

# Aggregate saved posts
online_data = {'Reddit': reddit_saves, 'Instagram': instagram_saves, 'TikTok': tiktok_saves}

# CherryPy web server
class Root:
    @cherrypy.expose
    def index(self):
        return cherrypy.engine.publish('render', 'index.html', online_data=json.dumps(online_data)).pop()

# Jinja2 template rendering engine
import jinja2
def jinja2processor(template, **kwargs):
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'))
    template = jinja_env.get_template(template)
    return template.render(**kwargs)

# Mount the application to the root of the web server
cherrypy.tree.mount(Root())

# Subscribe to the "render" event and pass it the jinja2processor function
cherrypy.engine.subscribe('render', jinja2processor)

# Start the web server
cherrypy.engine.start()
