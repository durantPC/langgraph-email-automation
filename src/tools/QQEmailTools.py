import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
import re
import os


class QQEmailToolsClass:
    def __init__(self, email_address=None, auth_code=None):
        """
        初始化QQ邮箱工具类
        
        @param email_address: QQ邮箱地址（如果为None，则从环境变量读取）
        @param auth_code: QQ邮箱授权码（如果为None，则从环境变量读取）
        """
        self.email_address = email_address or os.getenv("MY_EMAIL", "")
        self.auth_code = auth_code or os.getenv("QQ_EMAIL_AUTH_CODE", "")
        self.imap_server = "imap.qq.com"
        self.imap_port = 993
        self.smtp_server = "smtp.qq.com"
        self.smtp_port = 465
        
    def fetch_unanswered_emails(self, max_results=50):
        """
        获取未读邮件
        
        @param max_results: 最大返回数量
        @return: 邮件列表
        """
        unanswered_emails = []
        mail = None
        
        try:
            # 连接到IMAP服务器
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.auth_code)
            
            # 选择收件箱
            status, messages = mail.select('inbox')
            if status != 'OK':
                print(f"❌ 无法选择收件箱")
                mail.logout()
                return []
            
            # 搜索未读邮件（最近8小时）
            since_date = (datetime.now() - timedelta(hours=8)).strftime('%d-%b-%Y')
            search_criteria = f'(UNSEEN SINCE {since_date})'
            status, message_ids = mail.search(None, search_criteria)
                
            if status != 'OK' or not message_ids[0]:
                mail.logout()
                return []
            
            # 获取邮件ID列表
            email_ids = message_ids[0].split()
            email_ids = email_ids[-max_results:]  # 只取最新的N封
            
            filtered_count = 0
            fetch_failed_count = 0
            
            for email_id in email_ids:
                try:
                    # 获取邮件
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        fetch_failed_count += 1
                        continue
                    
                    # 解析邮件
                    email_body = msg_data[0][1]
                    msg = email.message_from_bytes(email_body)
            
                    # 解析邮件头
                    subject, encoding = decode_header(msg["Subject"])[0] if msg["Subject"] else (None, None)
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')
                    
                    # 获取原始 From 头（不进行 decode_header，直接使用原始字符串提取邮箱地址）
                    from_header = msg.get("From", "")
                    sender = None
                    if from_header:
                        # 直接从原始 From 头中提取邮箱地址（格式通常是 "显示名称 <email@example.com>" 或 "email@example.com"）
                        # 如果包含 < >，提取邮箱地址部分
                        if '<' in from_header and '>' in from_header:
                            try:
                                sender = from_header.split('<')[1].split('>')[0].strip()
                            except (IndexError, AttributeError):
                                # 如果提取失败，尝试使用整个 from_header
                                sender = from_header.strip()
                        else:
                            # 如果没有 < >，直接使用 from_header
                            sender = from_header.strip()
                        
                        # 清理可能的引号和其他特殊字符
                        if sender:
                            sender = sender.strip('"\'')  # 移除首尾的引号
                            sender = sender.strip()
                    
                    # 提取发件人邮箱地址
                    sender_email = ""
                    if sender:
                        sender = str(sender).strip()
                        # 如果包含 < >，提取邮箱地址部分
                        if '<' in sender and '>' in sender:
                            try:
                                sender_email = sender.split('<')[1].split('>')[0].strip()
                            except (IndexError, AttributeError) as e:
                                # 如果提取失败，尝试使用整个 sender 字符串
                                print(f"⚠️ [获取邮件] 警告：提取邮箱地址失败: {e}, 使用原始值: {sender}")
                                sender_email = sender.strip()
                        else:
                            # 如果没有 < >，直接使用 sender
                            sender_email = sender.strip()
                    
                    # 清理可能的引号和其他特殊字符
                    if sender_email:
                        sender_email = sender_email.strip('"\'')  # 移除首尾的引号
                        sender_email = sender_email.strip()
                    
                    # 验证邮箱地址格式
                    if not sender_email or '@' not in sender_email:
                        print(f"⚠️ [获取邮件] 警告：无效的发件人地址格式，跳过此邮件")
                        print(f"   原始 From 头: {repr(msg.get('From', ''))}")
                        print(f"   解码后 sender: {repr(sender)}")
                        print(f"   提取后 sender_email: {repr(sender_email)}")
                        fetch_failed_count += 1
                        continue
                    
                    # 解析邮件正文
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain" or content_type == "text/html":
                                try:
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        charset = part.get_content_charset() or 'utf-8'
                                        body = payload.decode(charset, errors='ignore')
                                        if content_type == "text/html":
                                            # 简单去除HTML标签
                                            import re
                                            body = re.sub(r'<[^>]+>', '', body)
                                        break
                                except:
                                    pass
                    else:
                        try:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                charset = msg.get_content_charset() or 'utf-8'
                                body = payload.decode(charset, errors='ignore')
                        except:
                            pass
                    
                    # 获取Message-ID
                    message_id = msg.get("Message-ID", "")
                    references = msg.get("References", "")
                    in_reply_to = msg.get("In-Reply-To", "")
                    
                    # 构建邮件数据
                    email_data = {
                        'id': message_id or f"email_{email_id.decode()}",
                        'threadId': in_reply_to or message_id,
                        'messageId': message_id,
                        'references': references,
                        'sender': sender_email,
                        'subject': subject or '(无主题)',
                        'body': body,
                        'imap_id': email_id
                    }
                    
                    # 检查是否应该处理这封邮件
                    if self._should_process_email(email_data):
                        unanswered_emails.append(email_data)
                    else:
                        filtered_count += 1
                except Exception as e:
                    print(f"DEBUG: 获取邮件 {email_id} 失败: {e}")
                    fetch_failed_count += 1
                    continue
            
            print(f"DEBUG: 过滤掉 {filtered_count} 封邮件（获取失败: {fetch_failed_count}，被过滤: {filtered_count - fetch_failed_count}），最终返回 {len(unanswered_emails)} 封邮件")
            
            mail.logout()
            return unanswered_emails
            
        except Exception as e:
            print(f"❌ 获取邮件失败: {e}")
            if mail:
                try:
                    mail.logout()
                except:
                    pass
            return []
    
    def _should_process_email(self, email_data):
        """
        检查是否应该处理这封邮件
        
        @param email_data: 邮件数据
        @return: 是否应该处理
        """
        # 跳过自己发送的邮件
        if self.email_address in email_data['sender']:
            return False
        
        # 跳过空邮件
        if not email_data['body'].strip():
            return False
        
        return True
    
    def mark_email_as_read(self, email_id):
        """
        将邮件标记为已读
        
        @param email_id: 邮件的IMAP ID（bytes类型或字符串）
        @return: 是否成功
        """
        try:
            # 连接到IMAP服务器
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.auth_code)
            
            # 选择收件箱
            status, messages = mail.select('inbox')
            if status != 'OK':
                print(f"❌ 无法选择收件箱")
                mail.logout()
                return False
            
            # 处理 email_id 格式
            # IMAP序列号应该是数字字符串或bytes格式的数字
            email_id_str = None
            
            if isinstance(email_id, bytes):
                # 如果是bytes，直接解码为字符串
                try:
                    email_id_str = email_id.decode('utf-8')
                except:
                    email_id_str = email_id.decode('latin-1')
            elif isinstance(email_id, str):
                # 如果是字符串，检查是否是bytes的字符串表示形式（如 "b'89'"）
                email_id_str = email_id.strip()
                # 如果字符串是 "b'...'" 或 "b\"...\"" 格式，提取实际内容
                if email_id_str.startswith("b'") and email_id_str.endswith("'"):
                    # 提取 b'89' 中的 89
                    email_id_str = email_id_str[2:-1]
                elif email_id_str.startswith('b"') and email_id_str.endswith('"'):
                    # 提取 b"89" 中的 89
                    email_id_str = email_id_str[2:-1]
            else:
                # 其他类型，转换为字符串
                email_id_str = str(email_id)
            
            # 验证序列号格式（应该是纯数字）
            if not email_id_str or not email_id_str.isdigit():
                print(f"❌ 无效的邮件序列号格式: {email_id_str}")
                print(f"   原始值: {email_id}, 类型: {type(email_id)}")
                mail.logout()
                return False
            
            # 检查邮件是否存在（使用SEARCH命令验证）
            try:
                status, data = mail.search(None, f'UID {email_id_str}')
                if status == 'OK' and data[0]:
                    # 邮件存在，尝试标记为已读
                    status, response = mail.store(email_id_str, '+FLAGS', '\\Seen')
                    if status == 'OK':
                        print(f"✓ 邮件已标记为已读 (序列号: {email_id_str})")
                        mail.logout()
                        return True
                    else:
                        print(f"❌ 标记已读失败: {response}")
                        mail.logout()
                        return False
                else:
                    # 邮件不存在或已被删除
                    print(f"⚠️ 邮件不存在或已被删除 (序列号: {email_id_str})，跳过标记已读")
                    mail.logout()
                    return False
            except Exception as store_err:
                # 如果SEARCH失败，尝试直接STORE（兼容旧格式）
                try:
                    status, response = mail.store(email_id_str, '+FLAGS', '\\Seen')
                    if status == 'OK':
                        print(f"✓ 邮件已标记为已读 (序列号: {email_id_str})")
                        mail.logout()
                        return True
                    else:
                        print(f"❌ 标记已读失败: {response}")
                        print(f"   序列号: {email_id_str}, 类型: {type(email_id)}")
                        mail.logout()
                        return False
                except Exception as e:
                    print(f"❌ 标记邮件为已读时出错: {e}")
                    print(f"   序列号: {email_id_str}, 类型: {type(email_id)}")
                    mail.logout()
                    return False
            
        except Exception as e:
            print(f"❌ 标记邮件为已读时出错: {e}")
            print(f"   邮件ID: {email_id}, 类型: {type(email_id)}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def create_draft_reply(self, initial_email, reply_text):
        """
        发送邮件回复
        注意：QQ邮箱不支持通过IMAP创建草稿，因此直接发送邮件
        """
        result = self.send_reply(initial_email, reply_text)
        return result
    
    def send_reply(self, initial_email, reply_text):
        """
        发送回复邮件
        
        @param initial_email: 原始邮件对象（需要有sender, subject, messageId, references, imap_id属性）
        @param reply_text: 回复内容
        @return: 是否成功
        """
        try:
            # 提取收件人邮箱地址（处理可能包含名称的格式，如 "名称 <email@example.com>"）
            sender_email = initial_email.sender
            if not sender_email:
                print(f"❌ [发送邮件] 错误：收件人地址为空，原始邮件对象: {initial_email}")
                raise ValueError("收件人地址为空，无法发送邮件")
            
            # 如果包含 < >，提取邮箱地址部分
            if '<' in sender_email and '>' in sender_email:
                try:
                    sender_email = sender_email.split('<')[1].split('>')[0].strip()
                except (IndexError, AttributeError) as e:
                    print(f"❌ [发送邮件] 提取邮箱地址失败: {e}, 原始地址: {initial_email.sender}")
                    raise ValueError(f"无法从地址中提取邮箱: {initial_email.sender}")
            
            # 清理可能的空白字符
            sender_email = sender_email.strip()
            
            # 验证邮箱地址格式
            if not sender_email:
                print(f"❌ [发送邮件] 错误：提取后的邮箱地址为空，原始地址: {initial_email.sender}")
                raise ValueError(f"提取后的邮箱地址为空: {initial_email.sender}")
            
            if '@' not in sender_email:
                print(f"❌ [发送邮件] 错误：邮箱地址格式无效（缺少@符号），地址: {sender_email}, 原始: {initial_email.sender}")
                raise ValueError(f"无效的收件人地址格式（缺少@符号）: {sender_email}")
            
            print(f"📧 [发送邮件] 收件人地址: {sender_email}")
            
            # 创建回复邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = sender_email
            msg['Subject'] = f"Re: {initial_email.subject}"
            
            # 设置回复相关的头信息
            if initial_email.messageId:
                msg['In-Reply-To'] = initial_email.messageId
                if initial_email.references:
                    msg['References'] = initial_email.references
                else:
                    msg['References'] = initial_email.messageId
            
            # 添加回复内容
            msg.attach(MIMEText(reply_text, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.email_address, self.auth_code)
            server.send_message(msg)
            server.quit()
            
            print(f"✓ 回复已发送给: {sender_email}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 发送回复失败: {error_msg}")
            print(f"   发件人: {self.email_address}")
            print(f"   收件人: {getattr(initial_email, 'sender', '未设置')}")
            print(f"   主题: {getattr(initial_email, 'subject', '未设置')}")
            import traceback
            print(traceback.format_exc())
            return False
