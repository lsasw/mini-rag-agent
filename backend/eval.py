import asyncio
import time

import httpx

CASES = [
    {"question": "RAG 的核心流程是什么？", "expected_keywords": ["检索", "生成"]},
    {"question": "这个项目支持上传什么文档？", "expected_keywords": ["txt", "md", "pdf"]},
]


async def main() -> None:
    hits = 0
    started = time.perf_counter()
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=60) as client:
        for case in CASES:
            response = await client.post("/api/chat", json={"message": case["question"]})
            response.raise_for_status()
            answer = response.json()["answer"]
            matched = all(keyword.lower() in answer.lower() for keyword in case["expected_keywords"])
            hits += int(matched)
            print(f"- {case['question']} => {'PASS' if matched else 'MISS'}")

    elapsed = time.perf_counter() - started
    print(f"\nAccuracy: {hits}/{len(CASES)}")
    print(f"Average latency: {elapsed / len(CASES):.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
