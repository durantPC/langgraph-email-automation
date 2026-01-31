"""
自动清理历史记录（无需确认）
"""
import os
import json

USER_DATA_DIR = "data/users"

def auto_clear_history():
    """自动清理所有用户的历史记录"""
    files = [f for f in os.listdir(USER_DATA_DIR) if f.startswith("user_email_data_") and f.endswith(".json")]
    
    total_deleted = 0
    
    print("=" * 60)
    print("开始清理历史记录...")
    print("=" * 60)
    
    for filename in files:
        filepath = os.path.join(USER_DATA_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 读取失败: {filepath} - {e}")
            continue
        
        user = filename.replace("user_email_data_", "").replace(".json", "")
        history = data.get('history', [])
        original_count = len(history)
        
        if original_count == 0:
            print(f"ℹ️ 用户 {user}: 没有历史记录")
            continue
        
        # 清空历史记录
        data['history'] = []
        
        # 保存
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 用户 {user}: 已删除 {original_count} 条记录")
            total_deleted += original_count
        except Exception as e:
            print(f"❌ 保存失败: {filepath} - {e}")
    
    print("=" * 60)
    print(f"✅ 清理完成！共删除 {total_deleted} 条历史记录")
    print("=" * 60)

if __name__ == "__main__":
    auto_clear_history()
