#!/usr/bin/env python
"""
논문 기반 자동 블로그 글 생성 CLI 스크립트

사용법:
    python generate_blog.py "역류성식도염" --papers 12 --style hybrid
"""

import argparse
import sys
import os
import json
from datetime import datetime
from modules.pubmed_search import PubMedSearcher
from config import Config

def main():
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description='PubMed 논문을 수집하고 Claude Code가 블로그 글을 생성합니다.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python generate_blog.py "역류성식도염" --papers 12
  python generate_blog.py "당뇨병 식이요법" --papers 15 --style hybrid
  python generate_blog.py "비타민D" --papers 10 --output custom_name.md
        """
    )

    parser.add_argument(
        'topic',
        type=str,
        help='검색할 주제 (예: "역류성식도염", "당뇨병")'
    )

    parser.add_argument(
        '--papers',
        type=int,
        default=12,
        help=f'수집할 논문 개수 (기본값: 12, 범위: {Config.MIN_PAPER_COUNT}-{Config.MAX_PAPER_COUNT})'
    )

    parser.add_argument(
        '--style',
        type=str,
        choices=['academic', 'casual', 'hybrid'],
        default='hybrid',
        help='블로그 글 스타일 (기본값: hybrid)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='출력 파일명 (지정하지 않으면 자동 생성)'
    )

    args = parser.parse_args()

    # 입력 검증
    if not args.topic.strip():
        print("❌ 오류: 주제를 입력해주세요.")
        sys.exit(1)

    if args.papers < Config.MIN_PAPER_COUNT or args.papers > Config.MAX_PAPER_COUNT:
        print(f"❌ 오류: 논문 개수는 {Config.MIN_PAPER_COUNT}-{Config.MAX_PAPER_COUNT} 사이여야 합니다.")
        sys.exit(1)

    print("\n" + "="*70)
    print("📚 논문 기반 자동 블로그 글 생성기 (CLI)")
    print("="*70)
    print(f"주제: {args.topic}")
    print(f"논문 개수: {args.papers}개")
    print(f"글 스타일: {args.style}")
    print("="*70 + "\n")

    # 1단계: PubMed에서 논문 검색 및 수집
    print("🔍 1단계: PubMed 논문 검색 중...")
    print("-" * 70)

    try:
        searcher = PubMedSearcher(
            email=Config.PUBMED_EMAIL,
            api_key=Config.PUBMED_API_KEY
        )
        papers = searcher.search_and_fetch(args.topic, max_results=args.papers)

        if not papers:
            print("\n❌ 관련 논문을 찾을 수 없습니다.")
            print("💡 다른 검색어를 시도해보세요:")
            print("   - 더 일반적인 용어 사용")
            print("   - 영문 의학 용어 사용")
            print("   - 철자 확인")
            sys.exit(1)

        print(f"\n✅ {len(papers)}개의 논문 수집 완료!")

    except Exception as e:
        print(f"\n❌ 논문 검색 실패: {str(e)}")
        sys.exit(1)

    # 2단계: 논문 데이터를 파일로 저장
    print("\n📄 2단계: 논문 데이터 저장 중...")
    print("-" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = args.topic.replace(' ', '_').replace('/', '_')

    # JSON 파일로 저장 (프로그래밍 용도)
    json_filename = f"{safe_topic}_papers_{timestamp}.json"
    json_filepath = os.path.join(Config.OUTPUT_DIR, json_filename)

    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'topic': args.topic,
            'paper_count': len(papers),
            'collected_at': timestamp,
            'style': args.style,
            'papers': papers
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ JSON 저장: {json_filepath}")

    # Markdown 파일로 저장 (읽기 쉬운 형식)
    md_filename = f"{safe_topic}_papers_{timestamp}.md"
    md_filepath = os.path.join(Config.OUTPUT_DIR, md_filename)

    markdown_content = generate_markdown(args.topic, papers, args.style)
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"✓ Markdown 저장: {md_filepath}")

    # 3단계: Claude Code에게 작업 지시
    print("\n🤖 3단계: Claude Code 분석 요청")
    print("-" * 70)
    print(f"""
✅ 논문 수집이 완료되었습니다!

📁 저장된 파일:
   - {json_filepath}
   - {md_filepath}

🤖 다음 단계:
   Claude Code에서 아래 명령을 실행하세요:

   "{md_filepath} 파일을 읽고 {args.topic}에 대한 {args.style} 스타일의 블로그 글을 HTML 형식으로 작성해주세요."

💡 또는 자동으로 Claude Code에게 전달하시겠습니까?
   (이 스크립트를 Claude Code에서 실행 중이라면 자동으로 이어집니다)
    """)

    print("="*70 + "\n")

    # 메타데이터 반환 (Claude Code가 읽을 수 있도록)
    return {
        'success': True,
        'topic': args.topic,
        'paper_count': len(papers),
        'json_file': json_filepath,
        'markdown_file': md_filepath,
        'style': args.style
    }


def generate_markdown(topic: str, papers: list, style: str) -> str:
    """논문 정보를 읽기 쉬운 Markdown 형식으로 변환 - 약올리는언니 스타일"""

    # 약올리는언니 스타일은 기본
    style_descriptions = {
        'academic': '전문적이고 학술적인 톤',
        'casual': '친근하고 쉬운 톤 (약올리는언니 스타일)',
        'hybrid': '약올리는언니 스타일 - 친근하면서도 근거 있는 글'
    }

    md = f"""# {topic} - 논문 분석 자료

