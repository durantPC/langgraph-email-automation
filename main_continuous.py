"""
持续监控版本 - 每隔一段时间检查新邮件
"""
import time
from colorama import Fore, Style
from src.graph import Workflow
from dotenv import load_dotenv

# Load all env variables
load_dotenv()

# config - 增加递归限制以处理更多邮件
config = {'recursion_limit': 200}

workflow = Workflow()
app = workflow.app

initial_state = {
    "emails": [],
    "current_email": {
      "id": "",
      "threadId": "",
      "messageId": "",
      "references": "",
      "sender": "",
      "subject": "",
      "body": "",
      "imap_id": b""
    },
    "email_category": "",
    "generated_email": "",
    "rag_queries": [],
    "retrieved_documents": "",
    "writer_messages": [],
    "sendable": False,
    "trials": 0
}

# 持续监控配置
CHECK_INTERVAL = 900  # 每15分钟检查一次（900秒）

def format_time(seconds):
    """将秒数转换为易读的时间格式"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}小时{minutes}分钟"
        return f"{hours}小时"

print(Fore.GREEN + "=" * 60)
print("🚀 邮件自动化系统 - 持续监控模式")
print("=" * 60 + Style.RESET_ALL)
print(Fore.YELLOW + f"⏰ 检查间隔: {format_time(CHECK_INTERVAL)}" + Style.RESET_ALL)
print(Fore.YELLOW + "💡 按 Ctrl+C 停止监控\n" + Style.RESET_ALL)

try:
    cycle_count = 0
    while True:
        cycle_count += 1
        print(Fore.CYAN + f"\n{'='*60}")
        print(f"🔄 第 {cycle_count} 次检查 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}" + Style.RESET_ALL)
        
        try:
            # 运行工作流
            for output in app.stream(initial_state, config):
                for key, value in output.items():
                    print(Fore.CYAN + f"完成运行: {key}" + Style.RESET_ALL)
            
            print(Fore.GREEN + f"✅ 本轮检查完成" + Style.RESET_ALL)
            
        except Exception as e:
            print(Fore.RED + f"❌ 处理邮件时出错: {e}" + Style.RESET_ALL)
            import traceback
            traceback.print_exc()
        
        # 等待下一次检查
        print(Fore.YELLOW + f"\n⏳ 等待 {format_time(CHECK_INTERVAL)} 后进行下一次检查..." + Style.RESET_ALL)
        time.sleep(CHECK_INTERVAL)

except KeyboardInterrupt:
    print(Fore.GREEN + "\n\n👋 收到停止信号，正在退出...")
    print("=" * 60)
    print("✅ 邮件自动化系统已停止")
    print("=" * 60 + Style.RESET_ALL)

