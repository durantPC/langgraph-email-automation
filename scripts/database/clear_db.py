#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理向量数据库脚本
用于手动删除被锁定的 db 目录
"""
import os
import shutil
import time
import gc

def clear_database():
    """清理向量数据库目录"""
    db_path = "db"
    
    if not os.path.exists(db_path):
        print("✅ 数据库目录不存在，无需清理")
        return
    
    print("正在尝试清理向量数据库...")
    
    # 强制垃圾回收
    gc.collect()
    time.sleep(1)
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            shutil.rmtree(db_path)
            print(f"✅ 数据库目录已成功删除！")
            return
        except PermissionError as pe:
            if attempt < max_retries - 1:
                print(f"⚠️  删除失败（尝试 {attempt + 1}/{max_retries}），等待后重试...")
                time.sleep(2)
                gc.collect()
            else:
                print(f"❌ 无法删除数据库目录，文件可能被其他进程占用")
                print(f"\n请尝试以下方法：")
                print(f"1. 关闭所有 Python 进程（包括后端服务）")
                print(f"2. 在任务管理器中结束所有 python.exe 进程")
                print(f"3. 手动删除 '{os.path.abspath(db_path)}' 目录")
                print(f"4. 或者重启电脑后再运行此脚本")
                raise
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            raise

if __name__ == "__main__":
    try:
        clear_database()
        print("\n✅ 清理完成！现在可以运行 'python create_index.py' 重新创建向量索引")
    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        print(f"请手动删除 '{os.path.abspath('db')}' 目录")

