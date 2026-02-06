"""
블로그 자동 생성 텔레그램 봇

실행 방법:
    1. .env 파일에 TELEGRAM_BOT_TOKEN 추가
    2. python telegram_bot.py

기능:
    - 키워드 입력 → 토픽 분석 → 다중 선택 → 논문 검색/확인 → Hook 스타일 선택 → 블로그 생성
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Set

# 텔레그램 봇 라이브러리
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# 기존 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.smart_topic_extractor import SmartTopicExtractor
from modules.pubmed_search import PubMedSearcher
from modules.paper_analyzer import PaperAnalyzer
from modules.blog_generator import BlogGenerator
from modules.pmc_fulltext import PMCFullTextFetcher
from modules.llm_paper_analyzer import save_for_claude_analysis, create_batch_analysis_prompt
from modules.claude_paper_scorer import score_papers_with_claude
from modules.auto_blog_generator import generate_blog_auto, get_last_error_log
from config import Config

# 대화 상태 정의
(
    WAITING_KEYWORD,
    SELECTING_TOPICS,
    SEARCHING_PAPERS,
    SELECTING_HOOK_STYLE,
    CONFIRMING_DRAFT,
) = range(5)


class LoadingIndicator:
    """로딩 중 상태를 주기적으로 업데이트하는 클래스"""

    def __init__(self, bot, chat_id, base_message: str, interval: int = 10):
        self.bot = bot
        self.chat_id = chat_id
        self.base_message = base_message
        self.interval = interval
        self.message = None
        self.running = False
        self.task = None
        self.counter = 0
        self.dots = ["⏳", "⌛"]

    async def start(self):
        """로딩 시작"""
        self.running = True
        self.counter = 0
        self.message = await self.bot.send_message(
            chat_id=self.chat_id,
            text=f"{self.dots[0]} {self.base_message}",
            parse_mode='Markdown'
        )
        self.task = asyncio.create_task(self._update_loop())

    async def _update_loop(self):
        """10초마다 메시지 업데이트"""
        while self.running:
            await asyncio.sleep(self.interval)
            if not self.running:
                break
            self.counter += 1
            elapsed = self.counter * self.interval
            dot = self.dots[self.counter % 2]
            try:
                await self.message.edit_text(
                    f"{dot} {self.base_message}\n\n"
                    f"⏱️ 진행 중... ({elapsed}초 경과)",
                    parse_mode='Markdown'
                )
            except:
                pass

    async def update(self, new_message: str):
        """메시지 업데이트"""
        self.base_message = new_message
        if self.message:
            try:
                await self.message.edit_text(
                    f"⏳ {new_message}",
                    parse_mode='Markdown'
                )
            except:
                pass

    async def stop(self, final_message: str = None):
        """로딩 종료"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        if final_message and self.message:
            try:
                await self.message.edit_text(final_message, parse_mode='Markdown')
            except:
                pass

    async def delete(self):
        """메시지 삭제"""
        self.running = False
        if self.task:
            self.task.cancel()
        if self.message:
            try:
                await self.message.delete()
            except:
                pass

# Hook 스타일 정의
HOOK_STYLES = {
    'stat_shock': {
        'name': '📊 충격 통계',
        'desc': '"환자의 40%는 약이 듣지 않습니다..."',
        'template': '충격적인 통계로 시작'
    },
    'counterintuitive': {
        'name': '🔄 반직관 질문',
        'desc': '"커피, 정말 끊어야 할까요?"',
        'template': '상식을 뒤집는 질문'
    },
    'reader_situation': {
        'name': '🎯 독자 공감',
        'desc': '"자다가 속이 쓰려서 깼습니다..."',
        'template': '독자 상황 묘사 (2인칭)'
    },
    'news_trend': {
        'name': '📰 뉴스/트렌드',
        'desc': '"최근 발표된 연구에 따르면..."',
        'template': '최신 연구/뉴스 연결'
    },
    'conversation': {
        'name': '💬 대화체',
        'desc': '"검색해보면 다 비슷한 말만 나오죠?"',
        'template': '독자와 대화하듯'
    },
    'case_study': {
        'name': '👤 사례 소개',
        'desc': '"35세 직장인 A씨는..."',
        'template': '타인 사례로 시작'
    },
    'problem_direct': {
        'name': '⚡ 문제 직격',
        'desc': '"약 먹어도 재발. 진짜 원인은..."',
        'template': 'PAS 공식 적용'
    },
    'curiosity': {
        'name': '🔮 호기심 유발',
        'desc': '"가장 중요한 건 약도 식단도 아니었습니다..."',
        'template': '오픈 루프 기법'
    },
}


