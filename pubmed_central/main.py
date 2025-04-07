import requests
from bs4 import BeautifulSoup
import time

def search_pmc(query, max_results=5):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pmc",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    ids = res.json()["esearchresult"]["idlist"]
    return [f"PMC{id}" for id in ids]

def fetch_pmc_xml(pmc_id):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pmc", "id": pmc_id, "retmode": "xml"}
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.text

def parse_detailed_pmc_xml(xml, pmc_id=None):
    soup = BeautifulSoup(xml, "xml")

    # 제목
    title = soup.find("article-title")
    title = title.get_text(strip=True) if title else "(제목 없음)"

    # 저자
    authors = []
    for person in soup.find_all("contrib", {"contrib-type": "author"}):
        name = person.find("name")
        if name:
            given = name.find("given-names")
            surname = name.find("surname")
            full_name = f"{given.text} {surname.text}" if given and surname else name.text
            authors.append(full_name)
    authors_text = ", ".join(authors) if authors else "(저자 정보 없음)"

    # 저널
    journal = soup.find("journal-title")
    journal = journal.text.strip() if journal else "(저널 없음)"

    # 출판일
    pub_date = soup.find("pub-date")
    if pub_date:
        year = pub_date.find("year")
        month = pub_date.find("month")
        day = pub_date.find("day")
        pub_date_text = f"{year.text if year else ''}-{month.text if month else '01'}-{day.text if day else '01'}"
    else:
        pub_date_text = "(출판일 없음)"

    # DOI
    doi_tag = soup.find("article-id", {"pub-id-type": "doi"})
    doi = doi_tag.text.strip() if doi_tag else "(DOI 없음)"

    # 초록
    abstract_tag = soup.find("abstract")
    if abstract_tag:
        paragraphs = abstract_tag.find_all("p")
        abstract = "\n".join(p.get_text(strip=True) for p in paragraphs) if paragraphs else abstract_tag.get_text(strip=True)
    else:
        abstract = "(초록 없음)"

    # 본문 섹션 (앞부분 일부만 요약)
    sections = []
    for sec in soup.find_all("sec")[:3]:
        sec_title = sec.title.get_text(strip=True) if sec.title else "(제목 없음)"
        sec_text = sec.get_text(separator=" ", strip=True)
        sections.append((sec_title, sec_text))

    # 그림 (Figure)
    figures = []
    for fig in soup.find_all("fig"):
        label = fig.find("label")
        caption = fig.find("caption")
        graphic = fig.find("graphic")

        label_text = label.get_text(strip=True) if label else "(No label)"
        caption_text = caption.get_text(separator=" ", strip=True) if caption else "(No caption)"
        image_file = graphic.get("xlink:href") if graphic else "(No image)"
        image_url = None
        if pmc_id and image_file and "No image" not in image_file:
            image_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/bin/{image_file}"

        figures.append({
            "label": label_text,
            "caption": caption_text,
            "image_file": image_file,
            "image_url": image_url
        })

    return {
        "title": title,
        "authors": authors_text,
        "journal": journal,
        "pub_date": pub_date_text,
        "doi": doi,
        "abstract": abstract,
        "sections": sections,
        "figures": figures
    }

# 전체 실행
if __name__ == "__main__":
    query = "molecular gastronomy"
    pmc_ids = search_pmc(query)

    for pmc_id in pmc_ids:
        print(f"\n🔗 PMC ID: {pmc_id}")
        try:
            xml = fetch_pmc_xml(pmc_id)
            parsed = parse_detailed_pmc_xml(xml, pmc_id=pmc_id)

            print(f"📄 Title: {parsed['title']}")
            print(f"👨‍🔬 Authors: {parsed['authors']}")
            print(f"📚 Journal: {parsed['journal']}")
            print(f"📅 Published: {parsed['pub_date']}")
            print(f"🔗 DOI: {parsed['doi']}")
            print(f"\n📑 Abstract:\n{parsed['abstract']}")

            print("\n🧠 Sections Preview:")
            for idx, (sec_title, sec_text) in enumerate(parsed["sections"]):
                print(f"  ▶️ {sec_title}\n     {sec_text[:500]}{'...' if len(sec_text) > 500 else ''}\n")

            print("🖼️ Figures:")
            if parsed["figures"]:
                for fig in parsed["figures"]:
                    print(f"  • {fig['label']}")
                    print(f"    - Caption: {fig['caption']}")
                    print(f"    - Image File: {fig['image_file']}")
                    if fig["image_url"]:
                        print(f"    - Image URL: {fig['image_url']}")
                    print()
            else:
                print("  (No figures found)\n")

        except Exception as e:
            print(f"❌ Error parsing {pmc_id}: {e}")

        print("-" * 100)
        time.sleep(2)  # API rate limit 대응
