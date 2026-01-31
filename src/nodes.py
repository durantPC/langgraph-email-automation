from colorama import Fore, Style
from .agents import Agents
from .tools.QQEmailTools import QQEmailToolsClass
from .state import GraphState, Email, EmailUrgencyLevel
from .tools.EmailUrgencyDetector import urgency_detector


class Nodes:
    def __init__(self, email_address=None, auth_code=None, api_key=None, reply_model=None, embedding_model=None, signature=None, greeting=None, closing=None, reply_api_base=None, embedding_api_base=None):
        """
        初始化节点类
        
        @param email_address: QQ邮箱地址（如果为None，则从环境变量读取）
        @param auth_code: QQ邮箱授权码（如果为None，则从环境变量读取）
        @param api_key: AI API密钥（如果为None，则从环境变量读取）
        @param reply_model: 回复大模型（如果为None，则使用默认值）
        @param embedding_model: 嵌入大模型（如果为None，则使用默认值）
        @param signature: 邮件签名（如果为None，则使用默认值）
        @param greeting: 问候语（如果为None，则使用默认值）
        @param closing: 结束语（如果为None，则使用默认值）
        @param reply_api_base: 回复模型API base URL（如果为None，则使用默认值）
        @param embedding_api_base: 嵌入模型API base URL（如果为None，则使用默认值）
        """
        # 保存模板设置
        self.signature = signature or "Agentia 团队"
        self.greeting = greeting or "尊敬的客户，您好！"
        self.closing = closing or "祝好！"
        
        self.agents = Agents(
            api_key=api_key, 
            reply_model=reply_model, 
            embedding_model=embedding_model,
            signature=self.signature,
            greeting=self.greeting,
            closing=self.closing,
            reply_api_base=reply_api_base,
            embedding_api_base=embedding_api_base
        )
        self.email_tools = QQEmailToolsClass(email_address=email_address, auth_code=auth_code)

    def load_new_emails(self, state: GraphState) -> GraphState:
        """从QQ邮箱加载新邮件并更新状态"""
        print(Fore.YELLOW + "正在加载新邮件...\n" + Style.RESET_ALL)
        recent_emails = self.email_tools.fetch_unanswered_emails()
        emails = [Email(**email) for email in recent_emails]
        return {"emails": emails}

    def check_new_emails(self, state: GraphState) -> str:
        """检查是否有新邮件需要处理"""
        email_count = len(state['emails'])
        if email_count == 0:
            print(Fore.RED + "没有新邮件" + Style.RESET_ALL)
            return "empty"
        else:
            print(Fore.GREEN + f"有新邮件需要处理 (剩余 {email_count} 封)" + Style.RESET_ALL)
            return "process"
        
    def is_email_inbox_empty(self, state: GraphState) -> GraphState:
        return state

    def categorize_email(self, state: GraphState) -> GraphState:
        """使用AI代理对当前邮件进行分类，并检测紧急程度"""
        print(Fore.YELLOW + "正在检查邮件类别和紧急程度...\n" + Style.RESET_ALL)
        
        # 获取最后一封邮件
        current_email = state["emails"][-1]
        print(Fore.CYAN + f"处理邮件: {current_email.subject[:50]}..." + Style.RESET_ALL)
        print(Fore.CYAN + f"发件人: {current_email.sender}" + Style.RESET_ALL)
        
        # 检测邮件紧急程度
        try:
            urgency_level, urgency_keywords = urgency_detector.analyze_urgency(
                current_email.subject, 
                current_email.body
            )
            current_email.urgency_level = urgency_level
            current_email.urgency_keywords = urgency_keywords
            print(Fore.MAGENTA + f"邮件紧急程度: {urgency_level}" + Style.RESET_ALL)
            if urgency_keywords:
                print(Fore.MAGENTA + f"匹配关键词: {', '.join(urgency_keywords[:5])}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"⚠️ 紧急程度检测失败: {str(e)}" + Style.RESET_ALL)
            current_email.urgency_level = EmailUrgencyLevel.LOW
            current_email.urgency_keywords = []
        
        try: #邮件分类
            result = self.agents.categorize_email.invoke({"email": current_email.body})
            print(Fore.MAGENTA + f"邮件类别: {result.category.value}" + Style.RESET_ALL)
            category = result.category.value
        except Exception as e:
            # 如果结构化输出失败，尝试从错误信息中提取分类
            error_msg = str(e)
            print(Fore.YELLOW + f"⚠️ 结构化输出失败，尝试从文本中提取分类..." + Style.RESET_ALL)
            print(Fore.YELLOW + f"   错误: {error_msg[:200]}" + Style.RESET_ALL)
            
            # 从错误信息中提取返回的文本（支持单引号和双引号）
            if "input_value=" in error_msg:
                import re
                # 尝试匹配双引号
                match = re.search(r'input_value="([^"]+)"', error_msg)
                if not match:
                    # 尝试匹配单引号
                    match = re.search(r"input_value='([^']+)'", error_msg)
                
                if match:
                    text_output = match.group(1)
                    print(Fore.YELLOW + f"   模型返回文本: {text_output[:100]}..." + Style.RESET_ALL)
                    
                    # 尝试从文本中提取分类
                    text_lower = text_output.lower()
                    if "unrelated" in text_lower or "无关" in text_lower:
                        category = "unrelated"
                    elif "complaint" in text_lower or "投诉" in text_lower:
                        category = "customer_complaint"
                    elif "feedback" in text_lower or "反馈" in text_lower:
                        category = "customer_feedback"
                    elif "enquiry" in text_lower or "inquiry" in text_lower or "咨询" in text_lower:
                        category = "product_enquiry"
                    else:
                        # 默认分类为产品咨询
                        category = "product_enquiry"
                    
                    print(Fore.GREEN + f"✅ 从文本中提取到分类: {category}" + Style.RESET_ALL)
                else:
                    # 无法提取，使用默认分类
                    category = "product_enquiry"
                    print(Fore.YELLOW + f"⚠️ 无法提取分类，使用默认分类: {category}" + Style.RESET_ALL)
            else:
                # 无法提取，使用默认分类
                category = "product_enquiry"
                print(Fore.YELLOW + f"⚠️ 无法提取分类，使用默认分类: {category}" + Style.RESET_ALL)
        
        return {
            "email_category": category,
            "urgency_level": current_email.urgency_level,
            "urgency_keywords": current_email.urgency_keywords,
            "current_email": current_email
        }

    def route_email_based_on_category(self, state: GraphState) -> str:
        """根据邮件类别进行路由"""
        print(Fore.YELLOW + "根据类别路由邮件...\n" + Style.RESET_ALL)
        category = state["email_category"]
        if category == "product_enquiry":
            return "product related"
        elif category == "unrelated":
            return "unrelated"
        else:
            return "not product related"

    def construct_rag_queries(self, state: GraphState) -> GraphState:
        """根据邮件内容构建RAG查询"""
        print(Fore.YELLOW + "正在设计RAG查询...\n" + Style.RESET_ALL)
        email_content = state["current_email"].body
        
        try:
            query_result = self.agents.design_rag_queries.invoke({"email": email_content}) #RAG查询生成，这不是去知识库检索，给你生成问题，带着
            queries = query_result.queries
            
            # 可视化显示生成的查询问题
            print(Fore.GREEN + f"\n{'='*60}" + Style.RESET_ALL)
            print(Fore.GREEN + f"✨ 生成了 {len(queries)} 个 RAG 查询问题：" + Style.RESET_ALL)
            print(Fore.GREEN + f"{'='*60}" + Style.RESET_ALL)
            for i, query in enumerate(queries, 1):
                print(Fore.CYAN + f"  问题 {i}: {query}" + Style.RESET_ALL)
            print(Fore.GREEN + f"{'='*60}\n" + Style.RESET_ALL)
        except Exception as e:
            # 如果结构化输出失败，尝试从错误信息中提取查询
            error_msg = str(e)
            print(Fore.YELLOW + f"⚠️ RAG查询结构化输出失败，尝试从文本中提取..." + Style.RESET_ALL)
            print(Fore.YELLOW + f"   错误: {error_msg[:200]}" + Style.RESET_ALL)
            
            # 从错误信息中提取返回的文本
            if "input_value=" in error_msg:
                import re
                # 尝试匹配双引号
                match = re.search(r'input_value="([^"]+)"', error_msg)
                if not match:
                    # 尝试匹配单引号
                    match = re.search(r"input_value='([^']+)'", error_msg)
                
                if match:
                    text_output = match.group(1)
                    print(Fore.YELLOW + f"   模型返回文本: {text_output[:200]}..." + Style.RESET_ALL)
                    
                    # 从Markdown列表中提取查询（支持 - "query" 或 1. "query" 格式）
                    queries = []
                    # 匹配 - "内容" 或 1. "内容" 格式
                    query_matches = re.findall(r'[-\d]+\.?\s*["\']([^"\']+)["\']', text_output)
                    if query_matches:
                        queries = query_matches
                        print(Fore.GREEN + f"✅ 从文本中提取到 {len(queries)} 个查询" + Style.RESET_ALL)
                        
                        # 显示提取的查询问题
                        print(Fore.GREEN + f"\n{'='*60}" + Style.RESET_ALL)
                        print(Fore.GREEN + f"✨ 生成了 {len(queries)} 个 RAG 查询问题：" + Style.RESET_ALL)
                        print(Fore.GREEN + f"{'='*60}" + Style.RESET_ALL)
                        for i, query in enumerate(queries, 1):
                            print(Fore.CYAN + f"  问题 {i}: {query}" + Style.RESET_ALL)
                        print(Fore.GREEN + f"{'='*60}\n" + Style.RESET_ALL)
                    else:
                        # 如果没有匹配到，使用邮件内容的前100字作为查询
                        queries = [email_content[:100]]
                        print(Fore.YELLOW + f"⚠️ 无法提取查询，使用邮件内容作为查询" + Style.RESET_ALL)
                else:
                    # 无法提取，使用邮件内容作为查询
                    queries = [email_content[:100]]
                    print(Fore.YELLOW + f"⚠️ 无法提取查询，使用邮件内容作为查询" + Style.RESET_ALL)
            else:
                # 无法提取，使用邮件内容作为查询
                queries = [email_content[:100]]
                print(Fore.YELLOW + f"⚠️ 无法提取查询，使用邮件内容作为查询" + Style.RESET_ALL)
        
        return {"rag_queries": queries}

    def retrieve_from_rag(self, state: GraphState) -> GraphState:
        """基于RAG问题从内部知识库检索信息（根据邮件类型选择不同的检索策略）"""
        print(Fore.YELLOW + "正在从内部知识库检索信息...\n" + Style.RESET_ALL)
        
        # 获取邮件分类（优先从email_category获取，如果没有则从current_email获取）
        category = state.get("email_category", None)
        if category is None:
            # 如果email_category不存在，尝试从current_email获取
            current_email = state.get("current_email", {})
            if isinstance(current_email, dict):
                category = current_email.get("category", "product_enquiry")
            elif hasattr(current_email, "category"):
                category = current_email.category
            else:
                category = "product_enquiry"
        
        # 检查是否是RAG测试场景（通过检查current_email的subject或id）
        is_rag_test = False
        current_email_obj = state.get("current_email", {})
        if isinstance(current_email_obj, dict):
            is_rag_test = current_email_obj.get("subject") == "RAG测试" or current_email_obj.get("id") == "rag_test"
        elif hasattr(current_email_obj, "subject"):
            is_rag_test = current_email_obj.subject == "RAG测试" or (hasattr(current_email_obj, "id") and current_email_obj.id == "rag_test")
        
        # 根据邮件类型选择不同的RAG答案生成器
        # 对于RAG测试或unrelated类型，优先使用产品咨询检索策略（更全面）
        if category == "product_enquiry" or (is_rag_test and category == "unrelated"):
            rag_generator = self.agents.generate_rag_answer_product
            if is_rag_test:
                print("📋 [RAG测试] 使用产品咨询检索策略（更全面）")
            else:
                print("📦 使用产品咨询专用检索策略")
        elif category == "customer_complaint":
            rag_generator = self.agents.generate_rag_answer_complaint
            print("⚠️ 使用客户投诉专用检索策略")
        elif category == "customer_feedback":
            rag_generator = self.agents.generate_rag_answer_feedback
            print("💬 使用客户反馈专用检索策略")
        else:
            # 默认使用通用检索器
            rag_generator = self.agents.generate_rag_answer
            print("📋 使用通用检索策略")
        
        final_answer = ""
        queries = state.get("rag_queries", [])
        print(f"🔍 [RAG检索] 开始处理 {len(queries)} 个查询...")
        
        # 只处理第一个查询，避免多个查询导致超时
        # 如果第一个查询成功，就不处理后续查询
        if queries:
            query = queries[0]  # 只使用第一个查询
            try:
                print(f"🔍 [RAG检索] 正在处理查询: {query[:80]}...")
                print(f"⏳ [RAG检索] 开始调用rag_generator.invoke...")
                
                # 先手动检索一次，显示检索到的原始内容（用于调试）--测试代码
                if category == "product_enquiry" or (is_rag_test and category == "unrelated"):
                    debug_retriever = self.agents.product_retriever
                elif category == "customer_complaint":
                    debug_retriever = self.agents.complaint_retriever
                elif category == "customer_feedback":
                    debug_retriever = self.agents.feedback_retriever
                else:
                    debug_retriever = self.agents.retriever
                
                try:
                    retrieved_docs = debug_retriever.invoke(query)
                    print(f"📚 [RAG检索] 从数据库检索到 {len(retrieved_docs)} 个文档片段")
                    if retrieved_docs:
                        print(f"📄 [RAG检索] 检索到的原始内容（前3个片段）:")
                        for i, doc in enumerate(retrieved_docs[:3], 1):
                            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                            print(f"   片段 {i}: {content[:300]}...")
                    else:
                        print(f"⚠️ [RAG检索] 警告: 未从数据库检索到任何文档片段！")
                except Exception as debug_e:
                    print(f"⚠️ [RAG检索] 调试检索失败: {debug_e}")
                
                # 调用 RAG generator（内部会再次检索并生成答案）
                max_retries = 2
                rag_result = None
                for attempt in range(max_retries):
                    try:
                        rag_result = rag_generator.invoke(query)
                        break  # 成功则退出循环
                    except Exception as api_error:
                        error_msg = str(api_error)
                        if "Connection error" in error_msg or "timeout" in error_msg.lower():
                            if attempt < max_retries - 1:
                                print(f"⚠️ [RAG检索] API调用失败（尝试 {attempt + 1}/{max_retries}）: {error_msg}")
                                print(f"🔄 [RAG检索] 等待2秒后重试...")
                                import time
                                time.sleep(2)
                            else:
                                print(f"❌ [RAG检索] API调用失败（已重试{max_retries}次）: {error_msg}")
                                raise
                        else:
                            # 其他错误直接抛出
                            raise
                
                print(f"✅ [RAG检索] 查询完成，结果长度: {len(rag_result) if rag_result else 0}")
                if rag_result:
                    print(f"📝 [RAG检索] 结果预览: {rag_result[:200]}...")
                final_answer = rag_result if rag_result else "未找到相关信息"
                
            except Exception as e:
                print(f"❌ [RAG检索] 查询失败: {e}")
                import traceback
                traceback.print_exc()
                final_answer = f"检索失败: {str(e)}"
        else:
            print(f"⚠️ [RAG检索] 没有查询需要处理")
            final_answer = "未生成查询"
        
        print(f"✅ [RAG检索] 处理完成，结果长度: {len(final_answer)}")
        return {"retrieved_documents": final_answer}

    def write_draft_email(self, state: GraphState) -> GraphState:
        """根据当前邮件和检索信息编写草稿邮件"""
        print(Fore.YELLOW + "正在编写草稿邮件...\n" + Style.RESET_ALL)
        
        # Format input to the writer agent
        inputs = (
            f'# **EMAIL CATEGORY:** {state["email_category"]}\n\n'
            f'# **EMAIL CONTENT:**\n{state["current_email"].body}\n\n'
            f'# **INFORMATION:**\n{state["retrieved_documents"]}' # Empty for feedback or complaint
        )
        
        # Get messages history for current email
        writer_messages = state.get('writer_messages', [])
        
        # Write email
        try:
            draft_result = self.agents.email_writer.invoke({
                "email_information": inputs,
                "history": writer_messages
            })
            email = draft_result.email
        except Exception as e:
            error_msg = str(e)
            # 如果是 JSON 解析错误，尝试手动处理
            if "json" in error_msg.lower() or "control character" in error_msg.lower() or "validation error" in error_msg.lower():
                print(f"⚠️  JSON 解析错误，尝试使用备用方法: {e}")
                # 使用 LLM 直接生成文本，不使用 structured output
                from langchain_core.output_parsers import StrOutputParser
                from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
                from src.prompts import EMAIL_WRITER_PROMPT
                
                # 获取 LLM（从 agents 中获取）
                llm = self.agents.qwen_llm
                
                # 构建动态的邮件写作提示词（使用用户设置的模板）
                # 使用 replace 而不是 format，避免与 prompt 中的 JSON 格式冲突
                email_writer_prompt_template = EMAIL_WRITER_PROMPT.replace('{greeting}', self.greeting).replace('{closing}', self.closing).replace('{signature}', self.signature)
                
                # 创建不使用 structured output 的 chain
                writer_prompt = ChatPromptTemplate.from_messages([
                    ("system", email_writer_prompt_template),
                    MessagesPlaceholder("history"),
                    ("human", "{email_information}")
                ])
                text_chain = writer_prompt | llm | StrOutputParser()
                
                text_result = text_chain.invoke({
                    "email_information": inputs,
                    "history": writer_messages
                })
                
                # 尝试从文本中提取 JSON
                import json
                import re
                # 尝试提取 JSON 部分（支持多行）
                json_match = re.search(r'\{"email"\s*:\s*"([^"]*(?:\\.[^"]*)*)"\}', text_result, re.DOTALL)
                if json_match:
                    try:
                        # 提取 email 字段的值
                        email_content = json_match.group(1)
                        # 处理转义字符
                        email = email_content.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                    except Exception as parse_err:
                        print(f"⚠️  无法解析 JSON，使用原始文本: {parse_err}")
                        email = text_result.strip()
                else:
                    # 如果没有找到 JSON，直接使用文本（可能模型返回了纯文本）
                    email = text_result.strip()
            else:
                raise
        trials = state.get('trials', 0) + 1

        # Append writer's draft to the message list
        writer_messages.append(f"**Draft {trials}:**\n{email}")

        return {
            "generated_email": email, 
            "trials": trials,
            "writer_messages": writer_messages
        }

    def verify_generated_email(self, state: GraphState) -> GraphState:
        """使用校对代理验证生成的邮件"""
        print(Fore.YELLOW + "正在验证生成的邮件...\n" + Style.RESET_ALL)
        review = self.agents.email_proofreader.invoke({
            "initial_email": state["current_email"].body,
            "generated_email": state["generated_email"],
        })

        writer_messages = state.get('writer_messages', [])
        writer_messages.append(f"**Proofreader Feedback:**\n{review.feedback}")

        return {
            "sendable": review.send,
            "writer_messages": writer_messages
        }

    def must_rewrite(self, state: GraphState) -> str:
        """根据审查和尝试次数确定是否需要重写邮件"""
        email_sendable = state["sendable"]
        if email_sendable:
            print(Fore.GREEN + "邮件质量良好，准备发送！！！" + Style.RESET_ALL)
            if state["emails"]:
                state["emails"].pop()
                print(Fore.CYAN + f"剩余邮件数: {len(state['emails'])}" + Style.RESET_ALL)
            state["writer_messages"] = []
            return "send"
        elif state["trials"] >= 3:
            print(Fore.RED + "邮件质量不佳，已达到最大尝试次数，必须停止！！！" + Style.RESET_ALL)
            if state["emails"]:
                state["emails"].pop()
                print(Fore.CYAN + f"剩余邮件数: {len(state['emails'])}" + Style.RESET_ALL)
            state["writer_messages"] = []
            return "stop"
        else:
            print(Fore.RED + "邮件质量不佳，必须重写..." + Style.RESET_ALL)
            return "rewrite"

    def create_draft_response(self, state: GraphState) -> GraphState:
        """发送QQ邮箱回复（QQ邮箱不支持草稿，直接发送）"""
        print(Fore.YELLOW + "正在发送邮件回复...\n" + Style.RESET_ALL)
        self.email_tools.create_draft_reply(state["current_email"], state["generated_email"])
        
        return {"retrieved_documents": "", "trials": 0}

    def send_email_response(self, state: GraphState) -> GraphState:
        """直接使用QQ邮箱发送邮件回复"""
        print(Fore.YELLOW + "正在发送邮件...\n" + Style.RESET_ALL)
        self.email_tools.send_reply(state["current_email"], state["generated_email"])
        
        return {"retrieved_documents": "", "trials": 0}
    
    def skip_unrelated_email(self, state):
        """跳过无关邮件并从邮件列表中移除"""
        current_email = state.get("current_email")
        if current_email:
            print(Fore.YELLOW + f"正在跳过无关邮件: {current_email.subject[:50]}...\n" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "正在跳过无关邮件...\n" + Style.RESET_ALL)
        
        # 确保移除邮件
        if state["emails"]:
            state["emails"].pop()
            print(Fore.CYAN + f"剩余邮件数: {len(state['emails'])}" + Style.RESET_ALL)
        
        return state