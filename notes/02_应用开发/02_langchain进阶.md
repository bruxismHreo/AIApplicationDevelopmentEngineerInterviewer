# 应用开发 - LangChain进阶

> 学习时间：2026-01-29
> 理解程度：学习中

---

## 🎯 核心面试题

### Q1: Function Calling和传统Agent有什么区别？

**答案要点：**

| 特性 | 传统Agent | Function Calling |
|------|----------|-----------------|
| 工作方式 | 文本解析 | 结构化输出 |
| 可靠性 | 中等 | 高 |
| 速度 | 慢（多次循环）| 快（一次性）|
| 适用模型 | 所有模型 | GPT-4、Claude等 |

**关键区别：**
- 传统Agent：模型生成文本 → 解析文本 → 调用函数
- Function Calling：模型生成结构化数据 → 直接调用函数

---

### Q2: 如何设计一个Multi-Agent系统？

**答案要点：**

**常见模式：**

1. **层级式**：Main Agent管理多个Sub-Agent
2. **协作式**：多个Agent并行工作，共享结果
3. **竞争式**：多个Agent处理同一任务，选择最好的结果

**设计步骤：**
1. 明确任务目标
2. 拆分角色和职责
3. 定义每个Agent的工具
4. 设计Agent之间的通信机制
5. 处理Agent输出的一致性

---

### Q3: 如何调试复杂的RAG系统？

**答案要点：**

**调试方法：**
1. **LangSmith追踪**：可视化完整调用链
2. **Retriever测试**：检查检索质量
3. **Prompt测试**：验证提示词效果
4. **A/B测试**：比较不同配置

**常见问题排查：**
- 检索不到相关文档 → 调整chunk_size、top_k
- 回答不准确 → 优化提示词、增加上下文
- 速度慢 → 使用缓存、减少检索文档数

---

### Q4: 生产环境中如何保证Agent的稳定性？

**答案要点：**

**关键措施：**

1. **错误处理与重试**
   ```python
   @retry(stop=stop_after_attempt(3))
   def call_llm(prompt):
       # 带重试的调用
   ```

2. **输入验证**
   - 检查工具参数
   - 验证输入格式
   - 设置超时

3. **监控告警**
   - LangSmith追踪
   - 错误率监控
   - 性能指标

4. **降级策略**
   - Agent失败时回退到简单模式
   - 限制工具调用次数
   - 设置超时时间

---

## 📝 我的理解（费曼学习法）

**Function Calling的核心思想：**

传统Agent像"读说明书后操作"：
- 模型生成文本（说明书）
- 解析文本（理解说明书）
- 执行操作（可能理解错）

Function Calling像"直接接收指令"：
- 模型生成结构化指令
- 直接执行（不会理解错）

**Multi-Agent的核心思想：**

就像公司团队：
- 不同角色各司其职
- 主管分配任务
- 员工协作完成
- 共享工作成果

---

## 💡 面试官点评与补充

> ✅ 理解准确！

补充要点：
- **Function Calling是趋势**：GPT-4、Claude、Gemini都原生支持
- **Multi-Agent的挑战**：通信开销、一致性保证、调试困难
- **LangSmith的价值**：提供完整的可观测性，生产环境必备
- **最佳实践**：先测试单个Agent，再组合成Multi-Agent

---

## 🔑 核心知识点

### 1. Function Calling详解

**完整流程：**

```python
from langchain.tools import tool
from langchain_openai import ChatOpenAI

# 1. 定义函数（必须带类型注解和文档字符串）
@tool
def transfer_money(
    from_account: str,
    to_account: str,
    amount: float
) -> str:
    """
    转账功能

    Args:
        from_account: 转出账户
        to_account: 转入账户
        amount: 转账金额
    """
    # 实际业务逻辑
    return f"成功从 {from_account} 转账 {amount} 元到 {to_account}"

# 2. 绑定工具
llm = ChatOpenAI(model="gpt-4")
tools = [transfer_money]
llm_with_tools = llm.bind_functions(tools)

# 3. 调用
response = llm_with_tools.invoke("帮我转账100元")

# 4. 处理工具调用
if response.tool_calls:
    for tool_call in response.tool_calls:
        result = transfer_money(**tool_call['args'])
        print(f"执行：{tool_call['name']}({tool_call['args']})")
        print(f"结果：{result}")

        # 5. 将结果反馈给模型
        final_response = llm_with_tools.invoke([
            HumanMessage("帮我转账100元"),
            response,
            ToolMessage(result, tool_call_id=tool_call['id'])
        ])

        print(f"最终回答：{final_response.content}")
```

