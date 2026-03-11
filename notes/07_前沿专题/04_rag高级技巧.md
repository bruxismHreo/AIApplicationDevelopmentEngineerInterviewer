# 前沿专题 - RAG 高级技巧

> 学习时间：2026-03-11
> 理解程度：学习中

---

## 🎯 核心面试题

### Q1: 什么是 GraphRAG？它与传统 RAG 有什么区别？

**答案要点：**
- GraphRAG：知识图谱 + RAG 结合
- 传统 RAG：基于向量相似度的扁平检索
- GraphRAG：利用实体关系图谱进行多跳推理
- 优势：处理复杂关系查询、提高推理深度
- 实现：LLM 提取实体和关系 → 构建图谱 → 图谱检索

---

### Q2: 什么是 Agentic RAG？

**答案要点：**
- Agent 驱动的动态检索策略
- 不是固定检索流程，而是根据查询动态决定检索策略
- Agent 可以：多轮检索、重写查询、选择不同数据源
- 实现：使用 ReAct 或 LangGraph 构建
- 场景：复杂查询、需要多步推理的问题

---

### Q3: Hybrid Search（混合检索）如何实现？

**答案要点：**
- 结合向量检索和全文检索（BM25）
- 向量检索：捕捉语义相似度
- 全文检索：精确匹配关键词
- 结果融合：Reciprocal Rank Fusion (RRF) 或加权平均
- 实现：Qdrant、Weaviate 等支持混合检索

---

### Q4: 什么是 Query Transformation？有哪些常用技术？

**答案要点：**
- Query Rewriting：重写查询使其更清晰
- Query Expansion：扩展查询添加相关词
- Query Decomposition：将复杂查询拆解为多个子查询
- HyDE：生成假设性答案用于检索
- 目的：提高检索召回率和准确率

---

### Q5: 如何处理多跳问题（Multi-hop Question）？

**答案要点：**
- 多跳问题：需要多次检索和推理
- 方法 1：Agent 驱动的迭代检索
- 方法 2：GraphRAG 利用关系图谱
- 方法 3：Query Decomposition 分步处理
- 示例："A 公司的 CEO 的母校在哪里？"（需要先查 CEO，再查母校）

---

## 📝 我的理解（费曼学习法）

**[请用自己的话简单解释 RAG 高级技巧的核心概念]**

---

## 💡 面试官点评与补充

> RAG 高级技巧的核心是"理解查询意图"和"智能检索决策"。面试官会考察你能否根据不同场景选择合适的检索策略。

> 技巧选择决策树：
> - 简单事实查询 → 向量检索 + Rerank
> - 复杂关系查询 → GraphRAG
> - 不确定的查询意图 → Agentic RAG
> - 关键词重要 → Hybrid Search
> - 查询不清晰 → Query Transformation

---

## 🔑 核心知识点

### GraphRAG 详解

**原理：**
```
传统 RAG：
Query → Embedding → 向量检索 → 相关文档 → 答案

GraphRAG：
文档 → LLM 提取实体和关系 → 知识图谱
Query → 提取实体 → 图谱遍历 → 多跳推理 → 相关实体和文档 → 答案
```

**实现流程：**
```python
# 1. 构建知识图谱
from langchain.graphs import KnowledgeGraph
from langchain.chains import GraphQAChain

# 提取实体和关系
def extract_entities_and_relations(text):
    prompt = f"""
    从以下文本中提取实体和关系：
    {text}

    返回格式：[(实体1, 关系, 实体2), ...]
    """
    return llm.predict(prompt)

# 构建图谱
kg = KnowledgeGraph()
for doc in documents:
    entities_relations = extract_entities_and_relations(doc)
    kg.add_entities_and_relations(entities_relations)

# 2. 图谱检索
def graph_retrieval(query, kg):
    # 提取查询中的实体
    query_entities = extract_entities(query)

    # 图谱遍历
    relevant_entities = []
    for entity in query_entities:
        # 多跳推理
        neighbors = kg.get_neighbors(entity, depth=2)
        relevant_entities.extend(neighbors)

    return relevant_entities

# 3. 结合向量检索
def hybrid_retrieval(query):
    # 向量检索
    vector_results = vector_store.search(query, top_k=5)

    # 图谱检索
    graph_results = graph_retrieval(query, kg)

    # 合并结果
    return merge_and_rerank(vector_results, graph_results)
```

