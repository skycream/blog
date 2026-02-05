"""
자동 토픽 추출 모듈 (LLM/외부 라이브러리 없이)
- 의미 있는 토픽만 추출 (음식, 치료법, 생활습관 등)
- 불용어/일반 명사 철저히 필터링
"""

import re
from collections import Counter
from typing import List, Dict, Set


# 확장된 불용어 (제외할 단어들)
STOPWORDS = {
    # 문법적 어미/조사 포함 단어
    '것이', '수가', '등이', '때문', '경우', '정도', '이상', '이하', '이런', '저런', '그런',
    '있습니다', '합니다', '됩니다', '입니다', '습니다', '니다', '세요', '해요',
    '하는', '되는', '있는', '없는', '같은', '통해', '위해', '대한', '관한',
    '증상이', '원인이', '치료가', '효과가', '방법이', '음식이', '경우가',
    '것을', '수를', '등을', '때를', '곳을', '중을',
    '것은', '수는', '등은', '때는', '곳은',
    '듯한', '같이', '처럼', '만큼', '정도로', '때문에', '통해서',

    # 일반 명사 (너무 일반적인 것들)
    '증상', '원인', '치료', '효과', '방법', '경우', '문제', '결과', '상태', '정도',
    '느낌', '생각', '부분', '사람', '환자', '의사', '병원', '검사', '진단',
    '시간', '기간', '하루', '매일', '오늘', '내일', '어제', '최근', '요즘',
    '가장', '많이', '자주', '항상', '보통', '일반', '특히', '실제', '사실',
    '필요', '중요', '다양', '여러', '모든', '대부분', '일부', '전체',
    '생활', '습관', '관리', '예방', '개선', '유지', '도움', '역할',
    '질환', '질병', '건강', '몸', '신체', '체내', '체외',

    # 블로그 관련
    '포스팅', '글', '리뷰', '후기', '경험', '이야기', '소개', '정리', '내용',
    '추천', '공유', '참고', '확인', '클릭', '링크', '출처', '사진', '이미지',
    '블로그', '네이버', '티스토리', '인스타', '유튜브', '카페',

    # 기타 일반어
    '것', '수', '등', '더', '그', '이', '저', '때', '곳', '중', '뒤', '앞', '위', '아래',
    '안', '밖', '속', '후', '전', '간', '분', '명', '개', '번', '년', '월', '일', '시',

    # 모호한 짧은 단어 (문맥에 따라 의미 다름)
    '잠', '침', '단', '신', '배', '약', '차', '물', '밥', '국', '죽', '빵', '떡',
    '몸', '손', '발', '코', '입', '눈', '귀', '턱', '목', '팔', '다리', '배', '등',
    '악순환', '호전', '악화', '심한', '심하게', '가벼운',
}

