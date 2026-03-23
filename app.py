from flask import Flask, Response, jsonify, render_template_string, request
import base64
import json
import os
import random
import time

import requests

app = Flask(__name__)

cookie_str = os.getenv('QQMUSIC_COOKIE', '').strip()

INDEX_TEMPLATE = """
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QQ 音乐解析</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 24px;
            background: #f5f7fb;
            color: #1f2937;
        }
        .container {
            max-width: 860px;
            margin: 0 auto;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
            padding: 24px;
        }
        .notice {
            padding: 14px 16px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .notice.warning {
            background: #fff7ed;
            color: #c2410c;
            border: 1px solid #fdba74;
        }
        .notice.ok {
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #6ee7b7;
        }
        form {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        input {
            flex: 1 1 480px;
            padding: 12px 14px;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            font-size: 16px;
        }
        button {
            border: none;
            background: #2563eb;
            color: #fff;
            padding: 12px 18px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
        }
        pre {
            background: #0f172a;
            color: #e2e8f0;
            padding: 16px;
            border-radius: 12px;
            overflow: auto;
            min-height: 160px;
        }
        .tip {
            color: #4b5563;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>QQ 音乐解析服务</h1>
        <div class="notice {{ notice_class }}">{{ notice_message }}</div>
        <p class="tip">输入 QQ 音乐歌曲链接后可直接调用当前服务的 <code>/song</code> 接口进行测试。</p>
        <form id="song-form">
            <input id="song-url" type="url" placeholder="请输入 QQ 音乐歌曲链接" required>
            <button type="submit">开始解析</button>
        </form>
        <pre id="result">等待请求结果...</pre>
    </div>
    <script>
        const form = document.getElementById('song-form');
        const result = document.getElementById('result');
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const songUrl = document.getElementById('song-url').value.trim();
            result.textContent = '请求中...';
            try {
                const response = await fetch(`/song?url=${encodeURIComponent(songUrl)}`);
                const data = await response.json();
                result.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                result.textContent = `请求失败: ${error}`;
            }
        });
    </script>
</body>
</html>
"""


