import requests
from pprint import pprint
import time

headers = {"Content-Type": "application/json"}
BASE_URL = "https://api.arxivxplorer.com"

# 🔍 검색할 쿼리 리스트
queries = [
    "food science",
    "molecular gastronomy",
    "chemical analysis of food",
    "wine and cheese pairing",
    "cocktail chemistry",
    "flavor molecule graph neural networks",
    "umami prediction models",
    "LLM for recipe generation"
]

def search_arxiv(query, count=3):
    """arXiv Xplorer에서 의미론적 논문 검색"""
    url = f"{BASE_URL}/search"
    payload = {
        "query": query,
        "method": "semantic",
        "count": count,
        "page": 1
    }
    res = requests.post(url, json=payload, headers=headers)
    return res.json()

def get_sections(paper_id):
    """논문의 유효 섹션을 전부 출력"""
    print(f"\n\n======================")
    print(f"📘 논문 ID: {paper_id}")
    
    # 메타데이터 조회
    meta_url = f"{BASE_URL}/read_paper_metadata"
    meta_payload = {"paper_id": paper_id, "show_abstract": True}
    meta_res = requests.post(meta_url, json=meta_payload, headers=headers)
    meta_json = meta_res.json()

    print(f"📄 Title: {meta_json.get('title')}")
    print(f"👨‍🔬 Authors: {meta_json.get('authors')}")
    print(f"📅 Date: {meta_json.get('date')}")
    print(f"📑 Abstract: {meta_json.get('abstract')[:300]}...\n")

    toc_raw = meta_json.get("table_of_contents", "")
    section_titles = [line.strip() for line in toc_raw.strip().split("\n") if line.strip()]
    print(f"📚 Found {len(section_titles)} sections (TOC 기준)")

    for section_id in range(1, len(section_titles) + 1):
        print(f"\n🔎 Section {section_id}: {section_titles[section_id - 1]}")

        section_url = f"{BASE_URL}/read_section"
        section_payload = {"paper_id": paper_id, "section_id": section_id}
        section_res = requests.post(section_url, json=section_payload, headers=headers)

        try:
            content = section_res.json()
            if "Error" in content and "list index out of range" in content["Error"]:
                print("❌ 유효하지 않은 섹션입니다. 루프 종료.")
                break
        except Exception:
            content = section_res.text

        print("📖 내용:\n")
        pprint(content)  # 일부만 보기 좋게 출력
        print("\n" + "-"*50)
        time.sleep(0.5)  # 과도한 요청 방지용

# 🔁 전체 쿼리 순회
for query in queries:
    print(f"\n\n🧠 QUERY: {query}")
    papers = search_arxiv(query)

    for paper in papers:
        print(f"\n▶️ 논문: {paper['title']} ({paper['date']})")
        print(f"   ↳ ID: {paper['id']}")
        print(f"   ↳ First Author: {paper['first_author']}")
        print(f"   ↳ Abstract Snippet: {paper['abstract_snippet']}...\n")

        # 실제 섹션 내용까지 출력
        get_sections(paper["id"])

        time.sleep(2)  # API Rate limit 대응