# 의미 있는 토픽 키워드 (이것들은 추출)
MEANINGFUL_TOPICS = {
    # 음식/식품
    '양배추', '바나나', '브로콜리', '시금치', '당근', '감자', '고구마', '토마토',
    '사과', '배', '포도', '오렌지', '레몬', '자몽', '키위', '딸기', '블루베리',
    '우유', '요거트', '치즈', '두부', '콩', '견과류', '아몬드', '호두',
    '오트밀', '귀리', '현미', '잡곡', '통밀',
    '닭가슴살', '연어', '고등어', '참치', '계란', '달걀',
    '올리브유', '들기름', '참기름',
    '꿀', '프로폴리스', '마누카꿀',
    '녹차', '홍차', '생강차', '캐모마일', '루이보스',
    '프로바이오틱스', '유산균', '식이섬유',

    # 피해야 할 음식
    '커피', '카페인', '술', '알코올', '맥주', '소주', '와인',
    '탄산음료', '콜라', '사이다', '에너지음료',
    '튀김', '기름진음식', '패스트푸드', '인스턴트', '라면',
    '매운음식', '자극적음식', '짠음식',
    '초콜릿', '케이크', '과자', '빵', '밀가루',
    '야식', '과식', '폭식',

    # 약물/치료
    'PPI', '위산억제제', '제산제', '소화제',
    '오메프라졸', '에소메프라졸', '란소프라졸', '판토프라졸',
    '넥시움', '오메프론', '란스톤', '판토록',
    '개비스콘', '겔포스', '알마겔', '훼스탈',
    '위고비', '삭센다', '오젬픽', '세마글루타이드', '리라글루타이드',
    '메트포르민', '인슐린',
    '한방치료', '한약', '침치료', '뜸치료', '부항',
    '내시경', '위내시경', '대장내시경',
    '수술', '복강경', '절제술',

    # 생활습관
    '수면', '숙면', '불면', '수면자세',
    '베개', '침대', '매트리스',
    '운동', '걷기', '조깅', '수영', '요가', '필라테스', '헬스', '웨이트',
    '스트레칭', '복근', '코어',
    '체중감량', '다이어트', '단식', '간헐적단식', 'OMAD',
    '금연', '금주', '절주',
    '스트레스', '명상', '호흡', '이완',

    # 해부/병리
    '위산', '위액', '담즙',
    '식도', '십이지장', '소장', '대장',
    '괄약근', '하부식도괄약근', 'LES',
    '역류', '산역류', '담즙역류',
    '바렛식도', '식도협착', '식도암',
    '위염', '위궤양', '십이지장궤양',
    '헬리코박터',

    # 증상 (구체적인 것만)
    '속쓰림', '가슴쓰림', '명치통증',
    '신물', '트림', '구역질', '구토',
    '목이물감', '인후통', '쉰목소리',
    '기침', '가래', '천식',
    '복부팽만', '더부룩', '소화불량',

    # 관련 질환
    '역류성식도염', '위식도역류', 'GERD',
    '과민성대장', 'IBS', '변비', '설사',
    '비만', '당뇨', '고혈압', '고지혈증',
    '갑상선', '갑상선기능저하', '갑상선기능항진',
}

# 의미 있는 패턴 (이런 형태는 토픽으로 추출)
MEANINGFUL_PATTERNS = [
    (r'(\d+:\d+)\s*단식', 'lifestyle'),        # 16:8 단식
    (r'(\d+)시간\s*단식', 'lifestyle'),        # 16시간 단식
    (r'([가-힣]+)요법', 'treatment'),          # ~요법
    (r'([가-힣]+)치료', 'treatment'),          # ~치료
    (r'([가-힣]+)수술', 'treatment'),          # ~수술
    (r'([가-힣]+)주스', 'diet'),               # ~주스
    (r'([가-힣]+)차', 'diet'),                 # ~차 (녹차, 생강차 등)
    (r'([가-힣]+)즙', 'diet'),                 # ~즙
    (r'([가-힣]+)환', 'treatment'),            # ~환 (한약)
    (r'([가-힣]+)정', 'treatment'),            # ~정 (약)
    (r'([가-힣]+)제', 'treatment'),            # ~제 (제산제, 소화제 등)
]


