"""
LLM 기반 토픽 추출 모듈
- 블로그 본문을 Claude CLI가 분석하여 핵심 토픽 추출
- 하드코딩 사전 없이 자유로운 토픽 발견
"""

import os
import json
from datetime import datetime
from typing import List, Dict


def create_topic_extraction_prompt(blogs: List[Dict], keyword: str) -> str:
    """
    블로그 분석용 프롬프트 생성
    Claude CLI가 각 블로그의 핵심 토픽을 추출하도록 함
    """

    blogs_text = ""
    for i, blog in enumerate(blogs, 1):
        content_preview = blog.get('content', '')[:2000]  # 각 블로그 2000자까지
        blogs_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 블로그 #{i}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
제목: {blog.get('title', 'N/A')}
URL: {blog.get('url', 'N/A')}

본문:
{content_preview}

"""

    prompt = f"""
# 블로그 토픽 추출 요청

## 검색 키워드: {keyword}
## 분석할 블로그 수: {len(blogs)}개

당신은 콘텐츠 분석 전문가입니다.
아래 블로그들을 분석하여 각 블로그가 강조하는 **핵심 토픽/키워드**를 추출해주세요.

{blogs_text}

## 추출 지침

1. **각 블로그별로** 그 블로그가 특히 강조하거나 다루는 핵심 포인트를 2-5개 추출
2. **새로운 트렌드** 키워드도 발견해주세요 (예: 위고비, 오젬픽, 세마글루타이드 등 신약/신기술)
3. **구체적인 키워드**로 추출 (예: "식이요법" 보다 "16:8 단식", "OMAD" 등)
4. **실용적인 토픽** 우선 (독자들이 관심 가질 만한 것)
5. 키워드는 **한글**로 통일

## 출력 형식

JSON 형식으로 반환해주세요:

```json
{{
  "keyword": "{keyword}",
  "total_blogs": {len(blogs)},
  "blog_topics": [
    {{
      "blog_number": 1,
      "title": "블로그 제목",
      "main_topics": ["토픽1", "토픽2", "토픽3"],
      "trend_keywords": ["새로운 트렌드 키워드가 있다면"],
      "emphasis": "이 블로그가 특히 강조하는 포인트 한 문장"
    }},
    ...
  ],
  "aggregated_topics": {{
    "high_frequency": ["여러 블로그에서 공통으로 언급된 토픽들"],
    "trending": ["새롭거나 트렌디한 키워드들"],
    "practical": ["실용적인 조언/방법 관련 토픽들"],
    "medical": ["의학적/전문적 토픽들"]
  }},
  "top_10_topics": [
    {{"topic": "토픽명", "count": 언급된_블로그_수, "category": "카테고리"}},
    ...
  ],
  "recommended_pubmed_queries": [
    "영어로 된 PubMed 검색 쿼리 제안 (키워드 + 토픽 조합)",
    ...
  ]
}}
```

JSON만 반환하세요. 다른 설명은 필요 없습니다.
"""

    return prompt


def save_blogs_for_analysis(blogs: List[Dict], keyword: str, output_dir: str = "topic_data") -> str:
    """
    블로그 데이터를 Claude CLI 분석용으로 저장
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{keyword}_blogs_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # 분석 프롬프트 생성
    analysis_prompt = create_topic_extraction_prompt(blogs, keyword)

    data = {
        "keyword": keyword,
        "created_at": datetime.now().isoformat(),
        "total_blogs": len(blogs),
        "analysis_prompt": analysis_prompt,
        "blogs": blogs
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def parse_topic_extraction_result(json_text: str) -> Dict:
    """
    Claude가 반환한 토픽 추출 결과 파싱
    """
    try:
        # JSON 부분만 추출
        start = json_text.find('{')
        end = json_text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = json_text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    return {}


# 한글 토픽 → 영어 PubMed 쿼리 변환용 프롬프트
def create_topic_translation_prompt(topics: List[str], main_keyword_en: str) -> str:
    """
    추출된 한글 토픽을 PubMed 검색용 영어로 변환하는 프롬프트
    """
    topics_str = "\n".join([f"- {t}" for t in topics])

    return f"""
다음 한글 토픽들을 PubMed 검색에 적합한 영어 의학 용어로 변환해주세요.

메인 키워드 (영어): {main_keyword_en}

변환할 토픽들:
{topics_str}

## 출력 형식

JSON으로 반환:
```json
{{
  "translations": [
    {{"korean": "한글 토픽", "english": "English medical term", "pubmed_query": "{main_keyword_en} AND english_term"}}
  ]
}}
```

## 지침
1. 의학/과학 논문에서 사용되는 정확한 영어 용어 사용
2. 약품명은 성분명(generic name) 사용 (예: 위고비 → semaglutide)
3. 검색 효율을 위해 동의어도 포함 가능 (예: "obesity OR overweight")
"""
