"""
자동 블로그 생성 모듈
- Claude CLI로 논문 분석 → 블로그 HTML 생성까지 자동화
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


# 전역 에러 로그 저장
_last_error_log = []

def get_last_error_log() -> List[str]:
    """마지막 에러 로그 반환"""
    global _last_error_log
    return _last_error_log.copy()

def _log(msg: str):
    """로그 저장 및 출력"""
    global _last_error_log
    _last_error_log.append(msg)
    print(msg)

def generate_blog_auto(session_data: Dict, output_dir: str = "output") -> Optional[str]:
    """
    세션 데이터로 블로그 HTML 자동 생성

    Args:
        session_data: 키워드, 토픽, 논문, 스타일 정보 포함
        output_dir: HTML 저장 디렉토리

    Returns:
        생성된 HTML 파일 경로 (실패 시 None)
    """
    global _last_error_log
    _last_error_log = []  # 에러 로그 초기화

    try:
        os.makedirs(output_dir, exist_ok=True)

        keyword = session_data.get('keyword', '')
        topics = session_data.get('topics', [])
        papers = session_data.get('papers', [])
        hook_style = session_data.get('hook_style_name', '')
        hook_template = session_data.get('hook_style_template', '')

        _log(f"[DEBUG] keyword={keyword}, topics={topics}, papers={len(papers)}편, hook_style={hook_style}")

        if not papers:
            _log("[오류] 논문이 없습니다")
            return None

        # 1단계: 논문 분석
        _log(f"[1단계] 논문 {len(papers)}편 분석 중...")
        analysis_result, analysis_error = analyze_papers_with_claude(papers, keyword, topics)

        if not analysis_result:
            _log(f"[오류] 논문 분석 실패")
            if analysis_error:
                _log(f"[상세] {analysis_error}")
            return None

        _log(f"[1단계 완료] 분석 결과 {len(analysis_result)}자")

        # 2단계: 블로그 HTML 생성
        _log(f"[2단계] 블로그 HTML 생성 중...")
        html_content, html_error = generate_html_with_claude(
            keyword=keyword,
            topics=topics,
            analysis_result=analysis_result,
            hook_style=hook_style,
            hook_template=hook_template
        )

        if not html_content:
            _log("[오류] HTML 생성 실패")
            if html_error:
                _log(f"[상세] {html_error}")
            return None

        _log(f"[2단계 완료] HTML {len(html_content)}자 생성")

        # 3단계: 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{keyword}_blog_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        _log(f"[완료] HTML 저장: {filepath}")
        return filepath

    except Exception as e:
        _log(f"[generate_blog_auto 예외] {type(e).__name__}: {e}")
        import traceback
        _log(traceback.format_exc())
        return None


def analyze_papers_with_claude(papers: List[Dict], keyword: str, topics: List[str]) -> tuple:
    """Claude CLI로 논문 분석

    Returns:
        (result, error) - 성공 시 (result, None), 실패 시 (None, error_message)
    """

    # 채택된 논문만 분석 (관련성점수 75점 이상 또는 점수 있는 것)
    accepted_papers = [p for p in papers if p.get('관련성점수', 0) >= 75 or p.get('관련성점수') is None]

    if not accepted_papers:
        accepted_papers = papers[:10]  # fallback: 상위 10개

    # 논문 요약 텍스트 생성 (더 짧게)
    papers_text = ""
    for i, paper in enumerate(accepted_papers[:8], 1):  # 최대 8편으로 줄임
        title = paper.get('title', '')[:100]  # 제목 100자로 제한
        abstract = paper.get('abstract', '')[:400]  # 초록 400자로 제한
        conclusion = paper.get('conclusion', '')[:400]
        score = paper.get('관련성점수', 'N/A')

        content = conclusion if conclusion else abstract

        papers_text += f"""
[논문 {i}] {title}
{content[:400]}
"""

    topics_str = ", ".join(topics) if topics else "없음"

    prompt = f"""논문 분석 요청: {keyword}

{papers_text}

