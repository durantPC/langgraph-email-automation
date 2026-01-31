"""
知识库索引构建模块
支持自动构建和重建向量索引
"""
import os
import shutil
from typing import List, Optional
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置常量
DATA_DIR = os.getenv("KNOWLEDGE_DATA_DIR", "data")  # 知识库文档目录
ALLOWED_EXTENSIONS = ['.txt', '.md']  # 支持的文档格式（目前只支持文本文件）

def get_data_dir() -> str:
    """获取数据目录路径"""
    return DATA_DIR

def get_db_path(embedding_model: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """
    根据嵌入模型自动确定数据库路径
    
    @param embedding_model: 嵌入模型名称（如果为None，则从环境变量读取）
    @param api_key: API密钥（如果为None，则从环境变量读取）
    @return: 数据库路径
    """
    if embedding_model is None:
        embedding_model = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-4B")
    
    if api_key is None:
        api_key = os.getenv("SILICONFLOW_API_KEY")
    
    if not api_key:
        # 如果没有API密钥，使用默认路径
        return "db"
    
    try:
        # 创建临时embeddings来检测维度
        embeddings = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=api_key,
            openai_api_base="https://api.siliconflow.cn/v1",
            request_timeout=60
        )
        test_vector = embeddings.embed_query("test")
        current_dim = len(test_vector)
        
        # 根据维度选择数据库目录
        if current_dim == 1024:
            return "db_1024"
        elif current_dim == 2560:
            return "db_2560"
        elif current_dim == 4096:
            return "db_4096"
        else:
            return f"db_{current_dim}"
    except Exception as e:
        print(f"⚠️ [索引构建] 无法检测维度，使用默认路径: {e}")
        return "db"

