from datetime import datetime

from backend.rag.chain import answer_with_rag
from backend.schemas import ChatResponse


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    allowed = set("0123456789+-*/(). %")
    if any(char not in allowed for char in expression):
        return "表达式包含不支持的字符。"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"计算失败：{exc}"


async def answer_with_agent(question: str) -> ChatResponse:
    tool_notes: list[str] = []
    lowered = question.lower()

    if "时间" in question or "time" in lowered:
        tool_notes.append(f"get_current_time() => {get_current_time()}")

    if "计算" in question or "calc" in lowered:
        expression = question.replace("计算", "").replace("calc", "").strip()
        if expression:
            tool_notes.append(f"calculate({expression!r}) => {calculate(expression)}")

    response = await answer_with_rag(question)
    if tool_notes:
        response.answer = response.answer + "\n\n工具调用记录：\n" + "\n".join(f"- {note}" for note in tool_notes)
    response.mode = response.mode.replace("rag:", "agent:")
    return response
