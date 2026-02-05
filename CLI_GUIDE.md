# CLI 스크립트 사용 가이드

## 🚀 빠른 시작

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 블로그 글 생성

```bash
python generate_blog.py "역류성식도염" --papers 12 --style hybrid
```

**그게 끝입니다!** 스크립트가:
1. ✅ PubMed에서 논문 12개 자동 검색
2. ✅ 논문 정보를 파일로 저장
3. ✅ Claude Code에게 분석 요청

---

## 📝 명령어 옵션

### 기본 문법

```bash
python generate_blog.py "<주제>" [옵션들]
```

### 필수 인자

- `<주제>`: 검색할 건강/의학 주제
  - 예: "역류성식도염", "당뇨병 식이요법", "비타민D"

### 선택 옵션

| 옵션 | 설명 | 기본값 | 예시 |
|------|------|--------|------|
| `--papers` | 수집할 논문 개수 (5-30) | 12 | `--papers 15` |
| `--style` | 글 스타일 (academic/casual/hybrid) | hybrid | `--style casual` |
| `--output` | 출력 파일명 지정 | 자동 생성 | `--output my_blog.md` |

---

## 💡 사용 예시

### 1. 기본 사용

```bash
python generate_blog.py "역류성식도염"
```

→ 12개 논문, 하이브리드 스타일

### 2. 논문 개수 조정

```bash
python generate_blog.py "당뇨병 식이요법" --papers 20
```

→ 20개 논문 수집 (더 상세한 분석)

### 3. 스타일 변경

```bash
# 학술적 스타일
python generate_blog.py "비타민D 결핍" --style academic

# 대중적 스타일
python generate_blog.py "간헐적 단식" --style casual

# 하이브리드 스타일 (추천)
python generate_blog.py "고혈압" --style hybrid
```

### 4. 복잡한 주제

```bash
python generate_blog.py "코로나19 후유증" --papers 15 --style hybrid
```

---

## 🔄 워크플로우

### Step 1: 스크립트 실행

```bash
python generate_blog.py "역류성식도염" --papers 12
```

**출력:**
```
======================================================================
📚 논문 기반 자동 블로그 글 생성기 (CLI)
======================================================================
주제: 역류성식도염
논문 개수: 12개
글 스타일: hybrid
======================================================================

🔍 1단계: PubMed 논문 검색 중...
----------------------------------------------------------------------
✓ 12개의 논문을 찾았습니다.
✓ 12/12 논문 정보 수집 완료
✓ 총 12개 논문 수집 완료

📄 2단계: 논문 데이터 저장 중...
----------------------------------------------------------------------
✓ JSON 저장: output/역류성식도염_papers_20240205_150330.json
✓ Markdown 저장: output/역류성식도염_papers_20240205_150330.md

🤖 3단계: Claude Code 분석 요청
----------------------------------------------------------------------
✅ 논문 수집이 완료되었습니다!

📁 저장된 파일:
   - output/역류성식도염_papers_20240205_150330.json
   - output/역류성식도염_papers_20240205_150330.md

🤖 다음 단계:
   Claude Code에서 아래 명령을 실행하세요:

   "output/역류성식도염_papers_20240205_150330.md 파일을 읽고
    역류성식도염에 대한 hybrid 스타일의 블로그 글을 HTML 형식으로 작성해주세요."

======================================================================
```

### Step 2: Claude Code에서 분석 요청

**방법 1: Claude Code에서 직접**
```
생성된 Markdown 파일을 읽고 블로그 글을 작성해주세요.
```

**방법 2: 파일 경로 제공**
```
output/역류성식도염_papers_20240205_150330.md를 분석해서
하이브리드 스타일의 블로그 글을 HTML로 작성해주세요.
```

### Step 3: 결과 확인

Claude Code가 자동으로:
1. 📖 Markdown 파일 읽기
2. 🤖 12개 논문 종합 분석
3. ✍️ HTML 블로그 글 생성
4. 💾 `output/` 폴더에 저장

---

## 📊 생성되는 파일

### 1. JSON 파일 (프로그래밍용)

```
output/역류성식도염_papers_20240205_150330.json
```

**내용:**
```json
{
  "topic": "역류성식도염",
  "paper_count": 12,
  "collected_at": "20240205_150330",
  "style": "hybrid",
  "papers": [
    {
      "pmid": "12345678",
      "title": "논문 제목",
      "authors": ["저자1", "저자2"],
      "journal": "저널명",
      "year": "2023",
      "abstract": "초록 내용...",
      "study_type": "Meta-Analysis",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
    }
  ]
}
```

### 2. Markdown 파일 (읽기용)

```
output/역류성식도염_papers_20240205_150330.md
```

