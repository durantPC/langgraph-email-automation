from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .structure_outputs import *
from .prompts import (
    CATEGORIZE_EMAIL_PROMPT,
    GENERATE_RAG_QUERIES_PROMPT,
    EMAIL_WRITER_PROMPT,
    EMAIL_PROOFREADER_PROMPT,
    GENERATE_RAG_ANSWER_PROMPT,
    GENERATE_RAG_ANSWER_PRODUCT_ENQUIRY,
    GENERATE_RAG_ANSWER_CUSTOMER_COMPLAINT,
    GENERATE_RAG_ANSWER_CUSTOMER_FEEDBACK
)
import os

class Agents():
    def __init__(self, api_key=None, reply_model=None, embedding_model=None, signature=None, greeting=None, closing=None, reply_api_base=None, embedding_api_base=None):
        # 使用API调用模型
        # 优先使用传入的api_key，否则从环境变量读取
        if api_key is None:
            api_key = os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            raise ValueError("未找到 API 密钥，请在系统设置中配置或设置 SILICONFLOW_API_KEY 环境变量")
        
        # 使用传入的回复模型，如果没有则使用默认值
        if reply_model is None:
            reply_model = os.getenv("REPLY_MODEL", "moonshotai/Kimi-K2-Thinking")
        
        # 使用传入的API base URL，如果没有则使用默认值（硅基流动）
        if reply_api_base is None:
            reply_api_base = "https://api.siliconflow.cn/v1"
        if embedding_api_base is None:
            embedding_api_base = "https://api.siliconflow.cn/v1"
        
        self.qwen_llm = ChatOpenAI(
            model=reply_model,  # 使用传入的模型
            temperature=0.1,
            openai_api_key=api_key,
            openai_api_base=reply_api_base
        )
        qwen_llm = self.qwen_llm  # 保持向后兼容
        
        # QA assistant chat - 尝试使用嵌入模型，失败则用本地模型
        if embedding_model is None:
            embedding_model = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-4B")
        
        try:
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(
                model=embedding_model,  # 使用传入的嵌入模型
                openai_api_key=api_key,
                openai_api_base=embedding_api_base,
                request_timeout=60  # 增加超时时间到60秒，因为嵌入模型可能需要更长时间
            )
        except:
            # 使用本地嵌入模型作为备用
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        
        # 根据模型维度自动选择对应的数据库目录
        # 首先尝试根据模型名称推断维度（更可靠）
        current_dim = None
        embedding_model_lower = embedding_model.lower() if embedding_model else ""
        
        # 根据模型名称推断维度
        if "qwen3-embedding-8b" in embedding_model_lower or "embedding-8b" in embedding_model_lower:
            current_dim = 4096
            print(f"📐 [维度检测] 根据模型名称推断: {embedding_model} -> 4096维")
        elif "qwen3-embedding-4b" in embedding_model_lower or "embedding-4b" in embedding_model_lower:
            current_dim = 2560
            print(f"📐 [维度检测] 根据模型名称推断: {embedding_model} -> 2560维")
        elif "embedding-2b" in embedding_model_lower or "embedding-1.5b" in embedding_model_lower:
            current_dim = 1024
            print(f"📐 [维度检测] 根据模型名称推断: {embedding_model} -> 1024维")
        else:
            # 如果无法从名称推断，尝试通过API调用检测
            try:
                print(f"📐 [维度检测] 尝试通过API调用检测维度...")
                test_embedding = embeddings.embed_query("test")
                current_dim = len(test_embedding)
                print(f"📐 [维度检测] API调用成功: {embedding_model} -> {current_dim}维")
            except Exception as e:
                print(f"⚠️  [维度检测] API调用失败: {e}")
                current_dim = None
        
        # 根据维度选择数据库目录
        if current_dim == 1024:
            db_path = "db_1024"
        elif current_dim == 2560:
            db_path = "db_2560"
        elif current_dim == 4096:
            db_path = "db_4096"
        else:
            # 未知维度，使用维度作为目录名
            db_path = f"db_{current_dim}" if current_dim else "db"
            if current_dim:
                print(f"ℹ️  使用自定义维度数据库: {db_path}")
            else:
                print(f"⚠️  警告: 无法确定维度，使用默认目录: {db_path}")
                print(f"   嵌入模型: {embedding_model}")
                print(f"   建议: 检查模型名称或确保API调用成功")
        
        # 检查数据库是否存在
        if not os.path.exists(db_path):
            print(f"⚠️  警告: 数据库目录 {db_path} 不存在！")
            print(f"   当前嵌入模型: {embedding_model}")
            print(f"   当前模型维度: {current_dim}")
            print(f"   请运行对应的创建脚本：")
            if current_dim == 1024:
                print(f"   python create_index_1024.py")
            elif current_dim == 2560:
                print(f"   python create_index_2560.py")
            elif current_dim == 4096:
                print(f"   python create_index_4096.py")
            else:
                print(f"   请创建 {db_path} 目录的数据库")
            print(f"   或者使用其他已存在的数据库目录")
            # 创建空数据库（但会提示用户需要运行创建脚本）
            # 优先使用不指定 tenant/database 的方式（兼容旧数据库）
            try:
                # 方式1：直接使用 persist_directory，不指定 tenant/database（兼容旧数据库）
                vectorstore = Chroma(
                    persist_directory=db_path, 
                    embedding_function=embeddings,
                    collection_name="langchain"
                )
            except Exception as e1:
                # 方式2：如果方式1失败，尝试使用新版本的 tenant/database
                try:
                    import chromadb
                    client = chromadb.PersistentClient(
                        path=db_path,
                        tenant="default_tenant",
                        database="default_database"
                    )
                    vectorstore = Chroma(
                        client=client,
                        embedding_function=embeddings,
                        collection_name="langchain"
                    )
                except Exception as e2:
                    # 方式3：如果都失败，尝试不指定 tenant 和 database
                    print(f"⚠️  使用兼容模式创建数据库: {type(e1).__name__}: {str(e1)[:100]}")
                    try:
                        import chromadb
                        client = chromadb.PersistentClient(path=db_path)
                        vectorstore = Chroma(
                            client=client,
                            embedding_function=embeddings,
                            collection_name="langchain"
                        )
                    except Exception as e3:
                        # 最后回退：完全不使用 client，让 langchain_chroma 自己处理
                        print(f"⚠️  尝试最后兼容模式: {type(e3).__name__}: {str(e3)[:100]}")
                        vectorstore = Chroma(
                            persist_directory=db_path, 
                            embedding_function=embeddings
                        )
            print(f"   ⚠️  已创建空数据库，请运行创建脚本填充数据")
        else:
            # 数据库存在，直接使用
            # 优先使用不指定 tenant/database 的方式（兼容旧数据库）
            try:
                # 方式1：直接使用 persist_directory，不指定 tenant/database（兼容旧数据库）
                vectorstore = Chroma(
                    persist_directory=db_path, 
                    embedding_function=embeddings,
                    collection_name="langchain"
                )
            except Exception as e1:
                # 方式2：如果方式1失败，尝试使用新版本的 tenant/database
                try:
                    import chromadb
                    client = chromadb.PersistentClient(
                        path=db_path,
                        tenant="default_tenant",
                        database="default_database"
                    )
                    vectorstore = Chroma(
                        client=client,
                        embedding_function=embeddings,
                        collection_name="langchain"
                    )
                except Exception as e2:
                    # 方式3：如果都失败，尝试不指定 tenant 和 database
                    print(f"⚠️  使用兼容模式加载数据库: {type(e1).__name__}: {str(e1)[:100]}")
                    try:
                        import chromadb
                        client = chromadb.PersistentClient(path=db_path)
                        vectorstore = Chroma(
                            client=client,
                            embedding_function=embeddings,
                            collection_name="langchain"
                        )
                    except Exception as e3:
                        # 最后回退：完全不使用 client，让 langchain_chroma 自己处理
                        print(f"⚠️  尝试最后兼容模式: {type(e3).__name__}: {str(e3)[:100]}")
                        vectorstore = Chroma(
                            persist_directory=db_path, 
                            embedding_function=embeddings
                        )
            print(f"✅ 使用 {current_dim} 维数据库: {db_path}")
            # 检查数据库中的文档数量
            try:
                collection = vectorstore._collection
                count = collection.count()
                print(f"📊 [数据库信息] 数据库中共有 {count} 个文档块")
            except Exception as e:
                print(f"⚠️ [数据库信息] 无法获取文档数量: {e}")
        
        # 创建基础检索器（用于快速检索）
        # 使用相似度检索（similarity）而不是MMR，因为MMR需要更多计算时间
        # 增加检索数量，确保小文档也能被检索到
        base_retriever = vectorstore.as_retriever(
            search_type="similarity",  # 使用相似度检索，速度更快
            search_kwargs={"k": 20}  # 从15增加到20，提高覆盖率
        )
        
        # 为不同邮件类型创建专门的检索器
        # 产品咨询：使用similarity检索以提高速度（MMR虽然多样性更好，但速度慢2-3倍）
        # 注意：similarity检索已经足够准确，LLM会处理重复内容
        product_retriever = vectorstore.as_retriever(
            search_type="similarity",  # 改为similarity，速度提升2-3倍
            search_kwargs={
                "k": 12  # 从15减少到12，平衡速度和覆盖率
            }
        )
        
        # 客户投诉：需要快速找到处理流程和解决方案
        complaint_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}  # 从6增加到10，提高覆盖率
        )
        
        # 客户反馈：需要找到相关功能和改进建议
        feedback_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 8}  # 从5增加到8，提高覆盖率
        )
        
        # 保存retriever和vectorstore供调试使用
        self.retriever = base_retriever  # 默认使用基础检索器
        self.product_retriever = product_retriever
        self.complaint_retriever = complaint_retriever
        self.feedback_retriever = feedback_retriever
        self.vectorstore = vectorstore

        # 保存模板设置
        self.signature = signature or "Agentia 团队"
        self.greeting = greeting or "尊敬的客户，您好！"
        self.closing = closing or "祝好！"

        # Categorize email chain
        email_category_prompt = PromptTemplate(
            template=CATEGORIZE_EMAIL_PROMPT, 
            input_variables=["email"]
        )
        self.categorize_email = (
            email_category_prompt | 
            qwen_llm.with_structured_output(CategorizeEmailOutput)
        )

        # Used to design queries for RAG retrieval
        generate_query_prompt = PromptTemplate(
            template=GENERATE_RAG_QUERIES_PROMPT, 
            input_variables=["email"]
        )
        self.design_rag_queries = (
            generate_query_prompt | 
            qwen_llm.with_structured_output(RAGQueriesOutput)
        )
        
        # Generate answer to queries using RAG (通用版本)
        qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_PROMPT)
        self.generate_rag_answer = (
            {"context": base_retriever, "question": RunnablePassthrough()}
            | qa_prompt
            | qwen_llm
            | StrOutputParser()
        )
        
        # 为不同邮件类型创建专门的RAG答案生成器
        # 产品咨询
        product_qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_PRODUCT_ENQUIRY)
        self.generate_rag_answer_product = (
            {"context": product_retriever, "question": RunnablePassthrough()}
            | product_qa_prompt
            | qwen_llm
            | StrOutputParser()
        )
        
        # 客户投诉
        complaint_qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_CUSTOMER_COMPLAINT)
        self.generate_rag_answer_complaint = (
            {"context": complaint_retriever, "question": RunnablePassthrough()}
            | complaint_qa_prompt
            | qwen_llm
            | StrOutputParser()
        )
        
        # 客户反馈
        feedback_qa_prompt = ChatPromptTemplate.from_template(GENERATE_RAG_ANSWER_CUSTOMER_FEEDBACK)
        self.generate_rag_answer_feedback = (
            {"context": feedback_retriever, "question": RunnablePassthrough()}
            | feedback_qa_prompt
            | qwen_llm
            | StrOutputParser()
        )

        # Used to write a draft email based on category and related informations
        # 构建动态的邮件写作提示词（使用用户设置的模板）
        # 使用 replace 而不是 format，避免与 prompt 中的 JSON 格式冲突
        email_writer_prompt_template = EMAIL_WRITER_PROMPT.replace('{greeting}', self.greeting).replace('{closing}', self.closing).replace('{signature}', self.signature)
        
        writer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", email_writer_prompt_template),
                MessagesPlaceholder("history"),
                ("human", "{email_information}")
            ]
        )
        self.email_writer = (
            writer_prompt | 
            qwen_llm.with_structured_output(WriterOutput)
        )

        # Verify the generated email
        proofreader_prompt = PromptTemplate(
            template=EMAIL_PROOFREADER_PROMPT, 
            input_variables=["initial_email", "generated_email"]
        )
        self.email_proofreader = (
            proofreader_prompt | 
            qwen_llm.with_structured_output(ProofReaderOutput) 
        )