class BlogBotSession:
    """사용자별 세션 데이터 관리"""
    def __init__(self):
        self.keyword: str = ""
        self.keyword_en: str = ""
        self.topics: Dict[str, int] = {}  # 토픽: 언급횟수
        self.selected_topics: Set[str] = set()  # 선택된 토픽들
        self.hook_style: str = ""
        self.papers: List[Dict] = []
        self.search_queries: List[str] = []  # 실제 사용된 PubMed 검색 쿼리
        self.draft: str = ""
        self.created_at: datetime = datetime.now()
        self.session_id: str = datetime.now().strftime('%Y%m%d_%H%M%S')

    def save_to_file(self, step: str = ""):
        """세션 데이터를 파일로 저장"""
        import json
        save_dir = "session_data"
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{save_dir}/{self.keyword}_{self.session_id}_{step}.json"
        data = {
            'keyword': self.keyword,
            'keyword_en': self.keyword_en,
            'topics': self.topics,
            'selected_topics': list(self.selected_topics),
            'hook_style': self.hook_style,
            'papers': self.papers,
            'search_queries': self.search_queries,
            'created_at': self.created_at.isoformat(),
            'step': step
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[세션 저장] {filename}")

    @classmethod
    def load_from_file(cls, filepath: str) -> 'BlogBotSession':
        """파일에서 세션 불러오기"""
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        session = cls()
        session.keyword = data.get('keyword', '')
        session.keyword_en = data.get('keyword_en', '')
        session.topics = data.get('topics', {})
        session.selected_topics = set(data.get('selected_topics', []))
        session.hook_style = data.get('hook_style', '')
        session.papers = data.get('papers', [])
        session.search_queries = data.get('search_queries', [])
        session.session_id = data.get('created_at', '')[:15].replace('-', '').replace('T', '_').replace(':', '')
        return session

    @staticmethod
    def list_saved_sessions() -> List[Dict]:
        """저장된 세션 목록 반환"""
        import glob
        save_dir = "session_data"
        if not os.path.exists(save_dir):
            return []

        # 가장 최근 단계의 파일만 (키워드+세션ID별로 그룹핑)
        files = glob.glob(f"{save_dir}/*.json")
        sessions = {}

        for f in files:
            try:
                import json
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                key = f"{data.get('keyword')}_{data.get('created_at', '')[:10]}"
                step = data.get('step', '')

                # 더 높은 단계만 저장
                if key not in sessions or step > sessions[key].get('step', ''):
                    sessions[key] = {
                        'filepath': f,
                        'keyword': data.get('keyword'),
                        'step': step,
                        'papers_count': len(data.get('papers', [])),
                        'created_at': data.get('created_at', '')
                    }
            except:
                pass

        return sorted(sessions.values(), key=lambda x: x.get('created_at', ''), reverse=True)[:10]


# 사용자별 세션 저장소
user_sessions: Dict[int, BlogBotSession] = {}


def get_session(user_id: int) -> BlogBotSession:
    """사용자 세션 가져오기 (없으면 생성)"""
    if user_id not in user_sessions:
        user_sessions[user_id] = BlogBotSession()
    return user_sessions[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """봇 시작"""
    user_id = update.effective_user.id
    user_sessions[user_id] = BlogBotSession()  # 새 세션 시작

    await update.message.reply_text(
        "👋 *블로그 자동 생성 봇*에 오신 것을 환영합니다!\n\n"
        "블로그를 작성할 *키워드*를 입력해주세요.\n"
        "예: `역류성식도염`, `비타민D 결핍`, `간헐적 단식`",
        parse_mode='Markdown'
    )
    return WAITING_KEYWORD


async def receive_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """키워드 수신 및 토픽 분석"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    session = get_session(user_id)
    session.keyword = update.message.text.strip()

    # 로딩 표시 시작
    loading = LoadingIndicator(
        context.bot,
        chat_id,
        f"*'{session.keyword}'* 분석 중...\n인기 블로그 수집 및 Claude 분석 진행"
    )
    await loading.start()

    try:
        # 토픽 추출 (별도 스레드에서 실행)
        from concurrent.futures import ThreadPoolExecutor

        loop = asyncio.get_event_loop()
        extractor = SmartTopicExtractor()

        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                extractor.extract_topics,
                session.keyword,
                15  # max_blogs
            )

        # 로딩 종료
        await loading.delete()

        session.keyword_en = result.get('main_keyword_en', session.keyword)

        # Claude 분석 결과 가져오기
        by_category = result.get('by_category', {})
        trending = result.get('trending', [])

        # 카테고리 정의
        category_names = {
            'diet': '🍽️ 음식/식이',
            'treatment': '💊 치료/약물',
            'lifestyle': '🏃 생활습관',
            'symptom': '🩺 증상',
            'general': '📌 기타'
        }

        # 모든 토픽 수집 (카테고리별 + 트렌딩)
        all_topics = {}  # {topic_name: category}

        # 카테고리별 토픽 수집
        for cat in category_names.keys():
            cat_topics = by_category.get(cat, [])
            for t in cat_topics:
                topic_name = t['topic']
                if topic_name not in all_topics:
                    all_topics[topic_name] = cat

        # 트렌딩 토픽 추가
        for t in trending:
            topic_name = t['topic']
            if topic_name not in all_topics:
                all_topics[topic_name] = 'trending'

        # session.topics에 저장
        session.topics = all_topics

        # 세션 저장 (키워드 분석 완료)
        session.save_to_file("1_keyword_analyzed")

        # 카테고리별 분석 결과 메시지 생성
        analysis_msg = ""
        for cat, cat_name in category_names.items():
            cat_topics = by_category.get(cat, [])
            if cat_topics:
                topic_names = [t['topic'] for t in cat_topics]
                analysis_msg += f"{cat_name}: {', '.join(topic_names)}\n"

        # 트렌딩 키워드 추가
        if trending:
            trending_names = [t['topic'] for t in trending]
            analysis_msg += f"🆕 신규발견: {', '.join(trending_names)}\n"

        # 토픽 버튼 생성 (카테고리별로 정렬, 모든 토픽 포함)
        keyboard = []
        cat_emoji_map = {'diet': '🍽️', 'treatment': '💊', 'lifestyle': '🏃', 'symptom': '🩺', 'general': '📌', 'trending': '🆕'}

        for topic_name, cat in all_topics.items():
            cat_emoji = cat_emoji_map.get(cat, '📌')
            keyboard.append([
                InlineKeyboardButton(
                    f"⬜ {cat_emoji} {topic_name}",
                    callback_data=f"topic:{topic_name[:30]}"
                )
            ])

        # 완료/전체선택/건너뛰기 버튼
        keyboard.append([
            InlineKeyboardButton("✅ 전체 선택", callback_data="topic:SELECT_ALL"),
            InlineKeyboardButton("🚀 선택 완료", callback_data="topic:DONE"),
        ])
        keyboard.append([
            InlineKeyboardButton("⏭️ 토픽 없이 키워드만 검색", callback_data="topic:SKIP"),
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📊 *'{session.keyword}'* Claude 분석 완료!\n\n"
                f"📝 분석된 블로그: {result['blogs_analyzed']}개\n\n"
                f"*[분석 결과]*\n{analysis_msg}\n"
                f"👇 *글에 포함할 토픽을 선택하세요*"
            ),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        return SELECTING_TOPICS

    except Exception as e:
        # 로딩 종료
        await loading.delete()
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"❌ 분석 중 오류가 발생했습니다.\n\n"
                f"오류: {str(e)}\n\n"
                "/start 로 다시 시작해주세요."
            )
        )
        return ConversationHandler.END


async def toggle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """토픽 선택/해제 토글"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = get_session(user_id)

    data = query.data.replace("topic:", "")

    if data == "DONE":
        # 선택 완료 - 다음 단계로 (논문 검색)
        return await search_papers_and_show(update, context)

    elif data == "SKIP":
        # 토픽 선택 없이 진행 (키워드만으로 검색)
        session.selected_topics = set()
        return await search_papers_and_show(update, context)

    elif data == "SELECT_ALL":
        # 전체 선택 (모든 토픽)
        session.selected_topics = set(session.topics.keys())

    else:
        # 개별 토픽 토글
        if data in session.selected_topics:
            session.selected_topics.remove(data)
        else:
            session.selected_topics.add(data)

    # 키보드 업데이트 (모든 토픽 표시)
    keyboard = []
    cat_emoji_map = {'diet': '🍽️', 'treatment': '💊', 'lifestyle': '🏃', 'symptom': '🩺', 'general': '📌', 'trending': '🆕'}

    for topic, category in session.topics.items():
        cat_emoji = cat_emoji_map.get(category, '📌')
        if topic in session.selected_topics:
            btn_text = f"✅ {cat_emoji} {topic}"
        else:
            btn_text = f"⬜ {cat_emoji} {topic}"
        keyboard.append([
            InlineKeyboardButton(btn_text, callback_data=f"topic:{topic[:30]}")
        ])

    keyboard.append([
        InlineKeyboardButton("✅ 전체 선택", callback_data="topic:SELECT_ALL"),
        InlineKeyboardButton("🚀 선택 완료", callback_data="topic:DONE"),
    ])
    keyboard.append([
        InlineKeyboardButton("⏭️ 토픽 없이 키워드만 검색", callback_data="topic:SKIP"),
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    selected_count = len(session.selected_topics)
    selected_list = ', '.join(list(session.selected_topics)[:5])
    if len(session.selected_topics) > 5:
        selected_list += f" 외 {len(session.selected_topics) - 5}개"

    await query.edit_message_text(
        f"📊 *'{session.keyword}'* Claude 분석 완료!\n\n"
        f"✅ *선택된 토픽: {selected_count}개*\n"
        f"{selected_list if selected_list else '없음'}\n\n"
        "👇 토픽을 선택하세요",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return SELECTING_TOPICS


def escape_markdown(text: str) -> str:
    """Markdown 특수문자 이스케이프"""
    special_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text


def extract_insight(paper: dict) -> str:
    """논문에서 결론 추출 후 한글 번역 (전문 > 초록 순서로 시도)"""

    # 1순위: PMC 전문의 결론
    conclusion = paper.get("conclusion", "")
    # 2순위: 초록
    abstract = paper.get("abstract", "")

    # 사용할 텍스트 결정
    if conclusion and len(conclusion) > 50:
        source_text = conclusion
        source_type = "전문"
    elif abstract:
        source_text = abstract
        source_type = "초록"
    else:
        return "내용 없음"

    try:
        from deep_translator import GoogleTranslator

        # 마지막 2-3문장 추출 (결론 부분)
        sentences = [s.strip() for s in source_text.replace('\n', ' ').split('. ') if s.strip()]

        if len(sentences) >= 3:
            insight_en = '. '.join(sentences[-3:])
        elif len(sentences) >= 2:
            insight_en = '. '.join(sentences[-2:])
        else:
            insight_en = sentences[-1] if sentences else source_text[:300]

        if not insight_en.endswith('.'):
            insight_en += '.'

        # 너무 길면 자르기 (번역 API 제한)
        if len(insight_en) > 1000:
            insight_en = insight_en[:1000]

        # 한글로 번역
        translator = GoogleTranslator(source='en', target='ko')
        insight_kr = translator.translate(insight_en)

        # 출처 표시
        if paper.get("has_fulltext"):
            prefix = "[전문]"
        else:
            prefix = "[초록]"

        return f"{prefix} {insight_kr}" if insight_kr else f"{prefix} {insight_en}"

    except Exception as e:
        sentences = [s.strip() for s in source_text.replace('\n', ' ').split('. ') if s.strip()]
        if len(sentences) >= 2:
            return "[번역실패] " + '. '.join(sentences[-2:]) + '.'
        return "[번역실패] " + (sentences[-1] + '.' if sentences else "추출 실패")


async def search_papers_and_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """논문 검색 후 결과 표시 (Hook 스타일 선택 전)"""
    query = update.callback_query
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    session = get_session(user_id)

    selected_topics_str = ', '.join(list(session.selected_topics)[:5])
    if len(session.selected_topics) > 5:
        selected_topics_str += f" 외 {len(session.selected_topics)-5}개"

    # 로딩 표시 시작
    loading = LoadingIndicator(
        context.bot,
        chat_id,
        f"*논문 검색 중...*\n토픽: {selected_topics_str}"
    )
    await loading.start()

    try:
        # PubMed 검색
        await loading.update("*PubMed 논문 검색 중...*")

        searcher = PubMedSearcher(
            email=Config.PUBMED_EMAIL,
            api_key=Config.PUBMED_API_KEY
        )

        all_papers = []
        search_queries_used = []  # 실제 사용된 검색 쿼리 기록

        if session.selected_topics:
            # 토픽이 선택된 경우: 키워드 + 토픽 조합 검색
            for topic in list(session.selected_topics)[:5]:  # 최대 5개 토픽
                # 토픽을 영어로 변환
                topic_en = SmartTopicExtractor.KR_TO_EN.get(topic, topic)

                # 토픽이 한글이면 번역 시도
                if any('\uAC00' <= c <= '\uD7A3' for c in topic_en):  # 한글 포함 체크
                    try:
                        from deep_translator import GoogleTranslator
                        translator = GoogleTranslator(source='ko', target='en')
                        topic_en = translator.translate(topic)
                    except:
                        pass

                query_str = f"{session.keyword_en} AND {topic_en}"
                search_queries_used.append(query_str)
                print(f"[PubMed 검색] {query_str}")

                # 토픽당 30편씩 검색
                papers = searcher.search_and_fetch(query_str, max_results=30)
                all_papers.extend(papers)
        else:
            # 토픽 선택 없이 키워드만으로 검색
            query_str = session.keyword_en
            search_queries_used.append(query_str)
            print(f"[PubMed 검색] {query_str} (키워드만)")

            # 키워드만으로 100편 검색
            papers = searcher.search_and_fetch(query_str, max_results=100)
            all_papers.extend(papers)

        # 검색 쿼리 세션에 저장
        session.search_queries = search_queries_used

        # 중복 제거
        seen_pmids = set()
        unique_papers = []
        for paper in all_papers:
            pmid = paper.get('pmid')
            if pmid and pmid not in seen_pmids:
                seen_pmids.add(pmid)
                unique_papers.append(paper)

        # 논문이 5개 이하면 토픽 제외하고 키워드만으로 재검색
        if len(unique_papers) <= 5 and session.selected_topics:
            await loading.update(
                f"⚠️ *토픽 조합 결과 {len(unique_papers)}편뿐*\n키워드만으로 재검색 중..."
            )

            # 키워드만으로 재검색
            query_str = session.keyword_en
            search_queries_used = [f"{query_str} (키워드만 재검색)"]
            print(f"[PubMed 재검색] {query_str} (토픽 결과 부족으로 키워드만)")

            all_papers = searcher.search_and_fetch(query_str, max_results=100)

            # 중복 제거
            seen_pmids = set()
            unique_papers = []
            for paper in all_papers:
                pmid = paper.get('pmid')
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    unique_papers.append(paper)

            session.search_queries = search_queries_used

        session.papers = unique_papers

        # PMC에서 전문 가져오기 (상위 50편, 총 5분 제한)
        import time
        PMC_MAX_PAPERS = 50  # 상위 50편 PMC 검색
        PMC_TIMEOUT_TOTAL = 300  # 전체 5분 제한

        papers_to_check = unique_papers[:PMC_MAX_PAPERS]
        await loading.update(f"*논문 {len(unique_papers)}편 수집 완료!*\nPMC 전문 검색 중... (상위 {len(papers_to_check)}편)")

        pmc_fetcher = PMCFullTextFetcher(
            email=Config.PUBMED_EMAIL,
            api_key=Config.PUBMED_API_KEY
        )

        fulltext_count = 0
        pmc_start = time.time()

        for i, paper in enumerate(papers_to_check):
            # 전체 타임아웃 체크
            elapsed = int(time.time() - pmc_start)
            if elapsed > PMC_TIMEOUT_TOTAL:
                await loading.update(f"⏱️ PMC 검색 타임아웃 ({elapsed}초)\n전문 {fulltext_count}편 확보")
                break

            try:
                pmid = paper.get('pmid')
                if pmid:
                    fulltext_data = pmc_fetcher.get_paper_with_fulltext(pmid)
                    if fulltext_data:
                        paper["has_fulltext"] = True
                        paper["pmcid"] = fulltext_data.get("pmcid")
                        paper["conclusion"] = fulltext_data.get("conclusion", "")
                        paper["results"] = fulltext_data.get("results", "")
                        fulltext_count += 1
                    else:
                        paper["has_fulltext"] = False
            except Exception as e:
                paper["has_fulltext"] = False
                print(f"[PMC 오류] PMID {paper.get('pmid')}: {e}")

            # 5개마다 진행 상황 업데이트
            if (i + 1) % 5 == 0:
                elapsed = int(time.time() - pmc_start)
                await loading.update(
                    f"*PMC 전문 검색 중...*\n({i+1}/{len(papers_to_check)}) 전문: {fulltext_count}편 ({elapsed}초)"
                )

        # 나머지 논문은 전문 없음으로 표시
        for paper in unique_papers[PMC_MAX_PAPERS:]:
            paper["has_fulltext"] = False

        session.papers = unique_papers

        # Claude CLI로 관련성 점수 평가 (타임아웃 적용)
        await loading.update("*Claude가 관련성 점수 평가 중...*\n75점 이상만 채택됩니다 (최대 3분)")

        try:
            import concurrent.futures
            claude_start = time.time()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    score_papers_with_claude,
                    unique_papers,
                    session.keyword,
                    session.keyword_en,
                    list(session.selected_topics)
                )
                try:
                    accepted_papers, rejected_papers = future.result(timeout=180)  # 3분 타임아웃
                except concurrent.futures.TimeoutError:
                    await loading.update("⚠️ Claude 점수 평가 타임아웃 - 전체 논문 사용")
                    accepted_papers = unique_papers
                    rejected_papers = []

            claude_elapsed = int(time.time() - claude_start)
            print(f"[Claude 점수평가] {claude_elapsed}초, 채택: {len(accepted_papers)}편")

        except Exception as e:
            print(f"[Claude 점수평가 오류] {e}")
            await loading.update(f"⚠️ Claude 점수 평가 실패: {str(e)[:100]}")
            accepted_papers = unique_papers
            rejected_papers = []

        session.papers = accepted_papers if accepted_papers else unique_papers  # 채택된 논문만 저장

        # 전문 통계 계산
        fulltext_papers = [p for p in session.papers if p.get('has_fulltext')]

        # 검색 쿼리 표시 (최대 3개)
        queries_display = "\n".join([f"  • {q}" for q in session.search_queries[:3]])
        if len(session.search_queries) > 3:
            queries_display += f"\n  ...외 {len(session.search_queries)-3}개"

        # 세션 저장 (논문 검색 완료)
        session.save_to_file("2_papers_searched")

        # 로딩 종료
        await loading.delete()

        # 첫 번째 메시지: 요약 정보
        header_msg = (
            f"📚 *논문 검색 완료!*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 키워드: {session.keyword} ({session.keyword_en})\n"
            f"🏷️ 선택 토픽: {', '.join(list(session.selected_topics))}\n"
            f"📄 수집 논문: {len(unique_papers)}편\n"
            f"✅ *채택 논문: {len(accepted_papers)}편* (75점 이상)\n"
            f"❌ 미채택: {len(rejected_papers)}편\n"
            f"📗 전문 확보: {len(fulltext_papers)}편\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔍 *실제 검색 쿼리:*\n{queries_display}\n\n"
            f"📗 = 전문 | 📄 = 초록 | 🎯 = 관련성 점수\n\n"
            f"📑 *채택된 논문 목록:*\n"
        )

        await context.bot.send_message(chat_id=chat_id, text=header_msg, parse_mode='Markdown')

        # 진행 상황 메시지
        progress_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"📖 논문 분석 중... (0/{len(unique_papers)})"
        )

        paper_messages = []
        current_msg = ""

        for i, paper in enumerate(unique_papers, 1):
            # 진행 상황 업데이트 (10개마다)
            if i % 10 == 0:
                try:
                    await progress_msg.edit_text(f"📖 논문 분석 중... ({i}/{len(unique_papers)})")
                except:
                    pass

            title = paper.get('title', '제목 없음')
            journal = paper.get('journal', '저널 미상')
            year = paper.get('year', '연도 미상')
            has_fulltext = paper.get('has_fulltext', False)
            relevance_score = paper.get('관련성점수')
            score_reason = paper.get('점수근거', '')

            try:
                insight = extract_insight(paper)
            except Exception as e:
                insight = "번역 실패"

            # 전문 여부 표시
            fulltext_marker = "📗" if has_fulltext else "📄"

            # 관련성 점수 표시 (0점도 표시)
            score_display = f"🎯{relevance_score}점" if relevance_score is not None else ""

            # 전문 여부에 따라 다른 아이콘 표시
            paper_text = (
                f"{fulltext_marker} {i}. [{score_display}] {title}\n"
                f"   📰 {journal}, {year}\n"
                f"   💡 {insight}\n\n"
            )

            # 메시지 길이 체크 (3500자 넘으면 분리)
            if len(current_msg) + len(paper_text) > 3500:
                paper_messages.append(current_msg)
                current_msg = paper_text
            else:
                current_msg += paper_text

        if current_msg:
            paper_messages.append(current_msg)

        # 진행 메시지 삭제
        try:
            await progress_msg.delete()
        except:
            pass

        # 논문 목록 메시지들 전송 (Markdown 없이 일반 텍스트)
        for msg in paper_messages:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=msg
                )
            except Exception as e:
                # 실패시 짧게 잘라서 재시도
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=msg[:4000] + "..."
                )

        # 마지막: 확인 버튼
        keyboard = [
            [InlineKeyboardButton("✅ 논문 확인 완료, 도입부 스타일 선택", callback_data="papers:CONFIRM")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"총 *{len(session.papers)}편*의 논문을 수집했습니다.\n\n"
                f"위 논문들을 기반으로 블로그를 작성합니다.\n"
                f"확인 후 도입부 스타일을 선택해주세요."
            ),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        return SEARCHING_PAPERS

    except Exception as e:
        # 로딩 종료
        await loading.delete()
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"❌ 논문 검색 중 오류가 발생했습니다.\n\n"
                f"오류: {str(e)}\n\n"
                "/start 로 다시 시작해주세요."
            )
        )
        return ConversationHandler.END


