# 사용 가이드

## 🚀 빠른 시작

### 1. 패키지 설치

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 열어서 Anthropic API 키를 입력하세요:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
PUBMED_EMAIL=your_email@example.com
```

- **Anthropic API 키**: https://console.anthropic.com/settings/keys 에서 발급
- **PubMed 이메일**: 본인의 이메일 주소 (PubMed API 정책)

### 3. 서버 실행

```bash
python app.py
```

브라우저에서 http://localhost:5000 접속

---

## 💡 사용 방법

### 웹 인터페이스 사용

1. **주제 입력**: 건강/의학 관련 주제 입력
   - 예: "역류성식도염", "당뇨병 식이요법", "비타민D 결핍"

2. **논문 개수 선택**: 5-30개 (권장: 10-15개)
   - 많을수록 정확하지만 시간이 더 걸립니다
   - 평균 소요 시간: 10개 논문 기준 2-3분

3. **글 스타일 선택**:
   - **하이브리드** (추천): 과학적 근거 + 쉬운 설명
   - **학술적**: 전문가용, 논문 인용 엄격
   - **대중적**: 일반인용, 쉬운 언어

4. **생성 버튼 클릭**

5. **결과 확인**:
   - 미리보기: 브라우저에서 즉시 확인
   - 다운로드: HTML 파일로 저장

---

## 📊 생성되는 블로그 글 구조

생성된 글은 다음 섹션으로 구성됩니다:

1. **매력적인 제목과 인트로**
2. **핵심 요약** (3-5개 포인트)
3. **문제의 근본 원인** (메커니즘 설명)
4. **과학적으로 입증된 해결법**
   - 각 해결법마다 효과, 방법, 주의사항, 논문 근거 포함
5. **실천 가이드** (단계별 실행 방법)
6. **흔한 오해와 진실**
7. **결론 및 행동 촉구**
8. **참고 논문 목록** (표 형식, PubMed 링크)

모든 주장은 논문 번호로 근거를 명시합니다.

---

## 🔍 검색 최적화 팁

### 효과적인 주제 입력 방법

**✅ 좋은 예시:**
- "역류성식도염" (명확한 질환명)
- "당뇨병 식이요법" (질환 + 구체적 측면)
- "비타민D 결핍과 우울증" (명확한 관계)
- "간헐적 단식의 효과" (명확한 개입)

**❌ 피해야 할 예시:**
- "건강" (너무 광범위)
- "아픈 거" (불명확)
- "다이어트 방법 100가지" (과도하게 구체적)

### 논문 개수 선택 가이드

| 논문 개수 | 적합한 상황 | 예상 시간 |
|----------|------------|----------|
| 5-8개 | 빠른 개요 파악 | 1-2분 |
| 10-15개 | **권장: 균형잡힌 분석** | 2-3분 |
| 20-30개 | 매우 상세한 분석 필요 | 4-6분 |

---

## 🛠️ 문제 해결

### API 키 오류

```
✗ 설정 오류: ANTHROPIC_API_KEY가 설정되지 않았습니다
```

**해결:** `.env` 파일에서 API 키 확인

### 논문을 찾을 수 없음

```
✗ 검색 결과가 없습니다
```

**해결:**
- 검색어를 더 일반적으로 변경 (예: "GERD" → "역류성식도염")
- 한글 대신 영문 의학 용어 시도
- 철자 확인

### 생성 시간이 너무 오래 걸림

**해결:**
- 논문 개수를 줄이기 (10-12개 권장)
- 인터넷 연결 확인
- PubMed API 키 설정 (요청 제한 완화)

---

## 📁 출력 파일 관리

생성된 파일은 `output/` 디렉토리에 저장됩니다:

```
output/
├── 역류성식도염_20240205_143022.html
├── 당뇨병_식이요법_20240205_150331.html
└── ...
```

파일명 형식: `{주제}_{날짜}_{시간}.html`

---

## ⚡ 고급 사용법

### Python 스크립트로 직접 사용

```python
from modules import PubMedSearcher, PaperAnalyzer, BlogGenerator
from config import Config

# 논문 검색
searcher = PubMedSearcher(email=Config.PUBMED_EMAIL)
papers = searcher.search_and_fetch("역류성식도염", max_results=12)

# 논문 분석
analyzer = PaperAnalyzer(api_key=Config.ANTHROPIC_API_KEY)
analysis = analyzer.analyze_papers(papers, "역류성식도염")

# 블로그 글 생성
generator = BlogGenerator(api_key=Config.ANTHROPIC_API_KEY)
blog_html = generator.generate_blog_post("역류성식도염", analysis, style="hybrid")

# 파일로 저장
with open("output/my_blog.html", "w", encoding="utf-8") as f:
    f.write(blog_html)
```

### 커스텀 스타일 정의

`modules/blog_generator.py`의 `style_instructions` 딕셔너리를 수정하여 원하는 스타일 추가 가능

---

## 💰 비용 안내

### Anthropic API 비용 (Claude Sonnet 4.5)

- 입력: $3 / 1M 토큰
- 출력: $15 / 1M 토큰

**예상 비용 (논문 12개 기준):**
- 논문 분석: 약 $0.10-0.15
- 블로그 글 생성: 약 $0.05-0.08
- **총 1회 실행당: 약 $0.15-0.23** (약 200-300원)

### PubMed API

- **완전 무료**
- 이메일만 제공하면 사용 가능
- API 키 없이도 작동 (초당 3회 제한)

---

## 📞 문의 및 피드백

이슈가 있거나 기능 제안이 있다면:
- GitHub Issues에 등록
- 이메일로 연락

---

## ⚠️ 면책 조항

이 도구는 논문 정보를 기반으로 블로그 글을 생성하지만:
- **의학적 조언을 대체할 수 없습니다**
- 생성된 내용은 반드시 검토 후 게시하세요
- 건강 문제가 있다면 의료 전문가와 상담하세요
