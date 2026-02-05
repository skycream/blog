"""
토픽 추출 모듈
- 인기 블로그에서 LLM을 활용해 서브토픽 추출
- 독자 관심사 기반 키워드 발굴
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple
import time
import re
from urllib.parse import quote_plus
from collections import Counter
from anthropic import Anthropic

# 상위 디렉토리에서 Config 가져오기
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class BlogTopicExtractor:
    """블로그에서 LLM 기반 토픽 추출"""

    def __init__(self, output_dir: str = "topic_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9',
        }

        # Anthropic 클라이언트 (Config에서 API 키 로드)
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def extract_topics(self, main_keyword: str, max_blogs: int = 20) -> Dict:
        """
        메인 키워드로 블로그 검색 후 서브토픽 추출

        Args:
            main_keyword: 메인 검색 키워드 (예: "역류성식도염")
            max_blogs: 분석할 블로그 수

        Returns:
            {
                'main_keyword': str,
                'blogs_analyzed': int,
                'topics': List[Dict],  # 추출된 토픽들
                'topic_counts': Dict[str, int],  # 토픽별 언급 횟수
                'top_topics': List[str],  # 상위 토픽
                'search_queries': List[str],  # 논문 검색용 쿼리
            }
        """
        print(f"\n{'='*60}")
        print(f"[토픽 추출] '{main_keyword}' 분석 시작")
        print(f"{'='*60}")

        # 1. 블로그 URL 수집
        print(f"\n[1단계] 인기 블로그 수집 중...")
        blog_urls = self._collect_blog_urls(main_keyword, max_blogs)
        print(f"  → {len(blog_urls)}개 블로그 URL 수집")

        # 2. 블로그 내용 스크래핑
        print(f"\n[2단계] 블로그 내용 스크래핑 중...")
        blogs = self._scrape_blogs(blog_urls)
        print(f"  → {len(blogs)}개 블로그 스크래핑 완료")

        # 3. LLM으로 각 블로그에서 토픽 추출
        print(f"\n[3단계] LLM 토픽 추출 중...")
        all_topics = []
        for i, blog in enumerate(blogs):
            print(f"  → [{i+1}/{len(blogs)}] {blog['title'][:30]}... 분석 중")
            topics = self._extract_topics_from_blog(main_keyword, blog)
            all_topics.extend(topics)
            print(f"      추출된 토픽: {topics}")
            time.sleep(0.5)  # API 속도 제한

        # 4. 토픽 집계
        print(f"\n[4단계] 토픽 집계 중...")
        topic_counts = Counter(all_topics)
        top_topics = [topic for topic, count in topic_counts.most_common(15)]
        print(f"  → 총 {len(set(all_topics))}개 고유 토픽 발견")
        print(f"  → 상위 토픽: {top_topics[:10]}")

        # 5. 논문 검색용 쿼리 생성
        search_queries = self._generate_search_queries(main_keyword, top_topics)

        # 6. 결과 저장
        result = {
            'main_keyword': main_keyword,
            'analysis_date': datetime.now().isoformat(),
            'blogs_analyzed': len(blogs),
            'blogs': [{'url': b['url'], 'title': b['title']} for b in blogs],
            'all_topics': all_topics,
            'topic_counts': dict(topic_counts),
            'top_topics': top_topics,
            'search_queries': search_queries
        }

        save_path = os.path.join(
            self.output_dir,
            f"{main_keyword}_topics_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        result['saved_path'] = save_path
        print(f"\n  → 저장 완료: {save_path}")

        return result

    def _collect_blog_urls(self, keyword: str, max_count: int) -> List[str]:
        """네이버에서 블로그 URL 수집"""
        urls = []
        seen = set()

        # 다양한 검색어로 수집
        search_terms = [
            keyword,
            f"{keyword} 증상",
            f"{keyword} 원인",
            f"{keyword} 치료",
            f"{keyword} 음식",
            f"{keyword} 후기",
        ]

        for term in search_terms:
            if len(urls) >= max_count:
                break

            # 네이버 VIEW 탭
            try:
                search_url = f"https://search.naver.com/search.naver?where=view&query={quote_plus(term)}"
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'blog.naver.com' in href and re.search(r'/\d+$', href):
                        if href not in seen:
                            seen.add(href)
                            urls.append(href)
                            if len(urls) >= max_count:
                                break

                time.sleep(0.3)
            except Exception as e:
                print(f"    검색 오류 ({term}): {e}")

        return urls[:max_count]

    def _scrape_blogs(self, urls: List[str]) -> List[Dict]:
        """블로그 내용 스크래핑"""
        blogs = []

        for url in urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')

                # 제목 추출
                title = ""
                for selector in ['h1', '.se-title-text', '.title', 'title']:
                    elem = soup.select_one(selector)
                    if elem:
                        title = elem.get_text(strip=True)
                        if title:
                            break

                # 본문 추출
                content = ""
                content_selectors = [
                    '.se-main-container',
                    '#post-view-container',
                    '.post_ct',
                    'article',
                ]

                for selector in content_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        for tag in elem.select('script, style, nav, footer'):
                            tag.decompose()
                        content = elem.get_text(separator='\n', strip=True)
                        if len(content) > 200:
                            break

                # iframe 처리 (네이버 블로그)
                if len(content) < 200:
                    iframe = soup.select_one('iframe#mainFrame')
                    if iframe:
                        iframe_src = iframe.get('src', '')
                        if iframe_src and not iframe_src.startswith('http'):
                            iframe_src = f"https://blog.naver.com{iframe_src}"
                        if iframe_src:
                            response2 = requests.get(iframe_src, headers=self.headers, timeout=15)
                            soup2 = BeautifulSoup(response2.text, 'html.parser')
                            for selector in content_selectors:
                                elem = soup2.select_one(selector)
                                if elem:
                                    content = elem.get_text(separator='\n', strip=True)
                                    if len(content) > 200:
                                        break

                if content and len(content) > 200:
                    # 텍스트 길이 제한 (토큰 절약)
                    content = content[:3000]
                    blogs.append({
                        'url': url,
                        'title': title[:100] if title else 'N/A',
                        'content': content
                    })

                time.sleep(0.3)

            except Exception as e:
                continue

        return blogs

    def _extract_topics_from_blog(self, main_keyword: str, blog: Dict) -> List[str]:
        """LLM으로 블로그에서 서브토픽 추출"""
        prompt = f"""다음은 "{main_keyword}"에 관한 블로그 글입니다.

