# GitHub 每日好玩项目推送（PushPlus 微信版）

该仓库通过 GitHub Actions 每天自动拉取 GitHub Trending（每日热门项目）并使用 PushPlus 推送到微信，完全免费且无需自己常驻服务器。

## 特性

-  **每日自动推送**：GitHub Actions 定时拉取 Trending 项目并推送到微信
-  **两种数据源**：
  - Trending API（默认）：获取每日新增高星项目
  - GitHub Search API（可选）：按创建时间与星数搜索热门项目
-  **灵活过滤**：支持按关键词过滤（例如仅推送 Python/机器学习项目）
-  **美化输出**：HTML 格式，展示项目名称、描述、星数、编程语言
-  **简单部署**：仅需一个 PushPlus Token，无需本地部署

## 快速开始

### 1. 获取 PushPlus Token

1. 访问 [PushPlus 官网](https://www.pushplus.plus/)
2. 用微信扫码登录
3. 复制你的 **Token**（在用户界面顶部）

### 2. 部署到 GitHub

1. Fork 本仓库，或创建新仓库并复制以下文件：
   - `fetch_trending_pushplus.py`
   - `requirements.txt`
   - `.github/workflows/daily_push.yml`

2. 在仓库 **Settings**  **Secrets and variables**  **Actions** 中添加：
   - Key: `PUSHPLUS_TOKEN`
   - Value: 你的 PushPlus Token

3. （可选）在仓库 **Settings**  **Secrets and variables**  **Actions** 中添加：
   - Key: `GITHUB_TOKEN`
   - Value: 你的 GitHub Token（用于增加 API 速率限制，非必需）

### 3. 启用 Workflow

1. 进入 **Actions** 选项卡
2. 选择 **Daily GitHub Trending Push (PushPlus)**
3. 点击 **Enable workflow**
4. （可选）点击 **Run workflow** 手动测试一次

## 配置选项

在 `.github/workflows/daily_push.yml` 中修改以下环境变量：

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `TREND_COUNT` | `10` | 每次推送的项目数量 |
| `USE_SEARCH_API` | `false` | 是否使用 GitHub Search API（可选）|
| `KEYWORDS` | `''` | 过滤关键词，逗号分隔（例如：`python,machine-learning`） |
| `GITHUB_TOKEN` | 无 | 可选，增加 API 速率限制 |

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量并运行
export PUSHPLUS_TOKEN=your_token_here
python fetch_trending_pushplus.py
```

## 脚本说明

- `fetch_trending_pushplus.py`：
  - `fetch_trending_from_api()` - 从 Trending API 拉取项目（默认）
  - `fetch_trending_via_search()` - 从 GitHub Search API 拉取热门项目（可选）
  - `filter_interesting()` - 按关键词过滤项目
  - `build_html()` - 生成微信推送的 HTML 内容
  - `send_pushplus()` - 通过 PushPlus 发送消息

## 常见问题

**Q: 为什么收不到推送？**  
A: 检查 PushPlus Token 是否正确，且已在仓库 Secrets 中配置。可在 Actions 选项卡查看运行日志。

**Q: 能否改变推送时间？**  
A: 修改 `.github/workflows/daily_push.yml` 中的 `cron` 时间表（使用 UTC）。例如 `0 20 * * *` 为北京时间 04:00。

**Q: 能否推送特定语言的项目？**  
A: 在 `KEYWORDS` 环境变量中设置关键词（例如 `python,machine-learning`），脚本会过滤匹配的项目。

## 更新与贡献

如有改进建议或 Bug 报告，欢迎提 Issue 或 PR。