async def handle_paper_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """논문 결과 확인 후 Hook 스타일 선택으로 이동"""
    query = update.callback_query
    await query.answer()

    action = query.data.replace("papers:", "")

    if action == "CONFIRM":
        return await show_hook_styles(update, context)

    return SEARCHING_PAPERS


async def show_hook_styles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Hook 스타일 선택 화면"""
    query = update.callback_query
    user_id = update.effective_user.id
    session = get_session(user_id)

    # Hook 스타일 키보드
    keyboard = []
    for style_id, style_info in HOOK_STYLES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{style_info['name']}",
                callback_data=f"hook:{style_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🎲 랜덤 선택", callback_data="hook:RANDOM")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    selected_topics_str = ', '.join(list(session.selected_topics)[:5])
    if len(session.selected_topics) > 5:
        selected_topics_str += f" 외 {len(session.selected_topics)-5}개"

    await query.edit_message_text(
        f"✅ *토픽 선택 완료!*\n\n"
        f"📌 선택된 토픽: {selected_topics_str}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✍️ *도입부 스타일을 선택하세요:*\n\n"
        "📊 *충격 통계* - 숫자로 임팩트\n"
        "🔄 *반직관 질문* - 상식 뒤집기\n"
        "🎯 *독자 공감* - 상황 묘사\n"
        "📰 *뉴스/트렌드* - 최신 연구\n"
        "💬 *대화체* - 친근한 톤\n"
        "👤 *사례 소개* - 스토리텔링\n"
        "⚡ *문제 직격* - PAS 공식\n"
        "🔮 *호기심 유발* - 오픈 루프",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return SELECTING_HOOK_STYLE


async def select_hook_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Hook 스타일 선택 (논문은 이미 검색됨)"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = get_session(user_id)

    style_id = query.data.replace("hook:", "")

    if style_id == "RANDOM":
        import random
        style_id = random.choice(list(HOOK_STYLES.keys()))

    session.hook_style = style_id
    style_info = HOOK_STYLES[style_id]

    # 세션 저장 (스타일 선택 완료)
    session.save_to_file("3_style_selected")

    # 초안 생성 확인 (논문은 이미 검색되어 있음)
    keyboard = [
        [
            InlineKeyboardButton("✅ 블로그 생성", callback_data="confirm:YES"),
            InlineKeyboardButton("🔄 스타일 변경", callback_data="confirm:CHANGE_STYLE"),
        ],
        [
            InlineKeyboardButton("❌ 취소", callback_data="confirm:CANCEL"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"✅ *모든 설정 완료!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 키워드: {session.keyword}\n"
        f"🏷️ 선택 토픽: {len(session.selected_topics)}개\n"
        f"📄 수집 논문: {len(session.papers)}편\n"
        f"✍️ 도입 스타일: {style_info['name']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"이대로 블로그를 생성할까요?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return CONFIRMING_DRAFT


async def confirm_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """블로그 생성 확인"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    session = get_session(user_id)

    action = query.data.replace("confirm:", "")

    if action == "CANCEL":
        await query.edit_message_text(
            "❌ 취소되었습니다.\n\n"
            "/start 로 다시 시작할 수 있습니다."
        )
        return ConversationHandler.END

    elif action == "CHANGE_STYLE":
        return await show_hook_styles(update, context)

    elif action == "YES":
        chat_id = update.effective_chat.id

        # Hook 스타일 정보 가져오기
        style_info = HOOK_STYLES[session.hook_style]
        fulltext_count = sum(1 for p in session.papers if p.get('has_fulltext'))

        await query.edit_message_text(
            f"🤖 *블로그 자동 생성 시작!*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 키워드: {session.keyword}\n"
            f"🏷️ 토픽: {', '.join(list(session.selected_topics)[:3])}\n"
            f"📄 논문: {len(session.papers)}편\n"
            f"✍️ 스타일: {style_info['name']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━",
            parse_mode='Markdown'
        )

        # 세션 저장 (블로그 생성 시작 전)
        session.save_to_file("4_generation_started")

        # 로딩 표시 시작
        loading = LoadingIndicator(
            context.bot,
            chat_id,
            "*논문 분석 및 블로그 생성 중...*\nClaude가 논문을 분석하고 HTML을 생성합니다."
        )
        await loading.start()

        try:
            # 세션 데이터 구성
            session_data = {
                'keyword': session.keyword,
                'keyword_en': session.keyword_en,
                'topics': list(session.selected_topics),
                'hook_style': session.hook_style,
                'hook_style_name': style_info['name'],
                'hook_style_desc': style_info['desc'],
                'hook_style_template': style_info['template'],
                'papers': session.papers,
            }

            # 디버그 로깅
            print(f"[TG DEBUG] keyword={session.keyword}")
            print(f"[TG DEBUG] topics={list(session.selected_topics)}")
            print(f"[TG DEBUG] papers={len(session.papers)}편")
            print(f"[TG DEBUG] hook_style={session.hook_style}")
            if session.papers:
                print(f"[TG DEBUG] 첫 논문: {session.papers[0].get('title', 'N/A')[:50]}")

            # 자동 블로그 생성 (별도 스레드에서 실행)
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            # 진행 상황 업데이트 함수
            async def update_progress(step: int, message: str):
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"⏳ *{step}단계:* {message}",
                        parse_mode='Markdown'
                    )
                except:
                    pass

            # 블로그 생성 실행
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                html_path = await loop.run_in_executor(
                    executor,
                    generate_blog_auto,
                    session_data,
                    "output"
                )

            # 로딩 종료
            await loading.delete()

            if html_path and os.path.exists(html_path):
                # 성공 - HTML 파일 전송
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"✅ *블로그 생성 완료!*\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📌 키워드: {session.keyword}\n"
                        f"🏷️ 토픽: {', '.join(list(session.selected_topics)[:3])}\n"
                        f"📄 참고 논문: {len(session.papers)}편\n"
                        f"✍️ 스타일: {style_info['name']}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📁 HTML 파일을 전송합니다..."
                    ),
                    parse_mode='Markdown'
                )

                # HTML 파일 전송
                with open(html_path, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f,
                        filename=os.path.basename(html_path),
                        caption=f"📝 {session.keyword} 블로그 HTML\n네이버 블로그에 HTML 모드로 붙여넣기 하세요!"
                    )

                # HTML 미리보기 (일부)
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_preview = f.read()[:500] + "..."

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📄 *HTML 미리보기:*\n```html\n{html_preview}\n```\n\n/start 로 새 블로그 작성",
                    parse_mode='Markdown'
                )

            else:
                # 실패 - 에러 로그 표시
                error_logs = get_last_error_log()
                error_text = "\n".join(error_logs[-10:]) if error_logs else "알 수 없는 오류"

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"❌ *블로그 생성 실패*\n\n"
                        f"논문: {len(session.papers)}편\n"
                        f"토픽: {', '.join(list(session.selected_topics)[:3]) if session.selected_topics else '없음'}\n\n"
                        f"📋 *에러 로그:*\n```\n{error_text[:1500]}\n```\n\n"
                        f"/start 로 새 블로그 작성"
                    ),
                    parse_mode='Markdown'
                )

            return ConversationHandler.END

        except Exception as e:
            # 로딩 종료
            await loading.delete()

            # 에러 로그 포함
            error_logs = get_last_error_log()
            error_text = "\n".join(error_logs[-5:]) if error_logs else ""

            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"❌ 블로그 생성 중 오류가 발생했습니다.\n\n"
                    f"오류: {str(e)}\n\n"
                    f"📋 로그:\n```\n{error_text[:1000]}\n```\n\n"
                    "/start 로 다시 시작해주세요."
                ),
                parse_mode='Markdown'
            )
            return ConversationHandler.END


