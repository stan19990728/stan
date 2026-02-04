# 推送代码到 GitHub 指南

你的所有项目文件已在 `C:\Users\win11\github-trending-pushplus` 目录中创建。

## 方法 1：通过 GitHub Web 界面（最简单）

1. 访问 https://github.com/stan19990728/stan
2. 在仓库主页，点击 **Add file** → **Upload files**
3. 选择以下文件并上传：
   - `fetch_trending_pushplus.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
   - `.github/workflows/daily_push.yml`

4. 或者，点击 **Create new file** 逐个创建文件夹和文件

## 方法 2：通过 Git 命令行（推荐）

### 前置要求
- 安装 Git：https://git-scm.com/download/win
- 配置 GitHub SSH 或 HTTPS 凭证

### 推送步骤

```powershell
# 进入项目目录
cd C:\Users\win11\github-trending-pushplus

# 初始化 git 仓库
git init

# 配置 git 用户信息（如未配置过）
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: Add GitHub Trending daily push script"

# 添加远程仓库
git remote add origin https://github.com/stan19990728/stan.git

# 推送到 GitHub（第一次时需要认证）
git push -u origin main

# 如果上面的命令失败，试试：
git push -u origin master
```

### 首次推送可能需要认证

- **HTTPS 方式**：输入你的 GitHub 用户名和 Personal Access Token（PAT）
  - 创建 PAT：https://github.com/settings/tokens
  - 需要勾选 `repo` 权限

- **SSH 方式**：配置 SSH key
  - 生成 SSH key：`ssh-keygen -t ed25519 -C "your.email@example.com"`
  - 在 GitHub Settings → SSH and GPG keys 中添加公钥

## 方法 3：使用 GitHub Desktop（图形界面）

1. 下载 GitHub Desktop：https://desktop.github.com/
2. 登录你的 GitHub 账户
3. 点击 **File** → **Clone repository**
4. 选择 `stan19990728/stan`，克隆到本地
5. 将项目文件复制到克隆目录
6. 在 GitHub Desktop 中提交（Commit）并推送（Push）

## 完成后

推送完成后：
1. 访问 https://github.com/stan19990728/stan 验证文件已上传
2. 在仓库 **Settings** → **Secrets and variables** → **Actions** 中添加：
   - `PUSHPLUS_TOKEN`（你的 PushPlus Token）
3. 在 **Actions** 选项卡启用 workflow
4. 点击 **Run workflow** 测试一次
