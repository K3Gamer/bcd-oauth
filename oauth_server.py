import requests, os
from flask import Flask, request, redirect

CLIENT_ID = '1482357066923249715'
CLIENT_SECRET = 'X34ep4Y9QQJlruF3mHU7B-l1WotIhpIi'
WEBHOOK_URL = 'https://discord.com/api/webhooks/1519207703245750485/M7rzeoLj-Xm-_TZpLKiZCybNkQ9fAb43Fwjf7AZx22tsERiasx-MCY3H3pkrtpPL1TPb'

RENDER_URL = os.environ.get('RENDER_URL', 'http://localhost:5050')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://reliable-gingersnap-a8b667.netlify.app')

REDIRECT_URI = RENDER_URL + '/callback'

app = Flask(__name__)

@app.route('/')
def home():
    return 'BCD OAuth2 Server is running.'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Missing code', 400

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    token_res = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    if not token_res.ok:
        return f'Token exchange failed: {token_res.text}', 400

    access_token = token_res.json()['access_token']

    user_res = requests.get('https://discord.com/api/users/@me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    if not user_res.ok:
        return f'User fetch failed: {user_res.text}', 400

    user = user_res.json()
    user_id = user['id']
    username = user['username']
    avatar_hash = user.get('avatar')
    avatar_url = f'https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png' if avatar_hash else 'https://cdn.discordapp.com/embed/avatars/0.png'

    embed = {
        'embeds': [{
            'title': '📥 Đăng ký gia nhập BCD (OAuth2)',
            'color': 0x5865F2,
            'fields': [
                {'name': 'Tên', 'value': username, 'inline': True},
                {'name': 'ID Discord', 'value': user_id, 'inline': True},
                {'name': 'Phương thức', 'value': 'OAuth2 Discord'}
            ],
            'thumbnail': {'url': avatar_url},
            'footer': {'text': 'Bới Cái Đào'},
            'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }]
    }

    requests.post(WEBHOOK_URL, json=embed)

    return redirect(f'{FRONTEND_URL}/?oauth2=success')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
