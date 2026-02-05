"""
자동 블로그 생성 모듈
- Claude CLI로 논문 분석 → 블로그 HTML 생성까지 자동화
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


def generate_blog_auto(session_data: Dict, output_dir: str = "output") -> Optional[str]:
    """
    세션 데이터로 블로그 HTML 자동 생성

    Args:
        session_data: 키워드, 토픽, 논문, 스타일 정보 포함
        output_dir: HTML 저장 디렉토리

    Returns:
        생성된 HTML 파일 경로 (실패 시 None)
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        keyword = session_data.get('keyword', '')
        topics = session_data.get('topics', [])
        papers = session_data.get('papers', [])
        hook_style = session_data.get('hook_style_name', '')
        hook_template = session_data.get('hook_style_template', '')

        print(f"[DEBUG] keyword={keyword}, topics={topics}, papers={len(papers)}편, hook_style={hook_style}")

        if not papers:
            print("[오류] 논문이 없습니다")
            return None

        # 1단계: 논문 분석
        print(f"[1단계] 논문 {len(papers)}편 분석 중...")
        analysis_result = analyze_papers_with_claude(papers, keyword, topics)

        if not analysis_result:
            print("[오류] 논문 분석 실패 - Claude CLI 응답 없음")
            return None

        print(f"[1단계 완료] 분석 결과 {len(analysis_result)}자")

        # 2단계: 블로그 HTML 생성
        print(f"[2단계] 블로그 HTML 생성 중...")
        html_content = generate_html_with_claude(
            keyword=keyword,
            topics=topics,
            analysis_result=analysis_result,
            hook_style=hook_style,
            hook_template=hook_template
        )

        if not html_content:
            print("[오류] HTML 생성 실패 - Claude CLI 응답 없음")
            return None

        print(f"[2단계 완료] HTML {len(html_content)}자 생성")

        # 3단계: 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{keyword}_blog_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"[완료] HTML 저장: {filepath}")
        return filepath

    except Exception as e:
        print(f"[generate_blog_auto 예외] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_papers_with_claude(papers: List[Dict], keyword: str, topics: List[str]) -> Optional[str]:
    """Claude CLI로 논문 분석"""

    # 채택된 논문만 분석 (관련성점수 75점 이상 또는 점수 있는 것)
    accepted_papers = [p for p in papers if p.get('관련성점수', 0) >= 75 or p.get('관련성점수') is None]

    if not accepted_papers:
        accepted_papers = papers[:10]  # fallback: 상위 10개

    # 논문 요약 텍스트 생성
    papers_text = ""
    for i, paper in enumerate(accepted_papers[:15], 1):  # 최대 15편
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')[:800]
        conclusion = paper.get('conclusion', '')[:800]
        score = paper.get('관련성점수', 'N/A')

        content = conclusion if conclusion else abstract

        papers_text += f"""
━━━━━ 논문 {i} (관련성: {score}점) ━━━━━
제목: {title}
내용: {content}
"""

    topics_str = ", ".join(topics) if topics else "없음"

    prompt = f"""다음 논문들을 분석하여 블로그 작성에 필요한 핵심 정보를 추출해주세요.

## 키워드: {keyword}
## 토픽: {topics_str}

{papers_text}

## 분석 요청

각 논문에서 다음을 추출해주세요:
1. **핵심 발견** - 연구의 주요 결과 (수치 포함)
2. **실용적 조언** - 독자가 실천할 수 있는 구체적 조언
3. **인용 가능한 문장** - 블로그에 인용할 만한 핵심 문장

## 출력 형식

```
### 논문 1: [제목 요약]
- 핵심발견: ...
- 실용조언: ...
- 인용문장: "..."

### 논문 2: [제목 요약]
...
```

마지막에 전체 논문을 종합한 **핵심 메시지 3가지**도 정리해주세요."""

    try:
        import uuid

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
                timeout=300,
                encoding='utf-8'
            )
        finally:
            # 임시 파일 삭제
            try:
                os.remove(prompt_file)
            except:
                pass

        if result.returncode != 0:
            print(f"[분석 오류] returncode={result.returncode}")
            print(f"[stderr] {result.stderr[:500] if result.stderr else 'empty'}")
            print(f"[stdout] {result.stdout[:500] if result.stdout else 'empty'}")
            return None

        output = result.stdout.strip()
        if not output:
            print("[분석 오류] 빈 응답")
            return None

        return output

    except subprocess.TimeoutExpired:
        print("[타임아웃] 논문 분석 시간 초과 (5분)")
        return None
    except FileNotFoundError:
        print("[오류] Claude CLI를 찾을 수 없습니다. 'claude' 명령어가 PATH에 있는지 확인하세요.")
        return None
    except Exception as e:
        print(f"[오류] {type(e).__name__}: {e}")
        return None


def generate_html_with_claude(keyword: str, topics: List[str], analysis_result: str,
                              hook_style: str, hook_template: str) -> Optional[str]:
    """Claude CLI로 블로그 HTML 생성"""

    topics_str = ", ".join(topics) if topics else ""

    prompt = f"""다음 정보를 바탕으로 네이버 블로그용 HTML을 작성해주세요.

## 기본 정보
- 키워드: {keyword}
- 토픽: {topics_str}
- 도입부 스타일: {hook_style}

## 도입부 템플릿
{hook_template}

## 논문 분석 결과
{analysis_result}

## HTML 작성 요청

1. **도입부** - 위 템플릿을 참고하여 독자의 관심을 끄는 도입부 작성
2. **본문** - 논문 분석 결과를 바탕으로 신뢰성 있는 정보 전달
   - 연구 결과 인용 (저널명, 연도 포함)
   - 구체적 수치와 통계
   - 실용적 조언
3. **마무리** - 핵심 메시지 요약, 행동 촉구

## HTML 형식 요구사항
- 네이버 블로그 에디터 호환
- <div>, <p>, <h2>, <h3>, <ul>, <li>, <strong>, <em> 태그 사용
- 가독성 좋은 문단 구분
- 이모지 적절히 사용
- 2000-3000자 분량

## 출력
완성된 HTML 코드만 출력하세요. ```html 블록으로 감싸주세요."""

    try:
        import uuid

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
                timeout=300,
                encoding='utf-8'
            )
        finally:
            # 임시 파일 삭제
            try:
                os.remove(prompt_file)
            except:
                pass

        if result.returncode != 0:
            print(f"[HTML 생성 오류] returncode={result.returncode}")
            print(f"[stderr] {result.stderr[:500] if result.stderr else 'empty'}")
            print(f"[stdout] {result.stdout[:500] if result.stdout else 'empty'}")
            return None

        response = result.stdout.strip()
        if not response:
            print("[HTML 생성 오류] 빈 응답")
            return None

        # HTML 추출
        html = _extract_html(response)
        return html

    except subprocess.TimeoutExpired:
        print("[타임아웃] HTML 생성 시간 초과 (5분)")
        return None
    except FileNotFoundError:
        print("[오류] Claude CLI를 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"[오류] {type(e).__name__}: {e}")
        return None


def _extract_html(response: str) -> str:
    """응답에서 HTML 추출"""
    import re

    # ```html 블록 찾기
    html_match = re.search(r'```html\s*(.*?)\s*```', response, re.DOTALL)
    if html_match:
        return html_match.group(1).strip()

    # ``` 블록 찾기
    code_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # HTML 태그로 시작하면 전체 반환
    if response.strip().startswith('<'):
        return response.strip()

    return response
