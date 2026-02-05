"""Flask 웹 애플리케이션 메인"""
from flask import Flask, render_template, request, jsonify, send_file
from config import Config
from modules import PubMedSearcher, PaperAnalyzer, BlogGenerator
import os
from datetime import datetime
import traceback

app = Flask(__name__)
app.config.from_object(Config)

# 출력 디렉토리 생성
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_blog():
    """블로그 글 생성 API"""
    try:
        # 요청 데이터 파싱
        data = request.get_json()
        topic = data.get('topic', '').strip()
        paper_count = data.get('paper_count', Config.DEFAULT_PAPER_COUNT)
        style = data.get('style', 'hybrid')

        # 입력 검증
        if not topic:
            return jsonify({'error': '주제를 입력해주세요.'}), 400

        if paper_count < Config.MIN_PAPER_COUNT or paper_count > Config.MAX_PAPER_COUNT:
            return jsonify({
                'error': f'논문 개수는 {Config.MIN_PAPER_COUNT}-{Config.MAX_PAPER_COUNT} 사이여야 합니다.'
            }), 400

        # API 키 검증
        Config.validate()

        print(f"\n{'='*60}")
        print(f"새로운 블로그 글 생성 요청")
        print(f"주제: {topic}")
        print(f"논문 개수: {paper_count}")
        print(f"스타일: {style}")
        print(f"{'='*60}\n")

        # 1단계: PubMed에서 논문 검색
        searcher = PubMedSearcher(
            email=Config.PUBMED_EMAIL,
            api_key=Config.PUBMED_API_KEY
        )
        papers = searcher.search_and_fetch(topic, max_results=paper_count)

        if not papers:
            return jsonify({
                'error': '관련 논문을 찾을 수 없습니다. 다른 검색어를 시도해보세요.'
            }), 404

        # 2단계: Claude로 논문 분석
        analyzer = PaperAnalyzer(
            api_key=Config.ANTHROPIC_API_KEY,
            model=Config.ANTHROPIC_MODEL
        )
        analysis = analyzer.analyze_papers(papers, topic)

        if 'error' in analysis:
            return jsonify({'error': f'논문 분석 실패: {analysis["error"]}'}), 500

        # 3단계: 블로그 글 생성
        generator = BlogGenerator(
            api_key=Config.ANTHROPIC_API_KEY,
            model=Config.ANTHROPIC_MODEL
        )
        blog_html = generator.generate_blog_post(topic, analysis, style)

        # 4단계: 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic.replace(' ', '_')}_{timestamp}.html"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(blog_html)

        print(f"\n✓ 블로그 글이 생성되었습니다: {filepath}\n")
        print(f"{'='*60}\n")

        # 결과 반환
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'paper_count': len(papers),
            'preview': blog_html[:500] + '...'  # 미리보기
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"\n✗ 오류 발생:\n{traceback.format_exc()}")
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """생성된 파일 다운로드"""
    try:
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preview/<filename>')
def preview_file(filename):
    """생성된 파일 미리보기"""
    try:
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            return "파일을 찾을 수 없습니다.", 404

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        return content
    except Exception as e:
        return f"오류: {str(e)}", 500


@app.route('/health')
def health_check():
    """헬스 체크"""
    try:
        Config.validate()
        return jsonify({
            'status': 'healthy',
            'config': {
                'anthropic_api': '✓ 설정됨' if Config.ANTHROPIC_API_KEY else '✗ 미설정',
                'pubmed_email': Config.PUBMED_EMAIL,
                'model': Config.ANTHROPIC_MODEL
            }
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


if __name__ == '__main__':
    # 설정 검증
    try:
        Config.validate()
        print("\n" + "="*60)
        print("🚀 논문 기반 자동 블로그 글 생성기")
        print("="*60)
        print(f"✓ Anthropic API 키: 설정됨")
        print(f"✓ PubMed 이메일: {Config.PUBMED_EMAIL}")
        print(f"✓ Claude 모델: {Config.ANTHROPIC_MODEL}")
        print("="*60)
        print("\n💡 브라우저에서 http://localhost:5000 접속\n")

        app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)

    except ValueError as e:
        print(f"\n✗ 설정 오류: {e}")
        print("💡 .env 파일을 확인하고 ANTHROPIC_API_KEY를 설정하세요.\n")