def generate_blog_html(session: BlogBotSession) -> str:
    """세션 데이터로 블로그 HTML 생성 (AI 기반)"""
    style_info = HOOK_STYLES[session.hook_style]

    # API 키 확인
    api_key = Config.ANTHROPIC_API_KEY
    if not api_key or api_key == "your_api_key_here":
        # API 키가 없으면 기본 템플릿 사용
        return generate_blog_html_fallback(session)

    try:
        # 1. 논문 분석 (Claude AI)
        analyzer = PaperAnalyzer(api_key=api_key)
        analysis = analyzer.analyze_papers(session.papers, session.keyword)

        # 2. Hook 스타일 정보를 분석에 추가
        analysis['hook_style'] = session.hook_style
        analysis['hook_info'] = style_info
        analysis['selected_topics'] = list(session.selected_topics)

        # 3. 블로그 생성 (Claude AI)
        generator = BlogGenerator(api_key=api_key)

        # 스타일 매핑: hook_style을 blog_style로 변환
        style_map = {
            'stat_shock': 'hybrid',       # 통계 강조
            'counterintuitive': 'casual', # 질문형
            'reader_situation': 'casual', # 공감형
            'news_trend': 'hybrid',       # 뉴스형
            'conversation': 'casual',     # 대화체
            'case_study': 'casual',       # 사례형
            'problem_direct': 'hybrid',   # 문제 직격
            'curiosity': 'casual',        # 호기심형
        }
        blog_style = style_map.get(session.hook_style, 'hybrid')

        # Hook 스타일별 추가 지침을 분석에 포함
        hook_instructions = get_hook_instructions(session.hook_style, session.keyword)
        if 'raw_analysis' in analysis:
            analysis['raw_analysis'] = hook_instructions + "\n\n" + analysis['raw_analysis']
        else:
            analysis['hook_instructions'] = hook_instructions

        html_content = generator.generate_blog_post(
            topic=session.keyword,
            analysis=analysis,
            style=blog_style
        )

        return html_content

    except Exception as e:
        print(f"AI 생성 실패, 기본 템플릿 사용: {e}")
        return generate_blog_html_fallback(session)


