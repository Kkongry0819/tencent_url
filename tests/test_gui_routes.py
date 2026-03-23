import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


class TestGuiRoutes:
    def test_homepage_route_returns_expected_gui_markers(self, client, monkeypatch):
        monkeypatch.setattr(app_module, 'cookie_str', 'uin=test; qm_keyst=test-key')

        response = client.get('/')

        assert response.status_code == 200
        body = response.get_data(as_text=True)
        assert 'song-form' in body
        assert 'song-url' in body
        assert 'parse-button' in body
        assert 'result-area' in body

    def test_song_route_requires_url_parameter(self, client, monkeypatch):
        monkeypatch.setattr(app_module, 'cookie_str', 'uin=test; qm_keyst=test-key')

        response = client.get('/song')

        assert response.status_code == 400
        assert response.get_json() == {
            'success': False,
            'error': 'url parameter is required',
        }

    def test_song_route_rejects_invalid_qq_music_url(self, client, monkeypatch):
        monkeypatch.setattr(app_module, 'cookie_str', 'uin=test; qm_keyst=test-key')

        response = client.get('/song', query_string={'url': 'https://example.com/not-qqmusic'})

        assert response.status_code == 400
        assert response.get_json() == {
            'success': False,
            'error': '解析失败，未识别到歌曲 ID',
        }

    def test_song_route_requires_cookie_configuration(self, client, monkeypatch):
        monkeypatch.setattr(app_module, 'cookie_str', '')

        response = client.get('/song', query_string={'url': 'https://y.qq.com/n/ryqq/songDetail/testmid'})

        assert response.status_code == 400
        assert response.get_json() == {
            'success': False,
            'error': '服务端未配置 QQMUSIC_COOKIE',
        }

    def test_song_route_returns_expected_success_structure(self, client, monkeypatch):
        monkeypatch.setattr(app_module, 'cookie_str', 'uin=test; qm_keyst=test-key')
        monkeypatch.setattr(app_module.QQMusic, 'ids', lambda self, url: 'test-song-mid')
        monkeypatch.setattr(
            app_module.QQMusic,
            'get_music_song',
            lambda self, mid, sid: {
                'name': 'Test Song',
                'album': 'Test Album',
                'singer': 'Test Artist',
                'pic': 'https://example.com/cover.jpg',
                'mid': 'test-song-mid',
                'id': 123456,
            },
        )
        monkeypatch.setattr(
            app_module.QQMusic,
            'get_music_url',
            lambda self, songmid, file_type: {
                'url': f'https://cdn.example.com/{file_type}',
                'bitrate': file_type,
            },
        )
        monkeypatch.setattr(
            app_module.QQMusic,
            'get_music_lyric_new',
            lambda self, songid: {
                'lyric': 'test lyric',
                'tylyric': 'translated lyric',
            },
        )
        monkeypatch.setattr(app_module.time, 'sleep', lambda *_args, **_kwargs: None)

        response = client.get('/song', query_string={'url': 'https://y.qq.com/n/ryqq/songDetail/test-song-mid'})

        assert response.status_code == 200
        payload = response.get_json()
        assert payload['success'] is True
        assert payload['song'] == {
            'name': 'Test Song',
            'album': 'Test Album',
            'singer': 'Test Artist',
            'pic': 'https://example.com/cover.jpg',
            'mid': 'test-song-mid',
            'id': 123456,
        }
        assert payload['lyric'] == {
            'lyric': 'test lyric',
            'tylyric': 'translated lyric',
        }
        assert 'music_urls' in payload
        assert payload['music_urls']['flac'] == {
            'url': 'https://cdn.example.com/flac',
            'bitrate': 'flac',
        }
        assert payload['music_urls']['128'] == {
            'url': 'https://cdn.example.com/128',
            'bitrate': '128',
        }
        assert sorted(payload.keys()) == ['lyric', 'music_urls', 'song', 'success']
