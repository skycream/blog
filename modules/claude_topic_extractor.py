"""
Claude CLI 기반 토픽 추출 모듈
- Claude CLI를 subprocess로 호출하여 블로그 분석
- 새로운 트렌드 키워드도 자동 발견 (위고비, 오젬픽 등)
"""

import subprocess
import json
import re
from typing import List, Dict


def extract_topics_with_claude(blogs: List[Dict], main_keyword: str) -> Dict:
    """
    Claude CLI를 사용하여 블로그에서 토픽 추출

    Args:
        blogs: [{'content': '블로그 본문', 'title': '제목', ...}, ...]
        main_keyword: 메인 검색 키워드

    Returns:
        {
            'topics': [{'topic': '토픽명', 'count': 횟수, 'category': '카테고리'}, ...],
            'trending': [...],
            'topic_counts': {...}
        }
    """
    # 블로그 내용 요약 (토큰 제한 고려)
    blogs_summary = ""
    for i, blog in enumerate(blogs[:10], 1):  # 최대 10개
        title = blog.get('title', '')[:100]
        content = blog.get('content', '')[:1500]  # 각 블로그 1500자
        blogs_summary += f"\n[블로그 {i}] {title}\n{content}\n"

    # Claude에게 보낼 프롬프트
    prompt = f"""다음은 '{main_keyword}' 키워드로 검색한 인기 블로그들입니다.
이 블로그들을 분석하여 독자들이 관심 가질 만한 핵심 토픽/키워드를 추출해주세요.

{blogs_summary}

## 추출 지침
1. 구체적인 토픽 추출 (예: "식이요법" 보다 "16:8 단식", "양배추즙")
2. 새로운 트렌드 키워드 발견 (예: 위고비, 오젬픽, 세마글루타이드 등 신약/신기술)
3. 실용적인 토픽 우선 (음식, 치료법, 생활습관 등)
4. 일반적인 단어 제외 (증상, 원인, 치료, 효과 등 너무 일반적인 것)

## 출력 형식 (JSON만 출력)
```json
{{
  "topics": [
    {{"topic": "토픽명", "count": 언급블로그수, "category": "diet|treatment|lifestyle|symptom|trending"}}
  ],
  "trending": ["새로운/트렌디한 키워드들"]
}}
```

JSON만 반환하세요."""

    try:
        import uuid
        import os

        # 현재 디렉토리에 임시 파일 생성 (경로 문제 회피)
        prompt_file = f'_claude_temp_{uuid.uuid4().hex[:8]}.txt'
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        try:
            # cmd /c로 실행 (Windows 콘솔 환경 상속)
            result = subprocess.run(
                ['cmd', '/c', f'type {prompt_file} | claude -p --output-format text'],
                capture_output=True,
                text=True,
                timeout=180,
                encoding='utf-8'
            )
        finally:
            try:
                os.remove(prompt_file)
            except:
                pass

        if result.returncode != 0:
            print(f"[Claude CLI 오류] returncode={result.returncode}")
            print(f"[stderr] {result.stderr[:300] if result.stderr else 'empty'}")
            return _fallback_extraction(blogs, main_keyword)

        response = result.stdout.strip()

        # JSON 파싱
        parsed = _parse_claude_response(response)
        if parsed:
            return _format_result(parsed)
        else:
            print("[파싱 실패] Claude 응답을 파싱할 수 없습니다")
            return _fallback_extraction(blogs, main_keyword)

    except subprocess.TimeoutExpired:
        print("[타임아웃] Claude CLI 응답 시간 초과")
        return _fallback_extraction(blogs, main_keyword)
    except FileNotFoundError:
        print("[오류] Claude CLI를 찾을 수 없습니다")
        return _fallback_extraction(blogs, main_keyword)
    except Exception as e:
        print(f"[오류] {e}")
        return _fallback_extraction(blogs, main_keyword)


def _parse_claude_response(response: str) -> Dict:
    """Claude 응답에서 JSON 추출"""
    try:
        # JSON 블록 찾기
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # JSON 블록 없으면 전체에서 {} 찾기
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(response[start:end])

    except json.JSONDecodeError as e:
        print(f"[JSON 파싱 오류] {e}")

    return None


def _format_result(parsed: Dict) -> Dict:
    """파싱된 결과를 표준 형식으로 변환"""
    topics = parsed.get('topics', [])
    trending = parsed.get('trending', [])

    # topic_counts 생성
    topic_counts = {}
    for t in topics:
        topic_name = t.get('topic', '')
        count = t.get('count', 1)
        if topic_name:
            topic_counts[topic_name] = count

    # trending을 topics 형식으로 변환
    trending_topics = []
    for t in trending:
        if isinstance(t, str):
            trending_topics.append({
                'topic': t,
                'count': 1,
                'category': 'trending',
                'type': 'trending'
            })
        elif isinstance(t, dict):
            trending_topics.append(t)

    return {
        'total_topics': len(topics),
        'topics': topics[:20],
        'trending': trending_topics[:10],
        'topic_counts': topic_counts,
        'by_category': _group_by_category(topics)
    }


def _group_by_category(topics: List[Dict]) -> Dict:
    """토픽을 카테고리별로 그룹화"""
    by_category = {}
    for t in topics:
        cat = t.get('category', 'general')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(t)
    return by_category


def _fallback_extraction(blogs: List[Dict], main_keyword: str) -> Dict:
    """Claude CLI 실패 시 기본 추출 (auto_topic_extractor 사용)"""
    print("[폴백] 기본 토픽 추출 사용")
    from modules.auto_topic_extractor import extract_topics_auto
    return extract_topics_auto(blogs, main_keyword)
