# QQ音乐无损解析使用方法
先安装 文件所需要的依赖模块 
```bash
pip install -r requirements.txt
```
再运行app.py文件即可

# 环境要求
Python >= 3

# 使用方法
先设置环境变量 `QQMUSIC_COOKIE`，再启动服务。

Linux / macOS：
```bash
export QQMUSIC_COOKIE='你的完整 QQ 音乐 Cookie'
python app.py
```

Windows PowerShell：
```powershell
$env:QQMUSIC_COOKIE='你的完整 QQ 音乐 Cookie'
python app.py
```

Windows CMD：
```cmd
set QQMUSIC_COOKIE=你的完整 QQ 音乐 Cookie
python app.py
```
# 返回数据
song[] = 包含歌名 专辑 歌手 图片
lyric[] = 包含原文歌词 翻译歌词(如果有)
music_urls[] = 包含'm4a', '128', '320', 'flac', 'ape'等歌曲链接
其中flac和ape为无损 320为高品质 m4a和128为标准音质

# 注意事项
请通过环境变量 `QQMUSIC_COOKIE` 提供 Cookie，不需要再手动修改源码中的 `cookie_str`。
其中 要解析VIP歌曲以及无损以上音质 请获取会员账号的cookie
如果未配置 `QQMUSIC_COOKIE`，接口会返回“服务端未配置 QQMUSIC_COOKIE”。
