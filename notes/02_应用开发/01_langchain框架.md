# 应用开发 - LangChain框架

> 学习时间：2026-01-29
> 理解程度：学习中

---

## 🎯 核心面试题

### Q1: 什么是LangChain？它解决了什么问题？

**答案要点：**
- LangChain是开发AI应用的Python框架
- 解决了大模型应用开发的常见问题：链式调用、记忆管理、工具调用等
- 提供统一的接口，支持多种大模型（OpenAI、Llama、Qwen...）
- 核心价值：让AI应用开发更简单、更模块化

---

### Q2: LangChain的六大核心组件是什么？

**答案要点：**

| 组件 | 作用 | 例子 |
|------|------|------|
| **Model I/O** | 和大模型交互 | LLMs、Chat Models、Embeddings |
| **Prompts** | 提示词管理 | PromptTemplate、MessagesPlaceholder |
| **Chains** | 链式调用多个步骤 | SequentialChain、RouterChain |
| **Memory** | 对话历史管理 | ConversationBufferMemory |
| **Tools** | 外部工具调用 | 搜索、计算器、API |
| **Agents** | 自主决策的智能体 | ReAct Agent、OpenAI Functions |

---

### Q3: RAG和微调有什么区别？

**答案要点：**

| 对比 | RAG | 微调 |
|------|-----|------|
| **知识来源** | 外部文档（开卷考试）| 模型参数（闭卷考试）|
| **更新方式** | 更新文档（秒级） | 重新训练（小时-天级）|
| **成本** | 低 | 高 |
| **幻觉问题** | 减少（有参考资料）| 可能存在 |
| **适用场景** | 知识库问答、文档分析 | 特定风格、格式、领域 |

**选择建议：**
- 知识更新频繁 → RAG
- 需要特定风格 → 微调
- 最佳实践 → RAG + 微调组合

---

### Q4: Agent的ReAct工作流程是什么？

**答案要点：**
- ReAct = Reasoning（推理）+ Acting（行动）
- 循环：Thought → Action → Observation → Thought → ...
- 每次观察结果后再决定下一步行动
- 这是Agent"智能"的来源

---

## 📝 我的理解（费曼学习法）

**LangChain的核心思想：**

就像搭积木：
- 每个组件是一个积木（模型、提示词、记忆、工具...）
- Chains把积木搭成房子
- Agents是智能建筑师，能自主决策

**RAG vs 微调：**

- RAG = 开卷考试（给参考资料）
- 微调 = 重新学习（内化知识）

**Agent的智能：**

- 不是一次性完成任务
- 而是多次循环，每次观察后再决策
- 就像人解决问题：思考→行动→观察→调整

---

## 💡 面试官点评与补充

> ✅ 理解准确！

补充要点：
- **LangChain生态**：除了Python还有JavaScript版本，支持跨语言开发
- **LangSmith**：LangChain官方的调试和监控平台
- **LCEL（LangChain Expression Language）**：新的声明式语法，更简洁
- **生产环境考虑**：错误处理、重试机制、流式输出、成本控制

---

## 🔑 核心知识点

### 1. Model I/O（模型输入输出）

**三种模型类型：**

```python
# 1. LLMs - 文本生成
from langchain_openai import OpenAI
llm = OpenAI(model="gpt-3.5-turbo-instruct")
response = llm.invoke("写一首关于AI的诗")

# 2. Chat Models - 对话
from langchain_openai import ChatOpenAI
chat = ChatOpenAI(model="gpt-4")
messages = [HumanMessage(content="你好")]
response = chat.invoke(messages)

# 3. Embeddings - 向量化
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()
vector = embeddings.embed_query("今天天气很好")
```

**流式输出：**

```python
# 流式生成（实时显示）
for chunk in chat.stream("讲个故事"):
    print(chunk.content, end="")
```

---

### 2. Prompts（提示词管理）

**PromptTemplate：**

```python
from langchain.prompts import PromptTemplate

# 基础模板
prompt = PromptTemplate(
    template="你是一个{role}，请回答：{question}",
    input_variables=["role", "question"]
)

# 使用
formatted = prompt.format(role="客服", question="产品价格？")
```

**ChatPromptTemplate：**

```python
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}助手"),
    ("human", "{user_input}")
])

# 使用
messages = prompt.format_messages(role="客服", user_input="今天天气？")
```

**Few-shot示例：**

```python
from langchain.prompts.few_shot import FewShotPromptTemplate

examples = [
    {"input": "高兴", "output": "开心"},
    {"input": "悲伤", "output": "难过"}
]

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate(
        template="输入：{input}\n输出：{output}",
        input_variables=["input", "output"]
    ),
    prefix="以下是一些例子：",
    suffix="\n输入：{new_input}\n输出：",
    input_variables=["new_input"]
)
```

