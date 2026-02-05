"""
차별화된 블로그 생성 파이프라인

1. 기존 블로그 분석 → 뭐가 이미 있는지 파악
2. PubMed 논문 검색
3. 논문 vs 기존 블로그 비교 → 새로운 사실 추출
4. 차별화된 콘텐츠로 블로그 생성
"""

import argparse
import json
import os
from datetime import datetime
from typing import List, Dict

# 모듈 임포트
from modules.competitor_analyzer import CompetitorAnalyzer, NoveltyFinder
from modules.pubmed_search import PubMedSearcher
from modules.paper_classifier import PaperClassifier
from config import Config


def run_pipeline(keyword: str,
                 korean_keyword: str = None,
                 max_blogs: int = 10,
                 max_papers: int = 50,
                 skip_competitor: bool = False) -> Dict:
    """
    전체 파이프라인 실행

    Args:
        keyword: 영문 키워드 (PubMed 검색용)
        korean_keyword: 한글 키워드 (블로그 검색용, 없으면 keyword 사용)
        max_blogs: 분석할 경쟁 블로그 수
        max_papers: 검색할 논문 수
        skip_competitor: 경쟁 분석 스킵 (이미 데이터가 있을 때)
    """

    korean_keyword = korean_keyword or keyword
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(f"차별화 블로그 생성 파이프라인")
    print(f"영문 키워드: {keyword}")
    print(f"한글 키워드: {korean_keyword}")
    print("=" * 60)

    # ============================================
    # STEP 1: 경쟁 블로그 분석
    # ============================================
    print("\n[STEP 1] 경쟁 블로그 분석")

    analyzer = CompetitorAnalyzer(output_dir="competitor_data")

    if skip_competitor:
        competitor_data = analyzer.load_competitor_data(korean_keyword)
        if competitor_data:
            print(f"  → 기존 데이터 로드: {competitor_data['blog_count']}개 블로그")
        else:
            print("  → 기존 데이터 없음, 새로 분석...")
            competitor_data = analyzer.search_and_analyze(korean_keyword, max_blogs)
    else:
        competitor_data = analyzer.search_and_analyze(korean_keyword, max_blogs)

    # 공통 포인트 출력
    print("\n  [기존 블로그들의 공통 내용]")
    for point in competitor_data.get('common_points', []):
        print(f"    - {point}")

    # ============================================
    # STEP 2: PubMed 논문 검색
    # ============================================
    print("\n[STEP 2] PubMed 논문 검색")

    searcher = PubMedSearcher(email=Config.PUBMED_EMAIL)

    # 다양한 검색 쿼리 생성
    queries = [
        f"{keyword}",
        f"{keyword} treatment",
        f"{keyword} diet food",
        f"{keyword} lifestyle",
        f"{keyword} risk factors",
        f"{keyword} complications",
        f"{keyword} prevention",
        f"{keyword} novel findings",
        f"{keyword} recent advances",
        f"{keyword} meta-analysis",
    ]

    all_papers = []
    seen_pmids = set()

    for query in queries:
        papers = searcher.search(query, max_results=max_papers // len(queries))
        for paper in papers:
            if paper['pmid'] not in seen_pmids:
                seen_pmids.add(paper['pmid'])
                all_papers.append(paper)

    print(f"  → 총 {len(all_papers)}개 논문 수집")

    # ============================================
    # STEP 3: 새로운 사실 찾기
    # ============================================
    print("\n[STEP 3] 새로운 사실 찾기 (논문 vs 기존 블로그)")

    finder = NoveltyFinder()
    novel_facts = finder.find_novel_facts(all_papers, competitor_data, min_novelty_score=0.25)

    print(f"  → {len(novel_facts)}개 새로운 사실 발견")

    # 요약
    summary = finder.summarize_novel_findings(novel_facts, top_n=30)

    print(f"\n  [감성별 분류]")
    print(f"    - 긍정적 발견: {len(summary['by_sentiment']['positive'])}개")
    print(f"    - 부정적 발견: {len(summary['by_sentiment']['negative'])}개")
    print(f"    - 중립적 발견: {len(summary['by_sentiment']['neutral'])}개")

    print(f"\n  [카테고리별 분류]")
    for cat, facts in summary['by_category'].items():
        print(f"    - {cat}: {len(facts)}개")

    print(f"\n  [통계 데이터 포함 발견: {len(summary['statistics_findings'])}개]")

    # ============================================
    # STEP 4: 결과 저장
    # ============================================
    print("\n[STEP 4] 결과 저장")

    # 새로운 발견들 저장
    result = {
        'keyword': keyword,
        'korean_keyword': korean_keyword,
        'generated_at': datetime.now().isoformat(),
        'competitor_analysis': {
            'blog_count': competitor_data['blog_count'],
            'common_points': competitor_data['common_points'],
        },
        'papers_analyzed': len(all_papers),
        'novel_facts_summary': summary,
        'top_novel_facts': novel_facts[:50],
        'all_novel_facts': novel_facts,
    }

    output_path = os.path.join(output_dir, f"{keyword}_novel_facts_{datetime.now().strftime('%Y%m%d')}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  → 저장 완료: {output_path}")

    # ============================================
    # TOP 발견들 출력
    # ============================================
    print("\n" + "=" * 60)
    print("TOP 새로운 발견들 (기존 블로그에 없는 내용)")
    print("=" * 60)

    for i, fact in enumerate(novel_facts[:15], 1):
        sentiment_emoji = {'positive': '✅', 'negative': '⚠️', 'neutral': '📌'}[fact['sentiment']]
        stats_mark = '📊' if fact['has_statistics'] else ''

        print(f"\n{i}. {sentiment_emoji} {stats_mark} [{fact['category']}]")
        print(f"   {fact['fact'][:200]}...")
        print(f"   출처: PMID {fact['source_pmid']}")
        print(f"   새로움 점수: {fact['novelty_score']:.2f}")

    return result


def print_blog_outline(result: Dict):
    """블로그 글 아웃라인 생성"""

    print("\n" + "=" * 60)
    print("차별화 블로그 글 아웃라인")
    print("=" * 60)

    facts = result['all_novel_facts']

    # 카테고리별 정리
    categories = {
        'cause': '원인편 - 새로운 발견',
        'treatment': '치료편 - 새로운 발견',
        'diet': '식이요법편 - 새로운 발견',
        'lifestyle': '생활습관편 - 새로운 발견',
        'complications': '합병증편 - 새로운 발견',
        'prevention': '예방편 - 새로운 발견',
    }

    for cat_key, cat_name in categories.items():
        cat_facts = [f for f in facts if f['category'] == cat_key]

        if not cat_facts:
            continue

        print(f"\n### {cat_name}")

        # 긍정적 발견
        positive = [f for f in cat_facts if f['sentiment'] == 'positive']
        if positive:
            print("\n  [✅ 희소식]")
            for f in positive[:3]:
                print(f"    - {f['fact'][:150]}...")

        # 부정적 발견
        negative = [f for f in cat_facts if f['sentiment'] == 'negative']
        if negative:
            print("\n  [⚠️ 주의할 점]")
            for f in negative[:3]:
                print(f"    - {f['fact'][:150]}...")

        # 통계 데이터
        stats = [f for f in cat_facts if f['has_statistics']]
        if stats:
            print("\n  [📊 구체적 수치]")
            for f in stats[:3]:
                print(f"    - {f['fact'][:150]}...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='차별화된 블로그 생성')
    parser.add_argument('keyword', help='영문 키워드 (PubMed 검색용)')
    parser.add_argument('--korean', '-k', help='한글 키워드 (블로그 검색용)')
    parser.add_argument('--blogs', type=int, default=10, help='분석할 경쟁 블로그 수')
    parser.add_argument('--papers', type=int, default=50, help='검색할 논문 수')
    parser.add_argument('--skip-competitor', action='store_true', help='경쟁 분석 스킵')
    parser.add_argument('--outline', action='store_true', help='블로그 아웃라인 출력')

    args = parser.parse_args()

    result = run_pipeline(
        keyword=args.keyword,
        korean_keyword=args.korean,
        max_blogs=args.blogs,
        max_papers=args.papers,
        skip_competitor=args.skip_competitor
    )

    if args.outline:
        print_blog_outline(result)
