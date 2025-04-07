import os
import json
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube

# API 키 설정 (환경 변수에서 가져오는 방식 권장)
API_KEY = os.environ.get("YOUTUBE_API_KEY")

# 유튜브 API 초기화
youtube = build("youtube", "v3", developerKey=API_KEY)

# 검색 키워드
KEYWORD = "와인 안주"  # 예: 술, 음식, beer food pairing, sake sushi 등
MAX_RESULTS = 10

# 출력 폴더 설정
DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 검색 실행
request = youtube.search().list(
    q=KEYWORD,
    part="snippet",
    type="video",
    maxResults=MAX_RESULTS
)
response = request.execute()

# 결과 저장 리스트
results = []

# 영상별 처리
for item in response["items"]:
    video_id = item["id"]["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # 자막 가져오기
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        transcript_text = " ".join([t['text'] for t in transcript_data])
    except (TranscriptsDisabled, NoTranscriptFound):
        transcript_text = None

    # 영상 다운로드
    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        file_path = stream.download(output_path=DOWNLOAD_DIR, filename=f"{video_id}.mp4")
    except Exception as e:
        print(f"[!] 다운로드 실패: {video_url} ({e})")
        file_path = None

    # 데이터 저장
    video_data = {
        "videoId": video_id,
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "channelTitle": item["snippet"]["channelTitle"],
        "publishTime": item["snippet"]["publishedAt"],
        "url": video_url,
        "transcript": transcript_text,
        "videoPath": file_path
    }
    results.append(video_data)
    print(f"[✓] 완료: {video_id}")

# JSON으로 저장
output_file = f"youtube_{KEYWORD.replace(' ', '_')}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n총 {len(results)}개의 영상을 수집하고 '{output_file}'로 저장했습니다.")
