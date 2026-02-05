"""웹 검색을 통한 연관 키워드 추출 모듈"""
import requests
import urllib.parse
import time
from typing import List, Dict, Optional


class WebSearchKeywordExtractor:
    """Google Autocomplete와 DuckDuckGo를 사용한 연관 키워드 추출"""

    def __init__(self, delay: float = 0.5):
        """
        Args:
            delay: API 요청 간 대기 시간 (초)
        """
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def extract_related_keywords(self, keyword: str, max_keywords: int = 15) -> List[Dict]:
        """
        여러 소스에서 연관 키워드 추출

        Args:
            keyword: 기본 키워드
            max_keywords: 최대 키워드 개수

        Returns:
            연관 키워드 리스트 [{'keyword': str, 'source': str}, ...]
        """
        print(f"\n🔍 '{keyword}' 연관 키워드 검색 중...")

        all_keywords = []
        seen = set()

        # 1. Google Autocomplete
        google_keywords = self._google_autocomplete(keyword)
        for kw in google_keywords:
            if kw.lower() not in seen and kw.lower() != keyword.lower():
                seen.add(kw.lower())
                all_keywords.append({'keyword': kw, 'source': 'google'})

        time.sleep(self.delay)

        # 2. DuckDuckGo Related Topics
        ddg_keywords = self._duckduckgo_related(keyword)
        for kw in ddg_keywords:
            if kw.lower() not in seen and kw.lower() != keyword.lower():
                seen.add(kw.lower())
                all_keywords.append({'keyword': kw, 'source': 'duckduckgo'})

        time.sleep(self.delay)

        # 3. Google Autocomplete with suffixes
        suffixes = ['증상', '원인', '치료', '음식', '약', '운동', 'symptoms', 'treatment', 'diet', 'cause']
        for suffix in suffixes[:5]:  # 처음 5개만 시도
            suffix_keywords = self._google_autocomplete(f"{keyword} {suffix}")
            for kw in suffix_keywords[:2]:  # 각 suffix당 2개만
                if kw.lower() not in seen:
                    seen.add(kw.lower())
                    all_keywords.append({'keyword': kw, 'source': 'google_extended'})
            time.sleep(self.delay / 2)

        # 결과 제한
        result = all_keywords[:max_keywords]
        print(f"✓ {len(result)}개의 연관 키워드를 찾았습니다.")

        return result

    def _google_autocomplete(self, keyword: str) -> List[str]:
        """
        Google Autocomplete API를 사용한 키워드 추출
        (무료 비공식 API)
        """
        try:
            encoded = urllib.parse.quote(keyword)
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={encoded}"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list) and len(data) >= 2:
                suggestions = data[1]
                if isinstance(suggestions, list):
                    return [s for s in suggestions if isinstance(s, str)]

            return []

        except Exception as e:
            print(f"  ⚠️ Google Autocomplete 실패: {str(e)}")
            return []

    def _duckduckgo_related(self, keyword: str) -> List[str]:
        """
        DuckDuckGo Instant Answer API를 사용한 연관 키워드 추출
        """
        try:
            encoded = urllib.parse.quote(keyword)
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            keywords = []

            # Related Topics
            related = data.get('RelatedTopics', [])
            for item in related:
                if isinstance(item, dict):
                    # Direct topic
                    if 'Text' in item:
                        text = item['Text']
                        # 첫 번째 문장에서 키워드 추출
                        first_part = text.split('.')[0].split(',')[0]
                        if len(first_part) < 50:
                            keywords.append(first_part.strip())
                    # Subtopics
                    if 'Topics' in item:
                        for sub in item['Topics'][:3]:
                            if isinstance(sub, dict) and 'Text' in sub:
                                first_part = sub['Text'].split('.')[0].split(',')[0]
                                if len(first_part) < 50:
                                    keywords.append(first_part.strip())

            return keywords[:10]

        except Exception as e:
            print(f"  ⚠️ DuckDuckGo 실패: {str(e)}")
            return []

    def get_search_queries(self, keyword: str, related_keywords: List[Dict]) -> List[str]:
        """
        기본 키워드와 연관 키워드를 조합하여 검색 쿼리 생성

        Args:
            keyword: 기본 키워드
            related_keywords: 연관 키워드 리스트

        Returns:
            검색 쿼리 리스트
        """
        queries = [keyword]  # 기본 키워드

        for item in related_keywords:
            kw = item['keyword']
            # 이미 기본 키워드가 포함되어 있으면 그대로 사용
            if keyword.lower() in kw.lower():
                queries.append(kw)
            else:
                # 기본 키워드와 조합
                queries.append(f"{keyword} {kw}")

        return queries


def main():
    """테스트 실행"""
    extractor = WebSearchKeywordExtractor()

    test_keywords = ["역류성식도염", "GERD"]

    for keyword in test_keywords:
        print(f"\n{'='*60}")
        print(f"테스트: {keyword}")
        print('='*60)

        related = extractor.extract_related_keywords(keyword, max_keywords=10)

        print("\n📋 연관 키워드:")
        for i, item in enumerate(related, 1):
            print(f"  {i}. {item['keyword']} (소스: {item['source']})")

        queries = extractor.get_search_queries(keyword, related)
        print("\n🔍 생성된 검색 쿼리:")
        for i, query in enumerate(queries[:5], 1):
            print(f"  {i}. {query}")


if __name__ == "__main__":
    main()
