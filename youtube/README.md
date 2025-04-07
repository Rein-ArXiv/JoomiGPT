# YouTube Pairing Crawler (Video + Transcript)

This script crawls YouTube for **food and alcohol pairing** videos and saves:

- Video metadata (title, description, channel, etc.)
- Subtitles (if available)
- MP4 video files

---

## 🔍 Keyword Example

- `와인 안주`, `beer food pairing`, `sake sushi`, `일식 와인 페어링`

---

## 📁 Output

- JSON metadata: `youtube_와인_안주.json`
- Video files: `/downloads/{videoId}.mp4`

Each entry in the JSON includes:

| Field         | Description               |
|---------------|---------------------------|
| `videoId`     | YouTube video ID          |
| `title`       | Video title               |
| `description` | Video description         |
| `channelTitle`| Channel name              |
| `publishTime` | Published date (UTC)      |
| `url`         | Video URL                 |
| `transcript`  | Full transcript (if any)  |
| `videoPath`   | Downloaded file path      |

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install google-api-python-client youtube-transcript-api pytube
```
## Set your API Key

```
export YOUTUBE_API_KEY="your_api_key"
```
## Run the script
```
python main.py
```