**多轮Function Calling：**

```python
def multi_turn_function_calling(user_query: str):
    messages = [HumanMessage(user_query)]

    max_turns = 5  # 最多5轮

    for turn in range(max_turns):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # 检查是否需要调用工具
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # 执行工具
            for tool_call in response.tool_calls:
                tool = next(t for t in tools if t.name == tool_call['name'])
                result = tool.func(**tool_call['args'])
                messages.append(
                    ToolMessage(result, tool_call_id=tool_call['id'])
                )
        else:
            # 没有工具调用，结束
            break

    return response.content
```

---

### 2. Multi-Agent模式详解

**模式1：层级式（Hierarchical）**

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import SystemMessage

# 1. 定义子Agent
researcher = create_openai_functions_agent(
    llm=llm,
    tools=[search_tool, wiki_tool],
    prompt=SystemMessage(content="你是研究员，负责收集资料")
)

writer = create_openai_functions_agent(
    llm=llm,
    tools=[file_tool],
    prompt=SystemMessage(content="你是写作员，负责撰写报告")
)

# 2. 定义主Agent（Router）
from langchain.agents import initialize_agent

router_tools = [
    Tool(
        name="Research",
        func=lambda x: researcher_executor.invoke({"input": x})['output'],
        description="收集资料和调研"
    ),
    Tool(
        name="Write",
        func=lambda x: writer_executor.invoke({"input": x})['output'],
        description="撰写报告"
    )
]

