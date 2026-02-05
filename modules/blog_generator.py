"""블로그 글 생성 모듈"""
from anthropic import Anthropic
from typing import Dict
from datetime import datetime


class BlogGenerator:
    """Claude API를 사용한 블로그 글 생성"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Args:
            api_key: Anthropic API 키
            model: 사용할 Claude 모델
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def generate_blog_post(self, topic: str, analysis: Dict, style: str = "hybrid") -> str:
        """
        분석 결과를 블로그 글로 생성

        Args:
            topic: 주제
            analysis: 논문 분석 결과
            style: 글 스타일 ('academic', 'casual', 'hybrid')

        Returns:
            HTML 형식의 블로그 글
        """
        print(f"\n✍️  블로그 글 생성 중...")

        # 스타일별 프롬프트
        blog_prompt = self._create_blog_prompt(topic, analysis, style)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                messages=[{
                    "role": "user",
                    "content": blog_prompt
                }]
            )

            blog_content = response.content[0].text
            print("✓ 블로그 글 생성 완료")

            # HTML로 래핑
            html_output = self._wrap_in_html(topic, blog_content, analysis)
            return html_output

        except Exception as e:
            print(f"✗ 블로그 글 생성 실패: {str(e)}")
            return f"<p>오류: {str(e)}</p>"

    def _create_blog_prompt(self, topic: str, analysis: Dict, style: str) -> str:
        """블로그 글 생성용 프롬프트"""

        style_instructions = {
            "academic": """
- 전문적이고 학술적인 톤
- 논문 인용을 엄격하게 표기
- 통계와 수치를 상세히 제시
- 의학 전문 용어 사용
- 대상 독자: 의료인, 연구자
""",
            "casual": """
- 친근하고 쉬운 톤
- 일상적인 언어 사용
- 스토리텔링 포함
- 실생활 예시 다수
- 대상 독자: 일반 대중
""",
            "hybrid": """
- 과학적 근거는 명확히, 설명은 쉽게
- 핵심 통계는 제시하되 이해하기 쉽게 풀어쓰기
- 전문 용어는 괄호로 설명 추가
- 실천 가능한 조언 강조
- 대상 독자: 건강에 관심 있는 일반인
"""
        }

        analysis_summary = self._format_analysis_for_prompt(analysis)

        return f"""당신은 건강/의학 블로그 작가입니다. 아래 논문 분석 결과를 바탕으로 "{topic}"에 대한 블로그 글을 작성해주세요.

# 주제: {topic}

# 논문 분석 결과:
{analysis_summary}

# 글 스타일: {style.upper()}
{style_instructions[style]}

# 블로그 글 구성 (HTML 형식):

<article>

<header>
<h1>매력적인 제목 (클릭을 유도하되 과장 금지)</h1>
<p class="intro">핵심 메시지를 담은 인트로 (2-3문장)</p>
</header>

<section class="summary">
<h2>핵심 요약</h2>
<ul>
<li>3-5개의 핵심 포인트</li>
</ul>
</section>

<section class="main-content">
<h2>무엇이 문제인가? (또는 주제의 핵심)</h2>
<p>근본 원인, 메커니즘을 쉽게 설명</p>
<p><strong>핵심 통계/발견:</strong> 구체적 수치 제시</p>
<p class="citation">근거: [논문 번호들]</p>
</section>

<section class="solutions">
<h2>과학적으로 입증된 해결법</h2>

<div class="solution-item">
<h3>1. 첫 번째 해결법</h3>
<p><strong>효과:</strong> XX% 개선 (연구 결과)</p>
<p><strong>방법:</strong> 구체적 실천 방법</p>
<p><strong>주의사항:</strong> 있다면 명시</p>
<p class="citation">근거: [논문 번호들]</p>
</div>

<!-- 추가 해결법들 -->
</section>

<section class="practical-guide">
<h2>실천 가이드</h2>
<ol>
<li>단계별 실천 방법</li>
</ol>

<div class="warning-box">
<h4>⚠️ 주의사항</h4>
<ul>
<li>반드시 알아야 할 경고</li>
</ul>
</div>
</section>

<section class="myths">
<h2>흔한 오해와 진실</h2>
<div class="myth-item">
<p><strong>❌ 오해:</strong> 잘못된 통념</p>
<p><strong>✅ 진실:</strong> 과학적 사실</p>
</div>
</section>

<section class="conclusion">
<h2>결론</h2>
<p>핵심 메시지 재강조 및 행동 촉구</p>
</section>

<section class="references">
<h2>참고 논문</h2>
<!-- 논문 목록 표는 자동 삽입됩니다 -->
</section>

</article>

