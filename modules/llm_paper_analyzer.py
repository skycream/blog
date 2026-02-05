"""
LLM 기반 논문 분석 모듈
- 논문 전문/초록을 구조화된 정보로 추출
- Claude CLI에서 사용하도록 설계
"""

import json
from typing import Dict, List
from datetime import datetime


# 논문 분석 프롬프트 템플릿
PAPER_ANALYSIS_PROMPT = """
당신은 의학 논문 분석 전문가입니다. 아래 논문 정보를 분석하여 구조화된 JSON으로 반환해주세요.

## 논문 정보
- 제목: {title}
- 저널: {journal} ({year})
- PMID: {pmid}

## 초록/본문
{content}

## 분석 요청
위 논문을 분석하여 다음 JSON 형식으로 반환해주세요:

```json
{{
  "pmid": "{pmid}",
  "연구유형": "RCT/코호트/메타분석/리뷰/사례연구 중 택1",
  "연구대상": {{
    "인원": "N명 (숫자 또는 '명시안됨')",
    "특성": "연령대, 성별, 특이사항 등"
  }},
  "연구방법": "연구 설계 및 방법론 요약 (100자 이내)",
  "주요결과": {{
    "효과크기": "OR, RR, HR, % 등 구체적 수치 (있는 경우)",
    "통계적유의성": "p값 또는 95% CI (있는 경우)",
    "결과요약": "핵심 발견 (200자 이내)"
  }},
  "핵심결론": "이 연구의 핵심 결론과 의미 (500자 이내, 한글로)",
  "실용적시사점": "일반인이 알아야 할 실천 가능한 조언 (300자 이내, 한글로)",
  "한계점": "연구의 한계 (있는 경우, 100자 이내)",
  "신뢰도": "상/중/하 (연구 설계와 표본 크기 기반)"
}}
```

JSON만 반환하세요. 다른 설명은 필요 없습니다.
"""


def create_analysis_request(papers: List[Dict]) -> Dict:
    """
    논문 목록을 Claude CLI 분석용 요청 형식으로 변환
    """
    analysis_requests = []

    for paper in papers:
        # 분석할 내용 결정 (전문 > 초록)
        if paper.get('conclusion') and len(paper.get('conclusion', '')) > 100:
            content = f"[결론 섹션]\n{paper['conclusion']}"
            if paper.get('results'):
                content += f"\n\n[결과 섹션]\n{paper['results'][:2000]}"
        elif paper.get('abstract'):
            content = f"[초록]\n{paper['abstract']}"
        else:
            content = "내용 없음"

        request = {
            "pmid": paper.get('pmid', ''),
            "title": paper.get('title', ''),
            "journal": paper.get('journal', ''),
            "year": paper.get('year', ''),
            "authors": paper.get('authors', [])[:3],
            "has_fulltext": paper.get('has_fulltext', False),
            "content_for_analysis": content,
            "prompt": PAPER_ANALYSIS_PROMPT.format(
                title=paper.get('title', ''),
                journal=paper.get('journal', ''),
                year=paper.get('year', ''),
                pmid=paper.get('pmid', ''),
                content=content
            )
        }
        analysis_requests.append(request)

    return {
        "created_at": datetime.now().isoformat(),
        "total_papers": len(papers),
        "fulltext_count": sum(1 for p in papers if p.get('has_fulltext')),
        "papers": analysis_requests
    }


def create_batch_analysis_prompt(papers: List[Dict], keyword: str, topics: List[str] = None) -> str:
    """
    여러 논문을 한번에 분석하는 배치 프롬프트 생성
    - 관련성 점수 포함 (75점 이상만 채택)
    """
    papers_text = ""

    for i, paper in enumerate(papers, 1):
        # 분석할 내용 결정
        if paper.get('conclusion') and len(paper.get('conclusion', '')) > 100:
            content = paper['conclusion'][:1500]
            source = "전문-결론"
        elif paper.get('abstract'):
            content = paper['abstract']
            source = "초록"
        else:
            content = "내용 없음"
            source = "없음"

        papers_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 논문 #{i}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
제목: {paper.get('title', 'N/A')}
저널: {paper.get('journal', 'N/A')} ({paper.get('year', 'N/A')})
PMID: {paper.get('pmid', 'N/A')}
출처: {source}

