#!/usr/bin/env python
"""
시리즈 블로그 자동 생성 파이프라인

키워드 입력 → 웹 검색으로 연관 키워드 추출 → PubMed 논문 검색
→ 카테고리별 분류 → 시리즈 블로그 글 생성

사용법:
    python generate_series.py "역류성식도염" --total 50
    python generate_series.py "비타민D 결핍" --categories cause,treatment,diet
    python generate_series.py "GERD" --skip-web-search
"""

import argparse
import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

# 모듈 임포트
from modules.pubmed_search import PubMedSearcher
from modules.web_search import WebSearchKeywordExtractor
from modules.paper_classifier import PaperClassifier
from modules.series_generator import SeriesBlogGenerator
from config import Config


def search_with_related_keywords(
    searcher: PubMedSearcher,
    keyword_extractor: WebSearchKeywordExtractor,
    topic: str,
    total_papers: int,
    skip_web_search: bool = False
) -> List[Dict]:
    """
    연관 키워드를 포함하여 논문 검색

    Args:
        searcher: PubMed 검색기
        keyword_extractor: 키워드 추출기
        topic: 검색 주제
        total_papers: 목표 논문 개수
        skip_web_search: 웹 검색 건너뛰기

    Returns:
        수집된 논문 리스트
    """
    all_papers = []
    seen_pmids = set()

    # 1. 연관 키워드 추출 (옵션)
    if not skip_web_search:
        related_keywords = keyword_extractor.extract_related_keywords(
            topic,
            max_keywords=Config.MAX_RELATED_KEYWORDS
        )
        search_queries = keyword_extractor.get_search_queries(topic, related_keywords)
    else:
        print(f"\n🔍 웹 검색 건너뜀, 기본 쿼리만 사용")
        search_queries = create_default_queries(topic)

    papers_per_query = max(5, total_papers // len(search_queries))

    print(f"\n📚 {len(search_queries)}개 쿼리로 논문 검색 시작...")
    print("-" * 70)

    # 2. 각 쿼리로 논문 검색
    for i, query in enumerate(search_queries, 1):
        if len(all_papers) >= total_papers:
            print(f"\n✓ 목표 논문 수({total_papers}개)에 도달했습니다.")
            break

        print(f"\n[{i}/{len(search_queries)}] 검색: {query}")

        try:
            papers = searcher.search_and_fetch(query, max_results=papers_per_query)

            new_papers = 0
            for paper in papers:
                if paper['pmid'] not in seen_pmids:
                    if not is_animal_study(paper):
                        seen_pmids.add(paper['pmid'])
                        paper['search_query'] = query
                        all_papers.append(paper)
                        new_papers += 1

            print(f"   → 새로운 논문 {new_papers}개 추가")

        except Exception as e:
            print(f"   → 검색 실패: {str(e)}")
            continue

    return all_papers


def create_default_queries(topic: str) -> List[str]:
    """기본 검색 쿼리 생성 - 더 다양한 검색어 사용"""
    simple_topic = topic.split()[0]

    return [
        # 기본 검색
        topic,
        simple_topic,
        # 치료 관련
        f"{simple_topic} treatment",
        f"{simple_topic} therapy",
        f"{simple_topic} proton pump inhibitor",
        f"{simple_topic} medication",
        # 식이 관련
        f"{simple_topic} diet",
        f"{simple_topic} food",
        f"{simple_topic} nutrition",
        f"{simple_topic} caffeine alcohol",
        # 생활습관 관련
        f"{simple_topic} lifestyle",
        f"{simple_topic} obesity weight",
        f"{simple_topic} exercise",
        f"{simple_topic} sleep position",
        f"{simple_topic} smoking",
        # 원인 관련
        f"{simple_topic} pathophysiology",
        f"{simple_topic} risk factor",
        f"{simple_topic} etiology",
        # 예방/합병증
        f"{simple_topic} prevention",
        f"{simple_topic} barrett esophagus",
        f"{simple_topic} complications"
    ]


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


def filter_categories(
    categorized_papers: Dict[str, List[Dict]],
    selected_categories: Optional[List[str]]
) -> Dict[str, List[Dict]]:
    """선택된 카테고리만 필터링"""
    if not selected_categories:
        return categorized_papers

    return {
        cat: papers
        for cat, papers in categorized_papers.items()
        if cat in selected_categories
    }


def print_summary(topic: str, papers: List[Dict], categorized: Dict[str, List[Dict]]):
    """요약 정보 출력"""
    print("\n" + "=" * 70)
    print("📊 수집 결과 요약")
    print("=" * 70)
    print(f"주제: {topic}")
    print(f"총 논문 수: {len(papers)}개")
    print("\n카테고리별 분포:")

    classifier = PaperClassifier()
    for category, cat_papers in sorted(categorized.items(), key=lambda x: -len(x[1])):
        config = classifier.CATEGORY_KEYWORDS.get(category, {'korean_name': category})
        bar = "█" * min(len(cat_papers), 30)
        print(f"  {config.get('korean_name', category):8s}: {len(cat_papers):3d}개 {bar}")


def main():
    parser = argparse.ArgumentParser(
        description='시리즈 블로그 자동 생성 파이프라인',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_series.py "역류성식도염" --total 50
  python generate_series.py "비타민D 결핍" --categories cause,treatment,diet
  python generate_series.py "GERD" --skip-web-search --total 30
        """
    )

    parser.add_argument('topic', type=str, help='검색할 주제 (예: "역류성식도염", "GERD")')
    parser.add_argument('--total', type=int, default=50, help='목표 논문 개수 (기본값: 50)')
    parser.add_argument('--categories', type=str, default=None,
                        help='생성할 카테고리 (쉼표 구분). 예: cause,treatment,diet')
    parser.add_argument('--skip-web-search', action='store_true',
                        help='웹 검색 연관 키워드 추출 건너뛰기')
    parser.add_argument('--skip-generation', action='store_true',
                        help='블로그 글 생성 건너뛰기 (논문 수집만)')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='출력 디렉토리 (기본값: output)')

    args = parser.parse_args()

    # 출력 디렉토리 생성
    os.makedirs(args.output_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print("📚 시리즈 블로그 자동 생성 파이프라인")
    print("=" * 70)
    print(f"주제: {args.topic}")
    print(f"목표 논문: {args.total}개")
    print(f"웹 검색: {'건너뜀' if args.skip_web_search else '사용'}")
    if args.categories:
        print(f"선택 카테고리: {args.categories}")
    print("=" * 70)

    # API 클라이언트 초기화
    try:
        Config.validate()
        from anthropic import Anthropic
        anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        print("✓ Anthropic API 연결 성공")
    except Exception as e:
        print(f"⚠️ Anthropic API 연결 실패: {str(e)}")
        print("   블로그 글 생성이 제한됩니다.")
        anthropic_client = None

    # 검색기 초기화
    searcher = PubMedSearcher(
        email=Config.PUBMED_EMAIL,
        api_key=Config.PUBMED_API_KEY
    )
    keyword_extractor = WebSearchKeywordExtractor()

    # 1단계: 논문 수집
    print("\n" + "=" * 70)
    print("📖 1단계: 논문 수집")
    print("=" * 70)

    papers = search_with_related_keywords(
        searcher,
        keyword_extractor,
        args.topic,
        args.total,
        skip_web_search=args.skip_web_search
    )

    if not papers:
        print("\n❌ 논문을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"\n✅ 총 {len(papers)}개 논문 수집 완료!")

    # 2단계: 논문 분류
    print("\n" + "=" * 70)
    print("🏷️ 2단계: 논문 분류")
    print("=" * 70)

    classifier = PaperClassifier(anthropic_client=anthropic_client)
    categorized = classifier.classify_papers(papers)

    # 카테고리 필터링
    if args.categories:
        selected = [c.strip() for c in args.categories.split(',')]
        categorized = filter_categories(categorized, selected)

    # 요약 출력
    print_summary(args.topic, papers, categorized)

    # 중간 결과 저장 (JSON)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = args.topic.replace(' ', '_').replace('/', '_')

    json_filename = f"{safe_topic}_papers_{timestamp}.json"
    json_filepath = os.path.join(args.output_dir, json_filename)

    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'topic': args.topic,
            'total_papers': len(papers),
            'categorized': {k: len(v) for k, v in categorized.items()},
            'papers': papers
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📄 논문 데이터 저장: {json_filename}")

    # 3단계: 블로그 글 생성
    if not args.skip_generation:
        print("\n" + "=" * 70)
        print("✍️ 3단계: 시리즈 블로그 글 생성")
        print("=" * 70)

        # 카테고리별 최소 논문 수 확인
        valid_categories = {
            cat: papers_list
            for cat, papers_list in categorized.items()
            if len(papers_list) >= Config.MIN_PAPERS_PER_CATEGORY
        }

        if not valid_categories:
            print(f"\n⚠️ 각 카테고리에 최소 {Config.MIN_PAPERS_PER_CATEGORY}개 이상의 논문이 필요합니다.")
            print("   논문 수가 부족한 카테고리:")
            for cat, papers_list in categorized.items():
                if len(papers_list) < Config.MIN_PAPERS_PER_CATEGORY:
                    print(f"   - {cat}: {len(papers_list)}개")
            sys.exit(1)

        generator = SeriesBlogGenerator(
            anthropic_client=anthropic_client,
            output_dir=args.output_dir
        )

        results = generator.generate_all_posts(args.topic, valid_categories)

        if results:
            print("\n" + "=" * 70)
            print("✅ 생성 완료!")
            print("=" * 70)
            print(f"\n📁 생성된 파일 ({len(results)}개):")
            for result in results:
                print(f"   - {result['filename']}")
                print(f"     ({result['korean_name']}, 논문 {result['paper_count']}개)")

            # 시리즈 인덱스 파일 위치
            index_file = f"{safe_topic}_series_index.json"
            print(f"\n📋 시리즈 인덱스: {index_file}")
        else:
            print("\n⚠️ 생성된 글이 없습니다.")
    else:
        print("\n⏭️ 블로그 글 생성을 건너뛰었습니다.")

    print("\n" + "=" * 70)
    print("🎉 파이프라인 완료!")
    print("=" * 70)

    return {
        'success': True,
        'topic': args.topic,
        'paper_count': len(papers),
        'categories': list(categorized.keys())
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