def extract_topics_auto(blogs: List[Dict], main_keyword: str = "") -> Dict:
    """
    블로그 목록에서 의미 있는 토픽만 추출
    """
    all_topics = []
    all_phrases = []
    all_english = []

    # 메인 키워드 분리 (부분 문자열도 제외)
    keyword_parts = set()
    keyword_parts.add(main_keyword)
    # 2글자 이상 부분 문자열 추가
    for i in range(len(main_keyword)):
        for j in range(i+2, len(main_keyword)+1):
            part = main_keyword[i:j]
            if len(part) >= 2:
                keyword_parts.add(part)

    for blog in blogs:
        content = blog.get('content', '') + ' ' + blog.get('title', '')

        # 1. 의미 있는 키워드 매칭 (사전 기반, 2글자 이상만)
        for topic in MEANINGFUL_TOPICS:
            if len(topic) >= 2 and topic.lower() in content.lower():
                if topic not in keyword_parts and topic not in STOPWORDS:
                    all_topics.append(topic)

        # 2. 패턴 매칭 (복합어 추출)
        for pattern, category in MEANINGFUL_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                phrase = match if isinstance(match, str) else match
                # 패턴 전체 추출
                full_match = re.search(pattern, content)
                if full_match:
                    phrase = full_match.group(0)
                    if phrase not in keyword_parts and len(phrase) >= 3:
                        all_phrases.append((phrase, category))

        # 3. 영어 의학용어 추출
        english_pattern = r'\b([A-Z]{2,})\b'  # 대문자 약어
        eng_matches = re.findall(english_pattern, content)

        # 의미 있는 영어 용어만
        medical_terms = {'PPI', 'GERD', 'LES', 'IBS', 'BMI', 'OMAD', 'GLP', 'ACG'}
        for eng in eng_matches:
            if eng in medical_terms or eng in MEANINGFUL_TOPICS:
                all_english.append(eng)

        # 브랜드명/약품명 (대소문자 혼합)
        brand_pattern = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b'
        brands = re.findall(brand_pattern, content)
        for brand in brands:
            if len(brand) >= 4 and brand.lower() not in {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'they', 'what', 'when', 'which'}:
                # 약품명 같은 것만
                if any(suffix in brand.lower() for suffix in ['mab', 'nib', 'tide', 'prazole', 'pril', 'sartan', 'statin']):
                    all_english.append(brand)

    # 빈도 계산
    topic_counts = Counter(all_topics)
    phrase_counts = Counter([p[0] for p in all_phrases])
    phrase_categories = {p[0]: p[1] for p in all_phrases}
    english_counts = Counter(all_english)

    # 결과 병합
    topics = []
    seen = set()

    # 1. 패턴 매칭 결과 우선 (복합어)
    for phrase, count in phrase_counts.most_common(10):
        if phrase not in seen and count >= 1:
            topics.append({
                'topic': phrase,
                'count': count,
                'category': phrase_categories.get(phrase, 'general'),
                'type': 'phrase'
            })
            seen.add(phrase)

    # 2. 의미 있는 키워드 (불용어 재필터링)
    for topic, count in topic_counts.most_common(30):
        if topic not in seen and count >= 2 and topic not in STOPWORDS and len(topic) >= 2:
            topics.append({
                'topic': topic,
                'count': count,
                'category': categorize_topic(topic),
                'type': 'keyword'
            })
            seen.add(topic)

    # 3. 영어 용어 (트렌딩)
    trending = []
    for eng, count in english_counts.most_common(10):
        if eng not in seen and count >= 1:
            trending.append({
                'topic': eng,
                'count': count,
                'category': 'medical',
                'type': 'english'
            })
            seen.add(eng)

    # 카테고리별 분류
    by_category = {}
    for topic in topics:
        cat = topic['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(topic)

    # 정렬 (빈도순)
    topics.sort(key=lambda x: x['count'], reverse=True)

    return {
        'total_topics': len(topics),
        'topics': topics[:20],
        'by_category': by_category,
        'trending': trending[:10],
        'topic_counts': {t['topic']: t['count'] for t in topics[:20]}
    }


def categorize_topic(topic: str) -> str:
    """토픽 카테고리 분류"""
    topic_lower = topic.lower()

    # 음식 관련
    food_keywords = ['양배추', '바나나', '브로콜리', '오트밀', '우유', '요거트', '차', '즙', '주스',
                     '커피', '술', '알코올', '탄산', '튀김', '야식', '과식', '음식']
    if any(kw in topic_lower for kw in food_keywords):
        return 'diet'

    # 치료 관련
    treatment_keywords = ['약', '치료', 'ppi', '제산', '내시경', '수술', '한방', '한약', '침',
                          '프라졸', '넥시움', '개비스콘', '위고비', '삭센다', '오젬픽']
    if any(kw in topic_lower for kw in treatment_keywords):
        return 'treatment'

    # 생활습관
    lifestyle_keywords = ['운동', '수면', '자세', '베개', '다이어트', '단식', '금연', '금주',
                          '스트레스', '명상', '체중']
    if any(kw in topic_lower for kw in lifestyle_keywords):
        return 'lifestyle'

    # 증상
    symptom_keywords = ['쓰림', '통증', '역류', '트림', '구역', '이물감', '기침', '가래']
    if any(kw in topic_lower for kw in symptom_keywords):
        return 'symptom'

    return 'general'
