# 🤖 반도체 SW 개발 도구 통합 자동화 AI 에이전트

반도체 소프트웨어 개발 파이프라인에 사용되는 다양한 도구(QuickBuild, Perforce, Black Duck, Coverity, qTest, Polarion, ICManage)를 하나로 엮어, 복잡한 인프라 업무를 자동화하고 개발팀의 생산성을 높이는 AI 에이전트 프로젝트입니다.

---

## 1. 프레임워크 및 아키텍처 (Why LangGraph?)

다양한 REST API를 순차적이고 조건부로 호출해야 하는 복잡한 워크플로우를 제어하기 위해 **LangGraph 기반의 Tool-Calling 아키텍처**를 채택했습니다.

### 프레임워크 비교
*   **LlamaIndex:** 문서 검색(RAG)에는 강력하지만 복잡한 액션 제어에 한계가 있음.
*   **CrewAI/AutoGen:** 다중 에이전트 토론에는 좋으나 단일 인프라 제어용으로는 무거움.
*   **LangChain + LangGraph (✅ 채택):** 에이전트의 상태(State)를 기억하고, 분기 처리 및 도구 호출(Tool Calling) 순서를 제어하는 데 가장 최적화되어 있음.

### 시스템 아키텍처 구조
*   **Brain (LLM):** 로컬 오픈소스 LLM (Ollama - Qwen2.5 / Llama3 등) 또는 상용 API.
*   **Orchestrator:** LangGraph (작업 순서 및 상태 저장망).
*   **Tools (손과 발):** 각 사내 시스템(QuickBuild, Perforce 등)의 API를 래핑한 파이썬 함수들.

---

## 2. 핵심 작동 원리: ReAct (Reasoning + Acting)

이 에이전트는 단순한 챗봇이 아니라 **ReAct** 프롬프팅 기법을 사용하여 작동합니다. ReAct는 언어 모델이 **추론(생각)**과 **행동(도구 사용)**을 번갈아 가며 수행하도록 하는 기법입니다.

*   **Thought (생각):** "사용자가 빌드 1042번 실패 원인을 물어봤다. 먼저 빌드 상태 조회 도구를 써야겠다."
*   **Action (행동):** `check_build_status(build_id="1042")` 실행.
*   **Observation (관찰):** "빌드는 컴파일 에러로 실패했고, 관련 커밋은 9982번이다."
*   **Thought (생각):** "이제 9982번 커밋의 작성자를 찾는 도구를 써야겠다."

이러한 **[Thought $\rightarrow$ Action $\rightarrow$ Observation]** 루프를 통해 에이전트는 환각(거짓말)을 최소화하고, 실제 데이터를 바탕으로 정확한 문제 해결을 수행합니다.

---

## 3. 프로젝트 디렉토리 구조

유지보수와 도구 확장을 위해 모듈화된 디렉토리 구조를 사용합니다.

```text
langgraph-agent-project/
├── requirements.txt        # 패키지 의존성 목록
├── main.py                 # 프로그램 실행 엔트리포인트 (사용자 입력 및 결과 출력)
├── agent/                  # 에이전트 정의 폴더
│   ├── __init__.py
│   └── graph.py            # LangGraph 조립 및 LLM 설정
└── tools/                  # 연동할 시스템별 API 도구 모음 폴더
    ├── __init__.py
    ├── quickbuild.py       # 빌드 서버 연동 도구
    └── perforce.py         # 형상관리 연동 도구
```

---

## 4. 코드 설명 및 실행 방법

### 4.1. 환경 설정 및 실행
본 프로젝트는 API 키 발급 없이 완전 무료로 로컬에서 테스트하기 위해 **Ollama**를 사용합니다.

1.  [Ollama](https://ollama.com) 설치 후 터미널에서 모델 다운로드: `ollama run qwen2.5:7b`
2.  파이썬 패키지 설치: `pip install langgraph langchain-ollama`
3.  프로젝트 실행: `python main.py`

### 4.2. 핵심 코드 리뷰

#### 1) `tools/` (도구 정의)
AI가 사용할 도구는 반드시 `@tool` 데코레이터와 상세한 `docstring(설명문)`, 그리고 명확한 `Type Hint`를 가져야 합니다. AI는 이 설명을 읽고 도구 사용법을 스스로 깨우칩니다.

```python
# tools/quickbuild.py 예시
from langchain_core.tools import tool

@tool
def check_build_status(build_id: str) -> str:
    """주어진 빌드 ID의 상태와 에러 로그를 확인합니다."""
    if build_id == "1042":
        return "상태: FAILED, 관련 Changelist: 9982"
    return "상태: SUCCESS"
```

#### 2) `agent/graph.py` (에이전트 조립)
LLM과 정의된 Tool들을 LangGraph의 `create_react_agent`로 엮어줍니다.

```python
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from tools.quickbuild import check_build_status
from tools.perforce import get_commit_author

def setup_agent():
    # 1. 사용할 도구 리스트 등록
    tools = [check_build_status, get_commit_author]
    # 2. 로컬 LLM 연결 (Ollama)
    llm = ChatOllama(model="qwen2.5:7b", temperature=0)
    # 3. ReAct 에이전트 생성
    return create_react_agent(llm, tools)
```

#### 3) `main.py` (실행 및 루프 확인)
사용자의 입력을 받고 에이전트가 생각하고 행동하는 과정을 출력합니다.

```python
from agent.graph import setup_agent

agent_executor = setup_agent()
user_input = "빌드 1042번 상태 확인하고, 실패했으면 누가 커밋했는지 찾아서 보고해줘."

# 에이전트 스트리밍 실행 (사고 과정 추적)
for step in agent_executor.stream({"messages": [("user", user_input)]}):
    print(step)
```

---

## 5. 향후 개발 로드맵 (Use Cases)

현재는 기초 뼈대(Skeleton) 코드로 구성되어 있으며, 향후 다음 4가지 핵심 기능을 순차적으로 개발 및 연동할 예정입니다.

1.  **빌드 장애 자동 분석:** QuickBuild 실패 로그 분석 및 Perforce 커밋 담당자 자동 추적 알림.
2.  **보안/결함 티켓팅 자동화:** Coverity/Black Duck 스캔 결과를 분석하여 Polarion 이슈 자동 생성.
3.  **테스트 케이스 자동 생성:** Polarion 요구사항을 바탕으로 qTest 시나리오 초안 작성.
4.  **인프라 L1 헬프데스크:** RAG를 접목하여 툴 사용법 가이드 및 단순 권한 부여 자동화.