각 논문의 핵심 발견과 실용 조언을 요약해주세요."""

    try:
        import uuid

        # 현재 디렉토리에 임시 파일 생성 (경로 문제 회피)
        prompt_file = f'_claude_temp_{uuid.uuid4().hex[:8]}.txt'
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        _log(f"[분석] 프롬프트 길이: {len(prompt)}자, 논문 {len(accepted_papers[:8])}편")

        try:
            # 환경 변수 설정 (Claude CLI 인증용)
            env = os.environ.copy()
            home_dir = os.path.expanduser('~')
            env['HOME'] = home_dir
            env['USERPROFILE'] = home_dir

            # ANTHROPIC_API_KEY 제거 (있으면 CLI가 OAuth 대신 API키 사용 시도)
            if 'ANTHROPIC_API_KEY' in env:
                del env['ANTHROPIC_API_KEY']

            # cmd /c로 실행 (Windows 콘솔 환경 상속)
            result = subprocess.run(
                ['cmd', '/c', f'type {prompt_file} | claude -p --output-format text'],
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                env=env
            )
        finally:
            # 임시 파일 삭제
            try:
                os.remove(prompt_file)
            except:
                pass

        if result.returncode != 0:
            error_msg = f"returncode={result.returncode}\nstderr: {result.stderr[:300] if result.stderr else 'empty'}\nstdout: {result.stdout[:300] if result.stdout else 'empty'}"
            _log(f"[분석 오류] {error_msg}")
            return None, error_msg

        output = result.stdout.strip()
        if not output:
            return None, "빈 응답"

        return output, None

    except subprocess.TimeoutExpired:
        return None, "시간 초과 (5분)"
    except FileNotFoundError:
        return None, "Claude CLI를 찾을 수 없습니다"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def generate_html_with_claude(keyword: str, topics: List[str], analysis_result: str,
                              hook_style: str, hook_template: str) -> tuple:
    """Claude CLI로 블로그 HTML 생성

    Returns:
        (result, error) - 성공 시 (result, None), 실패 시 (None, error_message)
    """

    topics_str = ", ".join(topics) if topics else ""

    # 분석 결과 길이 제한
    analysis_short = analysis_result[:2000] if analysis_result else ""

    prompt = f"""키워드 '{keyword}'에 대한 블로그 HTML을 작성하세요.

스타일: {hook_style}
분석 결과: {analysis_short}

HTML 형식으로 2000자 내외로 작성하세요."""

    try:
        import uuid

        # 현재 디렉토리에 임시 파일 생성 (경로 문제 회피)
        prompt_file = f'_claude_temp_{uuid.uuid4().hex[:8]}.txt'
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        _log(f"[HTML] 프롬프트 길이: {len(prompt)}자")

        try:
            # 환경 변수 설정 (Claude CLI 인증용)
            env = os.environ.copy()
            home_dir = os.path.expanduser('~')
            env['HOME'] = home_dir
            env['USERPROFILE'] = home_dir

            # ANTHROPIC_API_KEY 제거 (있으면 CLI가 OAuth 대신 API키 사용 시도)
            if 'ANTHROPIC_API_KEY' in env:
                del env['ANTHROPIC_API_KEY']

            # cmd /c로 실행 (Windows 콘솔 환경 상속)
            result = subprocess.run(
                ['cmd', '/c', f'type {prompt_file} | claude -p --output-format text'],
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                env=env
            )
        finally:
            # 임시 파일 삭제
            try:
                os.remove(prompt_file)
            except:
                pass

        if result.returncode != 0:
            error_msg = f"returncode={result.returncode}\nstderr: {result.stderr[:300] if result.stderr else 'empty'}\nstdout: {result.stdout[:300] if result.stdout else 'empty'}"
            _log(f"[HTML 오류] {error_msg}")
            return None, error_msg

        response = result.stdout.strip()
        if not response:
            return None, "빈 응답"

        # HTML 추출
        html = _extract_html(response)
        return html, None

    except subprocess.TimeoutExpired:
        return None, "시간 초과 (5분)"
    except FileNotFoundError:
        return None, "Claude CLI를 찾을 수 없습니다"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


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
