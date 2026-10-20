import os
from dotenv import load_dotenv
from agent.graph import setup_agent

# 1. .env 파일에서 환경변수 불러오기
load_dotenv()

# 2. 에이전트 준비
agent_executor = setup_agent()

# 3. 사용자 입력 처리 및 실행
user_input = "빌드 1042번 상태 확인하고, 실패했으면 누가 커밋했는지 찾아서 보고해줘."
print(f"👤 사용자: {user_input}\n" + "-"*50)

for step in agent_executor.stream({"messages":[("user", user_input)]}):
    pass # 필요에 따라 과정 출력 로직 추가

# 최종 결과 출력
final_message = step['agent']['messages'][-1].content
print(f"\n🤖 최종 답변:\n{final_message}")