# 📧 邮件自动化系统

基于 **AI代理** 和 **RAG** 的智能客户支持邮件自动化系统。

![workflow](workflow.png)

## ✨ 功能特性

- 🔍 **智能分类** - AI自动分类邮件（产品咨询/客户投诉/客户反馈/无关邮件）
- 🤖 **RAG检索** - 基于知识库检索相关信息生成精准回复
- ✍️ **自动回复** - AI生成专业的邮件回复内容
- ✅ **质量校验** - 自动校验回复质量，确保专业性
- 🌐 **Web管理** - 美观的Web界面，轻松管理邮件

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **后端** | Python + FastAPI + LangGraph |
| **前端** | Vue 3 + Element Plus + ECharts |
| **LLM** | 硅基流动 (Qwen2-VL-7B) |
| **向量库** | ChromaDB |
| **邮箱** | QQ邮箱 SMTP/IMAP |

## 📁 项目结构

```
langgraph-email-automation/
│
├── 📄 根目录文件
│   ├── backend_api.py          # 后端API服务（FastAPI）
│   ├── main.py                  # 命令行单次运行
│   ├── main_continuous.py      # 命令行持续监控
│   ├── requirements.txt        # Python依赖
│   ├── workflow.png             # 工作流示意图
│   ├── README.md                # 项目说明文档
│   └── .env                    # 环境变量配置（需创建）
│
├── 📁 src/                     # 后端核心代码
│   ├── agents.py               # AI代理定义（LangChain）
│   ├── graph.py                # LangGraph工作流定义
│   ├── nodes.py                # 工作流节点实现
│   ├── prompts.py              # 提示词模板
│   ├── state.py                # 状态定义
│   ├── structure_outputs.py    # 结构化输出定义
│   └── tools/
│       └── QQEmailTools.py     # QQ邮箱工具（IMAP/SMTP）
│
├── 📁 frontend/                # 前端项目（Vue 3）
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API接口封装
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # 状态管理（Pinia）
│   │   ├── utils/              # 工具函数
│   │   └── styles/             # 样式文件
│   ├── package.json
│   └── vite.config.js
│
├── 📁 data/                    # 数据目录
│   ├── agency.txt              # 知识库文档
│   └── users/                  # 用户数据目录
│       ├── user_data.json      # 用户账号数据
│       ├── user_email_data_*.json  # 用户邮件历史
│       └── username_mapping.json  # 用户名映射
│
├── 📁 db/                      # 向量数据库（ChromaDB，默认）
├── 📁 db_1024/                 # 向量数据库（1024维）
├── 📁 db_2560/                 # 向量数据库（2560维）
└── 📁 db_4096/                 # 向量数据库（4096维）
│
├── 📁 docs/                    # 项目文档
│   ├── README.md               # 文档索引
│   ├── 使用文档.md             # 快速上手指南
│   ├── 说明文档.md             # 完整技术文档
│   └── ...                     # 其他文档
│
└── 📁 scripts/                 # 脚本目录
    ├── start_all.bat           # 一键启动
    ├── start_backend.bat       # 启动后端
    ├── start_frontend.bat      # 启动前端
    └── database/               # 数据库脚本
        ├── create_index.py     # 创建向量索引（默认）
        ├── create_index_1024.py # 创建1024维索引
        ├── create_index_2560.py # 创建2560维索引
        ├── create_index_4096.py # 创建4096维索引
        └── clear_db.py         # 清理数据库
```

**详细目录说明请查看** [说明文档 - 项目目录结构](docs/说明文档.md#项目目录结构)

## 🚀 快速开始

### 1. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# QQ邮箱配置
MY_EMAIL=your_email@qq.com
QQ_EMAIL_AUTH_CODE=your_auth_code

# 硅基流动API
SILICONFLOW_API_KEY=your_api_key
```

### 3. 创建向量索引

```bash
python scripts/database/create_index.py
```

**注意**：如果需要创建不同维度的向量索引，可以使用：
- `scripts/database/create_index_1024.py` - 1024维
- `scripts/database/create_index_2560.py` - 2560维
- `scripts/database/create_index_4096.py` - 4096维

### 4. 启动服务

**方式一：一键启动（推荐）**
```bash
# Windows
scripts\start_all.bat
```

**方式二：分别启动**
```bash
# 终端1 - 后端
python backend_api.py

# 终端2 - 前端
cd frontend
npm run dev
```

### 5. 访问系统

- 🌐 **前端界面**: http://localhost:3000
- 📡 **后端API**: http://localhost:8000
- 📚 **API文档**: http://localhost:8000/docs

**默认账号**: `admin` / `admin123`

## 📖 运行模式

| 模式 | 命令 | 说明 |
|------|------|------|
| **Web界面** | `python backend_api.py` + 前端 | 完整的Web管理界面 |
| **单次运行** | `python main.py` | 处理当前未读邮件后结束 |
| **持续监控** | `python main_continuous.py` | 每15分钟自动检查邮箱 |

详细说明请查看 [docs/运行模式说明.md](docs/运行模式说明.md)

## 📚 文档

### 快速开始
- 📖 **[使用文档](docs/使用文档.md)** ⭐ 推荐 - 简单精炼的快速上手指南
- 🚀 **[快速开始](docs/快速开始.md)** - 详细的5分钟配置指南

### 配置指南
- ⚙️ **[配置说明](docs/配置说明.md)** - 完整的配置说明
- 🔑 **[硅基流动配置指南](docs/硅基流动配置指南.md)** - API配置详解
- 🎯 **[模型选择说明](docs/模型选择说明.md)** - 模型选择指南

### 使用指南
- 📖 **[运行模式说明](docs/运行模式说明.md)** - 三种运行模式详解

### 技术文档
- 📘 **[说明文档](docs/说明文档.md)** - 详细完整的技术文档（架构、API、部署等）

### 项目历史
- 📜 **[变更摘要](docs/变更摘要.md)** - 重大变更记录
- 📝 **[更新日志](docs/更新日志.md)** - 版本更新历史

**📋 [完整文档索引](docs/README.md)** - 查看所有文档的导航和分类  
**📁 [文档结构说明](docs/文档结构说明.md)** - 了解文档组织方式

## 🔧 配置说明

### QQ邮箱授权码获取

1. 登录 QQ邮箱网页版
2. 进入 "设置" → "账户"
3. 开启 "IMAP/SMTP服务"
4. 生成授权码

### 硅基流动API

1. 访问 [硅基流动平台](https://siliconflow.cn/)
2. 注册并登录
3. 创建API密钥

## 📝 更新日志

查看 [docs/更新日志.md](docs/更新日志.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
