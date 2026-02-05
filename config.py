"""설정 파일"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """애플리케이션 설정"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'

    # Anthropic API
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = 'claude-sonnet-4-5-20250929'

    # PubMed API
    PUBMED_EMAIL = os.environ.get('PUBMED_EMAIL', 'user@example.com')
    PUBMED_API_KEY = os.environ.get('PUBMED_API_KEY')

    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

    # 검색 설정
    DEFAULT_PAPER_COUNT = 12
    MIN_PAPER_COUNT = 5
    MAX_PAPER_COUNT = 30

    # 시리즈 블로그 설정
    MAX_RELATED_KEYWORDS = 15  # 웹 검색에서 추출할 최대 연관 키워드 수
    MIN_PAPERS_PER_CATEGORY = 3  # 시리즈 글 생성에 필요한 카테고리당 최소 논문 수

    # 논문 카테고리 설정
    PAPER_CATEGORIES = [
        'cause',        # 원인
        'treatment',    # 치료
        'diet',         # 식이요법
        'lifestyle',    # 생활습관
        'prevention',   # 예방
        'complications' # 합병증
    ]

    # 출력 설정
    OUTPUT_DIR = 'output'
    ALLOWED_FORMATS = ['html', 'markdown']

    # 블로그 글 스타일
    BLOG_STYLE = 'hybrid'  # 'academic', 'casual', 'hybrid'

    @staticmethod
    def validate():
        """필수 설정 검증"""
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return True
