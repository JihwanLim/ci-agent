from langchain_core.tools import tool

@tool
def check_build_status(build_id: str) -> str:
    """주어진 빌드 ID의 상태와 에러 로그를 확인합니다."""
    print(f"🛠️ [Tool] QuickBuild 빌드 {build_id} 상태 조회 중...")
    if build_id == "1042":
        return "상태: FAILED, 사유: Compile Error, 관련 ChangeList: 9982"
    return "상태: SUCCESS"