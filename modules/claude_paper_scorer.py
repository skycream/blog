"""
Claude CLI 기반 논문 관련성 점수 평가 모듈
- 논문 검색 후 즉시 관련성 점수 평가
- 75점 이상만 채택
"""

import subprocess
import json
import re
from typing import List, Dict, Tuple


def score_papers_with_claude(papers: List[Dict], keyword: str, keyword_en: str, topics: List[str]) -> Tuple[List[Dict], List[Dict]]:
    """
    Claude CLI를 사용하여 논문 관련성 점수 평가
    - 배치 처리로 안정성 향상

    Returns:
        (채택된 논문 리스트, 미채택 논문 리스트)
    """
    if not papers:
        return [], []

    all_accepted = []
    all_rejected = []

    # 20편씩 배치 처리
    batch_size = 20
    for batch_start in range(0, len(papers), batch_size):
        batch_papers = papers[batch_start:batch_start + batch_size]
        accepted, rejected = _score_batch(batch_papers, keyword, keyword_en, topics, batch_start)
        all_accepted.extend(accepted)
        all_rejected.extend(rejected)

    return all_accepted, all_rejected


def _score_batch(papers: List[Dict], keyword: str, keyword_en: str, topics: List[str], start_idx: int) -> Tuple[List[Dict], List[Dict]]:
    """배치 단위로 점수 평가"""

    # 논문 요약 텍스트 생성 (제목 + 초록 앞부분만)
    papers_summary = ""
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', '')[:150]
        abstract = paper.get('abstract', '')[:300]
        papers_summary += f"""
[논문 {i}] PMID: {paper.get('pmid', 'N/A')}
제목: {title}
초록: {abstract[:300]}...
"""

    topics_str = ", ".join(topics) if topics else "없음"

    prompt = f"""논문 관련성 점수를 평가하세요.

키워드: {keyword} ({keyword_en})
토픽: {topics_str}

점수 기준:
- 키워드 직접 다룸: 80점, 밀접: 60-79점, 간접: 40-59점, 무관: 0-39점
- 토픽 관련: +15-20점, 일부: +5-14점
- 75점 이상만 채택

{papers_summary}

JSON만 출력:
[{{"번호":1,"점수":85,"채택":true}},{{"번호":2,"점수":50,"채택":false}}]"""

    try:
        import uuid
        import os

        # 현재 디렉토리에 임시 파일 생성 (경로 문제 회피)
        prompt_file = f'_claude_temp_{uuid.uuid4().hex[:8]}.txt'
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

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
                timeout=180,
                encoding='utf-8',
                env=env
            )
        finally:
            try:
                os.remove(prompt_file)
            except:
                pass

        if result.returncode != 0:
            print(f"[Claude CLI 오류] returncode={result.returncode}")
            print(f"[stderr] {result.stderr[:300] if result.stderr else 'empty'}")
            # 오류 시 제목 기반으로 간단히 필터링
            return _fallback_filter(papers, keyword, keyword_en)

        response = result.stdout.strip()
        scores = _parse_scores(response)

        if not scores:
            print("[파싱 실패] 점수를 파싱할 수 없습니다")
            return _fallback_filter(papers, keyword, keyword_en)

        accepted = []
        rejected = []

        for i, paper in enumerate(papers, 1):
            # 번호로 찾기
            score_info = None
            for s in scores:
                if s.get('번호') == i:
                    score_info = s
                    break

            if score_info:
                paper['관련성점수'] = score_info.get('점수', 0)
                if score_info.get('채택', False) or score_info.get('점수', 0) >= 75:
                    accepted.append(paper)
                else:
                    rejected.append(paper)
            else:
                # 점수 없으면 fallback 필터링
                if _is_relevant(paper, keyword, keyword_en):
                    paper['관련성점수'] = 75
                    accepted.append(paper)
                else:
                    paper['관련성점수'] = 0
                    rejected.append(paper)

        return accepted, rejected

    except subprocess.TimeoutExpired:
        print("[타임아웃] Claude CLI 응답 시간 초과")
        return _fallback_filter(papers, keyword, keyword_en)
    except FileNotFoundError:
        print("[오류] Claude CLI를 찾을 수 없습니다")
        return _fallback_filter(papers, keyword, keyword_en)
    except Exception as e:
        print(f"[오류] {e}")
        return _fallback_filter(papers, keyword, keyword_en)


def _fallback_filter(papers: List[Dict], keyword: str, keyword_en: str) -> Tuple[List[Dict], List[Dict]]:
    """Claude 실패 시 제목 기반 간단 필터링"""
    accepted = []
    rejected = []

    for paper in papers:
        if _is_relevant(paper, keyword, keyword_en):
            paper['관련성점수'] = 75
            accepted.append(paper)
        else:
            paper['관련성점수'] = 0
            rejected.append(paper)

    return accepted, rejected


def _is_relevant(paper: Dict, keyword: str, keyword_en: str) -> bool:
    """제목/초록에서 키워드 관련성 체크"""
    title = paper.get('title', '').lower()
    abstract = paper.get('abstract', '').lower()
    content = title + ' ' + abstract

    # 관련 키워드 리스트
    relevant_terms = [
        keyword_en.lower(),
        'gerd', 'gastroesophageal reflux', 'reflux', 'heartburn',
        'esophageal', 'esophagitis', 'acid reflux',
        'les', 'lower esophageal sphincter'
    ]

    # 관련 없는 키워드 (제외)
    irrelevant_terms = [
        'preterm', 'premature infant', 'neonate', 'bpd',
        'bruxism', 'apnea of prematurity', 'retinopathy',
        'voice disorder', 'vocal', 'tinnitus'
    ]

    # 관련 없는 키워드가 있으면 제외
    for term in irrelevant_terms:
        if term in content:
            return False

    # 관련 키워드가 있으면 포함
    for term in relevant_terms:
        if term in content:
            return True

    return False


def _parse_scores(response: str) -> List[Dict]:
    """Claude 응답에서 점수 JSON 추출"""
    try:
        # JSON 블록 찾기
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # JSON 블록 없으면 [] 찾기
        start = response.find('[')
        end = response.rfind(']') + 1
        if start != -1 and end > start:
            return json.loads(response[start:end])

    except json.JSONDecodeError as e:
        print(f"[JSON 파싱 오류] {e}")

    return []