**수집 논문 개수:** {len(papers)}개
**요청 스타일:** {style} ({style_descriptions[style]})
**수집 일시:** {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")}

---

## 📋 수집된 논문 목록

| 번호 | 제목 | 저자 | 저널 | 연도 | 유형 |
|------|------|------|------|------|------|
"""

    for i, paper in enumerate(papers, 1):
        authors_str = ", ".join(paper['authors'][:2]) if paper['authors'] else "Unknown"
        if len(paper['authors']) > 2:
            authors_str += " et al."

        md += f"| {i} | {paper['title']} | {authors_str} | {paper['journal']} | {paper['year']} | {paper['study_type']} |\n"

    md += "\n---\n\n## 📄 논문 상세 정보\n\n"

    for i, paper in enumerate(papers, 1):
        authors_str = ", ".join(paper['authors']) if paper['authors'] else "Unknown"
        if len(paper['authors']) > 3:
            authors_str = ", ".join(paper['authors'][:3]) + " et al."

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

    md += f"""
## 🎯 블로그 글 작성 지침 (약올리는언니 스타일)

위 {len(papers)}개의 논문을 분석해서 "{topic}"에 대한 블로그 글을 작성해주세요!

---

### ⚠️ 말투 규칙 (매우 중요!)

**기본 어미**: "~에요", "~하죠", "~거예요", "~해요", "~드려요"

❌ **절대 쓰지 마세요:**
- "~다", "~했다", "~이다" (딱딱함)
- "본 연구에서는", "유의미한 차이를 보였다" (학술체)

✅ **이렇게 쓰세요:**
- "~라고 해요"
- "~에 도움이 돼요"
- "~하신 분들 많으시죠?"

---

### 📝 문장 규칙

- **한 문장**: 15-25자 (짧게!)
- **한 문단**: 1-3문장만
- **줄바꿈**: 자주! 문단 사이에 빈 줄 필수

---

### 📊 논문/통계 인용 방법

❌ 이렇게 쓰지 마세요:
"메타분석 결과 위험비는 1.41(95% CI: 1.26-1.59)로 통계적으로 유의한 결과를 보였다(p<0.01)."

✅ 이렇게 쓰세요:
"여러 연구를 종합해보니까요,
~하신 분들은 약 1.4배 정도 위험이 높다고 해요.

꽤 의미 있는 차이죠?"

---

### 📋 글 구조 (이 순서대로!)

```html
<h1 class="title">[주제] - 매력적인 제목</h1>

<div class="section">
    <p>[주제]로 고생하시는 분들 많으시죠?</p>

    <blockquote>
    "독자의 전형적인 고민을 인용문으로"
    </blockquote>

    <p>이 질문에서 핵심을 알 수 있어요!</p>
</div>

<div class="deco">🌿</div>

<div class="section">
    <p>[주제]를 단순히 "~"로만 보면<br>
    설명이 안 되는 부분이 많아요.</p>

    <ul>
        <li>이런 경우</li>
        <li>저런 경우</li>
    </ul>
</div>

<div class="highlight purple">
    핵심 질문이나 개념을<br>
    아시나요?
</div>

<div class="section">
    <p>쉬운 설명을 여기에...</p>
    <p>우리 몸은 원래 ~하는 기능이 있어요.</p>
</div>

<h2>1. 첫 번째 해결 방법</h2>

<div class="section">
    <p>설명...</p>
    <p>실제 연구결과도 있어요!</p>
    <p>~라고 해요.</p>

    <div class="recommend-box">
        <h4>✅ 이런 분들께 추천해요!</h4>
        <ul>
            <li>~하는 경우</li>
            <li>~인 분들</li>
        </ul>
    </div>
</div>

<h2>2. 두 번째 해결 방법</h2>
...

<div class="caution">
    <strong>⚠️ 잠깐!</strong><br>
    모든 분께 해당되는 건 아니에요.<br>
    ~한 경우에는 전문가와 상담하세요.
</div>

<div class="summary-box">
    <h3>📝 정리하면요!</h3>
    <ol>
        <li>핵심 1</li>
        <li>핵심 2</li>
        <li>핵심 3</li>
    </ol>
</div>
```

---

### ✅ 최종 체크리스트

글을 완성한 후 확인하세요:

1. [ ] "~다"로 끝나는 문장이 없나요? → "~에요"로 수정
2. [ ] 문장이 25자를 넘지 않나요?
3. [ ] 복잡한 통계가 있나요? → 핵심 숫자만 남기기
4. [ ] 줄바꿈이 충분한가요?
5. [ ] 친구에게 말하는 듯한 느낌인가요?

---

**이제 위 규칙을 철저히 지켜서 블로그 글을 작성해주세요!**
**출력은 HTML 형식으로, 위 구조를 따라주세요.**
"""

    return md


if __name__ == "__main__":
    try:
        result = main()
        if result and result['success']:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
