"""
清理旧的历史记录脚本
用于删除摘要功能实现之前的邮件处理记录
"""
import os
import json
from datetime import datetime

# 用户数据目录
USER_DATA_DIR = "data/users"

def clear_old_history(username=None, before_date=None, dry_run=True):
    """
    清理旧的历史记录
    
    参数:
        username: 用户名，如果为 None 则清理所有用户
        before_date: 删除此日期之前的记录，格式 'YYYY-MM-DD'，如果为 None 则删除所有记录
        dry_run: 是否为试运行模式（只显示将要删除的记录，不实际删除）
    """
    if not os.path.exists(USER_DATA_DIR):
        print(f"❌ 用户数据目录不存在: {USER_DATA_DIR}")
        return
    
    # 获取所有用户的数据文件
    if username:
        files = [f"user_email_data_{username}.json"]
    else:
        files = [f for f in os.listdir(USER_DATA_DIR) if f.startswith("user_email_data_") and f.endswith(".json")]
    
    total_deleted = 0
    
    for filename in files:
        filepath = os.path.join(USER_DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️ 文件不存在: {filepath}")
            continue
        
        # 读取数据
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 读取文件失败: {filepath} - {e}")
            continue
        
        # 提取用户名
        user = filename.replace("user_email_data_", "").replace(".json", "")
        
        # 获取历史记录
        history = data.get('history', [])
        original_count = len(history)
        
        if original_count == 0:
            print(f"ℹ️ 用户 {user}: 没有历史记录")
            continue
        
        # 过滤记录
        if before_date:
            # 删除指定日期之前的记录
            filtered_history = []
            deleted_count = 0
            
            for record in history:
                record_time = record.get('time') or record.get('processed_time', '')
                record_date = record_time[:10] if record_time else ''
                
                if record_date and record_date < before_date:
                    deleted_count += 1
                    if dry_run:
                        print(f"  - 将删除: {record_date} | {record.get('subject', '无主题')[:30]}")
                else:
                    filtered_history.append(record)
            
            data['history'] = filtered_history
        else:
            # 删除所有记录
            deleted_count = original_count
            data['history'] = []
            
            if dry_run:
                print(f"  - 将删除所有 {deleted_count} 条记录")
        
        if deleted_count > 0:
            print(f"📊 用户 {user}: 原有 {original_count} 条记录，将删除 {deleted_count} 条，保留 {len(data.get('history', []))} 条")
            total_deleted += deleted_count
            
            # 如果不是试运行，保存数据
            if not dry_run:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"✅ 已保存: {filepath}")
                except Exception as e:
                    print(f"❌ 保存文件失败: {filepath} - {e}")
        else:
            print(f"ℹ️ 用户 {user}: 没有需要删除的记录")
    
    print(f"\n{'=' * 60}")
    if dry_run:
        print(f"🔍 试运行模式: 共将删除 {total_deleted} 条记录")
        print(f"💡 要实际删除，请运行: python scripts/clear_old_history.py --execute")
    else:
        print(f"✅ 已删除 {total_deleted} 条记录")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='清理旧的历史记录')
    parser.add_argument('--username', type=str, help='指定用户名（不指定则清理所有用户）')
    parser.add_argument('--before', type=str, help='删除此日期之前的记录，格式: YYYY-MM-DD（不指定则删除所有记录）')
    parser.add_argument('--execute', action='store_true', help='实际执行删除（不指定则为试运行模式）')
    parser.add_argument('--yes', action='store_true', help='跳过确认提示，直接执行')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("清理旧的历史记录")
    print("=" * 60)
    
    if args.username:
        print(f"📌 用户: {args.username}")
    else:
        print(f"📌 用户: 所有用户")
    
    if args.before:
        print(f"📅 删除日期: {args.before} 之前的记录")
    else:
        print(f"📅 删除日期: 所有记录")
    
    if args.execute:
        print(f"⚠️ 模式: 实际执行")
        if not args.yes:
            confirm = input("\n确认要删除吗？(yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ 已取消")
                exit(0)
    else:
        print(f"🔍 模式: 试运行（不会实际删除）")
    
    print("=" * 60)
    print()
    
    clear_old_history(
        username=args.username,
        before_date=args.before,
        dry_run=not args.execute
    )
