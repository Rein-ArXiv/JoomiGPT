import os, hashlib
from glob import glob
import sys

def fingerprint(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

print("스크립트 시작...")  # 시작 확인
print(f"현재 작업 디렉토리: {os.getcwd()}")  # 작업 디렉토리 확인

# 파일 존재 여부 확인
cleaned_files = glob("../data/cleaned/*.txt")
print(f"찾은 파일 개수: {len(cleaned_files)}")
if not cleaned_files:
    print("경고: data/cleaned/*.txt 경로에 파일이 없습니다!")
    print("data 폴더 구조:")
    for root, dirs, files in os.walk("data"):
        print(f"{root}: {files}")
    sys.exit(1)

# 각 파일 처리
for path in cleaned_files:
    try:
        print(f"처리 중: {path}")
        
        # 파일 읽기
        with open(path, encoding="utf-8") as fin:
            lines = fin.readlines()
        print(f"  - 원본 라인 수: {len(lines)}")
        
        # 중복 제거
        seen = set()
        out_lines = []
        for line in lines:
            h = fingerprint(line)
            if h not in seen:
                seen.add(h)
                out_lines.append(line)
        
        # 결과 저장
        with open(path, "w", encoding="utf-8") as fout:
            fout.writelines(out_lines)
        
        # 즉시 출력을 위해 버퍼 비우기
        print(f"✅ Dedup: {os.path.basename(path)} → {len(out_lines)} lines")
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ 오류 발생: {path} - {e}")
        sys.stdout.flush()

print("중복 제거 완료!")