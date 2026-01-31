from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os
import shutil

# Load environment variables from a .env file
load_dotenv()

print("=" * 60)
print("创建 4096 维向量数据库")
print("=" * 60)

# 加载文档
print("\n1. 加载文档...")
loader = TextLoader("./data/agency.txt")
docs = loader.load()

doc_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
doc_chunks = doc_splitter.split_documents(docs)
print(f"   文档块数量: {len(doc_chunks)}")

# 配置嵌入模型（4096维）
api_key = os.getenv("SILICONFLOW_API_KEY")
if not api_key:
    print("❌ 错误: 未找到 SILICONFLOW_API_KEY 环境变量！")
    exit(1)

# 使用 4096 维的模型
# 常见 4096 维模型：Qwen/Qwen3-Embedding-8B
embedding_model = "Qwen/Qwen3-Embedding-8B"
print(f"\n2. 使用嵌入模型: {embedding_model}")

try:
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        openai_api_key=api_key,
        openai_api_base="https://api.siliconflow.cn/v1"
    )

    # 测试维度
    print("   测试嵌入API...")
    test_vector = embeddings.embed_query("测试")
    actual_dim = len(test_vector)
    print(f"   ✅ API测试成功！向量维度: {actual_dim}")
    
    if actual_dim != 4096:
        print(f"   ⚠️  警告: 模型实际维度为 {actual_dim}，不是预期的 4096")
        print(f"   将使用实际维度创建数据库目录: db_{actual_dim}")

    # 创建数据库
    db_path = f"db_{actual_dim}" if actual_dim != 4096 else "db_4096"
    print(f"\n3. 创建向量数据库到: {db_path}")
    
    if os.path.exists(db_path):
        print(f"   删除旧的 {db_path} 目录...")
        try:
            shutil.rmtree(db_path)
            print(f"   ✅ 旧目录已删除")
        except Exception as e:
            print(f"   ⚠️  删除失败: {e}，继续尝试...")
    
    print("   正在向量化文档（可能需要1-2分钟，请耐心等待）...")
    import time
    start_time = time.time()
    
    vectorstore = Chroma.from_documents(
        documents=doc_chunks,
        embedding=embeddings,
        persist_directory=db_path,
        collection_name="langchain"
    )
    
    elapsed = time.time() - start_time
    print(f"   ✅ 向量数据库创建成功！耗时: {elapsed:.1f}秒")
    print(f"\n✅ 完成！数据库路径: {db_path}")
    print(f"   维度: {actual_dim}")
    print(f"   模型: {embedding_model}")
    
except Exception as e:
    print(f"\n❌ 创建失败: {e}")
    print(f"   请检查:")
    print(f"   1. API密钥是否正确")
    print(f"   2. 模型名称是否正确")
    print(f"   3. 网络连接是否正常")
    exit(1)