**优势：**
- 处理复杂关系查询
- 多跳推理能力
- 可解释性强（可以看到推理路径）

**挑战：**
- 图谱构建成本高
- 图谱维护复杂
- 需要高质量的实体关系提取

### Agentic RAG 详解

**核心思想：**
```python
# 传统 RAG：固定流程
query → vector_search → llm_generate → answer

# Agentic RAG：动态决策
query → agent_think → maybe_search → maybe_rewrite → ...
                  → maybe_multi_search → llm_generate → answer
```

**实现示例（LangGraph）：**
```python
from langgraph.graph import StateGraph

class RAGState(TypedDict):
    query: str
    context: List[str]
    answer: str
    need_search: bool
    search_count: int

def should_search(state: RAGState):
    # Agent 决定是否需要检索
    prompt = f"""
    查询：{state['query']}
    已有上下文：{state['context']}

    是否需要额外检索？
    """
    decision = llm.predict(prompt)
    return "yes" in decision.lower()

def search_node(state: RAGState):
    # 执行检索
    results = vector_store.search(state['query'], top_k=3)
    state['context'].extend(results)
    state['search_count'] += 1
    return state

def generate_node(state: RAGState):
    # 生成答案
    prompt = f"""
    上下文：{state['context']}
    问题：{state['query']}

    请回答问题：
    """
    state['answer'] = llm.predict(prompt)
    return state

# 构建图
graph = StateGraph(RAGState)
graph.add_node("search", search_node)
graph.add_node("generate", generate_node)
graph.add_conditional_edges(
    "search",
    should_search,
    {"yes": "search", "no": "generate"}
)

# 最多检索 3 次
def max_search_check(state: RAGState):
    if state['search_count'] >= 3:
        return "generate"
    return "search"
```

### Hybrid Search（混合检索）

**原理：**
```
向量检索：基于语义相似度
Query Embedding: [0.1, 0.5, 0.3, ...]
Doc Embedding:  [0.2, 0.4, 0.3, ...]
Similarity = Cosine(query, doc)

全文检索（BM25）：基于关键词匹配
Score = Σ IDF(qi) × f(qi, D) × (k1 + 1) / (f(qi, D) + k1)

融合：
Final Score = α × VectorScore + (1-α) × BM25Score
```

**实现示例（Qdrant）：**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import SearchRequest, Filter

client = QdrantClient(url="localhost:6333")

def hybrid_search(query, alpha=0.7):
    # 向量检索
    vector_results = client.search(
        collection_name="docs",
        query_vector=embedding_model.encode(query),
        limit=10
    )

    # 全文检索
    bm25_results = client.search(
        collection_name="docs",
        query_text=query,  # 需要 Qdrant 支持全文检索
        limit=10
    )

    # 融合结果（RRF）
    def rrf(results1, results2, k=60):
        scores = {}
        for rank, hit in enumerate(results1):
            scores[hit.id] = scores.get(hit.id, 0) + 1 / (k + rank + 1)
        for rank, hit in enumerate(results2):
            scores[hit.id] = scores.get(hit.id, 0) + 1 / (k + rank + 1)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return rrf(vector_results, bm25_results)
```

**参数调优：**
- `alpha`：向量检索权重（0-1）
- 根据数据特点调整：
  - 关键词重要的场景：降低 alpha
  - 语义理解重要的场景：提高 alpha

### Query Transformation 技术

**1. Query Rewriting（查询重写）：**
```python
def rewrite_query(query):
    prompt = f"""
    重写以下查询，使其更清晰、更完整：
    原查询：{query}

    重写后的查询：
    """
    return llm.predict(prompt)

# 示例
# 原查询："怎么弄？"
# 重写："如何使用 Python 读取 CSV 文件？"
```

**2. Query Expansion（查询扩展）：**
```python
def expand_query(query):
    prompt = f"""
    为以下查询生成 3 个相关的查询变体：
    原查询：{query}

    相关查询：
    """
    expansions = llm.predict(prompt).split('\n')
    return [query] + expansions

