## ⚡ 快速推送指南

### 项目文件位置
```
C:\Users\win11\github-trending-pushplus\
├── fetch_trending_pushplus.py      # 主脚本
├── requirements.txt                # Python 依赖
├── README.md                       # 项目文档
├── .gitignore                      # Git 忽略规则
├── .github/workflows/daily_push.yml # GitHub Actions 工作流
└── PUSH_GUIDE.md                   # 详细推送指南
```

### 🚀 最快推送方式（3 分钟）

#### 前提：已安装 Git
如果未安装，从 https://git-scm.com/download/win 下载安装

#### 推送命令
```powershell
cd C:\Users\win11\github-trending-pushplus

git init
git config user.name "Your Name"
git config user.email "your@email.com"
git add .
git commit -m "Initial commit: GitHub trending daily push"
git remote add origin https://github.com/stan19990728/stan.git
git push -u origin main
```

#### 如果 `main` 分支不存在
```powershell
git push -u origin master
```

### 🔧 推送后的配置步骤

1. **打开仓库**：https://github.com/stan19990728/stan

2. **添加 Secret**：
   - Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `PUSHPLUS_TOKEN`
   - Value: 你的 PushPlus Token

3. **启用 Workflow**：
   - Actions 选项卡
   - 选择 "Daily GitHub Trending Push (PushPlus)"
   - 点击 "Enable workflow"

4. **测试运行**：
   - 点击 "Run workflow" 手动触发
   - 检查你的微信，应该会收到推送

### ✅ 验证

- [ ] 代码已推送到 GitHub
- [ ] `PUSHPLUS_TOKEN` Secret 已配置
- [ ] Workflow 已启用
- [ ] 已手动运行一次验证（收到微信推送）

### 📋 功能说明

- **每天定时推送**：每天 09:00（北京时间）推送 10 个 GitHub 热门项目
- **自定义数量**：修改 workflow 中的 `TREND_COUNT` 环境变量
- **关键词过滤**：设置 `KEYWORDS` 环境变量过滤特定类型项目（例如：`python,machine-learning`）
- **两种数据源**：支持 Trending API（默认）和 GitHub Search API

### 🔗 相关链接

- PushPlus: https://www.pushplus.plus/
- GitHub Actions 文档: https://docs.github.com/en/actions
- Git 下载: https://git-scm.com/download/win
