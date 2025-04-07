# 🧪 PMC 논문 수집기 (PubMed Central Harvester)

PubMed Central(PMC)의 오픈 액세스 논문을 키워드 기반으로 자동 검색하고,  
논문의 제목, 저자, 초록, 저널, 본문 섹션, 그림(Figure) 정보 등을 구조화된 형태로 수집합니다.

---

## 🚀 주요 기능

- 키워드 기반 논문 검색 (`esearch.fcgi`)
- 논문 전문(XML) 수집 및 파싱 (`efetch.fcgi`)
- 다음 항목 추출:
  - 논문 제목, 저자, 저널명, 출판일, DOI
  - 초록(Abstract)
  - 본문 주요 섹션(Introduction, Methods 등)
  - Figure label, caption, 이미지 파일명 및 다운로드 URL
- BeautifulSoup 기반의 안정적인 파싱
- API rate limit 대응 (`time.sleep()`)

---

## ⚙️ 사용법

### 1. 설치

```bash
pip install requests beautifulsoup4
```

### 2. 실행

```bash
python main.py
```

### 3. 검색어 수정

스크립트 내에서 원하는 키워드를 변경합니다:

```python
query = "molecular gastronomy"  # 키워드를 변경하세요
```

---

## 📄 예시 출력

```
🔗 PMC ID: PMC11942250
📄 Title: Jasonia glutinosa(L.) DC.: Back in Our Pantries?
👨‍🔬 Authors: Marta Sofía Valero, Carlota Gómez-Rincón, Víctor López, Francisco Les
📚 Journal: International Journal of Molecular Sciences
📅 Published: 2025-3-12
🔗 DOI: 10.3390/ijms26062536

📑 Abstract:
Jasonia glutinosa(L.) DC., commonly known in Spain as “Rock Tea”, is a medicinal plant...

🧠 Sections Preview:
  ▶️ 1. Introduction
     Jasonia glutinosa (L.) DC., commonly known as rock tea, is an aromatic plant...
  ▶️ 2. Ethnomedicinal/Traditional Uses
     The exact time when the infusion of this plant first began...
  ▶️ 3. Phytochemical Composition
     Numerous phytochemical studies of J. glutinosa have been conducted...

🖼️ Figures:
  • Figure 1
    - Caption: Distribution of Jasonia glutinosa and its traditional uses.
    - Image File: ijms-26-02536-g001
    - Image URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11942250/bin/ijms-26-02536-g001

  • Figure 2
    - Caption: Methodologies carried out with J. glutinosa to study its activities.
    - Image File: ijms-26-02536-g002
    - Image URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11942250/bin/ijms-26-02536-g002
```

---

## 🧠 출력 항목 요약

| 항목       | 설명                                     |
|------------|------------------------------------------|
| 📄 Title    | 논문 제목                                |
| 👨‍🔬 Authors | 전체 저자명 목록                         |
| 📚 Journal  | 학회지 또는 출판 저널 이름               |
| 📅 Published| 출판 연도, 월, 일                        |
| 🔗 DOI      | Digital Object Identifier               |
| 📑 Abstract | 논문 초록 (요약문)                      |
| 🧠 Sections | 본문 주요 섹션별 내용 요약              |
| 🖼️ Figures  | 그림 번호, 캡션, 이미지 파일명 및 링크  |

---

## 💡 확장 가능 기능

- [ ] 이미지 자동 다운로드 기능 추가
- [ ] CSV/JSON 결과 저장
- [ ] LLM 기반 논문 요약
- [ ] LangChain 기반 논문 질의응답 시스템
- [ ] PDF 병합 및 요약 정리

---

## 📚 참고 자료

- [NCBI E-Utilities 공식 문서](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
- [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/)
- [BeautifulSoup4 Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
