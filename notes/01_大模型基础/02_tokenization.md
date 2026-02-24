# 大模型基础 - Tokenization（分词）

> 学习时间：2026-01-28
> 理解程度：学习中

---

## 🎯 核心面试题

### Q1: 什么是Subword Tokenization？为什么要用它？

**答案要点：**
- Subword是介于字符和词之间的文本单位
- 三大优势：解决生僻词OOV问题、词表大小可控（5万-10万）、支持多语言
- 任何词都可以拆成子词，即使没见过也能处理

---

### Q2: BPE算法的原理是什么？

**答案要点：**
1. 初始化：把所有词拆成字符
2. 统计：找出最常见的字符对
3. 合并：把最常见的字符对合并成新的子词
4. 迭代：重复2-3步，直到词表达到目标大小
5. 编码：用学习到的词表对新文本进行编码

**示例：**
```
原始：hug, pug, pun, bun
初始：h u g, p u g, p u n, b u n
合并1：pu（u和p最常连用）
合并2：un（u和n最常连用）
...
```

---

### Q3: 词级、字符级、子词级Tokenization的对比？

**答案要点：**

| 类型 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **词级** | 语义完整 | 词表大、OOV问题 | 早期NLP |
| **字符级** | 词表极小、无OOV | 序列长、语义碎片 | 中文等 |
| **子词级** | 平衡词表和语义 | 序列略长 | 现代大模型（GPT、BERT）|

---

## 📝 我的理解（费曼学习法）

**Subword的核心思想：**

把词拆成"有意义的片段"，就像拼乐高：
- 每个积木（子词）可以单独使用
- 也可以组合成复杂的结构（生僻词）
- 积木种类（词表）是有限的，但能拼出无限可能

**BPE算法类比：**

就像统计汉字使用频率：
1. 先统计：哪些字经常连在一起（如"人工"、"智能"）
2. 把常连的字合并成词
3. 重复这个过程，得到一个词表

---

## 💡 面试官点评与补充

> ✅ 理解准确！

补充点：
- **三种主流算法**：BPE（GPT）、WordPiece（BERT）、Unigram LM（T5）
- **Tokenization对性能的影响**：序列越长，注意力计算量越大（O(n²)）
- **中英文差异**：中文通常需要更多token，这就是为什么中文处理更贵

---

## 🔑 核心知识点

### 1. 为什么需要Subword？

**问题场景A：OOV（Out of Vocabulary）**
```
词级分词：生僻词 → [UNK] → 无法理解
子词分词：生僻词 → 拆成已知子词 → 能理解部分含义
```

**问题场景B：词表爆炸**
```
英文形态变化：run, runs, running, runner, ...
词级：需要存储所有变化 → 词表百万级
子词：["run", "##s", "##ning", "##ner"] → 词表可控
```

**问题场景C：多语言支持**
```
Subword算法是语言无关的，同一套算法可以处理：
- 中文
- 英文
- 代码
- 甚至emoji
```

### 2. BPE算法详解

**完整流程：**

```python
# 伪代码
def train_bpe(corpus, vocab_size):
    # 初始化：字符级词表
    vocab = set(char for word in corpus for char in word)

    # 初始化单词表示
    word_splits = {word: list(word) for word in corpus}

    while len(vocab) < vocab_size:
        # 统计最频繁的字符对
        pair = get_most_frequent_pair(word_splits)

        # 合并字符对
        word_splits = merge_pair(word_splits, pair)

        # 添加到词表
        vocab.add(''.join(pair))

    return vocab
```

**实际例子：**

```
语料：("hug", 10), ("pug", 5), ("pun", 12), ("bun", 4)

第1轮：
  统计：(u,g)=15, (p,u)=17, (u,n)=16
  合并：pu
  词表：{h,u,g,p,b,n,pu}

第2轮：
  统计：(u,n)=16, (pu,g)=5, (pu,n)=12
  合并：un
  词表：{h,u,g,p,b,n,pu,un}

第3轮：
  统计：(pu,n)=12, (b,un)=4, (h,u)=10
  合并：pun
  词表：{h,u,g,p,b,n,pu,un,pun}
...
```

### 3. 三种Subword算法对比

| 算法 | 代表模型 | 核心思想 | 优点 |
|------|---------|---------|------|
| **BPE** | GPT, RoBERTa | 从下往上合并字符 | 简单高效 |
| **WordPiece** | BERT | 选择最大化语言模型得分的合并 | 考虑上下文 |
| **Unigram LM** | T5, ALBERT | 从上往下，删除低频子词 | 更精细 |

### 4. 特殊Token

**BERT的特殊tokens：**
```
[CLS] - 句子开始，用于分类任务
[SEP] - 句子分隔符
[PAD] - 填充符，用于batch对齐
[UNK] - 未知字符（很少用到）
[MASK] - 掩码符，用于MLM预训练
```

**GPT的特殊tokens：**
```
<|endoftext|> - 文本结束符
<|startoftranscript|> - 转录开始（ Whisper ）
```

---

## 📌 重点记录

### 面试高频考点：

1. **为什么ChatGPT按token收费而不是按字？**
   - 不同语言的token密度不同（中文约1.5-2字/token，英文约4字符/token）
   - 模型内部处理的是token，不是字符

2. **Tokenization对推理性能的影响**
   - 序列越长 → 注意力计算量越大（O(n²)）
   - 优化方向：更好的tokenizer、序列压缩、flash attention

3. **中文分词的特殊性**
   - 英文有天然空格分隔，中文没有
   - 中文常用分词器：Byte-level BPE（字节级，避免特殊字符问题）

4. **代码Tokenization**
   - 代码有结构：缩进、括号匹配
   - GPT的tokenizer专门针对代码优化
   - 例如：`def`是一个token，`class`是一个token

### 常见误区：

❌ 误区1：Tokenization只是预处理，不影响模型性能
✅ 正解：Tokenization直接影响序列长度、词表大小、OOV率

❌ 误区2：中英文的token数量差不多
✅ 正解：中文通常需要更多token（约1.5-2倍）

❌ 误区3：BERT和GPT用一样的tokenizer
✅ 正解：算法类似但训练数据不同，GPT支持更多语言和代码

---

## 🔄 复习检查清单

- [x] 理解Subword的概念和优势
- [x] 掌握BPE算法的流程
- [x] 知道三种Tokenization级别的区别
- [ ] 了解WordPiece和Unigram LM的原理
- [ ] 能解释为什么中文token更贵
- [ ] 了解特殊Token的作用

---

## 📚 延伸阅读

- [SentencePiece](https://github.com/google/sentencepiece) - Google的tokenizer工具
- [tiktoken](https://github.com/openai/tiktoken) - OpenAI的tokenizer
- [HuggingFace Tokenizers](https://github.com/huggingface/tokenizers) - 高性能tokenizer库