---

### 3. Chains（链）⭐ 面试必考

**LLMChain（最简单）：**

```python
from langchain.chains import LLMChain

chain = LLMChain(
    llm=chat,
    prompt=prompt
)

result = chain.run(role="客服", user_input="产品价格？")
```

**SequentialChain（顺序执行）：**

```python
from langchain.chains import SequentialChain

# 步骤1：总结
summary_chain = LLMChain(
    llm=chat,
    prompt=summary_prompt,
    output_key="summary"
)

# 步骤2：翻译
translate_chain = LLMChain(
    llm=chat,
    prompt=translate_prompt,
    output_key="translation"
)

# 串联
overall_chain = SequentialChain(
    chains=[summary_chain, translate_chain],
    input_variables=["text"],
    output_variables=["translation"]
)

result = overall_chain.run(text="长文本...")
```

**RouterChain（条件路由）：**

```python
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser

# 定义多个提示词
prompts = [
    {"name": "代码", "description": "用于编程问题", "prompt": code_prompt},
    {"name": "写作", "description": "用于写作任务", "prompt": writing_prompt}
]

# 创建路由链
router_chain = MultiPromptChain.from_prompts(
    chat,
    prompts,
    output_key="result"
)

# 自动选择合适的提示词
result = router_chain.run("写一个Python函数")
```

**LCEL（新语法，推荐）：**

```python
# 使用LCEL更简洁
chain = (
    {"role": "客服"}
    | prompt
    | chat
    | StrOutputParser()
)

result = chain.invoke({"user_input": "产品价格？"})
```

---

### 4. Memory（记忆）⭐ 面试必考

**ConversationBufferMemory：**

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=chat,
    memory=memory,
    verbose=True
)

conversation.predict(input="我叫小明")
conversation.predict(input="我叫什么？")  # 能回答
```

**多种Memory类型：**

| 类型 | 原理 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **ConversationBufferMemory** | 保存所有对话 | 完整历史 | token多 | 短对话 |
| **ConversationBufferWindowMemory** | 只保留K轮 | token少 | 丢失早期信息 | 长对话 |
| **ConversationSummaryMemory** | 总结历史 | token少 | 需要额外计算 | 超长对话 |
| **VectorStoreMemory** | 向量检索 | 长期记忆 | 复杂度高 | 需要回忆早期内容 |

**ConversationSummaryMemory示例：**

```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(
    llm=chat,
    return_messages=True
)

# 自动总结之前的对话
memory.save_context(
    {"input": "我叫小明，喜欢编程"},
    {"output": "你好小明！很高兴认识你"}
)

# 后续对话会基于总结
memory.load_memory_variables({})
# {'history': '小明自我介绍叫小明，喜欢编程...'}
```

---

### 5. Tools（工具）⭐ 面试必考

**内置工具：**

```python
from langchain.tools import (
    Tool,
    DuckDuckGoSearchRun,  # 搜索
    WikipediaQueryRun,   # 维基百科
    PythonREPL,          # Python代码执行
    SerpAPIWrapper       # Google搜索
)

# 搜索工具
search = DuckDuckGoSearchRun()

# 定义自定义工具
def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"结果：{result}"
    except:
        return "计算错误"

tool = Tool(
    name="Calculator",
    func=calculator,
    description="计算数学表达式。输入：数学表达式字符串"
)
```

**Structured Tool（带参数验证）：**

```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    expression: str = Field(description="要计算的数学表达式")

calculator_tool = StructuredTool.from_function(
    func=calculator,
    name="Calculator",
    description="计算数学表达式",
    args_schema=CalculatorInput
)
```

**Tool Kits（工具集合）：**

```python
from langchain.agents import load_tools

# 加载常用工具集
tools = load_tools(
    ["ddg-search", "wikipedia", "python-repl"],
    llm=chat
)
```

---

### 6. Agents（智能体）⭐⭐⭐ 面试必考

**ReAct Agent：**

```python
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

tools = [search_tool, calculator_tool]

# 创建Agent
agent = initialize_agent(
    tools=tools,
    llm=chat,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,  # 打印思考过程
    handle_parsing_errors=True  # 错误处理
)

# 运行
result = agent.run("帮我查北京今天的天气，然后把温度换算成华氏度")
```

**Agent执行流程（verbose=True输出）：**

```
> Entering new AgentExecutor chain...

Thought: 用户需要查天气和温度转换，我应该先用搜索工具查天气
Action:
  Tool: duckduckgo-search
  Tool Input: 北京今天天气

Observation: 北京今天晴天，温度20°C

Thought: 现在需要把20°C转换成华氏度
Action:
  Tool: Calculator
  Tool Input: 20 * 9/5 + 32

