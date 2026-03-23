# QQ音乐无损解析使用方法

先安装项目所需依赖：

```bash
pip install -r requirements.txt
```

## 环境要求

Python >= 3

## 使用方法

### 1. 配置 QQMUSIC_COOKIE

启动服务前，请先设置环境变量 `QQMUSIC_COOKIE`。Cookie 需要从 `https://y.qq.com/` 登录后的浏览器请求中获取。

Linux / macOS:

```bash
export QQMUSIC_COOKIE='你的完整 QQ 音乐 Cookie'
python app.py
```

Windows PowerShell:

```powershell
$env:QQMUSIC_COOKIE='你的完整 QQ 音乐 Cookie'
python app.py
```

Windows CMD:

```cmd
set QQMUSIC_COOKIE=你的完整 QQ 音乐 Cookie
python app.py
```

如果未设置该环境变量，`/song` 接口会直接返回 `服务端未配置 QQMUSIC_COOKIE` 的 JSON 错误提示。

### 2. 启动服务

```bash
python app.py
```

启动后可访问：

- GUI 首页：`http://127.0.0.1:5122/`
- 解析接口：`http://127.0.0.1:5122/song?url=QQ音乐歌曲链接`

## 请求示例

如图箭头显示：

![url链接](https://raw.githubusercontent.com/Suxiaoqinx/tencent_url/refs/heads/main/fe14f9a6-16ca-423d-980b-c17015666dc0.png)

## 参数列表

请求链接选择 `http://ip:port/song`

请求方式 `GET`

| 参数列表 | 参数说明 |
| ---- | ---- |
| url | 解析获取到的 QQ 音乐地址 |

## 返回数据

- `song[]`：包含歌名、专辑、歌手、图片。
- `lyric[]`：包含原文歌词、翻译歌词（如果有）。
- `music_urls[]`：包含 `m4a`、`128`、`320`、`flac`、`ape` 等歌曲链接。

其中 `flac` 和 `ape` 为无损，`320` 为高品质，`m4a` 和 `128` 为标准音质。

## 演示站点

[在线解析](https://api.toubiec.cn/qqmusic.html)

## 注意事项

- 请通过环境变量 `QQMUSIC_COOKIE` 提供 Cookie，不再需要手动修改源码中的 `cookie_str`。
- 要解析 VIP 歌曲以及无损以上音质，请使用具备对应权限账号的 Cookie。
- 如果 `QQMUSIC_COOKIE` 格式不合法，接口会返回明确的 JSON 错误，避免服务端直接报 500。

## 反馈方法

请在 GitHub 的 Issues 反馈，或者到我[博客](https://www.toubiec.cn)反馈。
