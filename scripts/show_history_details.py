"""
显示历史记录详情
让用户确认要删除哪些记录
"""
import os
import json

USER_DATA_DIR = "data/users"

def show_history_details():
    """显示所有用户的历史记录详情"""
    files = [f for f in os.listdir(USER_DATA_DIR) if f.startswith("user_email_data_") and f.endswith(".json")]
    
    total_records = 0
    
    for filename in files:
        filepath = os.path.join(USER_DATA_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 读取失败: {filepath}")
            continue
        
        user = filename.replace("user_email_data_", "").replace(".json", "")
        history = data.get('history', [])
        
        if len(history) == 0:
            continue
        
        print(f"\n{'='*60}")
        print(f"用户: {user}")
        print(f"历史记录数量: {len(history)} 条")
        print(f"{'='*60}")
        
        for i, record in enumerate(history, 1):
            time = record.get('time') or record.get('processed_time', '未知时间')
            subject = record.get('subject', '无主题')
            sender = record.get('sender', '未知发件人')
            status = record.get('status', '未知状态')
            has_body_summary = bool(record.get('body_summary'))
            has_reply_summary = bool(record.get('reply_summary'))
            
            print(f"\n  [{i}] {time}")
            print(f"      主题: {subject[:50]}")
            print(f"      发件人: {sender[:30]}")
            print(f"      状态: {status}")
            print(f"      有原始邮件摘要: {'✅' if has_body_summary else '❌'}")
            print(f"      有回复内容摘要: {'✅' if has_reply_summary else '❌'}")
        
        total_records += len(history)
    
    print(f"\n{'='*60}")
    print(f"总计: {total_records} 条历史记录")
    print(f"{'='*60}")
    print(f"\n💡 这些记录将被清理（用户账号不会被删除）")

if __name__ == "__main__":
    show_history_details()
