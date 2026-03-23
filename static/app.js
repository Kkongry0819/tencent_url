const form = document.getElementById('song-form');
const input = document.getElementById('song-url');
const submitButton = document.getElementById('submit-button');
const resultPanel = document.getElementById('result-panel');
const errorMessage = document.getElementById('error-message');
const qualityList = document.getElementById('quality-list');
const lyricContent = document.getElementById('lyric-content');
const songFields = {
  cover: document.getElementById('song-cover'),
  name: document.getElementById('song-name'),
  singer: document.getElementById('song-singer'),
  album: document.getElementById('song-album'),
  mid: document.getElementById('song-mid'),
  id: document.getElementById('song-id')
};

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = '';
  errorMessage.hidden = true;
}

function resetResults() {
  resultPanel.hidden = true;
  qualityList.innerHTML = '';
  lyricContent.textContent = '暂无歌词';
  songFields.cover.src = '';
  songFields.cover.alt = '歌曲封面';
  songFields.name.textContent = '-';
  songFields.singer.textContent = '-';
  songFields.album.textContent = '-';
  songFields.mid.textContent = '-';
  songFields.id.textContent = '-';
}

function renderSong(song) {
  songFields.cover.src = song.pic || '';
  songFields.cover.alt = song.name ? `${song.name} 封面` : '歌曲封面';
  songFields.name.textContent = song.name || '-';
  songFields.singer.textContent = song.singer || '-';
  songFields.album.textContent = song.album || '-';
  songFields.mid.textContent = song.mid || '-';
  songFields.id.textContent = song.id || '-';
}

function renderQualityLinks(musicUrls) {
  const entries = Object.entries(musicUrls || {});
  qualityList.innerHTML = '';

  if (!entries.length) {
    const item = document.createElement('li');
    item.textContent = '暂无可用音质链接';
    qualityList.appendChild(item);
    return false;
  }

  entries.forEach(([key, info]) => {
    const item = document.createElement('li');
    const label = document.createElement('div');
    label.innerHTML = `<strong>${info.bitrate || key}</strong><br><small>${key}</small>`;

    const link = document.createElement('a');
    link.href = info.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = '打开下载链接';

    item.append(label, link);
    qualityList.appendChild(item);
  });

  return true;
}

function renderLyric(lyric) {
  const lyricText = lyric?.lyric || '暂无歌词';
  const translated = lyric?.tylyric ? `\n\n--- 翻译歌词 ---\n${lyric.tylyric}` : '';
  lyricContent.textContent = `${lyricText}${translated}`;
}

function resolveErrorMessage(data, status) {
  if (data?.error) {
    return data.error;
  }
  if (data?.song?.msg) {
    return data.song.msg;
  }
  if (status === 400) {
    return 'url parameter is required';
  }
  return '解析失败，请检查链接是否有效或稍后重试。';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearError();
  resetResults();

  const url = input.value.trim();
  if (!url) {
    showError('url parameter is required');
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = '解析中...';

  try {
    const response = await fetch(`/song?url=${encodeURIComponent(url)}`);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      showError(resolveErrorMessage(data, response.status));
      return;
    }

    if (data?.song?.msg) {
      showError(data.song.msg);
      return;
    }

    renderSong(data.song || {});
    renderLyric(data.lyric || {});
    const hasLinks = renderQualityLinks(data.music_urls);

    if (!hasLinks) {
      showError('未获取到可用音质链接，可能是 Cookie 未配置、权限不足，或当前歌曲暂不支持下载。');
    }

    resultPanel.hidden = false;
  } catch (error) {
    showError('解析失败，请检查网络连接、链接格式或服务端日志。');
    console.error(error);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = '开始解析';
  }
});
