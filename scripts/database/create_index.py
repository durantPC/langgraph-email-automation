from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

RAG_SEARCH_PROMPT_TEMPLATE = """
Using the following pieces of retrieved context, answer the question comprehensively and concisely.
Ensure your response fully addresses the question based on the given context.

**IMPORTANT:**
Just provide the answer and never mention or refer to having access to the external context or information in your answer.
If you are unable to determine the answer from the provided context, state 'I don't know.'

Question: {question}
Context: {context}
"""

print("Loading & Chunking Docs...")
loader = TextLoader("./data/agency.txt")
docs = loader.load()

doc_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
doc_chunks = doc_splitter.split_documents(docs)

print("Creating vector embeddings...")

api_key = os.getenv("SILICONFLOW_API_KEY")
if not api_key:
    print("⚠️  错误: 未找到 SILICONFLOW_API_KEY 环境变量！")
    exit(1)

print(f"使用API密钥: {api_key[:10]}...")
print("尝试使用嵌入模型: Qwen/Qwen3-Embedding-8B")

try:
    embeddings = OpenAIEmbeddings(
        model="Qwen/Qwen3-Embedding-8B",
        openai_api_key=api_key,
        openai_api_base="https://api.siliconflow.cn/v1"
    )

    # 先测试单个文本嵌入
    print("测试嵌入API...")
    test_vector = embeddings.embed_query("测试文本")
    print(f"✅ API测试成功！向量维度: {len(test_vector)}")

    print(f"\n文档块数量: {len(doc_chunks)}")
    print("正在向量化文档（可能需要1-2分钟，请耐心等待）...")
    
    import time
    start_time = time.time()
    
    try:
        print("开始批量向量化...")
        
        # 先删除旧的数据库（避免锁定问题）
        import shutil
        if os.path.exists("db"):
            print("删除旧的数据库...")
            try:
                shutil.rmtree("db")
                print("✅ 旧数据库已删除")
            except Exception as e:
                print(f"⚠️  删除旧数据库失败: {e}，继续尝试...")
        
        print("正在创建向量数据库（使用 LangChain 标准方式）...")
        print("提示：这可能需要1-2分钟，请耐心等待...\n")
        
        # 使用 LangChain 的标准方式
        vectorstore = Chroma.from_documents(
            documents=doc_chunks,
            embedding=embeddings,
            persist_directory="db",
            collection_name="langchain"
        )
        elapsed = time.time() - start_time
        print(f"✅ 向量数据库创建成功！耗时: {elapsed:.1f}秒")
    except Exception as batch_error:
        print(f"\n⚠️  批量向量化失败: {batch_error}")
        print(f"错误类型: {type(batch_error).__name__}")
        print("尝试逐个处理文档...")
        
        try:
            # 逐个添加文档
            vectorstore = Chroma(persist_directory="db", embedding_function=embeddings)
            for i, doc in enumerate(doc_chunks, 1):
                print(f"处理文档块 {i}/{len(doc_chunks)}...", end='\r')
                try:
                    vectorstore.add_documents([doc])
                except Exception as doc_error:
                    print(f"\n文档块 {i} 处理失败: {doc_error}")
                    continue
            print(f"\n✅ 向量数据库创建成功！")
        except Exception as sequential_error:
            print(f"\n❌ 逐个处理也失败: {sequential_error}")
            raise
        
except Exception as e:
    print(f"\n❌ 使用硅基流动嵌入模型失败: {e}")
    print("\n切换到本地嵌入模型（推荐）...")
    print("正在下载并加载本地模型，首次运行需要下载约400MB...")
    
    from langchain_community.embeddings import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    print("正在使用本地模型向量化文档...")
    vectorstore = Chroma.from_documents(doc_chunks, embeddings, persist_directory="db")
    print("✅ 使用本地嵌入模型创建向量数据库成功！")
    print("注意：主程序也会自动使用本地嵌入模型")

# Semantic vector search
vectorstore_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Test RAG chain
print("Test RAG chain...")

# 检查API密钥
api_key = os.getenv("SILICONFLOW_API_KEY")
if not api_key:
    print("⚠️  警告: 未找到 SILICONFLOW_API_KEY 环境变量！")
    print("   向量数据库已创建，但跳过RAG测试。")
    print("   请在 .env 文件中配置 SILICONFLOW_API_KEY")
else:
    try:
        prompt = ChatPromptTemplate.from_template(RAG_SEARCH_PROMPT_TEMPLATE)
        llm = ChatOpenAI(
            model="Qwen/Qwen3-VL-32B-Instruct",  # 使用Qwen3-VL-32B模型
            temperature=0.1,
            openai_api_key=api_key,
            openai_api_base="https://api.siliconflow.cn/v1"
        )

        rag_chain = (
            {"context": vectorstore_retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        query = "What are your pricing options?"
        print(f"Question: {query}")
        print("正在调用API生成回答...")
        result = rag_chain.invoke(query)
        print(f"Answer: {result}")
        print("\n✅ RAG测试成功！")
    except Exception as e:
        print(f"\n⚠️  RAG测试失败: {e}")
        print("   向量数据库已创建成功，但API调用出错。")
        print("   请检查:")
        print("   1. SILICONFLOW_API_KEY 是否正确")
        print("   2. 账户是否有可用额度")
        print("   3. 网络连接是否正常")

