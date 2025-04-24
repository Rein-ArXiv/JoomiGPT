# scripts/03_chunk.py
import os
from glob import glob
import nltk
nltk.download('punkt_tab')

from nltk.tokenize import sent_tokenize



MAX_CHAR = 1000   # 청크 최대 글자 수


def chunkify(sentences, max_chars=800):
    chunks, buf = [], ""
    for sent in sentences:
        if len(buf) + len(sent) > max_chars:
            chunks.append(buf.strip()); buf = sent
        else:
            buf += " " + sent
    if buf: chunks.append(buf.strip())
    return chunks

for path in glob("../data/cleaned/*.txt"):
    key = os.path.splitext(os.path.basename(path))[0]
    out_path = f"../data/chunks/{key}_chunks.txt"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(path, encoding="utf-8") as fin:
        lines = [l.strip() for l in fin if l.strip()]
    with open(out_path, "w", encoding="utf-8") as fout:
        for c in chunkify(lines):
            fout.write(c + "\n")
    print(f"✅ Chunked: {key}, {len(open(out_path).read().splitlines())} chunks")