# 然后对所有查询进行检索，合并结果
```

**3. Query Decomposition（查询分解）：**
```python
def decompose_query(query):
    prompt = f"""
    将以下复杂查询分解为多个简单子查询：
    原查询：{query}

    子查询：
    """
    sub_queries = llm.predict(prompt).split('\n')
    return sub_queries

# 示例
# 原查询："比较 Python 和 JavaScript 在机器学习方面的优缺点"
# 子查询：
# 1. "Python 机器学习的优势"
# 2. "Python 机器学习的劣势"
# 3. "JavaScript 机器学习的优势"
# 4. "JavaScript 机器学习的劣势"
```

**4. HyDE（Hypothetical Document Embeddings）：**
```python
def hyde_search(query):
    # 生成假设性答案
    prompt = f"""
    问题：{query}

    请生成一个详细的答案（即使是假设的）：
    """
    hypothetical_answer = llm.predict(prompt)

    # 使用假设性答案的 embedding 进行检索
    hypothetical_embedding = embedding_model.encode(hypothetical_answer)
    results = vector_store.search(hypothetical_embedding, top_k=5)

    return results

# 原理：假设性答案与真实答案在语义空间更接近
```

### Advanced Chunking（高级切片）

**语义切片：**
```python
def semantic_chunking(text, max_chunk_size=500):
    # 按句子分割
    sentences = text.split('.')

    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)

        # 检查语义完整性
        if is_semantically_complete(current_chunk):
            chunks.append('.'.join(current_chunk))
            current_chunk = []

        # 检查大小限制
        elif len('.'.join(current_chunk)) > max_chunk_size:
            chunks.append('.'.join(current_chunk))
            current_chunk = []

    return chunks

def is_semantically_complete(sentences):
    # 检查是否包含完整的思想
    # 可以使用句子数量、标点符号等
    return len(sentences) >= 3
```

**父子文档：**
```python
# 父文档：大块内容（用于生成答案）
# 子文档：小块内容（用于检索）

def parent_child_chunking(documents, child_size=100, parent_size=500):
    parent_chunks = []
    child_chunks = []

    for doc in documents:
        # 创建父文档
        parent_chunks.append({
            "content": doc,
            "size": len(doc)
        })

        # 创建子文档
        child_chunks.extend([
            {"content": doc[i:i+child_size], "parent_id": idx}
            for idx in range(len(parent_chunks)-1, len(parent_chunks))
            for i in range(0, len(doc), child_size)
        ])

    return parent_chunks, child_chunks

# 检索时：先检索子文档，再返回对应的父文档
```

---

## 📚 延伸阅读

- **论文**：GraphRAG: Knowledge Graph-Enhanced RAG
- **论文**：Hypothetical Document Embeddings (HyDE)
- **资源**：Microsoft GraphRAG GitHub
- **资源**：LlamaIndex Advanced RAG Techniques
- **资源**：LangChain Agentic RAG 文档

---

## 🔄 复习检查清单

- [ ] 理解 GraphRAG 的原理和实现
- [ ] 掌握 Agentic RAG 的动态检索策略
- [ ] 了解 Hybrid Search 的融合方法
- [ ] 掌握 Query Transformation 的四种技术
- [ ] 理解 Advanced Chunking 策略
- [ ] 能够处理多跳问题

---

## 📌 重点记录

### 面试高频考点：
- GraphRAG：知识图谱 + RAG，处理复杂关系查询
- Agentic RAG：Agent 驱动，动态检索决策
- Hybrid Search：向量 + 全文检索，RRF 融合
- Query Transformation：Rewriting、Expansion、Decomposition、HyDE
- 多跳问题：分步检索、图谱遍历、Agent 迭代

### 常见误区：
- 认为 GraphRAG 一定优于传统 RAG（视场景而定）
- 忽视 Query Transformation 的成本（需要额外的 LLM 调用）
- 过度依赖向量检索（关键词场景 Hybrid Search 更好）
- 忽视切片策略对检索效果的影响

### 工程实践要点：
- 简单场景优先使用传统 RAG + Rerank
- 复杂关系查询考虑 GraphRAG
- 不确定查询意图使用 Agentic RAG
- 关键词重要的场景使用 Hybrid Search
- 查询不清晰时使用 Query Transformation
- 切片策略需要根据数据特点定制
