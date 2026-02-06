"""PubMed Central 전문(Full Text) 가져오기 모듈"""
import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict
import time


class PMCFullTextFetcher:
    """PMC에서 오픈액세스 논문 전문을 가져오는 클래스"""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    PMC_OA_URL = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"

    def __init__(self, email: str, api_key: str = None):
        self.email = email
        self.api_key = api_key

    def get_pmcid_from_pmid(self, pmid: str) -> Optional[str]:
        """PMID로 PMCID 찾기"""
        try:
            url = f"{self.BASE_URL}/elink.fcgi"
            params = {
                "dbfrom": "pubmed",
                "db": "pmc",
                "id": pmid,
                "email": self.email,
                "retmode": "json"
            }
            if self.api_key:
                params["api_key"] = self.api_key

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            # PMCID 추출
            linksets = data.get("linksets", [])
            if linksets:
                linksetdbs = linksets[0].get("linksetdbs", [])
                for linksetdb in linksetdbs:
                    if linksetdb.get("dbto") == "pmc":
                        links = linksetdb.get("links", [])
                        if links:
                            return f"PMC{links[0]}"
            return None

        except Exception as e:
            return None

    def fetch_fulltext(self, pmcid: str) -> Optional[Dict]:
        """PMCID로 전문 가져오기"""
        try:
            # PMC ID에서 숫자만 추출
            pmc_num = pmcid.replace("PMC", "")

            url = f"{self.BASE_URL}/efetch.fcgi"
            params = {
                "db": "pmc",
                "id": pmc_num,
                "rettype": "xml",
                "email": self.email
            }
            if self.api_key:
                params["api_key"] = self.api_key

            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                return None

            # XML 파싱
            root = ET.fromstring(response.content)

            result = {
                "pmcid": pmcid,
                "sections": {}
            }

            # 본문 섹션 추출
            for sec in root.findall(".//sec"):
                sec_type = sec.get("sec-type", "")
                title_elem = sec.find("title")
                title = title_elem.text if title_elem is not None else ""

                # 섹션 텍스트 추출
                paragraphs = []
                for p in sec.findall(".//p"):
                    text = self._get_all_text(p)
                    if text:
                        paragraphs.append(text)

                if paragraphs:
                    section_key = sec_type or title.lower() or "unknown"
                    result["sections"][section_key] = {
                        "title": title,
                        "text": "\n\n".join(paragraphs)
                    }

            # 결론 섹션 찾기
            result["conclusion"] = self._extract_conclusion(result["sections"])

            # 결과 섹션 찾기
            result["results"] = self._extract_results(result["sections"])

            # 전체 텍스트
            all_text = []
            for sec_data in result["sections"].values():
                all_text.append(sec_data["text"])
            result["full_text"] = "\n\n".join(all_text)

            return result

        except Exception as e:
            return None

    def _get_all_text(self, element) -> str:
        """XML 요소에서 모든 텍스트 추출"""
        texts = []
        if element.text:
            texts.append(element.text)
        for child in element:
            texts.append(self._get_all_text(child))
            if child.tail:
                texts.append(child.tail)
        return "".join(texts).strip()

    def _extract_conclusion(self, sections: Dict) -> str:
        """결론 섹션 추출"""
        conclusion_keywords = ["conclusion", "conclusions", "summary", "concluding"]

        for key, data in sections.items():
            key_lower = key.lower()
            title_lower = data["title"].lower()

            for keyword in conclusion_keywords:
                if keyword in key_lower or keyword in title_lower:
                    return data["text"]

        return ""

    def _extract_results(self, sections: Dict) -> str:
        """결과 섹션 추출"""
        results_keywords = ["results", "findings", "result"]

        for key, data in sections.items():
            key_lower = key.lower()
            title_lower = data["title"].lower()

            for keyword in results_keywords:
                if keyword in key_lower or keyword in title_lower:
                    return data["text"]

        return ""

    def get_paper_with_fulltext(self, pmid: str, debug: bool = True) -> Optional[Dict]:
        """PMID로 전문 포함 논문 정보 가져오기"""
        import time as t
        start = t.time()

        # 1. PMCID 찾기
        pmcid = self.get_pmcid_from_pmid(pmid)
        if not pmcid:
            if debug:
                print(f"[PMC] PMID {pmid}: PMCID 없음 ({t.time()-start:.1f}초)")
            return None

        if debug:
            print(f"[PMC] PMID {pmid} -> {pmcid} ({t.time()-start:.1f}초)")

        # API 속도 제한 (0.34초 -> 0.1초로 줄임)
        time.sleep(0.1)

        # 2. 전문 가져오기
        fulltext = self.fetch_fulltext(pmcid)
        if not fulltext:
            if debug:
                print(f"[PMC] {pmcid}: 전문 없음 ({t.time()-start:.1f}초)")
            return None

        if debug:
            print(f"[PMC] {pmcid}: 전문 확보 ({t.time()-start:.1f}초)")
        return fulltext


def enhance_paper_with_fulltext(paper: Dict, fetcher: PMCFullTextFetcher) -> Dict:
    """논문에 전문 정보 추가"""
    pmid = paper.get("pmid")
    if not pmid:
        return paper

    fulltext_data = fetcher.get_paper_with_fulltext(pmid)

    if fulltext_data:
        paper["has_fulltext"] = True
        paper["pmcid"] = fulltext_data.get("pmcid")
        paper["conclusion"] = fulltext_data.get("conclusion", "")
        paper["results"] = fulltext_data.get("results", "")
        paper["full_text_length"] = len(fulltext_data.get("full_text", ""))
    else:
        paper["has_fulltext"] = False

    return paper