class QQMusic:
    def __init__(self):
        self.base_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg'
        self.guid = '10000'
        self.uin = '0'
        self.cookies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self._headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://y.qq.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        self.mac_headers = {
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'referer': 'https://i.y.qq.com',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'content-type': 'application/json',
            'accept': 'application/json',
            'Host': 'u.y.qq.com',
            'Connection': 'Keep-Alive'
        }
        self.file_config = {
            '128': {'s': 'M500', 'e': '.mp3', 'bitrate': '128kbps'},
            '320': {'s': 'M800', 'e': '.mp3', 'bitrate': '320kbps'},
            'flac': {'s': 'F000', 'e': '.flac', 'bitrate': 'FLAC'},
            'master': {'s': 'AI00', 'e': '.flac', 'bitrate': 'Master'},
            'atmos_2': {'s': 'Q000', 'e': '.flac', 'bitrate': 'Atmos 2'},
            'atmos_51': {'s': 'Q001', 'e': '.flac', 'bitrate': 'Atmos 5.1'},
            'ogg_640': {'s': 'O801', 'e': '.ogg', 'bitrate': '640kbps'},
            'ogg_320': {'s': 'O800', 'e': '.ogg', 'bitrate': '320kbps'},
            'ogg_192': {'s': 'O600', 'e': '.ogg', 'bitrate': '192kbps'},
            'ogg_96': {'s': 'O400', 'e': '.ogg', 'bitrate': '96kbps'},
            'aac_192': {'s': 'C600', 'e': '.m4a', 'bitrate': '192kbps'},
            'aac_96': {'s': 'C400', 'e': '.m4a', 'bitrate': '96kbps'},
            'aac_48': {'s': 'C200', 'e': '.m4a', 'bitrate': '48kbps'}
        }
        self.song_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg'
        self.lyric_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'

    def set_cookies(self, cookie_str):
        cookies = {}
        for cookie in cookie_str.split(';'):
            cookie = cookie.strip()
            if not cookie:
                continue
            if '=' not in cookie:
                raise ValueError('Cookie 项缺少等号分隔符')
            key, value = cookie.split('=', 1)
            key = key.strip()
            value = value.strip()
            if not key:
                raise ValueError('Cookie 键不能为空')
            cookies[key] = value

        if not cookies:
            raise ValueError('未解析到有效 Cookie 项')
        self.cookies = cookies

    def ids(self, url):
        """
        从不同类型的 URL 中提取歌曲 ID，支持重定向和 /songDetail/ URL 形式
        """
        if 'c6.y.qq.com' in url:
            response = requests.get(url, allow_redirects=False)
            url = response.headers.get('Location')

        if 'y.qq.com' in url:
            if '/songDetail/' in url:
                index = url.find('/songDetail/') + len('/songDetail/')
                song_id = url[index:].split('/')[0]
                return song_id

            if 'id=' in url:
                index = url.find('id=') + 3
                song_id = url[index:].split('&')[0]
                return song_id

        return None

    def get_music_url(self, songmid, file_type='flac'):
        """
        获取音乐播放URL
        """
        if file_type not in self.file_config:
            raise ValueError("Invalid file_type. Choose from 'm4a', '128', '320', 'flac', 'ape', 'dts")

        file_info = self.file_config[file_type]
        file = f"{file_info['s']}{songmid}{songmid}{file_info['e']}"

        req_data = {
            'req_1': {
                'module': 'vkey.GetVkeyServer',
                'method': 'CgiGetVkey',
                'param': {
                    'filename': [file],
                    'guid': self.guid,
                    'songmid': [songmid],
                    'songtype': [0],
                    'uin': self.uin,
                    'loginflag': 1,
                    'platform': '20',
                },
            },
            'loginUin': self.uin,
            'comm': {
                'uin': self.uin,
                'format': 'json',
                'ct': 24,
                'cv': 0,
            },
        }

        response = requests.post(self.base_url, json=req_data, cookies=self.cookies, headers=self.headers)
        data = response.json()
        purl = data['req_1']['data']['midurlinfo'][0]['purl']
        if purl == '':
            return None

        url = data['req_1']['data']['sip'][1] + purl
        prefix = purl[:4]
        bitrate = next((info['bitrate'] for key, info in self.file_config.items() if info['s'] == prefix), '')

        return {'url': url.replace('http://', 'https://'), 'bitrate': bitrate}

    def get_music_song(self, mid, sid):
        """
        获取歌曲信息
        """
        if sid != 0:
            req_data = {
                'songid': sid,
                'platform': 'yqq',
                'format': 'json',
            }
        else:
            req_data = {
                'songmid': mid,
                'platform': 'yqq',
                'format': 'json',
            }

        response = requests.post(self.song_url, data=req_data, cookies=self.cookies, headers=self.headers)
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            song_info = data['data'][0]
            album_info = song_info.get('album', {})
            singers = song_info.get('singer', [])
            singer_names = ', '.join([singer.get('name', 'Unknown') for singer in singers])
            album_mid = album_info.get('mid')
            img_url = f'https://y.qq.com/music/photo_new/T002R800x800M000{album_mid}.jpg?max_age=2592000' if album_mid else 'https://axidiqolol53.objectstorage.ap-seoul-1.oci.customer-oci.com/n/axidiqolol53/b/lusic/o/resources/cover.jpg'

            return {
                'name': song_info.get('name', 'Unknown'),
                'album': album_info.get('name', 'Unknown'),
                'singer': singer_names,
                'pic': img_url,
                'mid': song_info.get('mid', mid),
                'id': song_info.get('id', sid)
            }
        return {'msg': '信息获取错误/歌曲不存在'}

    def get_music_lyric(self, mid):
        """
        获取歌曲歌词 - 旧版歌词接口
        """
        url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
        params = {
            '_': str(int(time.time())),
            'format': 'json',
            'loginUin': ''.join(random.sample('1234567890', 10)),
            'songmid': mid
        }

        try:
            response = requests.get(url, headers=self._headers, cookies=self.cookies, params=params)
            response.raise_for_status()
            data = response.json()
            print(data)
            lyric = data.get('lyric', '')
            if lyric:
                return base64.b64decode(lyric).decode('utf-8')
            return '未找到歌词'

        except requests.RequestException as e:
            return f'请求错误: {e}'
        except Exception as e:
            return f'解码错误: {e}'

    def get_music_lyric_new(self, songid):
        """从QQ音乐电脑客户端接口获取歌词

        参数:
            songID (str): 音乐id

        返回值:
            dict: 通过['lyric']和['trans']来获取base64后的歌词内容

            其中 lyric为原文歌词 trans为翻译歌词
        """
        payload = {
            'music.musichallSong.PlayLyricInfo.GetPlayLyricInfo': {
                'module': 'music.musichallSong.PlayLyricInfo',
                'method': 'GetPlayLyricInfo',
                'param': {
                    'trans_t': 0,
                    'roma_t': 0,
                    'crypt': 0,
                    'lrc_t': 0,
                    'interval': 208,
                    'trans': 1,
                    'ct': 6,
                    'singerName': '',
                    'type': 0,
                    'qrc_t': 0,
                    'cv': 80600,
                    'roma': 1,
                    'songID': songid,
                    'qrc': 0,
                    'albumName': '',
                    'songName': '',
                },
            },
            'comm': {
                'wid': '',
                'tmeAppID': 'qqmusic',
                'authst': '',
                'uid': '',
                'gray': '0',
                'OpenUDID': '',
                'ct': '6',
                'patch': '2',
                'psrf_qqopenid': '',
                'sid': '',
                'psrf_access_token_expiresAt': '',
                'cv': '80600',
                'gzip': '0',
                'qq': '',
                'nettype': '2',
                'psrf_qqunionid': '',
                'psrf_qqaccess_token': '',
                'tmeLoginType': '2',
            },
        }

        try:
            res = requests.post(self.base_url, json=payload, cookies=self.cookies, headers=self.headers)
            res.raise_for_status()
            d = res.json()
            lyric_data = d['music.musichallSong.PlayLyricInfo.GetPlayLyricInfo']['data']
            if 'lyric' in lyric_data and lyric_data['lyric']:
                lyric = base64.b64decode(lyric_data['lyric']).decode('utf-8')
                tylyric = base64.b64decode(lyric_data['trans']).decode('utf-8')
            else:
                lyric = ''
                tylyric = ''
            return {'lyric': lyric, 'tylyric': tylyric}

        except Exception as e:
            print(f'Error fetching lyrics: {e}')
            return {'error': '无法获取歌词'}