def get_hook_instructions(hook_style: str, keyword: str) -> str:
    """Hook 스타일별 글쓰기 지침"""
    instructions = {
        'stat_shock': f"""
## 도입부 스타일: 충격 통계
- 가장 놀라운 통계 수치로 시작하세요
- "XX% 의 사람들이...", "10명 중 X명은..." 형식 사용
- 독자가 "정말?" 하고 놀랄 만한 숫자 선택
- 예: "{keyword} 환자의 40%는 약이 듣지 않습니다..."
""",
        'counterintuitive': f"""
## 도입부 스타일: 반직관 질문
- 상식을 뒤집는 질문으로 시작하세요
- 독자가 "당연히 그렇지 않나?"라고 생각하는 것에 도전
- 예: "커피, 정말 끊어야 할까요?", "{keyword}에 대한 이 상식, 틀렸습니다"
""",
        'reader_situation': f"""
## 도입부 스타일: 독자 공감
- 2인칭으로 독자의 상황을 묘사하세요
- "혹시 ~하신 적 있으신가요?", "~때문에 고민이시죠?"
- 독자가 "어, 이거 내 얘기다!" 느끼게
- 예: "자다가 속이 쓰려서 깬 적 있으시죠?", "{keyword} 때문에 밤잠 설치신 분들..."
""",
        'news_trend': f"""
## 도입부 스타일: 뉴스/트렌드
- 최신 연구 발표 소식으로 시작하세요
- "최근 연구에서 밝혀진...", "2024년 발표된 논문에 따르면..."
- 권위 있는 저널 이름 언급
- 예: "최근 JAMA에 발표된 연구가 {keyword}에 대한 새로운 사실을 밝혔습니다"
""",
        'conversation': f"""
## 도입부 스타일: 대화체
- 친구에게 말하듯 편하게 시작하세요
- "~하죠?", "~잖아요" 어미 사용
- 독자와 수다 떠는 느낌
- 예: "{keyword} 검색하면 다 비슷한 말만 나오잖아요?"
""",
        'case_study': f"""
## 도입부 스타일: 사례 소개
- 가상의 환자/사례로 시작하세요
- "30대 직장인 A씨는...", "주부 B씨의 경험담"
- 스토리텔링으로 몰입감 제공
- 예: "35세 직장인 A씨는 1년 넘게 {keyword}으로 고생하고 있었습니다..."
""",
        'problem_direct': f"""
## 도입부 스타일: 문제 직격
- 문제점을 바로 지적하며 시작하세요
- PAS 공식: Problem(문제) → Agitate(자극) → Solution(해결책)
- 기존 방법의 한계 언급
- 예: "약 먹어도 재발. {keyword}의 진짜 원인은 따로 있습니다"
""",
        'curiosity': f"""
## 도입부 스타일: 호기심 유발
- 결론을 살짝 암시만 하고 시작하세요
- 오픈 루프: 정보의 공백을 만들어 궁금증 유발
- "가장 중요한 건... 나중에 알려드릴게요" 느낌
- 예: "{keyword}에서 가장 중요한 건 약도 식단도 아니었습니다. 그게 뭘까요?"
""",
    }

    return instructions.get(hook_style, "")


