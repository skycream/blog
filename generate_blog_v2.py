#!/usr/bin/env python
"""
논문 기반 자동 블로그 글 생성 CLI v2 - 다중 검색 버전

하나의 주제에 대해 여러 각도로 검색하여 풍부한 논문을 수집합니다.

사용법:
    python generate_blog_v2.py "역류성식도염"
    python generate_blog_v2.py "GERD" --total 50
"""

import argparse
import sys
import os
import json
from datetime import datetime
from modules.pubmed_search import PubMedSearcher
from config import Config


def create_search_queries(topic: str) -> list:
    """
    하나의 주제에 대해 여러 검색 쿼리 생성
    더 다양하고 구체적인 검색어를 사용합니다.
    """
    # 기본 주제를 간단하게 변환
    simple_topic = topic.split()[0]  # 첫 단어만 (GERD, vitamin, etc.)

    queries = [
        # 기본 검색
        f"{topic}",
        f"{simple_topic}",

        # 치료 관련
        f"{simple_topic} treatment therapy",
        f"{simple_topic} proton pump inhibitor",
        f"{simple_topic} medication drug",
        f"{simple_topic} surgery surgical",

        # 생활습관
        f"{simple_topic} diet dietary food",
        f"{simple_topic} lifestyle modification",
        f"{simple_topic} weight loss obesity",
        f"{simple_topic} exercise physical activity",
        f"{simple_topic} sleep position",

        # 원인
        f"{simple_topic} pathophysiology",
        f"{simple_topic} risk factors",
        f"{simple_topic} etiology cause",

        # 증상/진단
        f"{simple_topic} symptoms diagnosis",
        f"{simple_topic} heartburn",

        # 보완요법
        f"{simple_topic} alternative complementary",
        f"{simple_topic} herbal natural",

        # 특수 상황
        f"{simple_topic} pregnancy",
        f"{simple_topic} complications",
    ]

    return queries


def search_multiple(searcher: PubMedSearcher, topic: str, total_papers: int = 50) -> list:
    """
    여러 검색어로 검색하여 논문 수집
    """
    queries = create_search_queries(topic)
    papers_per_query = max(10, total_papers // len(queries))

    all_papers = []
    seen_pmids = set()

    print(f"\n🔍 '{topic}'에 대해 {len(queries)}개 관점으로 검색합니다...")
    print("-" * 70)

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] 검색: {query}")

        try:
            papers = searcher.search_and_fetch(query, max_results=papers_per_query)

            # 중복 제거
            new_papers = 0
            for paper in papers:
                if paper['pmid'] not in seen_pmids:
                    # 동물 연구 제외
                    if not is_animal_study(paper):
                        seen_pmids.add(paper['pmid'])
                        paper['search_query'] = query  # 어떤 검색어로 찾았는지 기록
                        all_papers.append(paper)
                        new_papers += 1

            print(f"   → 새로운 논문 {new_papers}개 추가 (중복/동물연구 제외)")

        except Exception as e:
            print(f"   → 검색 실패: {str(e)}")
            continue

        # 충분히 모았으면 중단
        if len(all_papers) >= total_papers:
            print(f"\n✓ 목표 논문 수({total_papers}개)에 도달했습니다.")
            break

    return all_papers


def is_animal_study(paper: dict) -> bool:
    """동물 연구인지 확인"""
    title_lower = paper['title'].lower()
    abstract_lower = paper['abstract'].lower()

    animal_keywords = [
        'mice', 'mouse', 'rat', 'rats', 'rabbit', 'rabbits',
        'dog', 'dogs', 'cat', 'cats', 'canine', 'feline',
        'porcine', 'bovine', 'animal model', 'in vivo',
        'veterinary', 'murine'
    ]

    for keyword in animal_keywords:
        if keyword in title_lower or keyword in abstract_lower[:500]:
            return True

    return False


