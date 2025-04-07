# 🧠 arXivXplorer 기반 의미론적 논문 검색기

이 스크립트는 [arXivXplorer API](https://api.arxivxplorer.com)를 활용해 **의미 기반(semantic) 논문 검색**을 수행하고,  
각 논문의 **메타데이터 및 전체 섹션 내용을 자동으로 출력**합니다.

---

## 🚀 주요 기능

- 자연어 쿼리 기반 의미론적 논문 검색
- 논문 메타데이터(제목, 저자, 날짜, 초록) 출력
- 논문 목차(TOC) 파싱
- 각 섹션 내용을 자동 요청 및 출력
- API rate limit 대응 (`time.sleep()`)

---

## ⚙️ 사용법

### 1. 설치

```bash
pip install requests
```

### 2. 실행

```bash
python arxiv_searcher.py
```

### 3. 쿼리 수정

스크립트 상단의 `queries` 리스트를 수정하여 원하는 키워드로 검색할 수 있습니다:

```python
queries = [
    "food science",
    "LLM for recipe generation",
    "chemical analysis of food"
]
```

---

## 🧾 예시 출력 형태

실제 출력 결과는 실행 후 확인 가능합니다. 아래는 대략적인 출력 구조입니다:

```
🧠 QUERY: food science

▶️ 논문: The Chemistry of Culinary Transformation (2024-12-01)
   ↳ ID: abc123xyz
   ↳ First Author: Alice T. Cook
   ↳ Abstract Snippet: This paper discusses how molecular reactions influence taste perception...

======================
📘 논문 ID: abc123xyz
📄 Title: The Chemistry of Culinary Transformation
👨‍🔬 Authors: Alice T. Cook, Bob E. Taste
📅 Date: 2024-12-01
📑 Abstract: This paper discusses...

📚 Found 5 sections (TOC 기준)

🔎 Section 1: Introduction
📖 내용:
{ ... 섹션 내용 일부 ... }

🔎 Section 2: Related Work
📖 내용:
{ ... 섹션 내용 일부 ... }

...
```

> 🔁 실행할 때마다 다양한 최신 논문과 섹션 내용을 불러옵니다. 직접 돌려보는 걸 추천합니다!

---

## 🛠 확장 가능성

- [ ] 검색 쿼리 자동화 / 사용자 입력 기반 CLI
- [ ] 결과 CSV/JSON 저장
- [ ] 요약 모델 (LLM) 연동
- [ ] 임베딩 기반 논문 추천 시스템으로 확장

---

## 📚 관련 리소스

- [arXivXplorer API Docs](https://arxivxplorer.com/docs)
- [arXiv.org](https://arxiv.org)
- [OpenAI GPT + 논문 분석 파이프라인](https://platform.openai.com/)

---