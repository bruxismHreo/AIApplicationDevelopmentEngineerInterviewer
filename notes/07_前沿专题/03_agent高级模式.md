# 前沿专题 - Agent 高级模式

> 学习时间：2026-03-11
> 理解程度：学习中

---

## 🎯 核心面试题

### Q1: LangChain 和 LangGraph 的核心区别是什么？

**答案要点：**
- LangChain：链式调用，顺序执行，难以处理循环和条件分支
- LangGraph：状态图模型，支持循环、条件分支、多路径执行
- LangGraph 提供：可视化、状态管理、错误恢复、持久化
- 选择：简单任务用 LangChain，复杂工作流用 LangGraph

---

### Q2: 什么是 ReAct 模式？它的执行流程是怎样的？

**答案要点：**
- ReAct = Reasoning（推理）+ Acting（行动）
- 循环执行：Thought（思考）→ Action（行动）→ Observation（观察）
- 通过推理决定使用哪个工具，观察结果后继续推理
- 比纯 Chain 更灵活，能处理复杂的多步任务

---

### Q3: Plan-and-Execute 与 ReAct 的区别？

**答案要点：**
- ReAct：边思考边执行，逐步推理
- Plan-and-Execute：先规划完整计划，再逐步执行
- Plan-and-Execute 优势：全局视野，可优化计划
- Plan-and-Execute 劣势：规划阶段可能出错，难以动态调整
- 选择：复杂任务用 Plan-and-Execute，探索性任务用 ReAct

---

### Q4: CrewAI 和多 Agent 协作的应用场景？

**答案要点：**
- CrewAI：多个 Agent 各司其职，协作完成复杂任务
- 场景：研究助手（搜索 Agent + 分析 Agent + 写作 Agent）
- 协作模式：顺序执行、并行执行、层级协作
- 关键点：Agent 间通信、任务分配、结果聚合

---

### Q5: 如何设计一个具有记忆能力的 Agent？

**答案要点：**
- 短期记忆：对话历史（存储在 Message History）
- 长期记忆：向量数据库（存储重要信息）
- 记忆检索：根据当前查询检索相关历史
- 记忆更新：重要事件和用户偏好存储
- 工具：LangChain Memory、MemGPT、LlamaIndex Memory

---

## 📝 我的理解（费曼学习法）

**[请用自己的话简单解释 Agent 高级模式的核心概念]**

---

## 💡 面试官点评与补充

> Agent 框架的选择体现了架构师思维。面试官会考察你能否根据任务特点选择合适的框架。

> 框架选型决策树：
> - 简单链式任务 → LangChain Chains
> - 需要循环/条件 → LangGraph
> - 多 Agent 协作 → CrewAI / AutoGen
> - RAG 专用 → LlamaIndex Agents

---

## 🔑 核心知识点

### Agent 框架对比

| 框架 | 核心特点 | 适用场景 | 优势 | 劣势 |
|------|----------|----------|------|------|
| **LangChain** | 链式调用 | 简单任务 | 生态丰富、易上手 | 难以处理复杂流程 |
| **LangGraph** | 状态图 | 复杂工作流 | 可视化、支持循环 | 学习曲线陡 |
| **LlamaIndex Agents** | RAG 专用 | 知识密集型任务 | 与 RAG 深度集成 | 非 RAG 场景较弱 |
| **CrewAI** | 多 Agent 协作 | 团队协作任务 | 角色明确、易协作 | 配置复杂 |
| **AutoGen** | Agent 对话 | 多轮讨论 | 自动化对话流程 | 微软生态依赖 |

### ReAct 模式详解

**执行流程：**
```
用户输入：北京今天天气怎么样？

Thought 1: 用户想知道北京今天的天气，我需要调用天气查询工具
Action 1: get_weather(city="北京", date="今天")
Observation 1: 北京今天晴天，气温 15-25°C

Thought 2: 我已经获取到天气信息，可以回答用户
Action 2: finish(answer="北京今天晴天，气温 15-25°C")
```

**实现示例：**
```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool

# 定义工具
tools = [
    Tool(
        name="get_weather",
        func=lambda x: weather_api.get(x),
        description="获取城市天气信息"
    )
]

# 创建 ReAct Agent
agent = create_react_agent(
    llm=chat_model,
    tools=tools,
    prompt=react_prompt
)

# 执行
agent_executor = AgentExecutor(agent=agent, tools=tools)
result = agent_executor.invoke({"input": "北京今天天气怎么样？"})
```

### LangGraph 状态图

**核心概念：**
```python
from langgraph.graph import StateGraph, END

# 定义状态
class AgentState(TypedDict):
    messages: List[dict]
    next_action: str
    loop_count: int

# 定义节点
def reasoning_node(state: AgentState):
    # 推理逻辑
    return {"next_action": "search"}

def action_node(state: AgentState):
    # 执行工具
    return {"messages": [...]}

# 定义条件边
def should_continue(state: AgentState):
    if state["loop_count"] > 3:
        return END
    return "reasoning"

# 构建图
graph = StateGraph(AgentState)
graph.add_node("reasoning", reasoning_node)
graph.add_node("action", action_node)
graph.add_conditional_edges("action", should_continue)
graph.set_entry_point("reasoning")

# 编译和执行
app = graph.compile()
result = app.invoke({"messages": [], "loop_count": 0})
```

**与 LangChain 对比：**
```python
# LangChain：链式，难以循环
chain = (
    {"input" : RunnablePassthrough()}
    | prompt
    | chat_model
    | StrOutputParser()
)

# LangGraph：状态图，支持循环
# 可以基于状态决定下一步动作
```