제목: {blog['title']}
내용:
{blog['content'][:2000]}

이 글에서 "{main_keyword}"와 연관된 **서브토픽/키워드**를 추출해주세요.
예를 들어 "{main_keyword}과 커피의 관계", "{main_keyword}과 수면 자세" 등의 관계에서 "커피", "수면 자세" 같은 서브토픽입니다.

규칙:
1. 2-4개의 핵심 서브토픽만 추출
2. 한글로 작성 (영어 X)
3. 너무 일반적인 단어 제외 (증상, 원인, 치료 등)
4. 구체적이고 검색 가능한 키워드 선호 (예: 커피, 수면자세, PPI약물, 위내시경 등)
5. 쉼표로 구분하여 한 줄로 출력

출력 예시: 커피, 수면 자세, 체중 감량"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            # 응답 파싱
            text = response.content[0].text.strip()
            topics = [t.strip() for t in text.split(',') if t.strip()]

            # 너무 일반적인 키워드 필터링
            general_words = {'증상', '원인', '치료', '방법', '정보', '건강', '질환', '질병', '예방'}
            topics = [t for t in topics if t not in general_words and len(t) >= 2]

            return topics[:4]

        except Exception as e:
            print(f"      LLM 오류: {e}")
            return []

    def _generate_search_queries(self, main_keyword: str, topics: List[str]) -> List[str]:
        """PubMed 검색용 쿼리 생성"""
        # 한글 → 영문 매핑 (일반적인 건강 관련)
        kr_to_en = {
            '커피': 'coffee',
            '카페인': 'caffeine',
            '수면': 'sleep',
            '수면 자세': 'sleep position',
            '수면자세': 'sleep position',
            '체중': 'weight',
            '비만': 'obesity',
            '스트레스': 'stress',
            '식이': 'diet',
            '음식': 'food',
            '알코올': 'alcohol',
            '술': 'alcohol',
            '운동': 'exercise',
            '흡연': 'smoking',
            '담배': 'smoking',
            '약': 'medication',
            '약물': 'drug',
            'PPI': 'PPI',
            '수술': 'surgery',
            '내시경': 'endoscopy',
            '임신': 'pregnancy',
            '나이': 'age',
            '고령': 'elderly',
        }

        # 메인 키워드 영문 변환
        main_en = {
            '역류성식도염': 'GERD',
            '역류성 식도염': 'GERD',
            '위식도역류질환': 'GERD',
            '당뇨': 'diabetes',
            '고혈압': 'hypertension',
            '비타민D': 'vitamin D',
        }.get(main_keyword, main_keyword)

        queries = []
        for topic in topics:
            topic_en = kr_to_en.get(topic, topic)
            query = f"{main_en} AND {topic_en}"
            if query not in queries:
                queries.append(query)

        return queries


# CLI 테스트
if __name__ == "__main__":
    import sys

    keyword = sys.argv[1] if len(sys.argv) > 1 else "역류성식도염"

    extractor = BlogTopicExtractor()
    result = extractor.extract_topics(keyword, max_blogs=10)  # 테스트용 10개

    print(f"\n{'='*60}")
    print(f"최종 결과")
    print(f"{'='*60}")
    print(f"분석 블로그 수: {result['blogs_analyzed']}")
    print(f"\n토픽별 언급 횟수:")
    for topic, count in sorted(result['topic_counts'].items(), key=lambda x: -x[1])[:15]:
        print(f"  {topic}: {count}회")
    print(f"\n논문 검색 쿼리:")
    for q in result['search_queries'][:10]:
        print(f"  {q}")