@app.route('/', methods=['GET'])
def index():
    cookie_configured = bool(cookie_str)
    notice_message = (
        '当前服务未配置 QQ 音乐 Cookie，解析可能不可用'
        if not cookie_configured
        else '当前服务已配置 QQ 音乐 Cookie，可以在此页面直接测试解析能力'
    )
    notice_class = 'warning' if not cookie_configured else 'ok'
    return render_template_string(
        INDEX_TEMPLATE,
        notice_message=notice_message,
        notice_class=notice_class,
    )


@app.route('/song', methods=['GET'])
def get_song():
    song_url = request.args.get('url')
    if not song_url:
        return jsonify({'error': 'url parameter is required'}), 400

    if not cookie_str:
        return jsonify({'error': '服务端未配置 QQMUSIC_COOKIE'}), 503

    qqmusic = QQMusic()
    try:
        qqmusic.set_cookies(cookie_str)
    except ValueError as exc:
        return jsonify({'error': 'QQMUSIC_COOKIE 配置无效', 'detail': str(exc)}), 400

    songmid = qqmusic.ids(song_url)
    file_types = ['aac_48', 'aac_96', 'aac_192', 'ogg_96', 'ogg_192', 'ogg_320', 'ogg_640', 'atmos_51', 'atmos_2', 'master', 'flac', '320', '128']
    results = {}

    try:
        sid = int(songmid)
        mid = 0
    except (TypeError, ValueError):
        sid = 0
        mid = songmid

    info = qqmusic.get_music_song(mid, sid)
    for file_type in file_types:
        result = qqmusic.get_music_url(info['mid'], file_type)
        if result:
            results[file_type] = result
        time.sleep(0.1)
    lyric = qqmusic.get_music_lyric_new(info['id'])

    output = {
        'song': info,
        'lyric': lyric,
        'music_urls': results,
    }
    json_data = json.dumps(output)
    return Response(json_data, content_type='application/json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5122)
