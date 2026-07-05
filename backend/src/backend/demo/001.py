from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 定义各组件
retriever = ...          # 你的检索器
prompt = ChatPromptTemplate.from_template("...")
model = ChatOpenAI(model="gpt-4o-mini")
output_parser = ...      # 你的输出解析器

# 构建链
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | output_parser
)

# 调用
result = chain.invoke("什么是 RAG？")
result = chain.batch(["问题1", "问题2", "问题3"])

async def main():
    async for chunk in chain.astream("问题"):
        print(chunk)