def load_documents_from_dir(data_dir: Optional[str] = None, specific_file: Optional[str] = None) -> List:
    """
    从数据目录加载所有文档或特定文档
    
    @param data_dir: 数据目录路径（如果为None，使用默认路径）
    @param specific_file: 特定文件名（如果指定，只加载该文件）
    @return: 文档列表
    """
    if data_dir is None:
        data_dir = get_data_dir()
    
    if not os.path.exists(data_dir):
        print(f"⚠️ [索引构建] 数据目录不存在: {data_dir}")
        return []
    
    documents = []
    # 优化分块策略：增加chunk_size以提高上下文完整性
    # chunk_size=500: 提供更多上下文，减少信息截断
    # chunk_overlap=100: 增加重叠，确保关键信息不会在分块边界丢失
    doc_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 从300增加到500，提供更多上下文
        chunk_overlap=100,  # 从50增加到100，确保关键信息不丢失
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]  # 中文友好的分隔符
    )
    
    def load_file_with_encoding(filepath: str, filename: str) -> bool:
        """尝试使用多种编码加载文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin-1']
        
        for encoding in encodings:
            try:
                loader = TextLoader(filepath, encoding=encoding)
                docs = loader.load()
                chunks = doc_splitter.split_documents(docs)
                documents.extend(chunks)
                print(f"✅ [索引构建] 加载文件: {filename}, 块数: {len(chunks)}, 编码: {encoding}")
                return True
            except UnicodeDecodeError:
                continue
            except Exception as e:
                # 如果是其他错误（不是编码错误），记录并继续尝试下一个编码
                if encoding == encodings[-1]:  # 最后一个编码也失败了
                    print(f"❌ [索引构建] 加载文件失败 {filename}: {e}")
                    return False
                continue
        
        print(f"❌ [索引构建] 加载文件失败 {filename}: 无法使用任何编码读取文件")
        return False
    
    if specific_file:
        # 只加载特定文件
        filepath = os.path.join(data_dir, specific_file)
        if not os.path.exists(filepath):
            print(f"⚠️ [索引构建] 文件不存在: {filepath}")
            return []
        
        file_ext = os.path.splitext(specific_file)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            print(f"⚠️ [索引构建] 不支持的文件类型: {file_ext}")
            return []
        
        load_file_with_encoding(filepath, specific_file)
    else:
        # 加载目录下所有支持的文件
        print(f"📂 [索引构建] 扫描目录: {data_dir}")
        file_count = 0
        for filename in os.listdir(data_dir):
            filepath = os.path.join(data_dir, filename)
            if not os.path.isfile(filepath):
                print(f"⏭️ [索引构建] 跳过非文件: {filename}")
                continue
            
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                print(f"⏭️ [索引构建] 跳过不支持的文件类型: {filename} (扩展名: {file_ext})")
                continue
            
            file_count += 1
            print(f"📄 [索引构建] 准备加载文件 ({file_count}): {filename}")
            load_file_with_encoding(filepath, filename)
        
        print(f"📊 [索引构建] 共扫描到 {file_count} 个可索引文件")
    
    print(f"📊 [索引构建] 总共加载 {len(documents)} 个文档块")
    return documents

def build_index(
    embedding_model: Optional[str] = None,
    api_key: Optional[str] = None,
    data_dir: Optional[str] = None,
    specific_file: Optional[str] = None,
    db_path: Optional[str] = None
) -> dict:
    """
    构建向量索引
    
    @param embedding_model: 嵌入模型名称（如果为None，则从环境变量读取）
    @param api_key: API密钥（如果为None，则从环境变量读取）
    @param data_dir: 数据目录路径（如果为None，使用默认路径）
    @param specific_file: 特定文件名（如果指定，只索引该文件）
    @param db_path: 数据库路径（如果为None，自动检测）
    @return: 构建结果字典
    """
    try:
        # 获取配置
        if embedding_model is None:
            embedding_model = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-4B")
        
        if api_key is None:
            api_key = os.getenv("SILICONFLOW_API_KEY")
        
        if not api_key:
            return {
                "success": False,
                "error": "未找到 SILICONFLOW_API_KEY 环境变量"
            }
        
        # 加载文档
        print(f"📚 [索引构建] 开始加载文档...")
        documents = load_documents_from_dir(data_dir, specific_file)
        
        if not documents:
            return {
                "success": False,
                "error": "没有找到可索引的文档"
            }
        
        # 创建embeddings
        print(f"🔧 [索引构建] 使用嵌入模型: {embedding_model}")
        try:
            embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=api_key,
                openai_api_base="https://api.siliconflow.cn/v1",
                request_timeout=120  # 增加超时时间
            )
            
            # 测试维度
            test_vector = embeddings.embed_query("test")
            actual_dim = len(test_vector)
            print(f"✅ [索引构建] 嵌入模型测试成功，维度: {actual_dim}")
        except Exception as e:
            print(f"❌ [索引构建] 使用API嵌入模型失败: {e}")
            print("   尝试使用本地嵌入模型...")
            # 使用本地嵌入模型作为备用
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            actual_dim = 384  # 本地模型的默认维度
            print(f"✅ [索引构建] 使用本地嵌入模型，维度: {actual_dim}")
        
        # 确定数据库路径
        if db_path is None:
            db_path = get_db_path(embedding_model, api_key)
        
        print(f"💾 [索引构建] 数据库路径: {db_path}")
        
        # 删除旧的数据库（如果存在）
        if os.path.exists(db_path):
            print(f"🗑️ [索引构建] 删除旧的数据库: {db_path}")
            try:
                shutil.rmtree(db_path)
                print(f"✅ [索引构建] 旧数据库已删除")
            except Exception as e:
                print(f"⚠️ [索引构建] 删除旧数据库失败: {e}，继续尝试...")
        
        # 构建向量数据库
        print(f"🚀 [索引构建] 开始向量化文档（可能需要1-2分钟）...")
        import time
        start_time = time.time()
        
        try:
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=db_path,
                collection_name="langchain"
            )
            elapsed = time.time() - start_time
            print(f"✅ [索引构建] 向量数据库创建成功！耗时: {elapsed:.1f}秒")
            
            return {
                "success": True,
                "message": f"索引构建成功",
                "db_path": db_path,
                "dimension": actual_dim,
                "chunks": len(documents),
                "elapsed_time": elapsed
            }
        except Exception as e:
            print(f"❌ [索引构建] 批量创建失败，尝试逐个添加...")
            # 尝试逐个添加文档
            try:
                vectorstore = Chroma(
                    persist_directory=db_path, 
                    embedding_function=embeddings,
                    collection_name="langchain"
                )
                for i, doc in enumerate(documents, 1):
                    if i % 10 == 0:
                        print(f"   处理进度: {i}/{len(documents)}", end='\r')
                    try:
                        vectorstore.add_documents([doc])
                    except Exception as doc_error:
                        print(f"\n   ⚠️ 文档块 {i} 处理失败: {doc_error}")
                        continue
                
                elapsed = time.time() - start_time
                print(f"\n✅ [索引构建] 向量数据库创建成功！耗时: {elapsed:.1f}秒")
                
                return {
                    "success": True,
                    "message": f"索引构建成功（逐个添加模式）",
                    "db_path": db_path,
                    "dimension": actual_dim,
                    "chunks": len(documents),
                    "elapsed_time": elapsed
                }
            except Exception as sequential_error:
                error_msg = f"索引构建失败: {sequential_error}"
                print(f"❌ [索引构建] {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
    
    except Exception as e:
        error_msg = f"索引构建过程中出错: {str(e)}"
        print(f"❌ [索引构建] {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }

