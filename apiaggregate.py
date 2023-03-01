import cherrypy
import json
import os
import requests

class OnlineFootprint(object):

    @cherrypy.expose
    def index(self):
        # Define the APIs you want to use
        reddit_api = 'https://oauth.reddit.com/user/{username}/saved'
        instagram_api = 'https://www.instagram.com/{username}/saved/?__a=1'
        tiktok_api = 'https://www.tiktok.com/share/item/list?secUid=ABCDEFG&userId=123456789&count=10'

        # Define your API keys
        reddit_key = 'your_reddit_api_key'
        instagram_key = 'your_instagram_api_key'
        tiktok_key = 'your_tiktok_api_key'

        # Define your usernames for each platform
        reddit_username = 'your_reddit_username'
        instagram_username = 'your_instagram_username'
        tiktok_username = 'your_tiktok_username'

        # Access the APIs and collect data
        reddit_data = requests.get(reddit_api.format(username=reddit_username), headers={'Authorization': f'Bearer {reddit_key}'}).json()
        instagram_data = requests.get(instagram_api.format(username=instagram_username), headers={'Authorization': f'Bearer {instagram_key}'}).json()
        tiktok_data = requests.get(tiktok_api, headers={'Authorization': f'Bearer {tiktok_key}'}, params={'userId': '123456789'}).json()

        # Select only saved items on each platform
        reddit_saved_items = [item['data'] for item in reddit_data['data']['children'] if item['kind'] == 't3']
        instagram_saved_items = [item['node'] for item in instagram_data['graphql']['user']['edge_saved_media']['edges']]
        tiktok_saved_items = [item['itemInfos'] for item in tiktok_data['body']['itemList'] if item['itemType'] == 1]

        # Aggregate the data
        aggregated_data = {
            'reddit': reddit_saved_items,
            'instagram': instagram_saved_items,
            'tiktok': tiktok_saved_items
        }

        # Return the data as JSON
        return json.dumps(aggregated_data)

if __name__ == '__main__':
    # Set up CherryPy server
    config = {
        '/': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')]
        }
    }
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000))
    })
    cherrypy.quickstart(OnlineFootprint(), '/', config=config)
