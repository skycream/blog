"""
강화된 PubMed 검색 모듈
- 키워드 확장
- 다양한 검색어 조합
- 대량 논문 수집
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Set
import time
import re
from config import Config


class EnhancedPubMedSearcher:
    """강화된 PubMed 검색기"""

    def __init__(self, email: str = None):
        self.email = email or Config.PUBMED_EMAIL
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

        # 키워드 확장 사전
        self.keyword_expansions = {
            # 역류성식도염
            'GERD': ['GERD', 'gastroesophageal reflux', 'acid reflux', 'heartburn',
                     'esophagitis', 'LES dysfunction', 'Barrett esophagus'],
            '역류성식도염': ['GERD', 'gastroesophageal reflux', 'acid reflux', 'reflux esophagitis'],

            # 오렌지주스
            'orange juice': ['orange juice', 'citrus juice', 'fruit juice',
                            'citrus consumption', 'orange beverage'],
            '오렌지주스': ['orange juice', 'citrus juice', 'fruit juice'],

            # 러닝
            'running': ['running', 'jogging', 'aerobic exercise', 'endurance running',
                       'recreational running', 'distance running'],
            '러닝': ['running', 'jogging', 'aerobic exercise'],

            # 일반적인 건강 키워드 확장
            'health': ['health effects', 'health benefits', 'health outcomes', 'health risks'],
            'treatment': ['treatment', 'therapy', 'management', 'intervention'],
            'diet': ['diet', 'dietary', 'nutrition', 'food', 'consumption'],
        }

        # 주제별 세부 검색어
        self.topic_modifiers = {
            'general': ['', 'systematic review', 'meta-analysis', 'clinical trial'],
            'effects': ['effects', 'benefits', 'risks', 'outcomes'],
            'mechanism': ['mechanism', 'pathophysiology', 'etiology'],
            'epidemiology': ['prevalence', 'incidence', 'risk factors', 'epidemiology'],
        }

    def search_comprehensive(self, keyword: str,
                            max_total: int = 200,
                            years: int = 15) -> List[Dict]:
        """
        종합적인 검색 수행

        Args:
            keyword: 검색 키워드
            max_total: 최대 수집 논문 수
            years: 최근 몇 년 이내

        Returns:
            논문 정보 리스트
        """
        print(f"\n{'='*60}")
        print(f"종합 검색: {keyword}")
        print(f"목표: {max_total}개 논문")
        print('='*60)

        # 1. 키워드 확장
        expanded_keywords = self._expand_keyword(keyword)
        print(f"\n확장된 키워드: {expanded_keywords}")

        # 2. 다양한 검색 쿼리 생성
        queries = self._generate_queries(expanded_keywords, years)
        print(f"생성된 쿼리 수: {len(queries)}개")

        # 3. 검색 실행 및 PMID 수집
        all_pmids: Set[str] = set()
        per_query_limit = max(20, max_total // len(queries))

        for i, query in enumerate(queries):
            if len(all_pmids) >= max_total:
                break

            pmids = self._search_pmids(query, per_query_limit)
            new_pmids = set(pmids) - all_pmids
            all_pmids.update(new_pmids)

            if new_pmids:
                print(f"  [{i+1}/{len(queries)}] +{len(new_pmids)}개 (총 {len(all_pmids)}개)")

            time.sleep(0.35)  # API 제한 준수

        print(f"\n수집된 고유 PMID: {len(all_pmids)}개")

        # 4. 논문 상세 정보 가져오기
        pmid_list = list(all_pmids)[:max_total]
        papers = self._fetch_details(pmid_list)

        print(f"최종 수집 논문: {len(papers)}개")

        return papers

    def _expand_keyword(self, keyword: str) -> List[str]:
        """키워드 확장"""
        expanded = [keyword]

        # 사전에서 확장 키워드 찾기
        keyword_lower = keyword.lower()
        for key, expansions in self.keyword_expansions.items():
            if key.lower() in keyword_lower or keyword_lower in key.lower():
                expanded.extend(expansions)

        # 중복 제거
        return list(set(expanded))

    def _generate_queries(self, keywords: List[str], years: int) -> List[str]:
        """다양한 검색 쿼리 생성"""
        queries = []

        base_filter = f'AND (hasabstract[text]) AND ("last {years} years"[PDat]) AND (humans[MeSH Terms])'

        for kw in keywords:
            # 기본 검색
            queries.append(f'({kw}[Title/Abstract]) {base_filter}')

            # 고품질 연구 타입 추가
            for study_type in ['systematic review', 'meta-analysis', 'randomized controlled trial']:
                queries.append(f'({kw}[Title/Abstract]) AND ({study_type}[PT]) {base_filter}')

        # 중복 제거
        return list(set(queries))

    def _search_pmids(self, query: str, max_results: int) -> List[str]:
        """PMID 검색"""
        try:
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'xml',
                'email': self.email
            }

            response = requests.get(f"{self.base_url}esearch.fcgi", params=params, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            pmids = [id_elem.text for id_elem in root.findall('.//Id')]

            return pmids

        except Exception as e:
            print(f"    검색 오류: {e}")
            return []

    def _fetch_details(self, pmids: List[str], batch_size: int = 20) -> List[Dict]:
        """논문 상세 정보 가져오기"""
        papers = []

        print(f"\n논문 상세 정보 수집 중...")

        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]

            try:
                params = {
                    'db': 'pubmed',
                    'id': ','.join(batch),
                    'retmode': 'xml',
                    'email': self.email
                }

                response = requests.get(f"{self.base_url}efetch.fcgi", params=params, timeout=30)
                response.raise_for_status()

                root = ET.fromstring(response.content)

                for article in root.findall('.//PubmedArticle'):
                    paper = self._parse_article(article)
                    if paper:
                        papers.append(paper)

                print(f"  {len(papers)}/{len(pmids)} 완료")
                time.sleep(0.35)

            except Exception as e:
                print(f"  배치 처리 오류: {e}")
                continue

        return papers

    def _parse_article(self, article) -> Optional[Dict]:
        """XML에서 논문 정보 추출"""
        try:
            pmid = article.findtext('.//PMID', 'Unknown')
            title = article.findtext('.//ArticleTitle', 'No Title')

            # 저자
            authors = []
            for author in article.findall('.//Author')[:5]:
                lastname = author.findtext('LastName', '')
                initials = author.findtext('Initials', '')
                if lastname:
                    authors.append(f"{lastname} {initials}".strip())

            journal = article.findtext('.//Journal/Title', 'Unknown')
            year = article.findtext('.//PubDate/Year', 'N/A')

            # 초록
            abstract_parts = []
            for elem in article.findall('.//AbstractText'):
                if elem.text:
                    label = elem.get('Label', '')
                    text = elem.text
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)

            abstract = ' '.join(abstract_parts) if abstract_parts else ''

            # 논문 타입
            pub_types = [pt.text for pt in article.findall('.//PublicationType') if pt.text]

            return {
                'pmid': pmid,
                'title': title,
                'authors': authors,
                'journal': journal,
                'year': year,
                'abstract': abstract,
                'pub_types': pub_types,
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }

        except Exception as e:
            return None

    def extract_statistics(self, papers: List[Dict]) -> List[Dict]:
        """논문에서 통계 데이터 추출"""
        stats_findings = []

        stat_patterns = [
            r'(\d+\.?\d*)\s*%',  # 퍼센트
            r'(\d+\.?\d*)-fold',  # 배수
            r'[pP]\s*[<>=]\s*(0\.\d+)',  # p-value
            r'OR\s*[=:]\s*(\d+\.?\d*)',  # Odds Ratio
            r'RR\s*[=:]\s*(\d+\.?\d*)',  # Relative Risk
            r'HR\s*[=:]\s*(\d+\.?\d*)',  # Hazard Ratio
            r'CI\s*[=:]\s*(\d+\.?\d*)',  # Confidence Interval
            r'(\d+\.?\d*)\s*times',  # N times
            r'reduced?\s+by\s+(\d+\.?\d*)\s*%',  # reduced by X%
            r'increase[d]?\s+by\s+(\d+\.?\d*)\s*%',  # increased by X%
        ]

        for paper in papers:
            abstract = paper.get('abstract', '')
            if not abstract:
                continue

            # 문장 분리
            sentences = re.split(r'(?<=[.!?])\s+', abstract)

            for sentence in sentences:
                # 통계 패턴 검색
                has_stat = False
                for pattern in stat_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        has_stat = True
                        break

                if has_stat and 40 < len(sentence) < 500:
                    stats_findings.append({
                        'sentence': sentence,
                        'pmid': paper['pmid'],
                        'title': paper['title'],
                        'year': paper['year'],
                        'journal': paper['journal']
                    })

        # 연도 기준 정렬 (최신순)
        stats_findings.sort(key=lambda x: x.get('year', '0'), reverse=True)

        return stats_findings


def test_enhanced_search():
    """테스트"""
    searcher = EnhancedPubMedSearcher()

    keywords = ['GERD', 'orange juice', 'running']

    for kw in keywords:
        papers = searcher.search_comprehensive(kw, max_total=100)

        # 통계 추출
        stats = searcher.extract_statistics(papers)

        print(f"\n{'='*40}")
        print(f"{kw}: {len(papers)}개 논문, {len(stats)}개 통계 발견")
        print('='*40)

        for stat in stats[:5]:
            print(f"\n📊 {stat['sentence'][:150]}...")
            print(f"   → {stat['journal']} ({stat['year']}), PMID: {stat['pmid']}")


if __name__ == "__main__":
    test_enhanced_search()