def generate_blog_html_fallback(session: BlogBotSession) -> str:
    """API 키 없을 때 사용하는 기본 템플릿"""
    style_info = HOOK_STYLES[session.hook_style]
    intro_text = generate_intro_by_style(session)

    paper_highlights = []
    for paper in session.papers[:10]:
        if paper.get('abstract'):
            paper_highlights.append({
                'title': paper.get('title', ''),
                'abstract': paper.get('abstract', '')[:500],
                'journal': paper.get('journal', ''),
                'year': paper.get('year', '')
            })

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{session.keyword} - 블로그</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Noto Sans KR', sans-serif; line-height: 1.8; color: #333; background: #fafafa; }}
        .hero {{ width: 100%; height: 280px; object-fit: cover; }}
        .container {{ max-width: 720px; margin: 0 auto; padding: 20px; background: white; }}
        .badge {{ display: inline-block; background: #e8f5e9; color: #2e7d32; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 12px; }}
        h1 {{ font-size: 1.8rem; line-height: 1.4; margin-bottom: 20px; }}
        h2 {{ font-size: 1.4rem; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 2px solid #4CAF50; }}
        p {{ margin-bottom: 18px; font-size: 1.05rem; }}
        .intro-box {{ background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 25px; border-radius: 12px; margin: 25px 0; }}
        .citation {{ background: #fff8e1; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; font-style: italic; border-radius: 0 8px 8px 0; }}
        .highlight-box {{ background: #e8f5e9; border-radius: 12px; padding: 25px; margin: 25px 0; }}
        .highlight-box h4 {{ color: #2e7d32; margin-bottom: 15px; }}
        .highlight-box ul {{ margin-left: 20px; }}
        .highlight-box li {{ margin-bottom: 10px; }}
        .section-image {{ width: 100%; border-radius: 12px; margin: 25px 0; }}
        .references {{ background: #f5f5f5; padding: 25px; border-radius: 12px; margin-top: 40px; }}
        .references h4 {{ margin-bottom: 15px; color: #666; }}
        .references ul {{ font-size: 0.9rem; color: #666; margin-left: 20px; }}
        .references li {{ margin-bottom: 8px; }}
        .disclaimer {{ background: #eceff1; padding: 20px; border-radius: 8px; margin-top: 30px; font-size: 0.85rem; color: #666; }}
        .warning {{ background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <img src="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1200&h=280&fit=crop" class="hero">

    <div class="container">
        <span class="badge">{len(session.papers)}편 논문 분석</span>
        <h1>{session.keyword}, 논문이 말하는 진짜 이야기</h1>

        <div class="warning">
            <strong>⚠️ 안내:</strong> Anthropic API 키가 설정되지 않아 기본 템플릿으로 생성되었습니다.
            .env 파일에 ANTHROPIC_API_KEY를 설정하면 AI가 논문을 분석하여 더 풍부한 글을 작성합니다.
        </div>

        <div class="intro-box">
            {intro_text}
        </div>

        <h2>1. 주요 발견</h2>
        <p>이번 분석에서는 {', '.join(list(session.selected_topics)[:5])} 등의 토픽을 중심으로 {len(session.papers)}편의 논문을 검토했습니다.</p>

        <img src="https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?w=700&h=400&fit=crop" class="section-image">
'''

    for paper in paper_highlights[:3]:
        html += f'''
        <div class="citation">
            "{paper['abstract'][:300]}..."<br><br>
            — {paper['journal']}, {paper['year']}
        </div>
'''

    html += f'''
        <h2>2. 핵심 정리</h2>
        <div class="highlight-box">
            <h4>이 글의 핵심</h4>
            <ul>
'''

    for topic in list(session.selected_topics)[:5]:
        html += f'                <li>{session.keyword}과 {topic}의 관계에 대한 최신 연구 결과</li>\n'

    html += '''            </ul>
        </div>

        <div class="references">
            <h4>참고 논문</h4>
            <ul>
'''

    for paper in session.papers[:6]:
        html += f'                <li>{paper.get("title", "제목 없음")} ({paper.get("journal", "저널 미상")}, {paper.get("year", "연도 미상")})</li>\n'

    if len(session.papers) > 6:
        html += f'                <li>외 {len(session.papers) - 6}편</li>\n'

    html += '''            </ul>
        </div>

        <div class="disclaimer">
            <strong>면책 조항:</strong> 이 글은 의학 논문을 기반으로 한 건강 정보 제공 목적으로 작성되었습니다.
            구체적인 치료 결정은 반드시 담당 의료진과 상담하시기 바랍니다.
        </div>
    </div>
</body>
</html>'''

    return html


def generate_intro_by_style(session: BlogBotSession) -> str:
    """Hook 스타일에 따른 도입부 생성"""
    keyword = session.keyword
    topics = list(session.selected_topics)[:3]
    papers_count = len(session.papers)

    intros = {
        'stat_shock': f'''<p>{keyword} 관련 논문 {papers_count}편을 분석했습니다.
그 중 눈에 띄는 통계가 있었는데요. 기존에 알려진 것과 다른 결과들이 꽤 있었습니다.
특히 {topics[0] if topics else '최근 연구'}에 대한 내용이 인상적이었습니다.</p>''',

        'counterintuitive': f'''<p>{topics[0] if topics else keyword}, 정말 그렇게 중요할까요?
{papers_count}편의 논문을 분석해봤더니 의외의 답이 나왔습니다.
기존 상식과 다른 부분들이 꽤 있더라고요.</p>''',

        'reader_situation': f'''<p>혹시 {keyword} 때문에 고민이신가요?
인터넷에서 검색해봐도 비슷한 말만 나오고, 뭐가 맞는지 헷갈리셨을 겁니다.
그래서 이번에 {papers_count}편의 논문을 직접 분석해봤습니다.</p>''',

        'news_trend': f'''<p>최근 {keyword}에 대한 새로운 연구 결과들이 발표되고 있습니다.
{papers_count}편의 논문을 분석한 결과, {topics[0] if topics else '주요 발견'}에 대해
기존과 다른 시각의 연구들이 눈에 띄었습니다.</p>''',

        'conversation': f'''<p>{keyword} 검색해보면 다 비슷한 말만 나오죠?
{topics[0] if topics else '관련 정보'} 어쩌고, {topics[1] if len(topics) > 1 else '이것저것'} 어쩌고.
근데 논문을 직접 찾아보니까 좀 다른 얘기들이 있더라고요.</p>''',

        'case_study': f'''<p>{keyword}으로 고민하는 분들이 많습니다.
{papers_count}편의 연구를 분석해보니, {topics[0] if topics else '핵심 요인'}이
생각보다 중요한 역할을 한다는 걸 알 수 있었습니다.</p>''',

        'problem_direct': f'''<p>{keyword}. 검색하면 늘 같은 조언만 나옵니다.
하지만 그것만으로 해결이 됐으면 진작 나았겠죠?
{papers_count}편의 논문에서 찾은 다른 접근법을 정리해봤습니다.</p>''',

        'curiosity': f'''<p>{keyword}에서 가장 중요한 건 뭘까요?
{papers_count}편의 논문을 분석하고 나서야 알게 된 게 있습니다.
{topics[0] if topics else '핵심 요소'}에 대한 이야기인데요...</p>''',
    }

    return intros.get(session.hook_style, intros['reader_situation'])


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """대화 취소"""
    await update.message.reply_text(
        "❌ 취소되었습니다.\n\n"
        "/start 로 다시 시작할 수 있습니다."
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """도움말"""
    await update.message.reply_text(
        "📖 *블로그 자동 생성 봇 사용법*\n\n"
        "1️⃣ /start - 새 블로그 작성 시작\n"
        "2️⃣ 키워드 입력 (예: 역류성식도염)\n"
        "3️⃣ 관심 토픽 다중 선택\n"
        "4️⃣ 논문 검색 결과 확인\n"
        "5️⃣ 도입부 스타일 선택\n"
        "6️⃣ 블로그 생성 및 다운로드\n\n"
        "/retry - 이전 세션 이어서 진행\n"
        "/cancel - 진행 중인 작업 취소\n"
        "/help - 이 도움말 보기",
        parse_mode='Markdown'
    )


async def retry_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """저장된 세션 목록 표시 및 재시도"""
    user_id = update.effective_user.id
    sessions = BlogBotSession.list_saved_sessions()

    if not sessions:
        await update.message.reply_text(
            "📭 저장된 세션이 없습니다.\n\n"
            "/start 로 새 블로그를 작성하세요."
        )
        return ConversationHandler.END

    # 세션 목록 버튼 생성
    keyboard = []
    for i, s in enumerate(sessions[:5]):  # 최대 5개
        step_name = {
            '1_keyword_analyzed': '키워드분석',
            '2_papers_searched': '논문검색완료',
            '3_style_selected': '스타일선택',
            '4_generation_started': '생성시작'
        }.get(s['step'], s['step'])

        keyboard.append([
            InlineKeyboardButton(
                f"📄 {s['keyword']} ({step_name}, {s['papers_count']}편)",
                callback_data=f"retry:{i}"
            )
        ])

    keyboard.append([InlineKeyboardButton("❌ 취소", callback_data="retry:CANCEL")])

    # 세션 목록을 context에 저장
    context.user_data['retry_sessions'] = sessions[:5]

    await update.message.reply_text(
        "📂 *저장된 세션 목록*\n\n"
        "이어서 진행할 세션을 선택하세요:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

    return SELECTING_RETRY


async def handle_retry_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """재시도 세션 선택 처리"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data.replace("retry:", "")

    if data == "CANCEL":
        await query.edit_message_text("❌ 취소되었습니다.\n\n/start 로 새로 시작하세요.")
        return ConversationHandler.END

    try:
        idx = int(data)
        sessions = context.user_data.get('retry_sessions', [])
        if idx >= len(sessions):
            await query.edit_message_text("❌ 잘못된 선택입니다.")
            return ConversationHandler.END

        selected = sessions[idx]
        filepath = selected['filepath']

        # 세션 불러오기
        session = BlogBotSession.load_from_file(filepath)
        user_sessions[user_id] = session

        step = selected['step']

        # 단계에 따라 다음 진행
        if step == '4_generation_started' or step == '3_style_selected':
            # 블로그 생성 바로 진행
            await query.edit_message_text(
                f"✅ *세션 불러오기 완료!*\n\n"
                f"📌 키워드: {session.keyword}\n"
                f"📄 논문: {len(session.papers)}편\n"
                f"🏷️ 토픽: {len(session.selected_topics)}개\n\n"
                f"블로그 생성을 시작합니다...",
                parse_mode='Markdown'
            )

            # 블로그 생성 시작
            return await _generate_blog_from_session(update, context, session)

        elif step == '2_papers_searched':
            # 스타일 선택부터
            await query.edit_message_text(
                f"✅ *세션 불러오기 완료!*\n\n"
                f"📌 키워드: {session.keyword}\n"
                f"📄 논문: {len(session.papers)}편\n\n"
                f"도입부 스타일을 선택해주세요.",
                parse_mode='Markdown'
            )
            return await show_hook_styles(update, context)

        else:
            # 처음부터 (토픽 선택)
            await query.edit_message_text(
                f"✅ *세션 불러오기 완료!*\n\n"
                f"📌 키워드: {session.keyword}\n\n"
                f"/start 로 다시 시작하거나 계속 진행하세요."
            )
            return ConversationHandler.END

    except Exception as e:
        await query.edit_message_text(f"❌ 세션 불러오기 실패: {e}")
        return ConversationHandler.END


async def _generate_blog_from_session(update: Update, context: ContextTypes.DEFAULT_TYPE, session: BlogBotSession) -> int:
    """세션에서 블로그 생성"""
    chat_id = update.effective_chat.id

    # Hook 스타일 정보 가져오기 (키가 없으면 첫 번째 스타일 사용)
    style_info = HOOK_STYLES.get(session.hook_style)
    if not style_info:
        # 저장된 스타일 키가 없으면 첫 번째 스타일 사용
        first_key = list(HOOK_STYLES.keys())[0]
        style_info = HOOK_STYLES[first_key]
        session.hook_style = first_key

    # 로딩 표시 시작
    loading = LoadingIndicator(
        context.bot,
        chat_id,
        "*논문 분석 및 블로그 생성 중...*\n(재시도)"
    )
    await loading.start()

    try:
        from concurrent.futures import ThreadPoolExecutor
        from modules.auto_blog_generator import generate_blog_auto, get_last_error_log

        session_data = {
            'keyword': session.keyword,
            'keyword_en': session.keyword_en,
            'topics': list(session.selected_topics),
            'hook_style': session.hook_style,
            'hook_style_name': style_info['name'],
            'hook_style_desc': style_info['desc'],
            'hook_style_template': style_info.get('template', ''),
            'papers': session.papers
        }

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            html_path = await loop.run_in_executor(
                executor,
                generate_blog_auto,
                session_data,
                "output"
            )

        await loading.delete()

        if html_path:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ *블로그 생성 완료!*\n\n📄 파일: `{html_path}`",
                parse_mode='Markdown'
            )

            # 파일 전송
            with open(html_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    filename=os.path.basename(html_path)
                )
        else:
            error_logs = get_last_error_log()
            error_text = "\n".join(error_logs[-10:]) if error_logs else "알 수 없는 오류"
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ *블로그 생성 실패*\n\n```\n{error_text[:1500]}\n```",
                parse_mode='Markdown'
            )

    except Exception as e:
        await loading.delete()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ 오류: {e}"
        )

    return ConversationHandler.END


# 재시도 상태 추가
SELECTING_RETRY = 99


def main():
    """봇 실행"""
    # Config에서 토큰 가져오기 (dotenv 자동 로드)
    token = Config.TELEGRAM_BOT_TOKEN

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
        print("   .env 파일에 TELEGRAM_BOT_TOKEN=your_token 을 추가하세요.")
        print("   토큰은 @BotFather 에서 발급받을 수 있습니다.")
        return

    # 봇 애플리케이션 생성
    application = Application.builder().token(token).build()

    # 대화 핸들러 설정
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("retry", retry_command),
        ],
        states={
            WAITING_KEYWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_keyword)
            ],
            SELECTING_TOPICS: [
                CallbackQueryHandler(toggle_topic, pattern="^topic:")
            ],
            SEARCHING_PAPERS: [
                CallbackQueryHandler(handle_paper_result, pattern="^papers:")
            ],
            SELECTING_HOOK_STYLE: [
                CallbackQueryHandler(select_hook_style, pattern="^hook:")
            ],
            CONFIRMING_DRAFT: [
                CallbackQueryHandler(confirm_generation, pattern="^confirm:")
            ],
            SELECTING_RETRY: [
                CallbackQueryHandler(handle_retry_selection, pattern="^retry:")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # 봇 실행
    print("🤖 블로그 생성 봇이 시작되었습니다!")
    print("   Ctrl+C 로 종료할 수 있습니다.")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
