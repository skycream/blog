"""Claude API를 사용한 논문 분석 모듈"""
from anthropic import Anthropic
from typing import List, Dict
import json


class PaperAnalyzer:
    """Claude API를 사용한 논문 종합 분석"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Args:
            api_key: Anthropic API 키
            model: 사용할 Claude 모델
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def analyze_papers(self, papers: List[Dict], topic: str) -> Dict:
        """
        수집한 논문들을 종합 분석

        Args:
            papers: 논문 정보 리스트
            topic: 분석 주제

        Returns:
            분석 결과 딕셔너리
        """
        if not papers:
            return {"error": "분석할 논문이 없습니다."}

        print(f"\n🤖 Claude가 {len(papers)}개 논문을 분석 중...")

        # 논문 정보를 텍스트로 정리
        papers_text = self._format_papers_for_analysis(papers)

        # Claude에게 분석 요청
        analysis_prompt = self._create_analysis_prompt(topic, papers_text, len(papers))

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            )

            analysis_text = response.content[0].text
            print("✓ 논문 분석 완료")

            # 분석 결과 구조화
            analysis = self._structure_analysis(analysis_text, papers)
            return analysis

        except Exception as e:
            print(f"✗ 논문 분석 실패: {str(e)}")
            return {"error": str(e)}

    def _format_papers_for_analysis(self, papers: List[Dict]) -> str:
        """논문 정보를 분석용 텍스트로 포맷"""
        formatted = []

        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper['authors']) if paper['authors'] else "Unknown"
            if len(paper['authors']) > 3:
                authors_str += " et al."

            paper_text = f"""
[논문 {i}]
제목: {paper['title']}
저자: {authors_str}
저널: {paper['journal']} ({paper['year']})
연구 유형: {paper['study_type']}
PMID: {paper['pmid']}

초록:
{paper['abstract']}

---
"""
            formatted.append(paper_text)

        return "\n".join(formatted)

    def _create_analysis_prompt(self, topic: str, papers_text: str, paper_count: int) -> str:
        """논문 분석용 프롬프트 생성"""
        return f"""당신은 의학/건강 분야의 전문 리서처입니다. 아래 {paper_count}개의 논문들을 분석하여 "{topic}"에 대한 종합적인 인사이트를 제공해주세요.

# 분석 주제: {topic}

# 수집된 논문들:
{papers_text}

# 분석 요구사항:

1. **과학적 합의점 도출**
   - 여러 논문들이 공통적으로 지지하는 핵심 발견은?
   - 가장 신뢰도 높은 근거는 무엇인가? (메타분석 > RCT > 코호트 순)

2. **주요 발견 정리**
   - 원인/메커니즘
   - 효과적인 치료법/해결법
   - 예방 방법
   - 주의사항

3. **논쟁적인 부분 식별**
   - 논문들 간 상반된 결과가 있다면?
   - 아직 명확하지 않은 영역은?

4. **실생활 적용**
   - 일반인이 실천할 수 있는 구체적 조언
   - 수치와 통계를 활용한 명확한 가이드

5. **중요한 경고사항**
   - 잘못된 통념이나 오해
   - 주의해야 할 부작용이나 위험

6. **논문 인용**
   - 핵심 주장마다 어떤 논문(번호)을 근거로 하는지 명시
   - 예: "연구에 따르면 XX는 YY% 개선 효과를 보였습니다 (논문 3, 7)"

**출력 형식:**
구조화된 JSON 형식으로 반환해주세요:

{{
  "summary": "전체 요약 (3-5문장)",
  "key_findings": [
    {{"finding": "발견 내용", "evidence": "근거 논문 번호들", "confidence": "높음/중간/낮음"}}
  ],
  "mechanisms": "작용 메커니즘 설명",
  "solutions": [
    {{"solution": "해결법", "evidence": "근거", "effectiveness": "효과 정도"}}
  ],
  "practical_advice": [
    {{"advice": "실천 조언", "rationale": "이유"}}
  ],
  "controversies": ["논쟁적 부분들"],
  "warnings": ["주의사항들"],
  "research_quality": "전반적인 연구 품질 평가"
}}
"""

    def _structure_analysis(self, analysis_text: str, papers: List[Dict]) -> Dict:
        """분석 결과를 구조화"""
        try:
            # JSON 추출 시도
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = analysis_text[json_start:json_end]
                structured = json.loads(json_str)
            else:
                # JSON이 없으면 텍스트 그대로 반환
                structured = {
                    "raw_analysis": analysis_text
                }

            # 원본 논문 정보 추가
            structured['papers'] = papers
            structured['paper_count'] = len(papers)

            return structured

        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트 그대로 반환
            return {
                "raw_analysis": analysis_text,
                "papers": papers,
                "paper_count": len(papers)
            }

    def generate_paper_summary_table(self, papers: List[Dict]) -> str:
        """논문 목록 표 생성 (HTML)"""
        html = """<table class="paper-table">
<thead>
<tr>
<th>번호</th>
<th>논문 제목</th>
<th>저자/저널</th>
<th>연도</th>
<th>연구 유형</th>
</tr>
</thead>
<tbody>
"""

        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper['authors'][:2]) if paper['authors'] else "Unknown"
            if len(paper['authors']) > 2:
                authors_str += " et al."

            html += f"""<tr>
<td>{i}</td>
<td><a href="{paper['url']}" target="_blank">{paper['title']}</a></td>
<td>{authors_str} / {paper['journal']}</td>
<td>{paper['year']}</td>
<td>{paper['study_type']}</td>
</tr>
"""

        html += "</tbody>\n</table>"
        return html