**작성 원칙:**
1. 모든 주장에는 논문 근거 명시
2. 통계는 정확하게, 하지만 이해하기 쉽게
3. "연구에 따르면", "XX% 개선" 등 구체적 표현
4. 과장 금지, 팩트 중심
5. 읽기 쉬운 문단 길이 (3-5문장)
6. 소제목으로 스캔 가능하게
7. 실천 가능한 조언 우선

이제 블로그 글을 작성해주세요 (HTML 형식):
"""

    def _format_analysis_for_prompt(self, analysis: Dict) -> str:
        """분석 결과를 프롬프트용으로 포맷"""
        if 'raw_analysis' in analysis:
            return analysis['raw_analysis']

        formatted = []

        if 'summary' in analysis:
            formatted.append(f"전체 요약:\n{analysis['summary']}\n")

        if 'key_findings' in analysis:
            formatted.append("핵심 발견:")
            for finding in analysis['key_findings']:
                formatted.append(f"- {finding.get('finding', '')} (근거: 논문 {finding.get('evidence', '')}, 신뢰도: {finding.get('confidence', '')})")
            formatted.append("")

        if 'mechanisms' in analysis:
            formatted.append(f"작용 메커니즘:\n{analysis['mechanisms']}\n")

        if 'solutions' in analysis:
            formatted.append("해결법:")
            for sol in analysis['solutions']:
                formatted.append(f"- {sol.get('solution', '')} (효과: {sol.get('effectiveness', '')}, 근거: {sol.get('evidence', '')})")
            formatted.append("")

        if 'practical_advice' in analysis:
            formatted.append("실천 조언:")
            for advice in analysis['practical_advice']:
                formatted.append(f"- {advice.get('advice', '')} (이유: {advice.get('rationale', '')})")
            formatted.append("")

        if 'controversies' in analysis:
            formatted.append("논쟁적 부분:")
            for controversy in analysis['controversies']:
                formatted.append(f"- {controversy}")
            formatted.append("")

        if 'warnings' in analysis:
            formatted.append("주의사항:")
            for warning in analysis['warnings']:
                formatted.append(f"- {warning}")

        return "\n".join(formatted)

    def _wrap_in_html(self, topic: str, blog_content: str, analysis: Dict) -> str:
        """블로그 글을 완전한 HTML 문서로 래핑"""
        paper_count = analysis.get('paper_count', 0)
        current_date = datetime.now().strftime("%Y년 %m월 %d일")

        # 논문 목록 표 생성
        papers_table = self._generate_paper_table(analysis.get('papers', []))

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - 논문 기반 건강 정보</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
            background-color: #f9f9f9;
        }}
        article {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 0.5em;
            color: #1a1a1a;
            line-height: 1.3;
        }}
        h2 {{
            font-size: 1.8em;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.3em;
        }}
        h3 {{
            font-size: 1.3em;
            margin-top: 1.2em;
            color: #34495e;
        }}
        .intro {{
            font-size: 1.2em;
            color: #555;
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
        }}
        .citation {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 0.5em;
            font-style: italic;
        }}
        .solution-item {{
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }}
        .warning-box {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }}
        .warning-box h4 {{
            margin-top: 0;
            color: #856404;
        }}
        .myth-item {{
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .meta-info {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        ul, ol {{
            padding-left: 25px;
        }}
        li {{
            margin: 8px 0;
        }}
        strong {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <article>
        <div class="meta-info">
            📚 {paper_count}개의 논문 분석 기반 | 작성일: {current_date}
        </div>

        {blog_content}

        <section class="references">
            <h2>참고 논문 목록</h2>
            <p>이 글은 아래 {paper_count}개의 논문을 분석하여 작성되었습니다.</p>
            {papers_table}
        </section>

        <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 0.9em;">
            <p><strong>면책 조항:</strong> 이 글은 과학 논문을 기반으로 작성되었으나 의학적 조언을 대체할 수 없습니다.
            건강 문제가 있다면 반드시 의료 전문가와 상담하세요.</p>
            <p>생성 도구: 논문 기반 자동 블로그 글 생성기 (PubMed + Claude AI)</p>
        </footer>
    </article>
</body>
</html>"""

        return html

    def _generate_paper_table(self, papers: list) -> str:
        """논문 목록 HTML 표 생성"""
        if not papers:
            return "<p>논문 정보를 불러올 수 없습니다.</p>"

        html = """<table>
<thead>
<tr>
<th style="width: 5%;">번호</th>
<th style="width: 45%;">논문 제목</th>
<th style="width: 30%;">저자 / 저널</th>
<th style="width: 10%;">연도</th>
<th style="width: 10%;">링크</th>
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
<td>{paper['title']}</td>
<td>{authors_str}<br/><em>{paper['journal']}</em></td>
<td>{paper['year']}</td>
<td><a href="{paper['url']}" target="_blank">PubMed</a></td>
</tr>
"""

        html += "</tbody>\n</table>"
        return html
