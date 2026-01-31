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

# Run the automation
print(Fore.GREEN + "正在启动工作流..." + Style.RESET_ALL)
for output in app.stream(initial_state, config):
    for key, value in output.items():
        print(Fore.CYAN + f"完成运行: {key}:" + Style.RESET_ALL)


