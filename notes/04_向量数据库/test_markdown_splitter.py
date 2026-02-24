#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown文档6级标题切分测试Demo

测试向量数据库文档切分策略中支持6级标题的功能
"""

from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.schema import Document
import json


def test_markdown_splitter():
    """测试Markdown 6级标题切分功能"""

    # 测试文档（包含完整的6级标题层级）
    md_document = """
# 第一章 AI应用开发工程师面试指南

本章介绍AI应用开发工程师面试的准备工作。

## 1.1 学习方向

### 1.1.1 大模型基础

大模型基础是面试的重要内容。

#### 1.1.1.1 Transformer架构

Transformer是现代大模型的基础架构。

##### 1.1.1.1.1 注意力机制

注意力机制是Transformer的核心。

###### 1.1.1.1.1.1 自注意力

自注意力机制让模型能够理解上下文关系。

这里详细解释自注意力的原理和实现...

## 1.2 应用开发

应用开发是实践能力的体现。

### 1.2.1 LangChain框架

LangChain是应用开发的重要框架。

#### 1.2.1.1 Agent开发

Agent开发是高级应用开发技能。

这里介绍Agent开发的最佳实践...

## 1.3 Prompt工程

Prompt工程是优化AI模型效果的关键。

### 1.3.1 CoT技巧

思维链技巧能够提升复杂推理能力。

这里详细说明CoT的使用场景...

# 第二章 向量数据库

向量数据库是RAG系统的核心组件。

## 2.1 Embedding基础

Embedding将文本转换为向量表示。

### 2.1.1 余弦相似度

余弦相似度用于衡量向量之间的相似程度。

这里介绍余弦相似度的计算方法...

## 2.2 索引方法

索引方法决定了向量检索的性能。

### 2.2.1 HNSW索引

HNSW是最流行的向量索引方法。

#### 2.2.1.1 图结构原理

HNSW基于分层图结构实现高效检索。

这里详细说明HNSW的图结构原理...
"""

    print("=" * 80)
    print("Markdown文档6级标题切分测试")
    print("=" * 80)

    # 创建支持6级标题的切分器
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),      # H1 标题
            ("##", "Header 2"),     # H2 标题
            ("###", "Header 3"),    # H3 标题
            ("####", "Header 4"),   # H4 标题
            ("#####", "Header 5"),  # H5 标题
            ("######", "Header 6"), # H6 标题
        ]
    )

    # 执行切分
    print("\n📄 开始切分文档...\n")
    docs = markdown_splitter.split_text(md_document)

    # 输出切分结果
    print(f"✅ 切分完成！共生成 {len(docs)} 个chunk\n")
    print("=" * 80)

    for i, doc in enumerate(docs, 1):
        print(f"\n{'='*80}")
        print(f"Chunk {i}:")
        print(f"{'='*80}")

        # 显示元数据
        print("\n🏷️  元数据（标题层级）:")
        if doc.metadata:
            for level in range(1, 7):
                header_key = f"Header {level}"
                if header_key in doc.metadata:
                    print(f"  {header_key}: {doc.metadata[header_key]}")
        else:
            print("  (无标题层级)")

        # 显示内容预览
        content = doc.page_content
        print(f"\n📝 内容预览（前150字符）:")
        print(f"  {content[:150]}...")

        # 显示统计信息
        print(f"\n📊 统计信息:")
        print(f"  总字符数: {len(content)}")
        print(f"  总行数: {content.count(chr(10))}")
        print(f"  标题层级深度: {len(doc.metadata)}")

    print(f"\n{'='*80}")
    print("切分结果汇总")
    print(f"{'='*80}")

    # 统计各层级深度
    depth_distribution = {}
    for doc in docs:
        depth = len(doc.metadata)
        depth_distribution[depth] = depth_distribution.get(depth, 0) + 1

    print("\n📊 标题层级深度分布:")
    for depth in sorted(depth_distribution.keys()):
        count = depth_distribution[depth]
        bar = "█" * count
        print(f"  {depth}级标题: {count:2d}个chunk {bar}")

    # 保存结果到文件
    output_data = {
        "total_chunks": len(docs),
        "depth_distribution": depth_distribution,
        "chunks": [
            {
                "chunk_id": i,
                "metadata": doc.metadata,
                "content_length": len(doc.page_content),
                "content_preview": doc.page_content[:200]
            }
            for i, doc in enumerate(docs, 1)
        ]
    }

    output_file = "markdown_split_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 结果已保存到: {output_file}")
    print("=" * 80)


def test_with_file(file_path: str):
    """从文件读取Markdown并测试切分"""
    print(f"\n📂 从文件读取: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 创建切分器
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "H1"),
                ("##", "H2"),
                ("###", "H3"),
                ("####", "H4"),
                ("#####", "H5"),
                ("######", "H6"),
            ]
        )

        # 切分文档
        docs = markdown_splitter.split_text(md_content)

        print(f"✅ 切分完成！共 {len(docs)} 个chunk\n")

        # 显示前3个chunk的结果
        for i, doc in enumerate(docs[:3], 1):
            print(f"\n--- Chunk {i} ---")
            print(f"元数据: {doc.metadata}")
            print(f"内容长度: {len(doc.page_content)} 字符")
            print(f"内容预览:\n{doc.page_content[:200]}...")

        if len(docs) > 3:
            print(f"\n... 还有 {len(docs) - 3} 个chunk")

    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 {file_path}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def demo_rag_usage():
    """演示在RAG系统中如何使用"""
    print("\n" + "="*80)
    print("RAG系统使用示例")
    print("="*80)

    code_example = '''
# 在RAG系统中使用Markdown标题切分
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# 1. 切分Markdown文档
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "H1"),
        ("##", "H2"),
        ("###", "H3"),
        ("####", "H4"),
        ("#####", "H5"),
        ("######", "H6"),
    ]
)

with open("docs/intro.md", "r", encoding="utf-8") as f:
    md_content = f.read()

docs = splitter.split_text(md_content)

# 2. 向量化并存储到向量数据库
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="markdown_docs"
)

# 3. 检索示例（带标题过滤）
query = "Transformer的注意力机制是如何工作的？"
results = vectorstore.similarity_search(query, k=3)

# 4. 输出结果（包含标题路径）
for i, doc in enumerate(results, 1):
    print(f"\\n结果 {i}:")
    print(f"  标题路径: {doc.metadata}")
    print(f"  内容: {doc.page_content[:100]}...")
'''

    print("\n💡 代码示例:")
    print(code_example)
    print("="*80)


if __name__ == "__main__":
    # 运行测试
    test_markdown_splitter()

    # 演示RAG系统使用
    demo_rag_usage()

    # 如果有测试文件，可以取消注释下面的代码
    # test_with_file("test.md")

    print("\n✅ 测试完成！")
    print("\n💡 使用提示:")
    print("   1. 修改 md_document 变量测试不同文档结构")
    print("   2. 使用 test_with_file('your_file.md') 测试真实文档")
    print("   3. 查看生成的 markdown_split_result.json 了解详细切分结果")
