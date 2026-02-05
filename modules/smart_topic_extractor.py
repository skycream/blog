"""
스마트 토픽 추출 모듈
- 인기 블로그 수집 → 자동 토픽 추출
- 빈도 기반 + 패턴 매칭으로 새로운 트렌드 키워드 자동 발견
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

# Claude CLI 기반 토픽 추출 모듈
from modules.claude_topic_extractor import extract_topics_with_claude


class SmartTopicExtractor:
    """블로그에서 독자 관심 토픽 추출"""

    # 건강 관련 토픽 키워드 사전
    TOPIC_KEYWORDS = {
        # 음식/식이
        '양배추': ['양배추'],
        '바나나': ['바나나'],
        '오트밀': ['오트밀', '귀리'],
        '커피': ['커피', '카페인'],
        '술': ['술', '음주', '알코올'],
        '기름진음식': ['기름진', '튀김', '지방'],
        '매운음식': ['매운', '자극적', '맵고'],
        '야식': ['야식', '늦은 식사', '밤에 먹'],
        '초콜릿': ['초콜릿', '초콜렛'],
        '탄산음료': ['탄산', '콜라', '사이다'],

        # 생활습관
        '수면자세': ['수면 자세', '수면자세', '잠자는 자세', '누워', '베개'],
        '스트레스': ['스트레스'],
        '운동': ['운동', '헬스', '조깅'],
        '흡연': ['흡연', '담배'],
        '체중': ['체중', '비만', 'BMI', '살'],
        '과식': ['과식', '폭식', '많이 먹'],

        # 해부/병리
        '하부식도괄약근': ['괄약근', 'LES', '조임근'],
        '위산': ['위산', '산역류'],
        '바렛식도': ['바렛', 'Barrett', '바렛식도'],
        '식도협착': ['협착', '좁아'],

        # 증상
        '기침': ['기침'],
        '가래': ['가래'],
        '목이물감': ['목 이물', '목이물', '걸린 듯'],
        '가슴쓰림': ['가슴 쓰', '가슴쓰', '속쓰림', '속 쓰림'],
        '신물': ['신물', '신맛'],

        # 치료
        '약물치료': ['PPI', '위산억제', '약물', '에소메프라졸', '오메프라졸'],
        '한방치료': ['한방', '한의원', '침 치료', '침치료', '한약'],
        '수술': ['수술', '복강경'],
        '내시경': ['내시경'],

        # 기타
        '재발': ['재발', '다시'],
        '만성': ['만성', '오래'],
        '나이': ['나이', '노화', '중년', '고령'],
        '임신': ['임신', '임산부'],
    }

    # 한글 → 영문 매핑 (PubMed 검색용)
    KR_TO_EN = {
        '양배추': 'cabbage',
        '바나나': 'banana',
        '오트밀': 'oatmeal',
        '커피': 'coffee caffeine',
        '술': 'alcohol',
        '기름진음식': 'fatty food',
        '매운음식': 'spicy food',
        '야식': 'late night eating',
        '초콜릿': 'chocolate',
        '탄산음료': 'carbonated beverage',
        '수면자세': 'sleep position',
        '스트레스': 'stress psychological',
        '운동': 'exercise physical activity',
        '흡연': 'smoking',
        '체중': 'obesity weight',
        '과식': 'overeating meal size',
        '하부식도괄약근': 'lower esophageal sphincter LES',
        '위산': 'gastric acid',
        '바렛식도': 'Barrett esophagus',
        '식도협착': 'esophageal stricture',
        '기침': 'chronic cough',
        '목이물감': 'globus sensation',
        '약물치료': 'PPI proton pump inhibitor',
        '한방치료': 'acupuncture traditional medicine',
        '수술': 'surgery fundoplication',
        '내시경': 'endoscopy',
        '재발': 'recurrence relapse',
        '나이': 'age elderly',
        '임신': 'pregnancy',
        '가슴쓰림': 'heartburn',
        '신물': 'acid regurgitation',
        '만성': 'chronic',
        '가래': 'phlegm mucus',
    }

    def __init__(self, output_dir: str = "topic_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9',
        }

    def extract_topics(self, main_keyword: str, max_blogs: int = 20) -> Dict:
        """
        메인 키워드로 블로그 검색 후 서브토픽 추출
        - 규칙 기반 추출 (기본) + LLM 분석용 데이터 저장

        Returns:
            {
                'main_keyword': str,
                'blogs_analyzed': int,
                'topic_counts': Dict[str, int],
                'top_topics': List[str],
                'search_queries': List[str],  # PubMed 검색용
                'llm_analysis_file': str,  # Claude CLI 분석용 파일 경로
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

        # 3. Claude CLI로 토픽 추출
        print(f"\n[3단계] Claude CLI로 토픽 추출 중...")
        auto_result = extract_topics_with_claude(blogs, main_keyword)

        # 자동 추출된 토픽
        auto_topics = auto_result.get('topics', [])
        trending = auto_result.get('trending', [])

        print(f"  → Claude 추출: {len(auto_topics)}개 토픽 발견")
        if trending:
            print(f"  → 트렌딩 키워드: {[t['topic'] for t in trending[:5]]}")

        # 4. 토픽 집계 (자동 추출 결과 사용)
        topic_counts = auto_result.get('topic_counts', {})

        # 상위 토픽 (빈도순)
        top_topics = [t['topic'] for t in auto_topics[:15]]

        # 트렌딩 키워드도 추가 (영어 용어 등)
        for t in trending[:5]:
            if t['topic'] not in top_topics:
                top_topics.append(t['topic'])

        # 5. LLM 분석용 데이터 저장 (Claude CLI가 분석할 수 있도록)
        print(f"\n[4단계] LLM 분석용 데이터 저장 중...")
        llm_analysis_file = self._save_for_llm_analysis(blogs, main_keyword)
        print(f"  → LLM 분석 파일: {llm_analysis_file}")

        # 6. 논문 검색용 쿼리 생성 (자동 번역 포함)
        main_en = self._get_main_keyword_english(main_keyword)
        search_queries = []
        for topic in top_topics[:12]:
            topic_en = self._get_topic_english(topic)
            query = f"{main_en} AND {topic_en}"
            search_queries.append(query)

        # 7. 결과 저장
        result = {
            'main_keyword': main_keyword,
            'main_keyword_en': main_en,
            'analysis_date': datetime.now().isoformat(),
            'blogs_analyzed': len(blogs),
            'blogs': [{'url': b['url'], 'title': b['title'], 'content_preview': b['content'][:500]} for b in blogs],
            'topic_counts': dict(topic_counts),
            'top_topics': top_topics,
            'topics': auto_topics,  # [{topic, count, category}, ...]
            'by_category': auto_result.get('by_category', {}),
            'trending': trending,  # [{topic, count, category}, ...]
            'trending_topics': [t['topic'] for t in trending],
            'search_queries': search_queries,
            'llm_analysis_file': llm_analysis_file,
        }

        save_path = os.path.join(
            self.output_dir,
            f"{main_keyword}_topics_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        result['saved_path'] = save_path
        print(f"\n  → 저장 완료: {save_path}")
        print(f"\n{'='*60}")
        print(f"[Claude 토픽 추출 완료]")
        print(f"  - 발견된 토픽: {len(top_topics)}개")
        if trending:
            print(f"  - 트렌딩 키워드: {[t['topic'] for t in trending[:3]]}")
        print(f"  - 검색 쿼리: {len(search_queries)}개")
        print(f"{'='*60}")

        return result

    def _save_for_llm_analysis(self, blogs: List[Dict], keyword: str) -> str:
        """블로그 데이터를 LLM 분석용으로 저장"""
        from modules.llm_topic_extractor import save_blogs_for_analysis
        return save_blogs_for_analysis(blogs, keyword, self.output_dir)

    def _collect_blog_urls(self, keyword: str, max_count: int) -> List[str]:
        """네이버에서 블로그 URL 수집"""
        urls = []
        seen = set()

        search_terms = [
            keyword,
            f"{keyword} 증상",
            f"{keyword} 원인",
            f"{keyword} 치료",
            f"{keyword} 음식",
            f"{keyword} 후기",
            f"{keyword} 좋은음식",
        ]

        for term in search_terms:
            if len(urls) >= max_count:
                break

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

                # 제목
                title = ""
                for selector in ['h1', '.se-title-text', '.title', 'title']:
                    elem = soup.select_one(selector)
                    if elem:
                        title = elem.get_text(strip=True)
                        if title:
                            break

                # 본문
                content = ""
                for selector in ['.se-main-container', '#post-view-container', '.post_ct', 'article']:
                    elem = soup.select_one(selector)
                    if elem:
                        for tag in elem.select('script, style, nav, footer'):
                            tag.decompose()
                        content = elem.get_text(separator='\n', strip=True)
                        if len(content) > 200:
                            break

                # iframe 처리
                if len(content) < 200:
                    iframe = soup.select_one('iframe#mainFrame')
                    if iframe:
                        iframe_src = iframe.get('src', '')
                        if iframe_src and not iframe_src.startswith('http'):
                            iframe_src = f"https://blog.naver.com{iframe_src}"
                        if iframe_src:
                            response2 = requests.get(iframe_src, headers=self.headers, timeout=15)
                            soup2 = BeautifulSoup(response2.text, 'html.parser')
                            for selector in ['.se-main-container', '#post-view-container', '.post_ct']:
                                elem = soup2.select_one(selector)
                                if elem:
                                    content = elem.get_text(separator='\n', strip=True)
                                    if len(content) > 200:
                                        break

                if content and len(content) > 200:
                    blogs.append({
                        'url': url,
                        'title': title[:100] if title else 'N/A',
                        'content': content[:5000]
                    })

                time.sleep(0.3)

            except Exception:
                continue

        return blogs

    def _extract_topics_rule_based(self, content: str) -> List[str]:
        """규칙 기반 토픽 추출"""
        found_topics = []
        content_lower = content.lower()

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    found_topics.append(topic)
                    break  # 하나만 매칭되면 충분

        return found_topics

    def _get_main_keyword_english(self, keyword: str) -> str:
        """메인 키워드를 영어로 변환 (매핑 없으면 Google 번역)"""
        mapping = {
            # 소화기 질환
            '역류성식도염': 'GERD gastroesophageal reflux',
            '역류성 식도염': 'GERD gastroesophageal reflux',
            '위식도역류질환': 'GERD gastroesophageal reflux',
            '위염': 'gastritis',
            '위궤양': 'gastric ulcer',
            '과민성대장': 'IBS irritable bowel syndrome',
            '과민성대장증후군': 'IBS irritable bowel syndrome',
            '변비': 'constipation',
            '설사': 'diarrhea',
            '소화불량': 'dyspepsia indigestion',

            # 대사/내분비
            '당뇨': 'diabetes mellitus',
            '당뇨병': 'diabetes mellitus',
            '제2형당뇨': 'type 2 diabetes',
            '고혈압': 'hypertension',
            '고지혈증': 'hyperlipidemia dyslipidemia',
            '비만': 'obesity',
            '갑상선': 'thyroid',

            # 영양/식이
            '비타민D': 'vitamin D',
            '비타민D 결핍': 'vitamin D deficiency',
            '철분 결핍': 'iron deficiency anemia',
            '간헐적 단식': 'intermittent fasting',
            '간헐적단식': 'intermittent fasting',
            '키토제닉': 'ketogenic diet',
            '저탄수화물': 'low carbohydrate diet',

            # 정신건강
            '불면증': 'insomnia sleep disorder',
            '우울증': 'depression',
            '불안장애': 'anxiety disorder',
            '스트레스': 'psychological stress',

            # 피부/모발
            '탈모': 'hair loss alopecia',
            '여드름': 'acne',
            '아토피': 'atopic dermatitis',

            # 근골격
            '관절염': 'arthritis',
            '골다공증': 'osteoporosis',
            '허리통증': 'low back pain',

            # 심혈관
            '심장병': 'heart disease cardiovascular',
            '동맥경화': 'atherosclerosis',

            # 기타
            '두통': 'headache migraine',
            '편두통': 'migraine',
            '알레르기': 'allergy',
        }

        # 매핑에 있으면 반환
        result = mapping.get(keyword)
        if result:
            return result

        # 매핑에 없으면 Google 번역 시도
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='ko', target='en')
            translated = translator.translate(keyword)
            print(f"  [자동번역] '{keyword}' → '{translated}'")
            return translated
        except Exception as e:
            print(f"  [번역실패] '{keyword}' 그대로 사용")
            return keyword

    def _get_topic_english(self, topic: str) -> str:
        """토픽을 영어로 변환 (매핑 → Google 번역 순서)"""
        # 1. 이미 영어면 그대로 반환
        if re.match(r'^[A-Za-z0-9\s\-]+$', topic):
            return topic

        # 2. 매핑에 있으면 사용
        if topic in self.KR_TO_EN:
            return self.KR_TO_EN[topic]

        # 3. Google 번역 시도
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='ko', target='en')
            translated = translator.translate(topic)
            return translated
        except Exception:
            return topic


# CLI 테스트
if __name__ == "__main__":
    import sys

    keyword = sys.argv[1] if len(sys.argv) > 1 else "역류성식도염"

    extractor = SmartTopicExtractor()
    result = extractor.extract_topics(keyword, max_blogs=20)

    print(f"\n{'='*60}")
    print(f"논문 검색용 쿼리")
    print(f"{'='*60}")
    for q in result['search_queries']:
        print(f"  {q}")
