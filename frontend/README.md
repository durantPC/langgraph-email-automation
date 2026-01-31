# 📧 邮件自动化系统 - 前端

基于 Vue 3 + Element Plus 构建的邮件自动化系统前端界面。

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 📦 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - Vue 3组件库
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP客户端
- **ECharts** - 图表库
- **Vite** - 构建工具
- **Sass** - CSS预处理器

## 📁 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API接口
│   ├── assets/         # 资源文件
│   ├── components/     # 公共组件
│   ├── router/         # 路由配置
│   ├── stores/         # 状态管理
│   ├── styles/         # 全局样式
│   ├── views/          # 页面组件
│   │   ├── Login.vue       # 登录页
│   │   ├── Layout.vue      # 主布局
│   │   ├── Dashboard.vue   # 仪表盘
│   │   ├── Emails.vue      # 邮件管理
│   │   ├── History.vue     # 处理记录
│   │   ├── Knowledge.vue   # 知识库
│   │   └── Settings.vue    # 系统设置
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── index.html          # HTML模板
├── package.json        # 依赖配置
└── vite.config.js      # Vite配置
```

## 🔐 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 🎨 功能模块

### 1. 登录页面
- 用户登录验证
- 记住我功能
- 美观的渐变背景

### 2. 仪表盘
- 统计数据卡片
- 邮件分类饼图
- 处理趋势折线图
- 最近处理记录

### 3. 邮件管理
- 邮件列表展示
- 筛选和搜索
- 邮件详情预览
- 处理和回复功能

### 4. 处理记录
- 历史记录查询
- 按日期/分类/状态筛选
- 导出CSV功能

### 5. 知识库
- 文档管理
- RAG测试功能
- 索引管理

### 6. 系统设置
- 邮箱配置
- AI配置
- 监控配置
- 回复模板

## 🔗 API代理

开发模式下，API请求会代理到后端服务：

```
/api/* -> http://localhost:8000/*
```

## 📝 注意事项

1. 确保后端API服务已启动（端口8000）
2. 首次运行需要安装依赖
3. 开发模式支持热更新