내용:
{content}

"""

    # 토픽 목록 문자열
    topics_str = ", ".join(topics) if topics else "없음"

    prompt = f"""
# 논문 분석 요청

## 메인 키워드: {keyword}
## 선택된 토픽(부주제): {topics_str}
## 총 논문 수: {len(papers)}편

당신은 의학 논문 분석 전문가입니다.
아래 {len(papers)}편의 논문을 각각 분석하고, **관련성 점수**를 매겨주세요.

{papers_text}

## 관련성 점수 기준 (100점 만점)

**키워드가 중심이고, 토픽은 부주제입니다.**

1. **키워드 관련성 (80점 만점)**
   - 논문이 메인 키워드 '{keyword}'를 직접 다루면: 80점
   - 키워드와 밀접하게 관련되면: 60-79점
   - 간접적으로만 관련되면: 40-59점
   - 거의 관련 없으면: 0-39점

2. **토픽 관련성 (20점 만점)**
   - 선택된 토픽 중 하나 이상을 구체적으로 다루면: 15-20점
   - 토픽과 일부 관련되면: 5-14점
   - 토픽과 무관하면: 0점

**75점 이상인 논문만 채택됩니다.**

## 출력 형식

각 논문에 대해 다음 구조의 JSON을 생성하고, 전체를 배열로 묶어주세요:

```json
[
  {{
    "번호": 1,
    "pmid": "12345678",
    "관련성점수": 85,
    "점수근거": "키워드 80점(직접 다룸) + 토픽 5점(식이 관련 언급)",
    "채택여부": true,
    "제목_한글": "논문 제목 한글 번역",
    "연구유형": "RCT/코호트/메타분석/리뷰/사례연구/실험연구",
    "연구대상": "대상자 수와 특성 (예: 성인 1,234명, 평균 45세)",
    "주요결과": "핵심 발견과 효과 크기 (예: 위험도 40% 감소, OR=0.6)",
    "핵심결론": "이 연구의 결론과 의미를 상세히 설명 (최대 500자, 한글)",
    "실용적시사점": "일반인이 실천할 수 있는 구체적 조언 (최대 300자, 한글)",
    "신뢰도": "상/중/하",
    "원문_초록": "채택된 논문만! 초록 원문 전체를 그대로 복사",
    "원문_결론": "채택된 논문만! 결론 원문 전체를 그대로 복사 (있는 경우)"
  }},
  ...
]
```

## 중요 지침
1. **관련성점수 75점 미만이면 채택여부를 false로 설정**
2. 채택여부가 false인 논문: 핵심결론, 실용적시사점, 원문_초록, 원문_결론 모두 "미채택"으로 표시
3. **채택여부가 true인 논문: 원문_초록과 원문_결론을 반드시 원문 그대로 포함** (블로그 작성 시 디테일한 내용 참조용)
4. 모든 분석 내용은 한글로 작성 (원문은 영어 그대로)
5. 핵심결론은 충분히 상세하게 (최대 500자)
6. 실용적시사점은 "~하세요", "~이 좋습니다" 형태의 실천 조언
7. 효과 크기(%, OR, RR 등)가 있으면 반드시 포함
8. JSON 배열만 반환하세요.
"""

    return prompt


def save_for_claude_analysis(papers: List[Dict], keyword: str, output_path: str) -> str:
    """
    Claude CLI 분석을 위한 파일 저장
    """
    # 배치 프롬프트 생성
    batch_prompt = create_batch_analysis_prompt(papers, keyword)

    # 저장할 데이터
    data = {
        "keyword": keyword,
        "created_at": datetime.now().isoformat(),
        "total_papers": len(papers),
        "fulltext_count": sum(1 for p in papers if p.get('has_fulltext')),
        "analysis_prompt": batch_prompt,
        "papers_raw": papers
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_path


# 분석 결과 파싱
def parse_analysis_result(json_text: str) -> List[Dict]:
    """
    Claude가 반환한 JSON 분석 결과 파싱
    """
    try:
        # JSON 부분만 추출
        start = json_text.find('[')
        end = json_text.rfind(']') + 1
        if start != -1 and end > start:
            json_str = json_text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    return []
