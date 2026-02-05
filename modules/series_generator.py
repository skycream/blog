"""시리즈 블로그 글 생성 모듈"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from .blog_style import BLOG_STYLE_PROMPT


class SeriesBlogGenerator:
    """카테고리별 시리즈 블로그 글 생성"""

    # 시리즈 순서 및 설정
    SERIES_ORDER = [
        ('cause', '원인편', '왜 생기는 걸까요?'),
        ('treatment', '치료편', '어떻게 치료할까요?'),
        ('diet', '식이요법편', '뭘 먹고, 뭘 피해야 할까요?'),
        ('lifestyle', '생활습관편', '일상에서 어떻게 관리할까요?'),
        ('prevention', '예방편', '미리 예방하는 방법!'),
        ('complications', '합병증편', '주의해야 할 점들')
    ]

    # 시리즈 HTML 템플릿 (네비게이션 포함)
    SERIES_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Malgun Gothic', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 2.2;
            color: #333;
            background: #fafafa;
            font-size: 17px;
        }}

        .blog-post {{
            max-width: 720px;
            margin: 0 auto;
            background: white;
            padding: 50px 40px;
        }}

        /* 시리즈 헤더 */
        .series-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}

        .series-header .series-title {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}

        .series-header .episode {{
            font-size: 1.4em;
            font-weight: bold;
        }}

        .series-header .subtitle {{
            font-size: 0.95em;
            margin-top: 8px;
            opacity: 0.85;
        }}

        .greeting {{
            text-align: center;
            margin-bottom: 40px;
            font-size: 1.1em;
        }}

        .title {{
            font-size: 1.6em;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin-bottom: 50px;
            line-height: 1.5;
        }}

        .section {{
            margin: 50px 0;
        }}

        p {{
            margin: 20px 0;
        }}

        .highlight {{
            background: #f8f9fa;
            padding: 30px;
            margin: 30px 0;
            text-align: center;
            font-size: 1.2em;
            line-height: 2;
            border-radius: 10px;
        }}

        .highlight.purple {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .highlight.green {{
            background: #e8f5e9;
            color: #2e7d32;
        }}

        .highlight.blue {{
            background: #e3f2fd;
            color: #1565c0;
        }}

        .highlight.yellow {{
            background: #fff8e1;
            color: #f57f17;
        }}

        blockquote {{
            background: #f5f5f5;
            border-left: 4px solid #9c27b0;
            padding: 25px 30px;
            margin: 30px 0;
            font-size: 1.1em;
            color: #555;
        }}

        ul, ol {{
            margin: 25px 0;
            padding-left: 25px;
        }}

        li {{
            margin: 15px 0;
        }}

        .recommend-box {{
            background: #fce4ec;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
        }}

        .recommend-box h4 {{
            color: #c2185b;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}

        h2 {{
            font-size: 1.3em;
            color: #333;
            margin: 50px 0 25px 0;
            padding-left: 15px;
            border-left: 4px solid #9c27b0;
        }}

        h3 {{
            font-size: 1.15em;
            color: #555;
            margin: 35px 0 20px 0;
        }}

        .caution {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 25px;
            margin: 30px 0;
        }}

        .summary-box {{
            background: #e8f5e9;
            padding: 30px;
            border-radius: 10px;
            margin: 40px 0;
        }}

        .summary-box h3 {{
            color: #2e7d32;
            margin-top: 0;
        }}

        .closing {{
            text-align: center;
            margin: 60px 0 40px 0;
            font-size: 1.1em;
            color: #666;
        }}

        .divider {{
            text-align: center;
            margin: 50px 0;
            color: #ddd;
        }}

        .deco {{
            text-align: center;
            margin: 40px 0;
            font-size: 2em;
        }}

        /* 시리즈 네비게이션 */
        .series-nav {{
            display: flex;
            justify-content: space-between;
            margin: 50px 0;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
        }}

        .series-nav a {{
            color: #667eea;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            transition: background 0.3s;
        }}

        .series-nav a:hover {{
            background: #e8e8e8;
        }}

        .series-nav .prev::before {{
            content: "← ";
        }}

        .series-nav .next::after {{
            content: " →";
        }}

        .series-nav .disabled {{
            color: #ccc;
            pointer-events: none;
        }}

        /* 시리즈 목차 */
        .series-toc {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
        }}

        .series-toc h4 {{
            color: #667eea;
            margin-bottom: 15px;
        }}

        .series-toc ul {{
            list-style: none;
            padding: 0;
        }}

        .series-toc li {{
            margin: 10px 0;
        }}

        .series-toc a {{
            color: #555;
            text-decoration: none;
        }}

        .series-toc a:hover {{
            color: #667eea;
        }}

        .series-toc .current {{
            font-weight: bold;
            color: #667eea;
        }}

        .references {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid #eee;
        }}

        .references h3 {{
            font-size: 1em;
            color: #888;
            margin-bottom: 20px;
        }}

        .references ul {{
            list-style: none;
            padding: 0;
        }}

        .references li {{
            font-size: 0.85em;
            color: #888;
            margin: 10px 0;
            padding-left: 15px;
            border-left: 2px solid #ddd;
        }}

        .references a {{
            color: #1976d2;
            text-decoration: none;
        }}

        .keyword {{
            color: #9c27b0;
            font-weight: bold;
        }}

        .stat {{
            background: #fff9c4;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .disclaimer {{
            margin-top: 50px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            font-size: 0.85em;
            color: #777;
            text-align: center;
        }}
    </style>
</head>
<body>
    <article class="blog-post">

        <div class="series-header">
            <div class="series-title">📚 {series_title} 시리즈</div>
            <div class="episode">{episode_number}. {episode_title}</div>
            <div class="subtitle">{episode_subtitle}</div>
        </div>

        <div class="series-toc">
            <h4>📋 시리즈 목차</h4>
            {toc_html}
        </div>

        <div class="greeting">
            안녕하세요!<br>
            오늘은 <strong>{topic}</strong>의 <strong>{episode_title}</strong>이에요!
        </div>

        <div class="deco">🌿</div>

        {content}

        <div class="divider">🌸</div>

        <div class="series-nav">
            {prev_link}
            {next_link}
        </div>

        <div class="closing">
            다음 편에서 또 만나요!<br>
            항상 건강하세요! 💚
        </div>

        <div class="references">
            <h3>📚 참고한 연구들</h3>
            <p style="font-size: 0.9em; color: #888; margin-bottom: 20px;">
                이 글은 아래 연구들을 참고했어요.
            </p>
            {references}
        </div>

        <div class="disclaimer">
            이 글은 논문을 바탕으로 작성했지만, 의학적 조언을 대체할 수 없어요.<br>
            건강 문제가 있다면 꼭 전문가와 상담하세요!
        </div>

    </article>
</body>
</html>'''

    def __init__(self, anthropic_client=None, output_dir: str = 'output'):
        """
        Args:
            anthropic_client: Anthropic API 클라이언트
            output_dir: 출력 디렉토리
        """
        self.anthropic_client = anthropic_client
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plan_series(self, topic: str, categorized_papers: Dict[str, List[Dict]]) -> Dict:
        """
        시리즈 구조 계획

        Args:
            topic: 주제
            categorized_papers: 카테고리별 논문

        Returns:
            시리즈 계획 정보
        """
        episodes = []
        episode_num = 1

        for category, korean_name, subtitle in self.SERIES_ORDER:
            papers = categorized_papers.get(category, [])

            if len(papers) >= 3:  # 최소 3개 이상의 논문이 있는 카테고리만 포함
                episodes.append({
                    'number': episode_num,
                    'category': category,
                    'korean_name': korean_name,
                    'subtitle': subtitle,
                    'paper_count': len(papers)
                })
                episode_num += 1

        # general 카테고리가 있고 다른 에피소드가 있으면 통합편으로 추가
        if 'general' in categorized_papers and len(categorized_papers['general']) >= 3:
            if episodes:
                episodes.append({
                    'number': episode_num,
                    'category': 'general',
                    'korean_name': '종합편',
                    'subtitle': '알아두면 좋은 정보들',
                    'paper_count': len(categorized_papers['general'])
                })

        return {
            'topic': topic,
            'total_episodes': len(episodes),
            'episodes': episodes,
            'created_at': datetime.now().isoformat()
        }

    def generate_series_post(
        self,
        topic: str,
        category: str,
        papers: List[Dict],
        episode_info: Dict,
        series_plan: Dict
    ) -> str:
        """
        개별 시리즈 글 생성

        Args:
            topic: 주제
            category: 카테고리
            papers: 해당 카테고리 논문들
            episode_info: 에피소드 정보
            series_plan: 전체 시리즈 계획

        Returns:
            생성된 HTML 콘텐츠
        """
        if not self.anthropic_client:
            return self._generate_placeholder(topic, episode_info, papers)

        # 논문 정보를 텍스트로 변환
        papers_text = self._format_papers_for_prompt(papers)

        # 시리즈 컨텍스트 생성
        series_context = self._create_series_context(episode_info, series_plan)

        # 프롬프트 생성
        prompt = self._create_generation_prompt(
            topic, category, episode_info, papers_text, series_context
        )

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text

            # HTML 태그만 추출
            if '<div' in content or '<h1' in content or '<h2' in content:
                # HTML 컨텐츠가 있으면 그대로 사용
                pass
            else:
                # 마크다운을 HTML로 변환 (간단한 변환)
                content = self._markdown_to_html(content)

            return content

        except Exception as e:
            print(f"  ⚠️ 글 생성 실패: {str(e)}")
            return self._generate_placeholder(topic, episode_info, papers)

    def generate_all_posts(
        self,
        topic: str,
        categorized_papers: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        전체 시리즈 글 생성

        Args:
            topic: 주제
            categorized_papers: 카테고리별 논문

        Returns:
            생성된 글 정보 리스트
        """
        print(f"\n📝 '{topic}' 시리즈 블로그 생성 시작...")

        # 시리즈 계획
        series_plan = self.plan_series(topic, categorized_papers)

        if not series_plan['episodes']:
            print("  ⚠️ 생성할 시리즈가 없습니다. (각 카테고리에 최소 3개 이상의 논문 필요)")
            return []

        print(f"  📚 총 {series_plan['total_episodes']}편 생성 예정")

        results = []
        timestamp = datetime.now().strftime("%Y%m%d")
        safe_topic = topic.replace(' ', '_').replace('/', '_')

        for episode in series_plan['episodes']:
            print(f"\n  [{episode['number']}/{series_plan['total_episodes']}] {episode['korean_name']} 생성 중...")

            papers = categorized_papers.get(episode['category'], [])

            # 글 생성
            content = self.generate_series_post(
                topic, episode['category'], papers, episode, series_plan
            )

            # 전체 HTML 조립
            html = self._assemble_html(topic, episode, series_plan, content, papers)

            # 파일 저장
            filename = f"{safe_topic}_series_{episode['korean_name']}_{timestamp}.html"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            results.append({
                'episode': episode['number'],
                'category': episode['category'],
                'korean_name': episode['korean_name'],
                'filename': filename,
                'filepath': filepath,
                'paper_count': len(papers)
            })

            print(f"    ✓ {filename} 저장 완료")

        # 시리즈 인덱스 저장
        index_filename = f"{safe_topic}_series_index.json"
        index_filepath = os.path.join(self.output_dir, index_filename)

        with open(index_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'series_plan': series_plan,
                'posts': results,
                'generated_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 시리즈 인덱스 저장: {index_filename}")

        return results

    def _format_papers_for_prompt(self, papers: List[Dict]) -> str:
        """논문 정보를 프롬프트용 텍스트로 변환"""
        text = ""
        for i, paper in enumerate(papers[:15], 1):  # 최대 15개
            text += f"\n[{i}] {paper.get('title', 'No title')}\n"
            text += f"저자: {', '.join(paper.get('authors', [])[:3])}\n"
            text += f"저널: {paper.get('journal', 'Unknown')} ({paper.get('year', 'N/A')})\n"
            text += f"초록: {paper.get('abstract', 'No abstract')[:800]}\n"
            text += "-" * 50 + "\n"
        return text

    def _create_series_context(self, episode_info: Dict, series_plan: Dict) -> str:
        """시리즈 컨텍스트 생성"""
        context = f"이 글은 '{series_plan['topic']}' 시리즈의 {episode_info['number']}편입니다.\n"
        context += f"전체 {series_plan['total_episodes']}편 중 {episode_info['korean_name']}에 해당합니다.\n\n"

        context += "시리즈 구성:\n"
        for ep in series_plan['episodes']:
            marker = "👉 " if ep['number'] == episode_info['number'] else "   "
            context += f"{marker}{ep['number']}. {ep['korean_name']} - {ep['subtitle']}\n"

        return context

    def _create_generation_prompt(
        self,
        topic: str,
        category: str,
        episode_info: Dict,
        papers_text: str,
        series_context: str
    ) -> str:
        """글 생성 프롬프트 생성"""
        return f'''{BLOG_STYLE_PROMPT}

# 시리즈 정보
{series_context}

# 이번 편의 주제
- 제목: {episode_info['korean_name']}
- 부제: {episode_info['subtitle']}
- 카테고리: {category}

# 참고 논문들 ({episode_info['paper_count']}개)
{papers_text}

# 작성 규칙

1. 이 글은 시리즈의 일부이므로, 다른 편에서 다룰 내용은 "~편에서 자세히 다룰게요!"라고 언급만 하세요.
2. 이번 편의 주제({episode_info['korean_name']})에 집중하세요.
3. 논문에서 나온 구체적인 수치와 방법을 사용하세요.
4. 말투 규칙을 철저히 지키세요 ("~에요", "~하죠", "~거예요").

# 출력 형식

HTML로 작성하되, 다음 구조를 따르세요:
- <h2>, <h3>로 소제목
- <p>로 문단
- <ul>, <ol>로 목록
- <blockquote>로 인용
- <div class="highlight purple/green/blue">로 강조
- <div class="caution">로 주의사항
- <div class="recommend-box">로 추천
- <div class="summary-box">로 정리

지금 {topic}의 {episode_info['korean_name']}을 작성해주세요!'''

    def _generate_placeholder(self, topic: str, episode_info: Dict, papers: List[Dict]) -> str:
        """API 없이 플레이스홀더 생성"""
        papers_list = "\n".join([
            f"<li>{p.get('title', 'Unknown')[:80]}... ({p.get('year', 'N/A')})</li>"
            for p in papers[:10]
        ])

        return f'''
<h1 class="title">{topic} - {episode_info['korean_name']}</h1>

<div class="section">
    <p>{episode_info['subtitle']}</p>

    <blockquote>
    이 글은 {len(papers)}개의 논문을 바탕으로 작성될 예정이에요!
    </blockquote>
</div>

<div class="highlight yellow">
    ⚠️ 이 글은 플레이스홀더입니다.<br>
    Anthropic API 키가 필요합니다.
</div>

<h2>참고 논문 목록</h2>

<ul>
{papers_list}
</ul>

<div class="summary-box">
    <h3>📝 정리</h3>
    <p>이 글이 완성되면 {episode_info['korean_name']}에 대한 상세한 정보를 확인할 수 있어요!</p>
</div>
'''

    def _assemble_html(
        self,
        topic: str,
        episode_info: Dict,
        series_plan: Dict,
        content: str,
        papers: List[Dict]
    ) -> str:
        """전체 HTML 조립"""
        # 목차 생성
        toc_items = []
        for ep in series_plan['episodes']:
            if ep['number'] == episode_info['number']:
                toc_items.append(f'<li class="current">📍 {ep["number"]}. {ep["korean_name"]}</li>')
            else:
                # 실제로는 파일 링크를 넣어야 하지만, 생성 시점에는 모든 파일이 없을 수 있음
                toc_items.append(f'<li>{ep["number"]}. {ep["korean_name"]}</li>')
        toc_html = f'<ul>{"".join(toc_items)}</ul>'

        # 이전/다음 링크
        current_idx = episode_info['number'] - 1
        episodes = series_plan['episodes']

        if current_idx > 0:
            prev_ep = episodes[current_idx - 1]
            prev_link = f'<a href="#" class="prev">{prev_ep["korean_name"]}</a>'
        else:
            prev_link = '<span class="disabled prev">처음이에요</span>'

        if current_idx < len(episodes) - 1:
            next_ep = episodes[current_idx + 1]
            next_link = f'<a href="#" class="next">{next_ep["korean_name"]}</a>'
        else:
            next_link = '<span class="disabled next">마지막이에요</span>'

        # 참고문헌 생성
        ref_items = []
        for paper in papers[:10]:
            authors = ', '.join(paper.get('authors', [])[:2])
            if len(paper.get('authors', [])) > 2:
                authors += ' et al.'
            ref_items.append(
                f'<li><a href="{paper.get("url", "#")}" target="_blank">'
                f'{paper.get("title", "Unknown")[:60]}...</a> '
                f'({paper.get("journal", "Unknown")}, {paper.get("year", "N/A")})</li>'
            )
        references = f'<ul>{"".join(ref_items)}</ul>'

        # 템플릿에 값 채우기
        return self.SERIES_HTML_TEMPLATE.format(
            title=f"{topic} - {episode_info['korean_name']}",
            series_title=topic,
            episode_number=episode_info['number'],
            episode_title=episode_info['korean_name'],
            episode_subtitle=episode_info['subtitle'],
            toc_html=toc_html,
            topic=topic,
            content=content,
            prev_link=prev_link,
            next_link=next_link,
            references=references
        )

    def _markdown_to_html(self, text: str) -> str:
        """간단한 마크다운을 HTML로 변환"""
        import re

        # 헤딩
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

        # 굵은 글씨
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

        # 리스트
        lines = text.split('\n')
        result = []
        in_list = False

        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(f'<li>{line.strip()[2:]}</li>')
            elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                if not in_list:
                    result.append('<ol>')
                    in_list = True
                result.append(f'<li>{line.strip()[3:]}</li>')
            else:
                if in_list:
                    result.append('</ul>' if result[-2].startswith('<ul') else '</ol>')
                    in_list = False
                if line.strip():
                    result.append(f'<p>{line}</p>')
                else:
                    result.append('')

        if in_list:
            result.append('</ul>')

        return '\n'.join(result)


def main():
    """테스트 실행"""
    # 테스트 데이터
    test_papers = {
        'cause': [
            {'title': 'Pathophysiology of GERD', 'abstract': 'Test abstract', 'authors': ['Kim A'], 'journal': 'J Med', 'year': '2023', 'url': '#'},
            {'title': 'Risk factors for reflux', 'abstract': 'Test abstract', 'authors': ['Lee B'], 'journal': 'J Med', 'year': '2022', 'url': '#'},
            {'title': 'Etiology of esophageal disease', 'abstract': 'Test abstract', 'authors': ['Park C'], 'journal': 'J Med', 'year': '2021', 'url': '#'},
        ],
        'treatment': [
            {'title': 'PPI therapy outcomes', 'abstract': 'Test abstract', 'authors': ['Choi D'], 'journal': 'J Med', 'year': '2023', 'url': '#'},
            {'title': 'Surgical treatment options', 'abstract': 'Test abstract', 'authors': ['Jung E'], 'journal': 'J Med', 'year': '2022', 'url': '#'},
            {'title': 'Drug effectiveness comparison', 'abstract': 'Test abstract', 'authors': ['Han F'], 'journal': 'J Med', 'year': '2021', 'url': '#'},
        ],
        'diet': [
            {'title': 'Dietary factors in GERD', 'abstract': 'Test abstract', 'authors': ['Yoon G'], 'journal': 'J Nutr', 'year': '2023', 'url': '#'},
            {'title': 'Food triggers for reflux', 'abstract': 'Test abstract', 'authors': ['Kang H'], 'journal': 'J Nutr', 'year': '2022', 'url': '#'},
            {'title': 'Nutrition and esophageal health', 'abstract': 'Test abstract', 'authors': ['Song I'], 'journal': 'J Nutr', 'year': '2021', 'url': '#'},
        ]
    }

    generator = SeriesBlogGenerator(output_dir='output')
    plan = generator.plan_series('역류성식도염', test_papers)

    print("\n📚 시리즈 계획:")
    print(json.dumps(plan, indent=2, ensure_ascii=False))

    # API 없이 플레이스홀더로 테스트
    results = generator.generate_all_posts('역류성식도염', test_papers)

    print(f"\n✓ {len(results)}개 파일 생성 완료")


if __name__ == "__main__":
    main()
