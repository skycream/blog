# 논문 기반 자동 블로그 글 생성기

의학/건강 주제에 대해 PubMed 논문을 자동으로 검색하고 분석하여 블로그 글을 생성하는 웹 애플리케이션입니다.

## 주요 기능

- **자동 논문 검색**: PubMed API를 통해 관련 논문 10-15개 자동 수집
- **AI 기반 분석**: Claude API로 논문 내용을 종합 분석
- **블로그 글 생성**: 과학적 근거와 가독성을 겸비한 하이브리드 스타일
- **HTML 출력**: 블로그에 바로 게시 가능한 HTML 형식

## 기술 스택

- **Backend**: Python, Flask
- **논문 검색**: PubMed API (Biopython)
- **AI 분석**: Anthropic Claude API
- **Frontend**: HTML, CSS, JavaScript

## 설치 방법

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 입력
```

## 사용 방법

```bash
# 서버 실행
python app.py

# 브라우저에서 접속
http://localhost:5000
```

1. 웹 페이지에서 건강/의학 주제 입력 (예: "역류성식도염", "당뇨병")
2. 검색할 논문 개수 선택 (10-20개)
3. "블로그 글 생성" 버튼 클릭
4. 진행 상황 확인 후 결과 다운로드

## 프로젝트 구조

```
blog/
├── app.py                    # Flask 메인 애플리케이션
├── requirements.txt          # 패키지 의존성
├── config.py                # 설정
├── .env                     # 환경 변수 (API 키)
├── templates/               # HTML 템플릿
│   ├── index.html          # 메인 페이지
│   └── result.html         # 결과 페이지
├── static/                  # 정적 파일
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── modules/                 # 핵심 모듈
│   ├── __init__.py
│   ├── pubmed_search.py    # PubMed 검색
│   ├── paper_analyzer.py   # 논문 분석
│   └── blog_generator.py   # 블로그 글 생성
├── output/                  # 생성된 블로그 글
└── README.md
```

## 라이선스

MIT License
