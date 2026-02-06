"""봇 환경에서 Claude CLI 테스트"""
import subprocess
import os
import uuid

def test_claude():
    prompt = "Say hello"
    prompt_file = f'_claude_test_{uuid.uuid4().hex[:8]}.txt'

    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)

    # 환경 변수 설정
    env = os.environ.copy()
    env['HOME'] = os.path.expanduser('~')
    env['USERPROFILE'] = os.path.expanduser('~')

    print(f"HOME: {env.get('HOME')}")
    print(f"USERPROFILE: {env.get('USERPROFILE')}")
    print(f"Current dir: {os.getcwd()}")
    print(f"Prompt file: {prompt_file}")
    print(f"File exists: {os.path.exists(prompt_file)}")

    try:
        result = subprocess.run(
            ['cmd', '/c', f'type {prompt_file} | claude -p --output-format text'],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            env=env
        )

        print(f"returncode: {result.returncode}")
        print(f"stdout: {result.stdout[:500] if result.stdout else 'empty'}")
        print(f"stderr: {result.stderr[:500] if result.stderr else 'empty'}")
    finally:
        try:
            os.remove(prompt_file)
        except:
            pass

if __name__ == '__main__':
    test_claude()
