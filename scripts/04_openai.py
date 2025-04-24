# scripts/02_summarize_chunks_openai.py

import os
import time
from glob import glob
from pathlib import Path

from openai import OpenAI
from tqdm import tqdm

BASE_DIR    = Path(__file__).resolve().parent.parent
CHUNKS_DIR  = BASE_DIR / "data" / "chunks"        # 원본 청크(txt)
SUMMARY_DIR = BASE_DIR / "data" / "summaries"     # 요약본 저장
SUMMARY_DIR.mkdir(exist_ok=True, parents=True)

client = OpenAI()           # OPENAI_API_KEY from env
MODEL  = "gpt-4o"
BATCH  = 5                  # 한 번에 처리할 줄(스크립트) 개수
TEMP   = 0.0                # 결정적 요약

SYSTEM_PROMPT = (
    "당신은 식음료 칼럼니스트입니다.\n"
    "아래 유튜브 영상 스크립트를 읽고, 음식·술 페어링 핵심만 담아 2~3문장의 매끄러운 한국어로 요약하세요.\n"
    "불필요한 대화체는 제거하고, 반드시 음식명과 술 페어링 정보를 포함해 주세요.\n"
    "출력은 입력 순서대로, 한 줄에 하나의 요약을 반환합니다."
)

def batcher(lines, n):
    for i in range(0, len(lines), n):
        yield lines[i : i + n]

def summarize_batch(lines_batch: list[str]) -> list[str]:
    prompt = "\n\n---\n\n".join(lines_batch)
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=TEMP,
        messages=[
            {"role": "system",  "content": SYSTEM_PROMPT},
            {"role": "user",    "content": prompt},
        ],
    )
    # 모델이 구분자로 응답했다고 가정하고 split
    outputs = resp.choices[0].message.content.strip().split("\n\n---\n\n")
    # 만약 길이가 다르면, 남는 부분은 빈문장으로 채우거나 원본을 돌려줌
    if len(outputs) < len(lines_batch):
        # simple fallback: pad with originals (or "")
        outputs += [""] * (len(lines_batch) - len(outputs))
    return outputs[: len(lines_batch)]

def process_file(fp: Path):
    lines = fp.read_text(encoding="utf-8").splitlines()
    summaries = []

    for batch in tqdm(list(batcher(lines, BATCH)), desc=fp.name):
        summaries.extend(summarize_batch(batch))
        time.sleep(0.2)  # rate-limit 완화

    outp = SUMMARY_DIR / fp.name
    outp.write_text("\n".join(summaries), encoding="utf-8")
    print(f"✅ {fp.name} → {outp} ({len(summaries)} summaries)")

if __name__ == "__main__":
    files = list(CHUNKS_DIR.glob("*.txt"))
    print(f"Found {len(files)} chunk files.")
    for f in files:
        process_file(f)
    print("🎉 All summaries generated.")
