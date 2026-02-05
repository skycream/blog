"""
블로그 자동 생성 파이프라인

실행 방법:
    python auto_pipeline.py "역류성식도염"

파이프라인 흐름:
    [1] 인기 블로그 수집 (네이버)
    [2] LLM/규칙 기반 토픽 추출 (독자 관심사 분석)
    [3] 토픽별 PubMed 논문 검색
    [4] 차별화 포인트 추출
    [5] HTML 블로그 글 생성
"""

import sys
import os
import json
from datetime import datetime

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.smart_topic_extractor import SmartTopicExtractor
from modules.pubmed_search import PubMedSearcher
from config import Config


def run_pipeline(keyword: str, max_blogs: int = 20, max_papers: int = 50):
    """
    전체 파이프라인 실행

    Args:
        keyword: 메인 키워드 (예: "역류성식도염")
        max_blogs: 분석할 블로그 수
        max_papers: 수집할 논문 수
    """
    print(f"\n{'#'*70}")
    print(f"# 블로그 자동 생성 파이프라인")
    print(f"# 키워드: {keyword}")
    print(f"# 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}")

    # ================================================================
    # STEP 1: 인기 블로그에서 토픽 추출
    # ================================================================
    print(f"\n\n{'='*70}")
    print(f"STEP 1: 인기 블로그 분석 → 독자 관심 토픽 추출")
    print(f"{'='*70}")

    extractor = SmartTopicExtractor()
    topic_result = extractor.extract_topics(keyword, max_blogs=max_blogs)

    top_topics = topic_result['top_topics'][:10]  # 상위 10개 토픽
    search_queries = topic_result['search_queries'][:10]

    print(f"\n📊 상위 독자 관심 토픽:")
    for i, topic in enumerate(top_topics, 1):
        count = topic_result['topic_counts'].get(topic, 0)
        print(f"   {i}. {topic} ({count}회 언급)")

    # ================================================================
    # STEP 2: PubMed 논문 검색
    # ================================================================
    print(f"\n\n{'='*70}")
    print(f"STEP 2: PubMed 논문 검색")
    print(f"{'='*70}")

    searcher = PubMedSearcher(
        email=Config.PUBMED_EMAIL,
        api_key=Config.PUBMED_API_KEY
    )

    all_papers = []
    papers_by_topic = {}

    for query in search_queries:
        print(f"\n  검색: {query}")
        try:
            # search_and_fetch로 상세 정보까지 가져오기
            papers = searcher.search_and_fetch(
                query=query,
                max_results=max_papers // len(search_queries) + 5
            )
            print(f"    → {len(papers)}편 수집 완료")

            # 토픽별 분류
            topic = query.split(' AND ')[1] if ' AND ' in query else query
            papers_by_topic[topic] = papers
            all_papers.extend(papers)

        except Exception as e:
            print(f"    → 오류: {e}")

    # 중복 제거
    seen_pmids = set()
    unique_papers = []
    for paper in all_papers:
        pmid = paper.get('pmid')
        if pmid and pmid not in seen_pmids:
            seen_pmids.add(pmid)
            unique_papers.append(paper)

    print(f"\n📚 총 {len(unique_papers)}편 고유 논문 수집 완료")

    # ================================================================
    # STEP 3: 결과 저장
    # ================================================================
    print(f"\n\n{'='*70}")
    print(f"STEP 3: 결과 저장")
    print(f"{'='*70}")

    # 파이프라인 결과 저장
    result = {
        'keyword': keyword,
        'keyword_en': topic_result.get('main_keyword_en', keyword),
        'pipeline_date': datetime.now().isoformat(),
        'blogs_analyzed': topic_result['blogs_analyzed'],
        'top_topics': top_topics,
        'topic_counts': topic_result['topic_counts'],
        'search_queries': search_queries,
        'papers_count': len(unique_papers),
        'papers_by_topic': {k: len(v) for k, v in papers_by_topic.items()},
        'papers': unique_papers[:100]  # 상위 100편만 저장
    }

    # 저장
    output_dir = "pipeline_data"
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(
        output_dir,
        f"{keyword}_pipeline_{datetime.now().strftime('%Y%m%d')}.json"
    )

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 저장 완료: {save_path}")

    # ================================================================
    # 요약 출력
    # ================================================================
    print(f"\n\n{'='*70}")
    print(f"📋 파이프라인 요약")
    print(f"{'='*70}")
    print(f"  • 키워드: {keyword}")
    print(f"  • 분석 블로그: {topic_result['blogs_analyzed']}개")
    print(f"  • 발견 토픽: {len(topic_result['topic_counts'])}개")
    print(f"  • 수집 논문: {len(unique_papers)}편")
    print(f"  • 저장 경로: {save_path}")

    print(f"\n📌 다음 단계:")
    print(f"   이 데이터를 기반으로 블로그 글을 작성하세요.")
    print(f"   토픽별 논문 분석 결과를 활용하여 차별화된 콘텐츠를 만들 수 있습니다.")

    # 토픽별 논문 수 출력
    print(f"\n📊 토픽별 논문 수:")
    for topic, count in sorted(papers_by_topic.items(), key=lambda x: -len(x[1])):
        print(f"   • {topic}: {len(count)}편")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python auto_pipeline.py <키워드>")
        print("예시: python auto_pipeline.py 역류성식도염")
        sys.exit(1)

    keyword = sys.argv[1]
    run_pipeline(keyword)
