"""논문 카테고리 분류 모듈"""
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


class PaperClassifier:
    """규칙 기반 + AI 보조 논문 분류"""

    # 카테고리별 키워드 사전
    CATEGORY_KEYWORDS = {
        'cause': {
            'keywords': [
                'pathophysiology', 'etiology', 'mechanism', 'risk factor', 'cause',
                'pathogenesis', 'origin', 'predisposing', 'susceptibility', 'associated with',
                'correlation', 'relationship between', 'underlying', 'development of'
            ],
            'weight': 1.0,
            'korean_name': '원인',
            'description': '질환의 원인, 발생 기전, 위험 요인'
        },
        'treatment': {
            'keywords': [
                'treatment', 'therapy', 'drug', 'medication', 'pharmaceutical',
                'PPI', 'proton pump inhibitor', 'H2 blocker', 'antacid', 'surgery',
                'surgical', 'laparoscopic', 'fundoplication', 'intervention',
                'pharmacological', 'therapeutic', 'efficacy', 'effectiveness'
            ],
            'weight': 1.0,
            'korean_name': '치료',
            'description': '약물치료, 수술, 의학적 개입'
        },
        'diet': {
            'keywords': [
                'diet', 'dietary', 'food', 'nutrition', 'nutritional', 'meal',
                'eating', 'beverage', 'caffeine', 'coffee', 'alcohol', 'spicy',
                'fatty food', 'citrus', 'chocolate', 'tomato', 'intake',
                'consumption', 'calorie', 'fiber', 'vegetable', 'fruit'
            ],
            'weight': 1.2,  # 식이 키워드에 약간 더 가중치
            'korean_name': '식이요법',
            'description': '음식, 영양, 식단 관련'
        },
        'lifestyle': {
            'keywords': [
                'lifestyle', 'exercise', 'physical activity', 'sleep', 'sleeping',
                'smoking', 'tobacco', 'weight', 'obesity', 'BMI', 'body mass',
                'stress', 'anxiety', 'posture', 'position', 'bed elevation',
                'behavior', 'behavioural', 'habit', 'sedentary'
            ],
            'weight': 1.0,
            'korean_name': '생활습관',
            'description': '운동, 수면, 체중, 스트레스 관리'
        },
        'prevention': {
            'keywords': [
                'prevention', 'preventive', 'protective', 'prophylaxis', 'prophylactic',
                'risk reduction', 'avoidance', 'screening', 'early detection',
                'lifestyle modification', 'health promotion'
            ],
            'weight': 0.9,
            'korean_name': '예방',
            'description': '예방법, 위험 감소'
        },
        'complications': {
            'keywords': [
                'complication', 'barrett', 'esophageal cancer', 'adenocarcinoma',
                'stricture', 'erosive', 'ulcer', 'bleeding', 'perforation',
                'aspiration', 'respiratory', 'dental erosion', 'laryngitis',
                'progression', 'outcome', 'prognosis'
            ],
            'weight': 1.0,
            'korean_name': '합병증',
            'description': '합병증, 예후, 진행'
        }
    }

    # 분류 신뢰도 임계값
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    LOW_CONFIDENCE_THRESHOLD = 0.3

    def __init__(self, anthropic_client=None):
        """
        Args:
            anthropic_client: Anthropic API 클라이언트 (AI 분류용)
        """
        self.anthropic_client = anthropic_client
        self._compile_patterns()

    def _compile_patterns(self):
        """정규표현식 패턴 미리 컴파일"""
        self.patterns = {}
        for category, config in self.CATEGORY_KEYWORDS.items():
            # 키워드를 정규표현식 패턴으로 변환 (단어 경계 포함)
            pattern_str = '|'.join(
                r'\b' + re.escape(kw) + r'\b'
                for kw in config['keywords']
            )
            self.patterns[category] = re.compile(pattern_str, re.IGNORECASE)

    def classify_papers(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        """
        논문 리스트를 카테고리별로 분류

        Args:
            papers: 논문 정보 리스트

        Returns:
            카테고리별 논문 딕셔너리
        """
        print("\n📊 논문 분류 중...")

        categorized = defaultdict(list)
        low_confidence_papers = []

        for paper in papers:
            category, confidence = self._rule_based_classify(paper)

            if confidence >= self.LOW_CONFIDENCE_THRESHOLD:
                paper['category'] = category
                paper['category_confidence'] = confidence
                categorized[category].append(paper)
            else:
                low_confidence_papers.append(paper)

        # 낮은 신뢰도 논문 처리
        if low_confidence_papers:
            print(f"  ⚠️ 분류가 애매한 논문 {len(low_confidence_papers)}개")

            if self.anthropic_client and len(low_confidence_papers) <= 20:
                # AI 분류 시도
                ai_results = self._ai_classify(low_confidence_papers)
                for paper, category in zip(low_confidence_papers, ai_results):
                    paper['category'] = category
                    paper['category_confidence'] = 0.5  # AI 분류는 중간 신뢰도
                    categorized[category].append(paper)
            else:
                # 기본 카테고리(general)로 분류
                for paper in low_confidence_papers:
                    paper['category'] = 'general'
                    paper['category_confidence'] = 0.2
                    categorized['general'].append(paper)

        # 결과 요약 출력
        print("\n✓ 분류 완료:")
        for category, category_papers in sorted(categorized.items()):
            config = self.CATEGORY_KEYWORDS.get(category, {'korean_name': '기타'})
            print(f"  - {config.get('korean_name', category)}: {len(category_papers)}개")

        return dict(categorized)

    def _rule_based_classify(self, paper: Dict) -> Tuple[str, float]:
        """
        규칙 기반 논문 분류

        Args:
            paper: 논문 정보

        Returns:
            (카테고리, 신뢰도 점수)
        """
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        text = f"{title} {title} {abstract}"  # 제목에 2배 가중치

        scores = {}

        for category, config in self.CATEGORY_KEYWORDS.items():
            pattern = self.patterns[category]
            matches = pattern.findall(text)

            # 기본 점수: 매칭된 키워드 개수 * 가중치
            base_score = len(matches) * config['weight']

            # 제목에서 매칭되면 추가 점수
            title_matches = pattern.findall(title)
            title_bonus = len(title_matches) * 0.5

            scores[category] = base_score + title_bonus

        if not scores or max(scores.values()) == 0:
            return 'general', 0.0

        # 가장 높은 점수의 카테고리 선택
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        # 신뢰도 계산 (정규화)
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0

        return best_category, confidence

    def _ai_classify(self, papers: List[Dict]) -> List[str]:
        """
        Claude AI를 사용한 논문 분류 (배치 처리)

        Args:
            papers: 분류할 논문 리스트

        Returns:
            카테고리 리스트
        """
        if not self.anthropic_client:
            return ['general'] * len(papers)

        try:
            # 논문 정보를 텍스트로 변환
            papers_text = ""
            for i, paper in enumerate(papers, 1):
                papers_text += f"\n[{i}] {paper.get('title', 'No title')}\n"
                papers_text += f"Abstract: {paper.get('abstract', 'No abstract')[:500]}...\n"

            categories_list = list(self.CATEGORY_KEYWORDS.keys())
            categories_desc = "\n".join([
                f"- {cat}: {config['description']}"
                for cat, config in self.CATEGORY_KEYWORDS.items()
            ])

            prompt = f"""다음 논문들을 아래 카테고리 중 하나로 분류해주세요.

카테고리:
{categories_desc}
- general: 위 카테고리에 해당하지 않는 경우

논문들:
{papers_text}

각 논문 번호에 대해 가장 적합한 카테고리를 한 줄에 하나씩 출력해주세요.
형식: [번호] 카테고리
예시:
[1] treatment
[2] diet
[3] cause"""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # 결과 파싱
            results = []
            for line in result_text.strip().split('\n'):
                for cat in categories_list + ['general']:
                    if cat in line.lower():
                        results.append(cat)
                        break
                else:
                    results.append('general')

            # 논문 개수와 결과 개수가 맞지 않으면 기본값 사용
            while len(results) < len(papers):
                results.append('general')

            return results[:len(papers)]

        except Exception as e:
            print(f"  ⚠️ AI 분류 실패: {str(e)}")
            return ['general'] * len(papers)

    def get_category_stats(self, categorized_papers: Dict[str, List[Dict]]) -> Dict:
        """
        카테고리별 통계 정보 반환

        Args:
            categorized_papers: 분류된 논문 딕셔너리

        Returns:
            통계 정보 딕셔너리
        """
        stats = {
            'total': sum(len(papers) for papers in categorized_papers.values()),
            'categories': {}
        }

        for category, papers in categorized_papers.items():
            config = self.CATEGORY_KEYWORDS.get(category, {'korean_name': category})
            avg_confidence = sum(p.get('category_confidence', 0) for p in papers) / len(papers) if papers else 0

            stats['categories'][category] = {
                'count': len(papers),
                'korean_name': config.get('korean_name', category),
                'average_confidence': round(avg_confidence, 2)
            }

        return stats

    @classmethod
    def get_available_categories(cls) -> List[str]:
        """사용 가능한 카테고리 목록 반환"""
        return list(cls.CATEGORY_KEYWORDS.keys())


def main():
    """테스트 실행"""
    # 테스트 논문 데이터
    test_papers = [
        {
            'title': 'Proton pump inhibitors for treatment of GERD',
            'abstract': 'This study evaluated the efficacy of PPI therapy in patients with gastroesophageal reflux disease.'
        },
        {
            'title': 'Dietary factors and gastroesophageal reflux',
            'abstract': 'We investigated the relationship between food intake, caffeine consumption and reflux symptoms.'
        },
        {
            'title': 'Pathophysiology of GERD: mechanisms and risk factors',
            'abstract': 'The etiology of GERD involves multiple pathogenic mechanisms including lower esophageal sphincter dysfunction.'
        },
        {
            'title': 'Lifestyle modifications for reflux management',
            'abstract': 'Weight loss, smoking cessation, and sleep position changes can improve GERD symptoms.'
        },
        {
            'title': 'Barrett esophagus and esophageal adenocarcinoma risk',
            'abstract': 'Long-term complications of GERD include progression to Barrett esophagus and cancer.'
        }
    ]

    classifier = PaperClassifier()
    categorized = classifier.classify_papers(test_papers)

    print("\n" + "="*60)
    print("분류 결과:")
    print("="*60)

    for category, papers in categorized.items():
        config = classifier.CATEGORY_KEYWORDS.get(category, {'korean_name': category})
        print(f"\n📁 {config.get('korean_name', category)} ({category}):")
        for paper in papers:
            print(f"  - {paper['title'][:60]}...")
            print(f"    신뢰도: {paper.get('category_confidence', 0):.2f}")

    stats = classifier.get_category_stats(categorized)
    print(f"\n📊 총 {stats['total']}개 논문 분류 완료")


if __name__ == "__main__":
    main()
