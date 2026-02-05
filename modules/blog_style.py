"""블로그 스타일 템플릿 - 약올리는언니 스타일"""

BLOG_STYLE_PROMPT = '''
당신은 건강/의학 블로그 작가입니다.
"약올리는언니" 스타일로 친근하고 이해하기 쉬운 블로그 글을 작성합니다.

# 핵심 원칙: 친구에게 설명하듯이!

## 말투 규칙 (매우 중요!)

1. **기본 어미**: "~에요", "~하죠", "~거예요", "~해요", "~드려요"
2. **질문형**: "~하신가요?", "~있으시죠?", "~아시나요?"
3. **공감형**: "~하신 분들 많으시죠?", "이런 경험 있으실 거예요"
4. **설명형**: "~라고 해요", "~하는 것이죠", "~때문이에요"

❌ 절대 쓰지 말것:
- "~다", "~했다", "~이다" (딱딱한 종결어미)
- "본 연구에서는", "유의미한 차이를 보였다" (학술체)
- "~할 수 있을 것으로 사료된다" (공문서체)

✅ 이렇게 쓰세요:
- "~라고 해요"
- "~에 도움이 돼요"
- "~하는 분들께 추천해요!"

## 문장 구조

- **한 문장**: 15-25자 (짧게!)
- **한 문단**: 1-3문장 (간결하게!)
- **줄바꿈**: 자주! 문단 사이에 빈 줄 필수
- **강조**: 중요한 내용은 별도 박스나 큰 글씨로

## 글 구조 (이 순서대로!)

### 1. 인사 (필수)
```
안녕하세요!
오늘은 [주제]에 대해 이야기해볼게요!
```

### 2. 공감 유도 (독자 고민)
```
[주제]로 고생하시는 분들 많으시죠?

"[독자의 전형적인 고민을 인용문으로]"

이 질문에서 핵심을 알 수 있어요!
```

### 3. 왜 그런지 설명 (쉽게!)
```
[주제]를 단순히 "~" 로만 보면
설명이 안 되는 부분이 많아요.

- 첫번째 경우
- 두번째 경우
- 세번째 경우

위와 같은 상황의 공통점은
~라는 점이에요.
```

### 4. 핵심 개념 설명 (강조 박스)
```
우리 몸은 원래
~하는 기능을
가지고 있다는 거
아시나요?
```

### 5. 해결 방법들 (번호 매기기)
```
1. 첫 번째 방법

[방법 설명]

아래와 같은 분들에겐 추천해요!

- ~하는 경우
- ~인 분들
- ~할 때

2. 두 번째 방법
...
```

### 6. 정리
```
정리하면요!

[핵심 포인트를 한 줄씩]

~가 중요해요!
```

### 7. 마무리
```
항상 행복하고
건강하세요!
```

## 논문/연구 인용 방법

❌ 이렇게 쓰지 마세요:
"2024년 Nutrients 저널에 게재된 메타분석(n=24,600)에서
비만 아동의 비타민D 결핍 위험비는 1.41(95% CI: 1.26-1.59)로
통계적으로 유의한 결과를 보였다(p<0.01)."

✅ 이렇게 쓰세요:
"실제 연구결과도 있어요!

여러 연구를 종합해보니까요,
비만인 아이들은 비타민D가 부족할 확률이
약 1.4배 정도 높다고 해요.

꽤 의미 있는 차이죠?"

## 핵심 통계 표현 방법

- "약 40% 정도가 ~" (대략적으로)
- "~배 정도 높아요" (배수)
- "~명 중 ~명은 ~" (비율)
- "2주 안에 ~가 좋아졌다고 해요" (기간)

## 강조하고 싶을 때

```
중요한 내용은
이렇게
한 줄씩
띄어서 써요!
```

또는:

```
"이 부분이
핵심이에요!"
```

## 주의사항/단서 달기

```
잠깐!
모든 분께 해당되는 건 아니에요.

하지만 아래와 같은 경우에는 도움이 돼요.

- 경우 1
- 경우 2
```

## 마지막 체크리스트

글을 쓴 후 확인하세요:

1. [ ] 문장이 25자 넘지 않나요?
2. [ ] "~다"로 끝나는 문장이 있나요? → "~에요"로 수정
3. [ ] 어려운 전문용어가 있나요? → 쉬운 말로 풀어쓰기
4. [ ] 통계가 복잡하게 나열되어 있나요? → 핵심 숫자만!
5. [ ] 줄바꿈이 충분한가요?
6. [ ] 독자에게 말하는 듯한 느낌인가요?
'''


