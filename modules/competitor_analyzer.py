"""
경쟁 블로그 분석 모듈
- 키워드로 기존 블로그 검색
- 내용 스크래핑 및 저장
- 주요 포인트 추출
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import time
import re
from urllib.parse import quote_plus, urljoin


class CompetitorAnalyzer:
    """경쟁 블로그 분석기"""

    def __init__(self, output_dir: str = "competitor_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def search_and_analyze(self, keyword: str, max_blogs: int = 20) -> Dict:
        """
        키워드로 블로그 검색 후 분석

        Args:
            keyword: 검색 키워드
            max_blogs: 분석할 최대 블로그 수 (기본 20개)

        Returns:
            {
                'keyword': str,
                'blogs': List[Dict],  # 개별 블로그 정보
                'common_points': List[str],  # 공통적으로 언급되는 내용
                'all_text': str,  # 전체 텍스트 (비교용)
                'saved_path': str  # 저장된 파일 경로
            }
        """
        print(f"\n[경쟁 블로그 분석] '{keyword}' 검색 중...")

        # 1. 여러 소스에서 블로그 URL 수집
        blog_urls = []

        # 다양한 검색어 조합 생성 (네이버 페이지네이션이 JS 기반이라 다양한 쿼리로 보완)
        search_queries = self._generate_search_queries(keyword)
        print(f"  → 검색어 조합 {len(search_queries)}개 사용")

        for i, query in enumerate(search_queries):
            if len(blog_urls) >= max_blogs * 2:  # 충분히 수집되면 중단
                break

            # 네이버 블로그 검색 (POST 탭)
            naver_post = self._search_naver_post(query, 10)
            blog_urls.extend(naver_post)

            time.sleep(0.5)

            # 네이버 VIEW 탭
            naver_view = self._search_naver_view(query, 10)
            blog_urls.extend(naver_view)

            time.sleep(0.5)

        # 중복 제거 후 현재 수 확인
        blog_urls = list(dict.fromkeys(blog_urls))
        print(f"  → 네이버 검색: {len(blog_urls)}개")

        # 티스토리 검색
        tistory = self._search_tistory(keyword, max_blogs // 2)
        blog_urls.extend(tistory)
        print(f"  → 티스토리: {len(tistory)}개 추가")

        time.sleep(0.5)

        # 구글 검색 (추가 소스)
        google = self._search_google_blogs(keyword, max_blogs // 2)
        blog_urls.extend(google)
        print(f"  → 구글: {len(google)}개 추가")

        # 최종 중복 제거
        blog_urls = list(dict.fromkeys(blog_urls))[:max_blogs]
        print(f"  → 총 {len(blog_urls)}개 고유 블로그 URL")

        # 2. 각 블로그 내용 스크래핑
        blogs = []
        all_text_parts = []

        for i, url in enumerate(blog_urls):
            print(f"  → [{i+1}/{len(blog_urls)}] 스크래핑 중...")
            blog_data = self._scrape_blog(url)
            if blog_data and blog_data.get('content') and len(blog_data['content']) > 200:
                blogs.append(blog_data)
                all_text_parts.append(blog_data['content'])
                print(f"      ✓ {blog_data.get('title', 'N/A')[:30]}... ({len(blog_data['content'])}자)")
            else:
                print(f"      ✗ 스크래핑 실패 또는 내용 부족")
            time.sleep(0.5)  # 요청 간격

        print(f"  → {len(blogs)}개 블로그 스크래핑 완료")

        # 3. 공통 포인트 추출
        all_text = "\n\n---\n\n".join(all_text_parts)
        common_points = self._extract_common_points(blogs, keyword)

        # 4. 결과 저장
        result = {
            'keyword': keyword,
            'search_date': datetime.now().isoformat(),
            'blog_count': len(blogs),
            'blogs': blogs,
            'common_points': common_points,
            'all_text': all_text
        }

        # 파일로 저장
        safe_keyword = re.sub(r'[^\w\s가-힣]', '', keyword).replace(' ', '_')
        save_path = os.path.join(self.output_dir, f"{safe_keyword}_{datetime.now().strftime('%Y%m%d')}.json")

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        result['saved_path'] = save_path
        print(f"  → 저장 완료: {save_path}")

        return result

    def _generate_search_queries(self, keyword: str) -> List[str]:
        """검색어 조합 생성 (다양한 블로그 수집용)"""
        # 기본 키워드
        queries = [keyword]

        # 다양한 확장 쿼리
        suffixes = [
            '증상', '원인', '치료', '음식', '약', '병원',
            '좋은음식', '나쁜음식', '예방', '자연치료',
            '생활습관', '후기', '경험', '완치'
        ]
        for suffix in suffixes:
            queries.append(f"{keyword} {suffix}")

        return queries[:10]  # 최대 10개 쿼리 사용

    def _search_naver_post(self, keyword: str, max_results: int = 20) -> List[str]:
        """네이버 블로그 검색 (POST 탭) - 페이지네이션 포함"""
        urls = []
        pages_to_fetch = (max_results // 10) + 2  # 충분한 페이지 수

        for page in range(pages_to_fetch):
            if len(urls) >= max_results:
                break

            start = page * 10 + 1
            try:
                search_url = f"https://search.naver.com/search.naver?where=post&query={quote_plus(keyword)}&start={start}"
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                found_in_page = 0
                # 모든 a 태그에서 블로그 링크 추출
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    # 네이버 블로그 포스트 링크
                    if 'blog.naver.com' in href and re.search(r'/\d+$', href):
                        if href not in urls:
                            urls.append(href)
                            found_in_page += 1
                    if len(urls) >= max_results:
                        break

                # 결과가 없으면 더 이상 페이지 없음
                if found_in_page == 0:
                    break

                time.sleep(0.3)  # 요청 간격

            except Exception as e:
                print(f"    네이버 POST 검색 오류 (page {page+1}): {e}")
                break

        return urls

    def _search_naver_view(self, keyword: str, max_results: int = 20) -> List[str]:
        """네이버 VIEW 탭 검색 (블로그+카페 통합) - 페이지네이션 포함"""
        urls = []
        pages_to_fetch = (max_results // 10) + 2

        for page in range(pages_to_fetch):
            if len(urls) >= max_results:
                break

            start = page * 10 + 1
            try:
                search_url = f"https://search.naver.com/search.naver?where=view&query={quote_plus(keyword)}&start={start}"
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                found_in_page = 0
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    # 네이버 블로그
                    if 'blog.naver.com' in href and re.search(r'/\d+$', href):
                        if href not in urls:
                            urls.append(href)
                            found_in_page += 1
                    # 포스트
                    elif 'post.naver.com' in href:
                        if href not in urls:
                            urls.append(href)
                            found_in_page += 1
                    if len(urls) >= max_results:
                        break

                if found_in_page == 0:
                    break

                time.sleep(0.3)

            except Exception as e:
                print(f"    네이버 VIEW 검색 오류 (page {page+1}): {e}")
                break

        return urls

    def _search_tistory(self, keyword: str, max_results: int = 10) -> List[str]:
        """티스토리 블로그 검색 (다음 검색 활용) - 페이지네이션 포함"""
        urls = []
        pages_to_fetch = (max_results // 10) + 2

        for page in range(1, pages_to_fetch + 1):
            if len(urls) >= max_results:
                break

            try:
                # 다음 검색에서 티스토리 검색
                search_url = f"https://search.daum.net/search?w=blog&q={quote_plus(keyword)}&p={page}"
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                found_in_page = 0
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'tistory.com' in href and href.startswith('http'):
                        # 리다이렉트 URL 제외
                        if 'search.daum.net' not in href and 'r.search.daum.net' not in href:
                            if href not in urls:
                                urls.append(href)
                                found_in_page += 1
                    if len(urls) >= max_results:
                        break

                if found_in_page == 0:
                    break

                time.sleep(0.3)

            except Exception as e:
                print(f"    티스토리 검색 오류 (page {page}): {e}")
                break

        return urls

    def _search_google_blogs(self, keyword: str, max_results: int = 10) -> List[str]:
        """구글에서 한국 건강 블로그 검색"""
        urls = []
        try:
            # 구글 검색 (네이버/티스토리 블로그 대상)
            search_url = f"https://www.google.com/search?q={quote_plus(keyword)}+site:blog.naver.com+OR+site:tistory.com&num={max_results}&hl=ko"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            for a in soup.find_all('a', href=True):
                href = a['href']
                # 구글 리다이렉트 URL에서 실제 URL 추출
                if '/url?q=' in href:
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    if ('blog.naver.com' in actual_url or 'tistory.com' in actual_url):
                        if actual_url not in urls:
                            urls.append(actual_url)
                elif ('blog.naver.com' in href or 'tistory.com' in href) and href.startswith('http'):
                    if href not in urls:
                        urls.append(href)
                if len(urls) >= max_results:
                    break

        except Exception as e:
            print(f"    구글 검색 오류: {e}")

        return urls

    def _scrape_blog(self, url: str) -> Optional[Dict]:
        """블로그 내용 스크래핑"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 제목 추출
            title = ""
            title_selectors = ['h1', '.tit_view', '.se-title-text', '.title',
                              '.tt_article_useless_p_margin h1', '.entry-title', 'title']
            for selector in title_selectors:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text(strip=True)
                    if title:
                        break

            # 본문 추출 (여러 패턴 시도)
            content = ""
            content_selectors = [
                '.se-main-container',  # 네이버 스마트에디터
                '#post-view-container',  # 네이버 새버전
                '.se_component_wrap',
                '.post_ct',
                '.post-content',
                '.article-content',
                '.entry-content',
                '.tt_article_useless_p_margin',  # 티스토리
                '.contents_style',  # 티스토리
                '#content',
                'article',
            ]

            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    # 스크립트, 스타일 태그 제거
                    for tag in elem.select('script, style, nav, footer, header, .btn, .comment'):
                        tag.decompose()
                    content = elem.get_text(separator='\n', strip=True)
                    if len(content) > 200:
                        break

            # 네이버 블로그 iframe 처리
            if 'blog.naver.com' in url and len(content) < 200:
                iframe = soup.select_one('iframe#mainFrame')
                if iframe:
                    iframe_src = iframe.get('src', '')
                    if iframe_src:
                        if not iframe_src.startswith('http'):
                            iframe_src = urljoin(url, iframe_src)
                        return self._scrape_blog(iframe_src)

            if not content or len(content) < 100:
                return None

            # 텍스트 정리
            content = self._clean_text(content)

            return {
                'url': url,
                'title': title[:100] if title else 'N/A',
                'content': content,
                'content_length': len(content),
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            return None

    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 연속 공백/줄바꿈 정리
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\t+', ' ', text)

        # 불필요한 문구 제거
        noise_patterns = [
            r'공감\d*',
            r'댓글\d*',
            r'구독하기',
            r'좋아요\d*',
            r'이웃추가',
            r'맨 위로',
            r'URL 복사',
            r'신고하기',
            r'본문 기타 기능',
            r'이 글에 공감한 블로거',
        ]
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text)

        return text.strip()

    def _extract_common_points(self, blogs: List[Dict], keyword: str) -> List[str]:
        """블로그들에서 공통적으로 언급되는 포인트 추출"""
        if not blogs:
            return []

        common_points = []

        # 키워드별 체크 패턴
        health_keywords = ['역류성식도염', 'GERD', '위식도역류', '식도염']
        if any(kw in keyword for kw in health_keywords):
            check_phrases = [
                ('커피', '카페인'),
                ('초콜릿',),
                ('술', '알코올', '음주'),
                ('기름진', '지방', '튀김'),
                ('매운', '자극적'),
                ('왼쪽', '수면 자세', '옆으로'),
                ('체중', '비만', 'BMI'),
                ('금연', '담배', '흡연'),
                ('PPI', '프로톤펌프', '양성자펌프억제제', '위산억제제'),
                ('바렛', 'Barrett', '바렛식도'),
                ('위산', '역류', '산역류'),
                ('괄약근', 'LES'),
                ('내시경',),
                ('스트레스',),
            ]
        else:
            # 일반적인 건강 관련 패턴
            check_phrases = [
                ('원인',),
                ('증상',),
                ('치료',),
                ('예방',),
                ('음식', '식이', '식단'),
                ('운동',),
                ('약', '약물'),
                ('병원', '진료'),
                ('부작용',),
                ('효과',),
            ]

        # 각 패턴이 얼마나 많은 블로그에서 언급되는지 확인
        for phrases in check_phrases:
            count = 0
            for blog in blogs:
                content = blog.get('content', '').lower()
                if any(phrase.lower() in content for phrase in phrases):
                    count += 1

            percentage = (count / len(blogs)) * 100 if blogs else 0
            if count >= 2 and percentage >= 40:  # 40% 이상에서 언급
                common_points.append(f"[{count}/{len(blogs)}개, {percentage:.0f}%] {'/'.join(phrases)}")

        return common_points

    def load_competitor_data(self, keyword: str) -> Optional[Dict]:
        """저장된 경쟁 블로그 데이터 로드"""
        safe_keyword = re.sub(r'[^\w\s가-힣]', '', keyword).replace(' ', '_')

        # 오늘 날짜 파일 먼저 확인
        today_path = os.path.join(self.output_dir, f"{safe_keyword}_{datetime.now().strftime('%Y%m%d')}.json")
        if os.path.exists(today_path):
            with open(today_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 가장 최근 파일 찾기
        import glob
        files = glob.glob(os.path.join(self.output_dir, f"{safe_keyword}_*.json"))
        if files:
            latest_file = max(files, key=os.path.getctime)
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return None


class NoveltyFinder:
    """
    논문과 기존 블로그 비교하여 새로운 사실 찾기
    """

    def __init__(self):
        self.positive_keywords = [
            '효과적', '개선', '감소', '예방', '도움', '좋은', '긍정적',
            'effective', 'improve', 'reduce', 'prevent', 'benefit', 'positive',
            'decrease', 'lower', 'protect', 'enhance'
        ]
        self.negative_keywords = [
            '위험', '증가', '악화', '부작용', '주의', '나쁜', '부정적',
            'risk', 'increase', 'worsen', 'adverse', 'caution', 'negative',
            'higher', 'elevate', 'damage', 'harmful'
        ]

    def find_novel_facts(self,
                         papers: List[Dict],
                         competitor_data: Dict,
                         min_novelty_score: float = 0.3) -> List[Dict]:
        """
        논문에서 기존 블로그에 없는 새로운 사실 찾기
        """
        existing_text = competitor_data.get('all_text', '').lower()
        novel_facts = []

        for paper in papers:
            abstract = paper.get('abstract', '')
            title = paper.get('title', '')
            pmid = paper.get('pmid', '')
            journal = paper.get('journal', 'Unknown Journal')
            year = paper.get('year', '')

            if not abstract:
                continue

            # 문장 단위로 분리
            sentences = self._split_sentences(abstract)

            for sentence in sentences:
                # 의미있는 문장인지 확인
                if len(sentence) < 30 or len(sentence) > 500:
                    continue

                # 숫자/통계가 포함된 문장 우선
                has_stats = bool(re.search(r'\d+\.?\d*\s*%|\d+\.?\d*-fold|p\s*[<>=]\s*0\.\d+|\d+\s*times', sentence))

                # 새로움 점수 계산
                novelty_score = self._calculate_novelty(sentence, existing_text)

                if novelty_score >= min_novelty_score or (has_stats and novelty_score >= 0.2):
                    sentiment = self._detect_sentiment(sentence)
                    category = self._detect_category(sentence)

                    novel_facts.append({
                        'fact': sentence,
                        'source': f"{title}",
                        'source_pmid': pmid,
                        'journal': journal,
                        'year': year,
                        'sentiment': sentiment,
                        'novelty_score': novelty_score,
                        'has_statistics': has_stats,
                        'category': category
                    })

        # 새로움 점수로 정렬
        novel_facts.sort(key=lambda x: (x['has_statistics'], x['novelty_score']), reverse=True)

        return novel_facts

    def _split_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_novelty(self, sentence: str, existing_text: str) -> float:
        """새로움 점수 계산 (0-1)"""
        sentence_lower = sentence.lower()

        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'and', 'or', 'but', 'if', 'then', 'else', 'when', 'where',
                     'that', 'this', 'these', 'those', 'it', 'its', 'of', 'in',
                     'to', 'for', 'with', 'on', 'at', 'by', 'from', 'as', 'into'}

        words = re.findall(r'\b[a-z가-힣]{3,}\b', sentence_lower)
        keywords = [w for w in words if w not in stopwords]

        if not keywords:
            return 0.0

        novel_count = sum(1 for kw in keywords if kw not in existing_text)
        novelty_ratio = novel_count / len(keywords)

        sentence_ngrams = self._get_ngrams(sentence_lower, 3)
        existing_ngrams = self._get_ngrams(existing_text, 3)

        if sentence_ngrams:
            overlap = len(sentence_ngrams & existing_ngrams) / len(sentence_ngrams)
            novelty_ratio = novelty_ratio * (1 - overlap * 0.5)

        return min(1.0, novelty_ratio)

    def _get_ngrams(self, text: str, n: int) -> set:
        """n-gram 추출"""
        words = text.split()
        return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))

    def _detect_sentiment(self, sentence: str) -> str:
        """감성 분석"""
        sentence_lower = sentence.lower()

        pos_count = sum(1 for kw in self.positive_keywords if kw in sentence_lower)
        neg_count = sum(1 for kw in self.negative_keywords if kw in sentence_lower)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _detect_category(self, sentence: str) -> str:
        """카테고리 분류"""
        sentence_lower = sentence.lower()

        categories = {
            'treatment': ['treatment', 'therapy', 'drug', 'medication', 'ppi', 'surgery', 'intervention'],
            'diet': ['diet', 'food', 'meal', 'nutrition', 'eating', 'coffee', 'alcohol', 'intake'],
            'lifestyle': ['lifestyle', 'sleep', 'exercise', 'weight', 'smoking', 'stress', 'physical activity'],
            'cause': ['cause', 'mechanism', 'pathophysiology', 'etiology', 'risk factor', 'associated'],
            'diagnosis': ['diagnosis', 'diagnostic', 'endoscopy', 'screening', 'detection'],
            'complications': ['complication', 'barrett', 'cancer', 'stricture', 'progression', 'adenocarcinoma'],
            'prevention': ['prevention', 'preventive', 'protective', 'prophylaxis'],
        }

        for category, keywords in categories.items():
            if any(kw in sentence_lower for kw in keywords):
                return category

        return 'general'

    def summarize_novel_findings(self, novel_facts: List[Dict], top_n: int = 20) -> Dict:
        """새로운 발견들 요약"""
        summary = {
            'total_novel_facts': len(novel_facts),
            'by_sentiment': {
                'positive': [],
                'negative': [],
                'neutral': []
            },
            'by_category': {},
            'top_findings': [],
            'statistics_findings': []
        }

        for fact in novel_facts[:top_n]:
            sentiment = fact['sentiment']
            category = fact['category']

            summary['by_sentiment'][sentiment].append(fact)

            if category not in summary['by_category']:
                summary['by_category'][category] = []
            summary['by_category'][category].append(fact)

            if fact['has_statistics']:
                summary['statistics_findings'].append(fact)

        summary['top_findings'] = novel_facts[:top_n]

        return summary


# CLI 테스트
if __name__ == "__main__":
    import sys

    keyword = sys.argv[1] if len(sys.argv) > 1 else "역류성식도염"

    analyzer = CompetitorAnalyzer()
    result = analyzer.search_and_analyze(keyword, max_blogs=20)

    print(f"\n{'='*60}")
    print(f"분석 결과")
    print(f"{'='*60}")
    print(f"키워드: {result['keyword']}")
    print(f"수집된 블로그: {result['blog_count']}개")
    print(f"\n공통 포인트:")
    for point in result['common_points']:
        print(f"  - {point}")
    print(f"\n저장 위치: {result['saved_path']}")