### Plan-and-Execute 模式

**两阶段执行：**
```
阶段 1：Planning
用户：帮我规划一次日本旅行
Planner Agent：
1. 了解用户偏好（时间、预算、兴趣）
2. 搜索目的地信息
3. 制定行程计划
4. 输出：7天行程单

阶段 2：Execution
Executor Agent：
1. 预订机票（Step 1）
2. 预订酒店（Step 2）
3. ...
7. 完成预订
```

**实现示例：**
```python
from langchain.chains import PlanAndExecute

# 规划器
planner = load_chain("planner_chain")

# 执行器
executor = load_chain("executor_chain")

# 组合
agent = PlanAndExecute(
    planner=planner,
    executor=executor,
    verbose=True
)

result = agent.run("帮我规划一次日本旅行")
```

### CrewAI 多 Agent 协作

**角色定义：**
```python
from crewai import Agent, Crew, Task

# 定义 Agent
researcher = Agent(
    role="研究员",
    goal="搜索并分析最新技术信息",
    backstory="你是一位资深的技术研究员..."
)

writer = Agent(
    role="技术作家",
    goal="将研究结果写成易懂的文章",
    backstory="你擅长将复杂技术概念解释清楚..."
)

reviewer = Agent(
    role="编辑",
    goal="审核文章质量并提出改进建议",
    backstory="你是一位经验丰富的技术编辑..."
)

# 定义任务
research_task = Task(
    description="研究 2024 年 RAG 技术的最新进展",
    agent=researcher
)

write_task = Task(
    description="基于研究结果写一篇技术文章",
    agent=writer
)

review_task = Task(
    description="审核文章并提供反馈",
    agent=reviewer
)

# 创建 Crew
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, write_task, review_task],
    process="sequential"  # 顺序执行
)

# 执行
result = crew.kickoff()
```

**协作模式：**
- **Sequential**：顺序执行，每个任务完成后才进行下一个
- **Parallel**：并行执行，多个 Agent 同时工作
- **Hierarchical**：层级协作，Manager Agent 分配任务

### Agent 记忆管理

**记忆类型：**
```
1. 短期记忆（对话历史）
   - 存储方式：Message History
   - 作用：保持上下文连续性
   - 容量：受上下文窗口限制

2. 长期记忆（知识库）
   - 存储方式：向量数据库
   - 作用：跨会话记忆
   - 容量：几乎无限

3. 工作记忆（当前任务）
   - 存储方式：状态变量
   - 作用：跟踪当前任务进度
   - 容量：当前会话
```

**实现示例：**
```python
from langchain.memory import VectorStoreMemory
from langchain.vectorstores import Chroma

# 长期记忆
vector_store = Chroma(...)
long_term_memory = VectorStoreMemory(
    vectorstore=vector_store,
    memory_key="history"
)

# Agent 记忆配置
agent = Agent(
    llm=chat_model,
    tools=tools,
    memory=long_term_memory,  # 长期记忆
    verbose=True
)

# 手动存储重要信息
def save_to_memory(agent, key, value):
    memory_vector = embedding_function.embed_query(f"{key}: {value}")
    vector_store.add_texts(
        texts=[f"{key}: {value}"],
        embeddings=[memory_vector],
        metadatas [{"type": "memory", "key": key}]
    )
```

### 其他 Agent 模式

**CoT (Chain-of-Thought)：**
```
让模型展示推理过程：
"让我一步步思考：首先...然后...最后..."
```

**Refine（迭代优化）：**
```
第一版答案 → 反思 → 改进 → 第二版答案 → ...
适用于：写作、代码优化、创意生成
```

**Self-Consistency（自我一致性）：**
```
多次生成答案，选择最一致的答案
适用于：数学推理、逻辑推理
```

---

## 📚 延伸阅读

- **论文**：ReAct: Synergizing Reasoning and Acting in Language Models
- **论文**：Plan-and-Solve Prompting
- **资源**：LangGraph 官方文档
- **资源**：CrewAI 官方文档
- **资源**：AutoGen 微软文档

---

## 🔄 复习检查清单

- [ ] 理解 LangChain vs LangGraph 的核心区别
- [ ] 掌握 ReAct 模式的执行流程
- [ ] 了解 Plan-and-Execute 与 ReAct 的区别
- [ ] 掌握 CrewAI 多 Agent 协作模式
- [ ] 理解 Agent 记忆管理机制
- [ ] 了解其他 Agent 模式（CoT、Refine、Self-Consistency）

---

## 📌 重点记录

### 面试高频考点：
- 框架对比：LangChain vs LangGraph vs LlamaIndex vs CrewAI
- ReAct 模式：Thought → Action → Observation 循环
- Plan-and-Execute：先规划后执行，适合复杂任务
- 多 Agent 协作：角色定义、任务分配、结果聚合
- 记忆管理：短期（对话历史）、长期（向量库）、工作（状态）

### 常见误区：
- 认为复杂场景一定要用 LangGraph（有时简单 Chain 更合适）
- 忽视 Agent 的可观测性（难以调试）
- 过度设计 Agent 系统（简单任务不需要多 Agent）
- 忽视记忆管理的成本（长期记忆需要检索和过滤）

### 工程实践要点：
- 简单任务用 Chain，复杂工作流用 Graph
- Agent 调试需要详细的日志和追踪
- 记忆检索需要相关性排序，避免噪声
- 多 Agent 系统需要明确的通信协议
- 考虑失败重试和错误恢复机制
