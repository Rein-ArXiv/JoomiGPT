# 파일: root/data/crawler/youtube/main.py

import os
import json
import asyncio
from pathlib import Path
from itertools import cycle

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    AgeRestricted
)
from pytube import YouTube
from tqdm.asyncio import tqdm

# ─── ① 프로젝트 절대 경로 설정 ──────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # root/
RAW_DIR  = BASE_DIR / "raw_dataset"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ─── ② API 키 로테이터 & 상수 정의 ───────────────────
API_KEYS = [
    "AIzaSyBjofHdSDlES3jHZnYU10GTb1V4equvfv8",
    "AIzaSyDlBNowOaVVCY0FLSt_qioMfqSZyATg4MM",
    "AIzaSyCOOMBn0UklXORCV-Yarznb3oSAV3ry8W4",
    "AIzaSyCfi9Pbe_xqLf2Yvgv_Sa06WsML8SlqBEw",
    "AIzaSyAsyCgVa6KaTEEFzdliMcwPMUGOigJ1ass"
]

QUERY_TEMPLATES = [
    "{food}에 어울리는 술 페어링",
    "{food} 술 추천",
    "what alcohol pairs well with {food}",
    "{food} pairing alcohol",
    "{food} and wine pairing",
    "{food} beer pairing",
    "{food} cocktail pairing",
    "{food} 와 어울리는 와인",
    "{food} 과 맥주 궁합",
    "best alcohol for {food}",
]

class YouTubeClientRotator:
    def __init__(self, api_keys: list[str]):
        if not api_keys:
            raise ValueError("API Key 리스트가 비어있습니다.")
        self._keys_cycle = cycle(api_keys)

    def next(self):
        key = next(self._keys_cycle)
        return build("youtube", "v3", developerKey=key)

client_rotator = YouTubeClientRotator(API_KEYS)

TARGET_PER_KEYWORD = 5000   # 키워드당 수집 목표
BATCH_SIZE         = 50     # Search API 최대값
REGION             = "KR"   # regionCode
SEM                = asyncio.Semaphore(10)  # 동시 자막 요청 제한


# ─── ③ 동기 자막 가져오기 함수 (to_thread 래핑 전용) ────
def _sync_fetch_transcript(video_id: str, cookie_path: str = None) -> str | None:
    try:
        kwargs = {"cookies": cookie_path} if cookie_path else {}
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, **kwargs)

        for lang in (["ko"], ["en"], None):
            try:
                transcript = (
                    transcript_list.find_transcript(lang)
                    if lang else
                    transcript_list.find_generated_transcript()
                )
                break
            except NoTranscriptFound:
                continue
        else:
            return None

        data = transcript.fetch()
        return " ".join(seg.text for seg in data)

    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
        return None

    except AgeRestricted:
        try:
            data = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=["ko", "en"],
                cookies=cookie_path
            )
            return " ".join(seg["text"] for seg in data)
        except Exception:
            return None

    except Exception:
        return None


# ─── ④ 비동기 래퍼 ────────────────────────────────────
async def fetch_transcript(video_id: str, cookie_path: str = None) -> str | None:
    async with SEM:
        return await asyncio.to_thread(_sync_fetch_transcript, video_id, cookie_path)


# ─── ⑤ 단일 비디오 처리 ──────────────────────────────
async def process_video(item: dict, food: str, cookie_path: str = None) -> dict | None:
    vid   = item["id"]["videoId"]
    title = item["snippet"]["title"]
    url   = f"https://www.youtube.com/watch?v={vid}"

    transcript = await fetch_transcript(vid, cookie_path)
    if not transcript or food not in transcript:
        return None

    recs = [s.strip() for s in transcript.split('.') if food in s]
    if not recs:
        return None

    return {"videoId": vid, "title": title, "url": url, "recommendations": recs}


# ─── ⑥ 키워드별 크롤링 루프 (JSONL append + key rotation) ───
async def crawl_for_keyword(food: str, cookie_path: str = None):
    out_path = RAW_DIR / f"{food}.jsonl"
    seen_ids = set()
    collected = 0

    # 기존에 저장된 영상 ID 로드 (중복 방지)
    if out_path.exists():
        with out_path.open("r", encoding="utf-8") as fin:
            for line in fin:
                seen_ids.add(json.loads(line)["videoId"])

    print(f"\n▶︎ [{food}] 수집 시작… 목표: {TARGET_PER_KEYWORD}개")

    # 1) 각 템플릿별로 페이징하며 수집
    for template in QUERY_TEMPLATES:
        if collected >= TARGET_PER_KEYWORD:
            break

        query = template.format(food=food)
        next_tok = None
        print(f"   ▶︎ 쿼리: {query!r}")

        while collected < TARGET_PER_KEYWORD:
            # API 키 로테이션
            youtube = client_rotator.next()
            resp = youtube.search().list(
                q          = query,
                part       = "snippet",
                type       = "video",
                maxResults = BATCH_SIZE,
                pageToken  = next_tok,
                regionCode = REGION
            ).execute()

            items    = resp.get("items", [])
            next_tok = resp.get("nextPageToken")
            if not items:
                break  # 이 쿼리로 더 이상 결과 없음

            # 비동기 자막+필터링
            tasks = [
                process_video(it, food, cookie_path)
                for it in items
                if it["id"]["videoId"] not in seen_ids
            ]
            async for fut in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
                out = await fut
                if out:
                    vid = out["videoId"]
                    seen_ids.add(vid)
                    with out_path.open("a", encoding="utf-8") as fw:
                        fw.write(json.dumps(out, ensure_ascii=False) + "\n")
                    collected += 1

            print(f"      → 누적: {collected}/{TARGET_PER_KEYWORD}")
            if not next_tok:
                break  # 페이지 순회 종료

    print(f"✅ [{food}] 최종 수집: {collected}개 → {out_path}")



# ─── ⑦ 메인 ─────────────────────────────────────────
async def main():
    kw_file = BASE_DIR / "keywords.txt"
    foods   = [line.strip() for line in kw_file.read_text(encoding="utf-8").splitlines() if line.strip()]

    cookie_path = str(BASE_DIR / "crawler" / "youtube" / "cookies.txt")
    for food in foods:
        await crawl_for_keyword(food, cookie_path=cookie_path)


if __name__ == "__main__":
    asyncio.run(main())
