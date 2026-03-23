from unittest.mock import patch

import app as app_module


class TestAppRoutes:
    def test_index_shows_missing_cookie_notice(self):
        client = app_module.app.test_client()

        with patch.object(app_module, 'cookie_str', ''):
            response = client.get('/')

        assert response.status_code == 200
        assert '当前服务未配置 QQ 音乐 Cookie，解析可能不可用' in response.get_data(as_text=True)

    def test_song_returns_error_when_cookie_missing(self):
        client = app_module.app.test_client()

        with patch.object(app_module, 'cookie_str', ''):
            response = client.get('/song', query_string={'url': 'https://y.qq.com/n/ryqq/songDetail/123'})

        assert response.status_code == 503
        assert response.get_json() == {'error': '服务端未配置 QQMUSIC_COOKIE'}

    def test_song_returns_error_when_cookie_invalid(self):
        client = app_module.app.test_client()

        with patch.object(app_module, 'cookie_str', 'invalid-cookie-without-equals'):
            response = client.get('/song', query_string={'url': 'https://y.qq.com/n/ryqq/songDetail/123'})

        assert response.status_code == 400
        assert response.get_json()['error'] == 'QQMUSIC_COOKIE 配置无效'
