from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from tools.quickbuild import check_build_status
from tools.perforce import get_commit_author

def setup_agent():
    # 1. 사용할 도구 목록 취합
    tools = [check_build_status, get_commit_author]
    
    # 2. LLM 초기화
    #llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm = ChatOllama(model="llama3.2:latest", temperature=0)
    
    # 3. 에이전트 그래프 생성 및 반환
    return create_react_agent(llm, tools)