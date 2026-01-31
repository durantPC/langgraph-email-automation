# 🚀 快速开始指南

> 5分钟快速部署邮件自动化系统

## 📋 目录

- [系统要求](#系统要求)
- [快速安装](#快速安装)
- [配置步骤](#配置步骤)
- [启动系统](#启动系统)
- [首次使用](#首次使用)
- [常见问题](#常见问题)

---

## 📌 系统要求

### 必需环境
- **Python**: 3.9 或更高版本
- **Node.js**: 16.0 或更高版本
- **npm**: 8.0 或更高版本

### 检查环境
```bash
python --version    # 应显示 Python 3.9+
node --version      # 应显示 v16.0+
npm --version       # 应显示 8.0+
```

---

## ⚡ 快速安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd langgraph-email-automation
```

### 2. 安装后端依赖
```bash
pip install -r requirements.txt
```

**国内用户加速（推荐）：**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 安装前端依赖
```bash
cd frontend
npm install
```

**国内用户加速（推荐）：**
```bash
npm install --registry=https://registry.npmmirror.com
```

---

## ⚙️ 配置步骤

### 步骤1：获取QQ邮箱授权码

1. 登录 [QQ邮箱网页版](https://mail.qq.com/)
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 开启 **IMAP/SMTP服务**
5. 点击 **生成授权码**，按提示发送短信
6. **复制授权码**（16位字母，如：`abcdefghijklmnop`）

### 步骤2：获取硅基流动API密钥

1. 访问 [硅基流动平台](https://siliconflow.cn/)
2. 注册并登录账号
3. 进入 **控制台** → **API密钥**
4. 点击 **创建密钥**
5. **复制API密钥**（格式：`sk-xxxxxx...`）

💡 **提示**：新用户通常有免费额度，足够测试使用！

### 步骤3：创建配置文件

在项目根目录创建 `.env` 文件：

```env
# QQ邮箱配置
MY_EMAIL=你的QQ邮箱@qq.com
QQ_EMAIL_AUTH_CODE=你的16位授权码

# 硅基流动API配置
SILICONFLOW_API_KEY=sk-你的API密钥
```

**示例：**
```env
MY_EMAIL=123456789@qq.com
QQ_EMAIL_AUTH_CODE=abcdefghijklmnop
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 步骤4：创建向量数据库

```bash
# 返回项目根目录
cd ..

# 创建向量索引
python scripts/database/create_index.py
```

**预期输出：**
```
正在创建向量索引...
✅ 索引创建成功！
Answer: ...（测试问答）
```

⏱️ **耗时**：首次运行约1-2分钟（需要下载嵌入模型）

---

## 🎬 启动系统

### 方式一：一键启动（推荐）

**Windows用户：**
```bash
scripts\start_all.bat
```

这会自动启动后端和前端服务。

### 方式二：手动启动

**终端1 - 启动后端：**
```bash
python backend_api.py
```

**预期输出：**
```
✅ [摘要线程池] 创建摘要生成线程池: 15 个工作线程
============================================================
🚀 邮件自动化系统 - 后端API服务
============================================================
📡 API地址: http://localhost:8000
📚 API文档: http://localhost:8000/docs
============================================================
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
✅ [WS] 主事件循环已保存，用于线程安全推送
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**终端2 - 启动前端：**
```bash
cd frontend
npm run dev
```

**预期输出：**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

---

## 🌐 首次使用

### 1. 访问系统

打开浏览器访问：**http://localhost:3000**

### 2. 登录系统

**默认账号：**
- 用户名：`admin`
- 密码：`admin123`

### 3. 配置邮箱

登录后，点击右上角 **设置** 图标：

1. **邮箱配置**
   - 邮箱地址：填写你的QQ邮箱
   - 授权码：填写QQ邮箱授权码

2. **AI模型配置**（可选，使用默认即可）
   - 回复模型：`Qwen/Qwen2.5-7B-Instruct`
   - 嵌入模型：`BAAI/bge-large-zh-v1.5`

3. **运行参数**（可选）
   - 检查间隔：900秒（15分钟）
   - 批量大小：4封
   - 单封并发：4个

4. 点击 **保存设置**

### 4. 开始使用

#### 方式A：手动处理邮件
1. 点击 **邮件管理** 页面
2. 点击 **刷新邮件** 按钮
3. 选择邮件，点击 **处理** 按钮
4. 查看AI生成的回复
5. 点击 **发送回复** 按钮

#### 方式B：自动处理邮件
1. 在 **设置** 页面开启 **自动处理**
2. 系统会自动监控邮箱
3. 新邮件到达时自动处理
4. 在 **历史记录** 查看处理结果

---

## 🎯 功能概览

### 📊 仪表盘
- 实时统计数据
- 邮件分类分布
- 处理趋势图表
- 最近活动记录

### 📧 邮件管理
- 查看未读邮件
- 手动处理邮件
- 批量处理邮件
- 编辑AI回复
- 发送回复

### 📜 历史记录
- 查看处理历史
- 搜索邮件
- 导出数据（Excel/CSV）
- 查看详细信息

### ⚙️ 设置
- 邮箱配置
- AI模型配置
- 运行参数
- 自动处理开关
- 自动发送开关

---

## ❓ 常见问题

### Q1: 安装依赖时报错？

**问题：** `pip install` 速度慢或失败

**解决：** 使用国内镜像源
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### Q2: 无法连接QQ邮箱？

**问题：** 提示 "邮箱连接失败"

**检查清单：**
1. ✅ 确认QQ邮箱地址正确
2. ✅ 确认授权码是16位字母（不是QQ密码！）
3. ✅ 确认已开启IMAP/SMTP服务
4. ✅ 检查网络连接

**重新获取授权码：**
1. 登录QQ邮箱网页版
2. 设置 → 账户 → 关闭IMAP服务
3. 重新开启IMAP服务
4. 生成新的授权码

---

### Q3: API调用失败？

**问题：** 提示 "API调用失败" 或 "401错误"

**检查清单：**
1. ✅ 确认API密钥正确（以 `sk-` 开头）
2. ✅ 确认API密钥有效（未过期）
3. ✅ 确认有足够的API额度
4. ✅ 检查网络连接

**测试API：**
```bash
curl -X POST "https://api.siliconflow.cn/v1/chat/completions" \
  -H "Authorization: Bearer sk-你的密钥" \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"user","content":"你好"}]}'
```

---

### Q4: 向量数据库错误？

**问题：** 提示 "向量数据库错误"

**解决：** 删除并重建数据库
```bash
# Windows
rmdir /s /q db
python scripts/database/create_index.py

# Linux/Mac
rm -rf db
python scripts/database/create_index.py
```

---

### Q5: 前端无法访问？

**问题：** 浏览器无法打开 http://localhost:3000

**检查清单：**
1. ✅ 确认前端已启动（`npm run dev`）
2. ✅ 确认端口3000未被占用
3. ✅ 检查防火墙设置
4. ✅ 尝试访问 http://127.0.0.1:3000

**更换端口：**
编辑 `frontend/vite.config.js`：
```javascript
export default defineConfig({
  server: {
    port: 3001  // 改为其他端口
  }
})
```

---

### Q6: 后端无法启动？

**问题：** 运行 `python backend_api.py` 报错

**常见错误：**

**错误1：** `ModuleNotFoundError: No module named 'xxx'`
```bash
pip install xxx
```

**错误2：** `Address already in use`（端口被占用）
```bash
# Windows - 查找占用8000端口的进程
netstat -ano | findstr :8000
# 结束进程
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -i :8000
kill -9 <进程ID>
```

**错误3：** `.env` 文件未找到
- 确认 `.env` 文件在项目根目录
- 确认文件名正确（不是 `.env.txt`）

---

### Q7: 邮件处理失败？

**问题：** 邮件状态显示 "处理失败"

**可能原因：**
1. API额度不足
2. 网络连接问题
3. 邮件内容过长
4. 模型不支持

**解决：**
1. 检查API额度
2. 检查网络连接
3. 查看后端日志（终端输出）
4. 尝试更换模型

---

### Q8: 如何更换AI模型？

**在Web界面更换：**
1. 进入 **设置** 页面
2. 在 **AI模型配置** 中选择模型
3. 点击 **保存设置**

**支持的模型：**
- `Qwen/Qwen2.5-7B-Instruct`（默认，速度快）
- `Qwen/Qwen2.5-72B-Instruct`（更强大）
- `deepseek-ai/DeepSeek-V2.5`（推理能力强）
- 更多模型请查看硅基流动平台

---

## 📚 进阶使用

### 自定义知识库

编辑 `data/agency.txt` 文件，添加你的业务知识：

```text
# 产品信息
我们的产品是...

# 常见问题
Q: 如何退款？
A: 退款流程是...

# 联系方式
客服电话：400-xxx-xxxx
```

**重建索引：**
```bash
python scripts/database/create_index.py
```

### 批量处理邮件

1. 点击 **邮件管理** 页面
2. 点击 **处理全部** 按钮
3. 系统会并发处理所有待处理邮件
4. 在 **历史记录** 查看结果

### 导出数据

1. 进入 **历史记录** 页面
2. 点击 **导出** 按钮
3. 选择格式（Excel 或 CSV）
4. 下载文件

---

## 🔗 相关链接

- **项目文档**: [README.md](README.md)
- **详细配置**: [docs/配置说明.md](docs/配置说明.md)
- **使用指南**: [docs/使用文档.md](docs/使用文档.md)
- **API文档**: http://localhost:8000/docs（启动后访问）

---

## 💡 提示

1. **首次使用建议**：先用手动模式处理几封邮件，熟悉系统后再开启自动处理
2. **API额度**：注意监控API使用量，避免超出额度
3. **数据备份**：定期备份 `data/users/` 目录
4. **日志查看**：遇到问题时查看终端日志输出
5. **模型选择**：根据需求选择合适的模型（速度 vs 质量）

---

## 🎉 开始使用

现在你已经完成了所有配置，可以开始使用邮件自动化系统了！

**祝你使用愉快！** 🚀

如有问题，请查看 [常见问题](#常见问题) 或提交 Issue。