main_agent = initialize_agent(
    tools=router_tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# 3. 执行
result = main_agent.invoke("写一份关于量子计算的报告")
```

**模式2：协作式（Collaborative）**

```python
import asyncio
from langchain.agents import AgentExecutor

async def collaborative_agents(task: str):
    """多个Agent并行工作"""

    # 1. 并发执行多个Agent
    results = await asyncio.gather(
        researcher_executor.ainvoke({"input": f"研究：{task}"}),
        analyst_executor.ainvoke({"input": f"分析：{task}"}),
        designer_executor.ainvoke({"input": f"设计：{task}"})
    )

    # 2. 汇总结果
    combined_context = "\n\n".join([
        f"研究员：{results[0]['output']}",
        f"分析师：{results[1]['output']}",
        f"设计师：{results[2]['output']}"
    ])

    # 3. 主Agent综合
    final_result = main_agent.invoke({
        "input": f"综合以下信息：\n{combined_context}"
    })

    return final_result['output']
```

**模式3：顺序链式（Sequential）**

```python
from langchain.chains import SequentialChain

# Agent1：收集
collector_chain = LLMChain(
    llm=llm,
    prompt=collector_prompt,
    output_key="research_data"
)

# Agent2：分析
analyzer_chain = LLMChain(
    llm=llm,
    prompt=analyzer_prompt,
    output_key="analysis"
)

# Agent3：撰写
writer_chain = LLMChain(
    llm=llm,
    prompt=writer_prompt,
    output_key="report"
)

# 串联
overall_chain = SequentialChain(
    chains=[collector_chain, analyzer_chain, writer_chain],
    input_variables=["topic"],
    output_variables=["report"]
)

result = overall_chain.run(topic="量子计算")
```

---

### 3. LangSmith调试

**启用追踪：**

```python
import os
from langchain.callbacks import LangChainTracer

# 配置
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "lsv2_..."
os.environ["LANGCHAIN_PROJECT"] = "my-rag-system"

# 自动追踪所有调用
tracer = LangChainTracer()

# 使用
result = rag_chain.invoke(
    {"query": "什么是Transformer？"},
    config={"callbacks": [tracer]}
)
```

**在LangSmith中查看：**

1. 访问 https://smith.langchain.com
2. 选择项目
3. 查看Traces：完整的调用链
4. 分析性能、成本、错误

**评估RAG系统质量：**

```python
from langsmith import Client
from langchain.evaluation import Evaluator

client = Client()

# 定义评估集
examples = [
    {
        "input": "什么是Transformer？",
        "output": "Transformer是一个深度学习模型架构..."
    },
    {
        "input": "BERT和GPT的区别？",
        "output": "BERT是双向理解，GPT是单向生成..."
    }
]

# 运行评估
evaluator = EEvaluator()
results = client.evaluate(
    rag_chain.invoke,
    examples,
    evaluators=[evaluator]
)

# 查看结果
for result in results:
    print(f"输入：{result.input}")
    print(f"输出：{result.output}")
    print(f"分数：{result.score}")
```

---

### 4. 生产环境最佳实践

**完整的生产级RAG系统：**

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.callbacks import (
    get_openai_callback,
    StreamingStdOutCallbackHandler
)
from tenacity import retry, stop_after_attempt
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionRAGSystem:
    def __init__(self, persist_directory: str):
        # 初始化组件
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            streaming=True
        )

        # 创建检索器
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.7  # 只返回相关性高的文档
            }
        )

        # 创建RAG链
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def query(self, question: str, stream: bool = False):
        """
        查询RAG系统

        Args:
            question: 用户问题
            stream: 是否流式输出

        Returns:
            回答结果
        """
        try:
            # 记录Token使用
            with get_openai_callback() as cb:
                if stream:
                    # 流式输出
                    for chunk in self.chain.stream(
                        {"query": question},
                        callbacks=[StreamingStdOutCallbackHandler()]
                    ):
                        yield chunk
                else:
                    # 普通输出
                    result = self.chain({"query": question})

                    logger.info(f"Token使用：{cb.total_tokens}")
                    logger.info(f"成本：${cb.total_cost}")
                    logger.info(f"参考文档：{len(result['source_documents'])}个")

                    return result["result"]

        except Exception as e:
            logger.error(f"查询失败：{e}")
            # 降级：返回基础回答
            return "抱歉，我暂时无法回答这个问题。"

# 使用
rag = ProductionRAGSystem("./chroma_db")
answer = rag.query("什么是Transformer？")
```

---

## 📌 重点记录

### 面试高频考点：

1. **Function Calling vs 传统Agent**
   - Function Calling：模型直接生成结构化函数调用
   - 传统Agent：模型生成文本，需要解析
   - Function Calling更可靠、更快速

2. **Multi-Agent设计原则**
   - 明确角色分工
   - 设计通信机制
   - 处理一致性
   - 考虑性能（并发 vs 串行）

3. **RAG系统调试**
   - 使用LangSmith追踪
   - 检查检索质量
   - 验证提示词效果
   - A/B测试不同配置

4. **生产环境稳定性**
   - 错误重试机制
   - 输入验证
   - 超时控制
   - 监控告警
   - 降级策略

### 常见误区：

❌ 误区1：Function Calling可以用在所有模型
✅ 正解：只有GPT-4、Claude等特定模型支持

❌ 误区2：Multi-Agent一定比单Agent好
✅ 正解：复杂任务才需要，简单任务单Agent更高效

❌ 误区3：RAG系统不需要监控
✅ 正解：生产环境必须监控，LangSmith提供完整可观测性

❌ 误区4：生产环境和开发环境配置一样
✅ 正解：生产环境需要重试、降级、监控等机制

### 实战建议：

**场景1：客户服务系统**
- Function Calling：调用订单查询、退款API
- Multi-Agent：路由、客服、技术支持
- 监控：LangSmith追踪所有对话

**场景2：代码助手**
- Function Calling：执行代码、文件操作
- 工具验证：沙箱环境执行代码
- 错误处理：代码执行失败时的降级

**场景3：研究报告生成**
- Multi-Agent：研究员、分析师、写作员
- 并行执行：提高效率
- 质量控制：审稿员Agent

---

## 🔄 复习检查清单

- [x] 理解Function Calling的原理
- [x] 掌握Function Calling的实现
- [ ] 了解不同的Multi-Agent模式
- [ ] 能设计一个Multi-Agent系统
- [ ] 了解LangSmith的使用方法
- [ ] 掌握生产环境的最佳实践
- [ ] 能实现一个生产级的RAG系统

---

## 📚 延伸阅读

- [OpenAI Function Calling文档](https://platform.openai.com/docs/guides/function-calling)
- [LangSmith文档](https://docs.smith.langchain.com/)
- [LangGraph - Multi-Agent框架](https://github.com/langchain-ai/langgraph)
- [Tenacity - 重试库](https://github.com/jd/tenacity)
