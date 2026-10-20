from langchain_core.tools import tool

@tool
def get_commit_author(changelist: str) -> str:
    """특정 Changelist(커밋 번호)의 작성자 이름과 ID를 조회합니다."""
    print(f"🛠️ [Tool] Perforce Changelist {changelist} 작성자 조회 중...")
    if changelist == "9082":
        return "jihwan0.lim"
    return "알 수 없음"