**내용:**
- 📋 논문 목록 표
- 📄 각 논문의 상세 정보 (제목, 저자, 초록)
- 🎯 Claude Code를 위한 분석 지침
- 📝 블로그 글 구조 템플릿

---

## 🎨 스타일 가이드

### Academic (학술적)
- **대상:** 의료인, 연구자
- **특징:** 전문 용어, 엄격한 인용, 상세한 통계
- **예시:** "본 메타분석(n=15,540)에서 PPI 고용량군은..."

### Casual (대중적)
- **대상:** 일반 대중
- **특징:** 쉬운 언어, 스토리텔링, 친근한 톤
- **예시:** "속쓰림으로 고생하시나요? 최신 연구에서..."

### Hybrid (하이브리드) ⭐ 추천
- **대상:** 건강에 관심 있는 일반인
- **특징:** 과학적 근거 + 쉬운 설명
- **예시:** "연구에 따르면 저탄수화물 식단이 역류를 30% 감소시켰습니다 (논문 3, 7)."

---

## ⚡ 팁과 트릭

### 논문 개수 선택

| 개수 | 용도 | 예상 시간 |
|------|------|----------|
| 5-8개 | 빠른 개요 | 1-2분 |
| 10-15개 | **균형잡힌 분석 (추천)** | 2-3분 |
| 20-30개 | 매우 상세한 분석 | 4-6분 |

### 효과적인 주제 입력

**✅ 좋은 예시:**
- "역류성식도염"
- "당뇨병 식이요법"
- "비타민D 결핍과 우울증"

**❌ 피할 예시:**
- "건강" (너무 광범위)
- "다이어트" (불명확)

### 검색 최적화

스크립트는 자동으로:
- ✅ 최근 10년 논문만 검색
- ✅ 고품질 연구 우선 (메타분석, RCT)
- ✅ 초록이 있는 논문만 선택
- ✅ 관련도 순으로 정렬

---

## 🛠️ 문제 해결

### "논문을 찾을 수 없습니다"

**원인:** 검색어가 너무 구체적이거나 오타

**해결:**
```bash
# 더 일반적인 용어 사용
python generate_blog.py "GERD" --papers 12  # ❌
python generate_blog.py "역류성식도염" --papers 12  # ✅

# 영문 의학 용어 시도
python generate_blog.py "gastroesophageal reflux" --papers 12
```

### PubMed API 오류

**원인:** 이메일이 설정되지 않음

**해결:**
`.env` 파일 확인:
```env
PUBMED_EMAIL=your_email@example.com
PUBMED_API_KEY=b7cff32b3d55985001c174a8c2fa3a7b1708
```

### 스크립트 실행 오류

```bash
# Python 경로 확인
python --version  # Python 3.8 이상 필요

# 패키지 재설치
pip install -r requirements.txt --upgrade
```

---

## 📁 출력 파일 관리

생성된 파일은 `output/` 폴더에 타임스탬프와 함께 저장됩니다:

```
output/
├── 역류성식도염_papers_20240205_150330.json
├── 역류성식도염_papers_20240205_150330.md
├── 역류성식도염_20240205_150500.html  (Claude가 생성)
└── ...
```

**파일명 규칙:**
- `{주제}_papers_{타임스탬프}.json/md` - 수집한 논문
- `{주제}_{타임스탬프}.html` - 최종 블로그 글

---

## 🔥 고급 사용법

### 배치 처리

여러 주제를 한 번에 처리:

```bash
# batch.sh (Linux/Mac)
#!/bin/bash
python generate_blog.py "역류성식도염" --papers 12
python generate_blog.py "당뇨병" --papers 15
python generate_blog.py "고혈압" --papers 10

# batch.bat (Windows)
@echo off
python generate_blog.py "역류성식도염" --papers 12
python generate_blog.py "당뇨병" --papers 15
python generate_blog.py "고혈압" --papers 10
```

### Python 스크립트에서 사용

```python
import subprocess
import json

# 논문 수집
result = subprocess.run([
    'python', 'generate_blog.py',
    '역류성식도염',
    '--papers', '12'
], capture_output=True)

# 결과 파일 읽기
with open('output/역류성식도염_papers_latest.json') as f:
    papers = json.load(f)

print(f"수집된 논문: {papers['paper_count']}개")
```

---

## 💰 비용

- **PubMed API**: 완전 무료
- **Claude Code**: 이미 사용 중인 Claude Code 구독으로 무료

**추가 비용 없음!** 🎉

---

## 📞 도움이 필요하신가요?

```bash
# 도움말 보기
python generate_blog.py --help

# 버전 확인
python generate_blog.py --version
```

문제가 있으면 언제든 Claude Code에서 질문하세요!