def categorize_papers(papers: list) -> dict:
    """논문을 카테고리별로 분류"""
    categories = {
        'treatment': [],      # 치료
        'diet': [],           # 식이
        'lifestyle': [],      # 생활습관
        'mechanism': [],      # 원인/메커니즘
        'prevention': [],     # 예방
        'general': []         # 일반
    }

    for paper in papers:
        query = paper.get('search_query', '').lower()
        title = paper['title'].lower()
        abstract = paper['abstract'].lower()

        if 'treatment' in query or 'therapy' in query or 'PPI' in query:
            categories['treatment'].append(paper)
        elif 'diet' in query or 'food' in title or 'dietary' in abstract:
            categories['diet'].append(paper)
        elif 'lifestyle' in query or 'exercise' in abstract or 'smoking' in abstract:
            categories['lifestyle'].append(paper)
        elif 'mechanism' in query or 'pathophysiology' in query:
            categories['mechanism'].append(paper)
        elif 'prevention' in query:
            categories['prevention'].append(paper)
        else:
            categories['general'].append(paper)

    return categories


def generate_detailed_markdown(topic: str, papers: list, categories: dict) -> str:
    """상세한 Markdown 보고서 생성"""

    md = f"""# {topic} - 종합 논문 분석 자료

**총 수집 논문:** {len(papers)}개
**수집 일시:** {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")}

---

## 📊 카테고리별 논문 분포

| 카테고리 | 논문 수 |
|----------|---------|
| 치료 (Treatment) | {len(categories['treatment'])}개 |
| 식이요법 (Diet) | {len(categories['diet'])}개 |
| 생활습관 (Lifestyle) | {len(categories['lifestyle'])}개 |
| 원인/메커니즘 | {len(categories['mechanism'])}개 |
| 예방 (Prevention) | {len(categories['prevention'])}개 |
| 일반 | {len(categories['general'])}개 |

---

## 📋 전체 논문 목록

| 번호 | 제목 | 저자 | 저널 | 연도 | 유형 |
|------|------|------|------|------|------|
"""

    for i, paper in enumerate(papers, 1):
        authors_str = ", ".join(paper['authors'][:2]) if paper['authors'] else "Unknown"
        if len(paper['authors']) > 2:
            authors_str += " et al."
        # 제목이 너무 길면 자르기
        title = paper['title'][:80] + "..." if len(paper['title']) > 80 else paper['title']
        md += f"| {i} | {title} | {authors_str} | {paper['journal']} | {paper['year']} | {paper['study_type']} |\n"

    # 카테고리별 상세 정보
    for cat_name, cat_papers in categories.items():
        if not cat_papers:
            continue

        cat_titles = {
            'treatment': '💊 치료 관련 논문',
            'diet': '🥗 식이요법 관련 논문',
            'lifestyle': '🏃 생활습관 관련 논문',
            'mechanism': '🔬 원인/메커니즘 관련 논문',
            'prevention': '🛡️ 예방 관련 논문',
            'general': '📚 일반 논문'
        }

        md += f"\n---\n\n## {cat_titles[cat_name]} ({len(cat_papers)}개)\n\n"

        for i, paper in enumerate(cat_papers, 1):
            authors_str = ", ".join(paper['authors'][:3]) if paper['authors'] else "Unknown"
            if len(paper['authors']) > 3:
                authors_str += " et al."

            md += f"""### [{i}] {paper['title']}

**저자:** {authors_str}
**저널:** {paper['journal']} ({paper['year']})
**연구 유형:** {paper['study_type']}
**PMID:** {paper['pmid']}
**링크:** {paper['url']}

**초록:**
{paper['abstract']}

---

"""

    # 분석 지침
    md += f"""
## 🎯 블로그 글 작성 지침 (약올리는언니 스타일)

위 {len(papers)}개의 논문을 분석해서 "{topic}"에 대한 **깊이 있는** 블로그 글을 작성해주세요!

### 📌 특히 다음 내용을 깊이 있게 다뤄주세요:

1. **치료 논문 ({len(categories['treatment'])}개)에서:**
   - 어떤 약이 효과적인지
   - 약의 종류별 차이점
   - 약 복용 시 주의사항

2. **식이요법 논문 ({len(categories['diet'])}개)에서:**
   - 구체적으로 어떤 음식이 좋은지/나쁜지
   - 얼마나 먹어야 하는지
   - 실제 연구에서 나온 구체적인 수치

3. **생활습관 논문 ({len(categories['lifestyle'])}개)에서:**
   - 구체적인 생활습관 변화 방법
   - 운동 종류, 시간, 빈도
   - 수면 자세, 식사 시간 등

4. **원인/메커니즘 논문 ({len(categories['mechanism'])}개)에서:**
   - 왜 이 병이 생기는지 쉽게 설명
   - 어떤 사람이 잘 걸리는지

---

### ⚠️ 말투 규칙 (매우 중요!)

**기본 어미**: "~에요", "~하죠", "~거예요", "~해요"

❌ **절대 쓰지 마세요:**
- "~다", "~했다", "~이다" (딱딱함)
- "본 연구에서는", "유의미한 차이를 보였다" (학술체)

✅ **이렇게 쓰세요:**
- "~라고 해요"
- "~에 도움이 돼요"
- "~하신 분들 많으시죠?"

---

### 📝 문장 규칙

- 한 문장: 15-25자
- 한 문단: 1-3문장
- 줄바꿈: 자주!

---

### 📊 통계 인용 방법

❌ "OR=5.08, 95% CI: 4.03-6.4, p<0.01"
✅ "야식을 자주 먹으면 약 5배 위험해요!"

---

### 📋 글 구조

1. 인사 + 공감 (독자 고민 인용)
2. 왜 이런 일이 생기는지 (원인)
3. 해결 방법들 (번호 매기기)
   - 각 방법마다 "이런 분께 추천!" 박스
4. 주의사항
5. 정리 (핵심 5가지)
6. 마무리

---

**이제 위 {len(papers)}개 논문을 꼼꼼히 분석해서**
**구체적이고 실용적인 블로그 글을 작성해주세요!**
**일반적인 말 대신, 논문에서 나온 구체적인 수치와 방법을 사용하세요!**
"""

    return md