Observation: 结果：68.0

Thought: 我知道了所有信息，可以回答用户
Final Answer: 北京今天晴天，温度20°C（68°F）

> Finished chain.
```

**OpenAI Functions Agent（推荐）：**

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor

from langchain.tools import tool

@tool
def search_weather(location: str) -> str:
    """查询指定城市的天气"""
    # 实际调用天气API
    return f"{location}今天晴天，25°C"

@tool
def calculate(expression: str) -> float:
    """计算数学表达式"""
    return eval(expression)

tools = [search_weather, calculate]

agent = create_openai_functions_agent(chat, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

result = agent_executor.invoke({
    "input": "帮我查北京天气"
})
```

---

### 7. RAG系统（检索增强生成）⭐⭐⭐ 面试必考

**完整流程：**

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 步骤1：加载文档
loader = TextLoader("document.txt")
documents = loader.load()

# 步骤2：分割文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(documents)

# 步骤3：向量化并存储
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings
)

# 步骤4：创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # 返回最相关的3个文档
)

# 步骤5：创建RAG链
rag_chain = RetrievalQA.from_chain_type(
    llm=chat,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# 步骤6：查询
result = rag_chain({"query": "公司的营收是多少？"})
print(result["result"])
print(result["source_documents"])
```

**不同检索策略：**

```python
# 1. 相似度检索（默认）
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# 2. MMR（平衡相关性和多样性）
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 10}
)

# 3. 相似度分数阈值
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.7}
)
```

**自定义RAG提示词：**

```python
from langchain.prompts import PromptTemplate

prompt_template = """使用以下上下文片段来回答问题。如果不知道答案，就说不知道，不要编造答案。

上下文：
{context}

问题：{question}

答案："""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

rag_chain = RetrievalQA.from_chain_type(
    llm=chat,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT}
)
```

---

### 8. Conversational RAG（带记忆的RAG）

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 创建记忆
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 创建对话式RAG
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=chat,
    retriever=retriever,
    memory=memory,
    return_source_documents=True
)

# 多轮对话
result1 = qa_chain({
    "question": "公司营收是多少？"
})
result2 = qa_chain({
    "question": "同比增长了多少？"  # 能理解上下文
})
```

---

## 📌 重点记录

### 面试高频考点：

1. **LangChain vs 直接调用API**
   - LangChain：组件化、可复用、易维护
   - 直接调用：简单但难以扩展
   - 生产环境推荐使用LangChain

2. **Chains的类型**
   - LLMChain：最简单
   - SequentialChain：顺序执行
   - RouterChain：条件路由
   - 推荐：使用LCEL新语法

3. **Memory的选择**
   - 短对话：ConversationBufferMemory
   - 长对话：ConversationSummaryMemory
   - 需要回忆早期内容：VectorStoreMemory

4. **Agent的ReAct模式**
   - Thought → Action → Observation 循环
   - 不是一次性完成，而是迭代优化
   - verbose=True可以看到思考过程

5. **RAG vs 微调**
   - RAG：开卷考试，更新快，成本低
   - 微调：闭卷考试，内化知识，效果更好
   - 最佳：RAG + 微调组合

### 常见误区：

❌ 误区1：LangChain只支持OpenAI
✅ 正解：支持数十种模型（Llama、Qwen、Claude...）

❌ 误区2：Agent总是比Chain好
✅ 正解：简单任务用Chain，复杂自主决策用Agent

❌ 误区3：RAG可以替代微调
✅ 正解：RAG和微调互补，各有优劣

❌ 误区4：Memory越多越好
✅ 正解：Memory增加token消耗，需要权衡

### 实战建议：

**场景1：问答机器人**
- ConversationalRetrievalChain
- ConversationBufferMemory
- 向量数据库存储知识库

**场景2：代码助手**
- OpenAI Functions Agent
- 代码执行工具（PythonREPL）
- 文件读写工具

**场景3：客服机器人**
- RouterChain路由不同问题类型
- 不同类型用不同的Chain
- 记录对话历史用于分析

**场景4：文档分析**
- RAG + 大上下文模型
- DocumentLoader加载各种格式
- 多轮对话总结文档

---

## 🔄 复习检查清单

- [x] 理解LangChain的六大核心组件
- [x] 掌握Chains的使用
- [x] 理解Memory的不同类型
- [x] 掌握Agent的ReAct工作流程
- [x] 理解RAG的完整流程
- [ ] 了解LCEL新语法
- [ ] 了解LangSmith调试平台
- [ ] 能独立实现一个完整的RAG系统

---

## 📚 延伸阅读

- [LangChain官方文档](https://python.langchain.com/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [LCEL文档](https://python.langchain.com/docs/expression_language/)
- [LangSmith平台](https://www.langchain.com/langsmith)
