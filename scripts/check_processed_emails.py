#!/usr/bin/env python3
"""
检查已处理邮件的统计数据
用于调试"已处理"统计是否正确
"""

import json
import os
from datetime import datetime

def load_user_data():
    """加载用户数据"""
    data_file = 'data/users/user_data.json'
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def check_processed_emails(username='admin'):
    """检查指定用户的已处理邮件"""
    user_data = load_user_data()
    
    if username not in user_data:
        print(f"❌ 用户 {username} 不存在")
        return
    
    user_info = user_data[username]
    emails_cache = user_info.get('emails_cache', [])
    history = user_info.get('history', [])
    
    print(f"\n{'='*80}")
    print(f"用户: {username}")
    print(f"{'='*80}\n")
    
    # 统计邮件缓存中的已处理邮件
    print(f"📧 邮件缓存 (emails_cache) 统计:")
    print(f"   总数: {len(emails_cache)} 封\n")
    
    processed_in_cache = {}
    for email in emails_cache:
        status = email.get('status', 'unknown')
        email_id = email.get('id', '')
        subject = email.get('subject', '无主题')
        time = email.get('time', '')
        
        if status not in processed_in_cache:
            processed_in_cache[status] = []
        
        processed_in_cache[status].append({
            'id': email_id[:30] if email_id else '无ID',
            'subject': subject[:50],
            'time': time
        })
    
    # 显示各状态的邮件
    for status in ['pending', 'processed', 'sent', 'skipped', 'failed']:
        emails = processed_in_cache.get(status, [])
        if emails:
            print(f"   状态 '{status}': {len(emails)} 封")
            for i, email in enumerate(emails[:5], 1):  # 只显示前5封
                print(f"      {i}. ID: {email['id']}")
                print(f"         主题: {email['subject']}")
                print(f"         时间: {email['time']}")
            if len(emails) > 5:
                print(f"      ... 还有 {len(emails) - 5} 封")
            print()
    
    # 统计历史记录中的已处理邮件
    print(f"\n📚 历史记录 (history) 统计:")
    print(f"   总数: {len(history)} 条\n")
    
    processed_in_history = {}
    for record in history:
        status = record.get('status', 'unknown')
        record_id = record.get('id', '')
        subject = record.get('subject', '无主题')
        time = record.get('time', '') or record.get('processed_time', '')
        
        if status not in processed_in_history:
            processed_in_history[status] = []
        
        processed_in_history[status].append({
            'id': record_id[:30] if record_id else '无ID',
            'subject': subject[:50],
            'time': time
        })
    
    # 显示各状态的记录
    for status in ['pending', 'success', 'processed', 'sent', 'skipped', 'failed']:
        records = processed_in_history.get(status, [])
        if records:
            print(f"   状态 '{status}': {len(records)} 条")
            for i, record in enumerate(records[:5], 1):  # 只显示前5条
                print(f"      {i}. ID: {record['id']}")
                print(f"         主题: {record['subject']}")
                print(f"         时间: {record['time']}")
            if len(records) > 5:
                print(f"      ... 还有 {len(records) - 5} 条")
            print()
    
    # 计算"已处理"统计（与后端逻辑一致）
    print(f"\n📊 '已处理' 统计计算:")
    print(f"   说明: 已处理包括 'processed'（已生成回复）、'sent'（已发送）、'skipped'（无关邮件已跳过）")
    processed_email_ids = set()
    
    # 从邮件缓存中统计
    cache_processed_count = 0
    for email in emails_cache:
        email_id = email.get('id', '')
        email_status = email.get('status', '')
        if email_id and email_status in ['processed', 'sent', 'skipped']:
            if email_id not in processed_email_ids:
                processed_email_ids.add(email_id)
                cache_processed_count += 1
    
    print(f"   从邮件缓存中找到: {cache_processed_count} 封 (状态为 'processed', 'sent' 或 'skipped')")
    
    # 从历史记录中统计
    history_processed_count = 0
    for record in history:
        record_id = record.get('id', '')
        record_status = record.get('status', '')
        if record_id and record_status in ['success', 'processed', 'sent', 'skipped']:
            if record_id not in processed_email_ids:
                processed_email_ids.add(record_id)
                history_processed_count += 1
    
    print(f"   从历史记录中找到: {history_processed_count} 条新增 (状态为 'success', 'processed', 'sent' 或 'skipped')")
    print(f"\n   ✅ 去重后的'已处理'总数: {len(processed_email_ids)} 封")
    
    # 显示所有已处理邮件的ID（前10个）
    if processed_email_ids:
        print(f"\n   已处理邮件的ID列表（前10个）:")
        for i, email_id in enumerate(list(processed_email_ids)[:10], 1):
            print(f"      {i}. {email_id[:50]}")
        if len(processed_email_ids) > 10:
            print(f"      ... 还有 {len(processed_email_ids) - 10} 个")
    
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
    check_processed_emails(username)
