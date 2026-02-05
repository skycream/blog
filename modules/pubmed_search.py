"""PubMed 논문 검색 모듈"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import time


class PubMedSearcher:
    """PubMed API를 사용한 논문 검색"""

    def __init__(self, email: str, api_key: Optional[str] = None):
        """
        Args:
            email: PubMed API 사용을 위한 이메일
            api_key: PubMed API 키 (선택사항, 있으면 요청 제한 완화)
        """
        self.email = email
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def search(self, query: str, max_results: int = 12,
               sort_by: str = "relevance", strict: bool = False) -> List[str]:
        """
        PubMed에서 논문 검색

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 개수
            sort_by: 정렬 기준 ("relevance", "pub_date", "cited")
            strict: True면 고품질 연구만, False면 더 많은 결과

        Returns:
            PubMed ID 리스트
        """
        try:
            # 검색 쿼리 최적화
            search_query = self._optimize_query(query, strict=strict)

            # PubMed API 요청
            params = {
                'db': 'pubmed',
                'term': search_query,
                'retmax': max_results,
                'sort': sort_by,
                'retmode': 'xml',
                'email': self.email
            }

            if self.api_key:
                params['api_key'] = self.api_key

            response = requests.get(f"{self.base_url}esearch.fcgi", params=params)
            response.raise_for_status()

            # XML 파싱
            root = ET.fromstring(response.content)
            pmids = [id_elem.text for id_elem in root.findall('.//Id')]

            print(f"✓ {len(pmids)}개의 논문을 찾았습니다.")
            return pmids

        except Exception as e:
            print(f"✗ PubMed 검색 실패: {str(e)}")
            return []

    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """
        논문 상세 정보 가져오기

        Args:
            pmids: PubMed ID 리스트

        Returns:
            논문 정보 딕셔너리 리스트
        """
        if not pmids:
            return []

        papers = []
        batch_size = 10  # 한 번에 가져올 논문 개수

        try:
            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i+batch_size]

                # API 요청 제한 준수
                if i > 0:
                    time.sleep(0.4)  # 초당 3회 제한

                # PubMed API 요청
                params = {
                    'db': 'pubmed',
                    'id': ','.join(batch_pmids),
                    'retmode': 'xml',
                    'email': self.email
                }

                if self.api_key:
                    params['api_key'] = self.api_key

                response = requests.get(f"{self.base_url}efetch.fcgi", params=params)
                response.raise_for_status()

                # XML 파싱
                root = ET.fromstring(response.content)

                # 각 논문 정보 파싱
                for article in root.findall('.//PubmedArticle'):
                    paper = self._parse_paper_xml(article)
                    if paper:
                        papers.append(paper)

                print(f"✓ {len(papers)}/{len(pmids)} 논문 정보 수집 완료")

            return papers

        except Exception as e:
            print(f"✗ 논문 정보 수집 실패: {str(e)}")
            return papers

    def _optimize_query(self, query: str, strict: bool = False) -> str:
        """검색 쿼리 최적화"""
        # 주 검색어를 제목/초록에서 검색
        main_query = f"({query}[Title/Abstract])"

        if strict:
            # 엄격 모드: 고품질 연구만
            filters = [
                "AND (Review[PT] OR Meta-Analysis[PT] OR Randomized Controlled Trial[PT] OR Clinical Trial[PT])",
                "AND (hasabstract[text])",
                "AND (\"last 10 years\"[PDat])"
            ]
        else:
            # 완화 모드: 더 많은 논문 수집
            filters = [
                "AND (hasabstract[text])",
                "AND (\"last 15 years\"[PDat])",  # 15년으로 확대
                "AND (humans[MeSH Terms])"  # 인간 대상 연구
            ]

        optimized = main_query
        for filter_str in filters:
            optimized += f" {filter_str}"

        return optimized

    def _parse_paper_xml(self, article_elem) -> Optional[Dict]:
        """XML 요소에서 논문 정보 추출"""
        try:
            # PMID
            pmid_elem = article_elem.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else 'Unknown'

            # 제목
            title_elem = article_elem.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else 'No Title'

            # 저자
            authors = []
            for author_elem in article_elem.findall('.//Author')[:5]:
                lastname = author_elem.find('LastName')
                initials = author_elem.find('Initials')
                if lastname is not None and initials is not None:
                    authors.append(f"{lastname.text} {initials.text}")

            # 저널
            journal_elem = article_elem.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else 'Unknown Journal'

            # 연도
            year_elem = article_elem.find('.//PubDate/Year')
            year = year_elem.text if year_elem is not None else 'N/A'

            # 초록
            abstract_texts = []
            for abstract_elem in article_elem.findall('.//AbstractText'):
                if abstract_elem.text:
                    abstract_texts.append(abstract_elem.text)
            abstract = ' '.join(abstract_texts) if abstract_texts else 'No abstract available'

            # 논문 타입
            pub_type_elem = article_elem.find('.//PublicationType')
            study_type = pub_type_elem.text if pub_type_elem is not None else 'Unknown'

            return {
                'pmid': pmid,
                'title': title,
                'authors': authors,
                'journal': journal,
                'year': year,
                'abstract': abstract,
                'study_type': study_type,
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }

        except Exception as e:
            print(f"✗ 논문 파싱 실패: {str(e)}")
            return None

    def search_and_fetch(self, query: str, max_results: int = 12, strict: bool = False) -> List[Dict]:
        """검색과 상세 정보 가져오기를 한 번에 수행"""
        print(f"\n🔍 '{query}' 검색 중...")
        pmids = self.search(query, max_results, strict=strict)

        if not pmids:
            print("✗ 검색 결과가 없습니다.")
            return []

        print(f"\n📄 논문 정보 수집 중...")
        papers = self.fetch_details(pmids)

        print(f"\n✓ 총 {len(papers)}개 논문 수집 완료\n")
        return papers
