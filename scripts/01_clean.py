import re, json, time, hashlib
from glob import glob
from pathlib import Path
from tqdm import tqdm
import multiprocessing as mp
from itertools import islice
from hanspell import spell_checker  # 맞춤법 검사 라이브러리 import 추가

# ─── 프로젝트 루트 & 데이터 디렉터리 설정 ─────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = BASE_DIR / "data" / "raw_dataset"
CLEAN_DIR  = BASE_DIR / "data" / "cleaned"
STOPWORDS  = set((BASE_DIR / "scripts" / "korean_stopwords.txt")
                 .read_text(encoding="utf-8").splitlines())

# Okt 초기화는 worker 내부에서 한 번만 수행
global_okt = None

def init_worker():
    global global_okt
    from konlpy.tag import Okt
    global_okt = Okt()
    print("Worker initialized with Okt")

def fingerprint(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def clean_line(line: str) -> str:
    # 소문자화→특수문자 제거→맞춤법 교정 정도까지만 적용
    s = re.sub(r"[^가-힣0-9\s\.\,\?]", " ", line)
    s = re.sub(r"\s+", " ", s).strip()
    # 불용어(의미 없는 조사/어미)만 제거
    for sw in STOPWORDS:
        s = s.replace(sw+" ", "")
    return s

    # 2) 맞춤법 교정 - 분할하여 처리 (hanspell의 문자 제한)
    try:
        # hanspell은 500자 제한이 있어서 짧은 단위로 나눠서 처리
        MAX_SPELL_LEN = 400  # 여유있게 설정
        if len(s) <= MAX_SPELL_LEN:
            checked = spell_checker.check(s)
            s = checked.checked
        else:
            # 긴 텍스트는 청크로 나눠서 처리
            chunks = [s[i:i+MAX_SPELL_LEN] for i in range(0, len(s), MAX_SPELL_LEN)]
            corrected_chunks = []
            for chunk in chunks:
                try:
                    checked = spell_checker.check(chunk)
                    corrected_chunks.append(checked.checked)
                except Exception as e:
                    print(f"Spell check error for chunk: {e}")
                    corrected_chunks.append(chunk)  # 오류 시 원본 사용
            s = ''.join(corrected_chunks)
    except Exception as e:
        print(f"Spell check error: {e}")
        # 맞춤법 오류 시 원본 사용

    # 3) 형태소 분석 → 어근 추출
    try:
        morphs = global_okt.morphs(s, stem=True)
        toks = [m for m in morphs if m not in STOPWORDS and len(m) > 1]
        return " ".join(toks)
    except Exception as e:
        print(f"Error in morphological analysis: {e}")
        return ""

def process_chunk(chunk):
    results = []
    for line in chunk:
        cleaned = clean_line(line)
        if cleaned:
            results.append(cleaned)
    return results

def process_file(path: Path):
    print(f"\n▶ Processing {path.name}")
    start = time.time()

    # 1) JSONL 파일 처리 단계별 확인
    print("  - 파일 로드 중...")
    raw_lines = []
    
    # 파일을 한 줄씩 읽어서 처리 (메모리 효율적)
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                obj = json.loads(line)
                raw_lines.extend(obj.get("recommendations", []))
                if i % 1000 == 0:
                    print(f"    * {i}줄 처리 완료, 현재 {len(raw_lines)}개 문장 추출")
            except json.JSONDecodeError:
                print(f"  - JSON 파싱 오류 (줄 {i})")
                continue
    
    total = len(raw_lines)
    print(f"  - 총 {total}개 문장 로드 완료")
    
    if total == 0:
        print("  - 처리할 문장이 없습니다.")
        return

    # 2) 맞춤법 청크 처리 경과 표시
    print("  - 병렬 처리 시작...")
    print("    * 각 작업자는 텍스트 정제, 맞춤법 검사, 형태소 분석을 수행합니다.")
    
    CHUNK_SIZE = 100  # 조정 가능
    chunks = [raw_lines[i:i+CHUNK_SIZE] for i in range(0, len(raw_lines), CHUNK_SIZE)]
    
    cleaned_all = []
    with mp.Pool(min(mp.cpu_count(), 4), initializer=init_worker) as pool:
        for result in tqdm(pool.imap(process_chunk, chunks), total=len(chunks), desc="  cleaning"):
            cleaned_all.extend(result)
            # 주기적으로 진행 상황 출력
            if len(cleaned_all) % 1000 == 0:
                print(f"    * {len(cleaned_all)}/{total} 완료")

    # 3) 길이·중복 필터
    print("  - 중복 필터링 중...")
    out, seen = [], set()
    for s in cleaned_all:
        if len(s.split()) < 3:
            continue
        h = fingerprint(s)
        if h in seen:
            continue
        seen.add(h)
        out.append(s)

    # 4) 비정상 비율 체크
    bad_rate = 1 - len(out) / total
    print(f"  - 필터링 후: {len(out)}개 문장 (bad_rate={bad_rate:.2%})")
    if bad_rate >= 0.02:
        print(f"  - 경고: 비정상 비율이 높습니다: {bad_rate:.2%}")
        # 비정상 비율이 높아도 계속 진행

    # 5) 저장
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    key = path.stem
    out_path = CLEAN_DIR / f"{key}.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(out))

    elapsed = time.time() - start
    print(f"✅ {path.name}: {elapsed:.1f}초 소요 → {out_path}")

if __name__ == "__main__":
    all_files = list(RAW_DIR.glob("*.jsonl"))
    print(f"Found {len(all_files)} files to process.")
    
    # 디버깅을 위해 하나의 파일만 처리
    # process_file(all_files[0])
    
    # 맞춤법 API 상태 확인
    print("맞춤법 검사기 상태 확인 중...")
    try:
        test_result = spell_checker.check("안녕하세요 반갑습니다.")
        print(f"맞춤법 검사기 정상 작동: {test_result.checked}")
    except Exception as e:
        print(f"⚠️ 경고: 맞춤법 검사기 오류 - {e}")
        print("맞춤법 검사 없이 진행합니다.")
    
    # 모든 파일 처리
    for p in all_files:
        process_file(p)
    print("\n🎉 All done.")