def main():
    parser = argparse.ArgumentParser(
        description='다중 검색으로 풍부한 논문을 수집합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_blog_v2.py "역류성식도염"
  python generate_blog_v2.py "GERD" --total 50
  python generate_blog_v2.py "vitamin D deficiency" --total 40
        """
    )

    parser.add_argument('topic', type=str, help='검색할 주제')
    parser.add_argument('--total', type=int, default=40, help='목표 논문 개수 (기본값: 40)')

    args = parser.parse_args()

    print("\n" + "="*70)
    print("📚 논문 기반 블로그 글 생성기 v2 (다중 검색)")
    print("="*70)
    print(f"주제: {args.topic}")
    print(f"목표 논문: {args.total}개")
    print("="*70)

    # 검색
    searcher = PubMedSearcher(
        email=Config.PUBMED_EMAIL,
        api_key=Config.PUBMED_API_KEY
    )

    papers = search_multiple(searcher, args.topic, args.total)

    if not papers:
        print("\n❌ 논문을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"\n✅ 총 {len(papers)}개 논문 수집 완료!")

    # 카테고리 분류
    categories = categorize_papers(papers)

    print("\n📊 카테고리별 분포:")
    print(f"   - 치료: {len(categories['treatment'])}개")
    print(f"   - 식이: {len(categories['diet'])}개")
    print(f"   - 생활습관: {len(categories['lifestyle'])}개")
    print(f"   - 원인/메커니즘: {len(categories['mechanism'])}개")
    print(f"   - 예방: {len(categories['prevention'])}개")
    print(f"   - 일반: {len(categories['general'])}개")

    # 파일 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = args.topic.replace(' ', '_').replace('/', '_')

    # JSON
    json_filename = f"{safe_topic}_v2_{timestamp}.json"
    json_filepath = os.path.join(Config.OUTPUT_DIR, json_filename)

    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'topic': args.topic,
            'total_papers': len(papers),
            'categories': {k: len(v) for k, v in categories.items()},
            'papers': papers
        }, f, ensure_ascii=False, indent=2)

    # Markdown
    md_filename = f"{safe_topic}_v2_{timestamp}.md"
    md_filepath = os.path.join(Config.OUTPUT_DIR, md_filename)

    markdown = generate_detailed_markdown(args.topic, papers, categories)
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"\n📄 파일 저장 완료:")
    print(f"   - {json_filepath}")
    print(f"   - {md_filepath}")

    print(f"""
{"="*70}

🎯 다음 단계:

Claude Code에서 아래 명령을 실행하세요:

"{md_filepath} 파일을 읽고
{args.topic}에 대한 깊이 있는 블로그 글을 작성해주세요.
논문에서 나온 구체적인 수치와 방법을 많이 사용해주세요."

{"="*70}
""")

    return {
        'success': True,
        'topic': args.topic,
        'paper_count': len(papers),
        'md_file': md_filepath
    }


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result['success'] else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