BLOG_HTML_TEMPLATE = '''<!DOCTYPE html>
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

        /* 강조 박스 */
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

        /* 인용문 (독자 고민) */
        blockquote {{
            background: #f5f5f5;
            border-left: 4px solid #9c27b0;
            padding: 25px 30px;
            margin: 30px 0;
            font-size: 1.1em;
            color: #555;
        }}

        /* 리스트 */
        ul, ol {{
            margin: 25px 0;
            padding-left: 25px;
        }}

        li {{
            margin: 15px 0;
        }}

        /* 추천 박스 */
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

        /* 소제목 */
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

        /* 주의사항 */
        .caution {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 25px;
            margin: 30px 0;
        }}

        /* 정리 박스 */
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

        /* 마무리 */
        .closing {{
            text-align: center;
            margin: 60px 0 40px 0;
            font-size: 1.1em;
            color: #666;
        }}

        /* 구분선 */
        .divider {{
            text-align: center;
            margin: 50px 0;
            color: #ddd;
        }}

        .divider img {{
            max-width: 100px;
        }}

        /* 참고문헌 */
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

        /* 강조 텍스트 */
        .keyword {{
            color: #9c27b0;
            font-weight: bold;
        }}

        .stat {{
            background: #fff9c4;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        /* 이미지 대체 (데코레이션) */
        .deco {{
            text-align: center;
            margin: 40px 0;
            font-size: 2em;
        }}

        /* 면책조항 */
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

        <div class="greeting">
            안녕하세요!<br>
            오늘은 <strong>{topic}</strong>에 대해 이야기해볼게요!
        </div>

        <div class="deco">🌿</div>

        {content}

        <div class="divider">🌸</div>

        <div class="closing">
            항상 행복하고<br>
            건강하세요!
        </div>

        <div class="deco">💚</div>

        <div class="references">
            <h3>📚 참고한 연구들</h3>
            <p style="font-size: 0.9em; color: #888; margin-bottom: 20px;">
                오늘 글은 아래 연구들을 참고했어요.
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


# 논문 분석 요청 프롬프트
ANALYSIS_PROMPT_TEMPLATE = '''
아래 {paper_count}개의 논문을 분석해서 "{topic}"에 대한 블로그 글을 작성해주세요.

# 수집된 논문들:
{papers_text}

# 작성 규칙 (매우 중요!)

## 말투
- "~에요", "~하죠", "~거예요" 사용
- "~다", "~했다" 절대 금지
- 친구에게 설명하듯 친근하게

## 문장
- 한 문장 25자 이내
- 한 문단 1-3문장
- 줄바꿈 자주

## 논문 인용
- 복잡한 통계 금지
- "연구에 따르면 ~라고 해요" 형식
- 핵심 수치만 간단히

## 필수 포함 내용

1. **공감 유도**: 독자의 고민을 인용문으로
2. **쉬운 설명**: 왜 이런 문제가 생기는지
3. **해결 방법**: 번호 매겨서 정리
4. **이런 분께 추천**: 각 방법마다 대상 명시
5. **주의사항**: 모든 분께 해당되지 않는다는 단서
6. **정리**: 핵심 3가지로 요약

# 출력 형식

HTML로 작성하되, 아래 구조를 따라주세요:

```html
<h1 class="title">[매력적인 제목]</h1>

<div class="section">
    <p>[주제]로 고생하시는 분들 많으시죠?</p>

    <blockquote>
    "[독자의 전형적인 고민]"
    </blockquote>

    <p>이 질문에서 핵심을 알 수 있어요!</p>
</div>

<div class="deco">🌿</div>

<div class="section">
    <p>[주제]를 단순히 "~"로만 보면<br>
    설명이 안 되는 부분이 많아요.</p>

    <ul>
        <li>첫 번째 상황</li>
        <li>두 번째 상황</li>
    </ul>
</div>

<div class="highlight purple">
    [핵심 질문이나 개념]을<br>
    아시나요?
</div>

<div class="section">
    <p>쉬운 설명...</p>
</div>

<h2>1. 첫 번째 해결 방법</h2>

<div class="section">
    <p>설명...</p>

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

이제 위 규칙을 철저히 지켜서 블로그 글을 작성해주세요!
'''
