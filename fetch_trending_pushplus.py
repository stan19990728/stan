#!/usr/bin/env python3
"""拉取 GitHub Trending 并通过 PushPlus 推送到微信。

使用方法：在环境变量 `PUSHPLUS_TOKEN` 中设置你的 PushPlus Token。
支持按语言、关键词筛选；也可推送 GitHub Search 热门项目。
"""
import os
import sys
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict

# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


TRENDING_API = "https://ghapi.huchen.dev/repositories"
GITHUB_SEARCH_API = "https://api.github.com/search/repositories"
PUSHPLUS_API = "https://www.pushplus.plus/send"

# 可选：如果有 GitHub Token（增加速率限制）
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')


def fetch_trending_from_api(since='daily', n=20) -> List[Dict]:
    """从 GitHub Trending API 拉取项目。"""
    try:
        url = f"{TRENDING_API}?since={since}&spoken_language=&"
        # 禁用 SSL 验证来规避 SSL 错误
        r = requests.get(url, timeout=15, verify=False)
        r.raise_for_status()
        data = r.json()
        return data[:n] if isinstance(data, list) else []
    except Exception as e:
        print(f"fetch trending API failed: {e}")
        # 尝试备选 API
        try:
            return fetch_trending_via_search(n)
        except:
            return []


def fetch_trending_via_search(n=10) -> List[Dict]:
    """通过 GitHub Search API 拉取最近创建的热门项目（备选）。"""
    try:
        # 拉取过去 7 天创建且 stars >= 10 的项目
        created_after = (datetime.now() - timedelta(days=7)).date().isoformat()
        query = f"created:>={created_after} stars:>=10 sort:stars-desc"

        headers = {}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'

        r = requests.get(
            GITHUB_SEARCH_API,
            params={'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': n},
            headers=headers,
            timeout=15,
            verify=False
        )
        r.raise_for_status()
        data = r.json()
        return data.get('items', [])
    except Exception as e:
        print(f"fetch trending via search failed: {e}")
        return []


def filter_interesting(repos: List[Dict], keywords=None) -> List[Dict]:
    """
    按关键词/语言筛选有趣项目。
    可根据需要添加过滤逻辑（例如排除教学/文档项目）。
    """
    if not keywords:
        # 默认保留所有（可根据需要加过滤，例如排除"awesome"/"list"等）
        return repos

    filtered = []
    kw_lower = [k.lower() for k in keywords]
    for repo in repos:
        name = (repo.get('name') or '').lower()
        desc = (repo.get('description') or '').lower()
        if any(k in name or k in desc for k in kw_lower):
            filtered.append(repo)
    return filtered


def get_readme_summary(repo_name: str, token: str = '') -> str:
    """尝试从 GitHub 获取项目 README 的前 150 字符作为摘要。"""
    try:
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
        
        # 尝试获取 README.md
        url = f"https://api.github.com/repos/{repo_name}/readme"
        r = requests.get(
            url,
            headers={**headers, 'Accept': 'application/vnd.github.v3.raw'},
            timeout=5,
            verify=False
        )
        if r.status_code == 200:
            text = r.text
            # 清理 markdown 语法，提取前 150 字符
            text = re.sub(r'[#*`\[\]\(\)!]', '', text).strip()
            # 去掉多余空白，取第一个有意义的句子或段落
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if lines:
                summary = ' '.join(lines)
                return (summary[:150] + '...' if len(summary) > 150 else summary)
    except:
        pass
    return ''


def translate_to_chinese(text: str) -> str:
    """使用免费翻译 API 将英文翻译成中文。"""
    if not text or len(text.strip()) < 5:
        return text
    
    try:
        # 使用百度翻译 API（免费）
        url = "https://fanyi.baidu.com/v2transapi"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        data = {
            'from': 'en',
            'to': 'zh',
            'query': text[:500],  # 限制长度
            'simple_means_flag': '3',
            'sign': '',
            'token': ''
        }
        r = requests.post(url, headers=headers, data=data, timeout=8, verify=False)
        if r.status_code == 200:
            result = r.json()
            if 'trans_result' in result and 'data' in result['trans_result']:
                translated = result['trans_result']['data'][0].get('dst', '')
                if translated:
                    return translated
    except:
        pass
    
    # 备用：使用简单的字典翻译服务
    try:
        api_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={requests.utils.quote(text[:300])}"
        r = requests.get(api_url, timeout=5, verify=False)
        if r.status_code == 200:
            result = r.json()
            if result and len(result) > 0 and len(result[0]) > 0:
                translated = ''.join([item[0] for item in result[0] if item[0]])
                return translated
    except:
        pass
    
    return text  # 翻译失败，返回原文



def build_html(repos):
    lines = []
    for i, repo in enumerate(repos, 1):
        if 'author' in repo and 'name' in repo:
            name = f"{repo.get('author', '')}/{repo.get('name', '')}"
            url = repo.get('url', '')
            desc = repo.get('description', '')
            stars = repo.get('stars', 0)
            language = repo.get('language', 'Unknown')
            repo_name = f"{repo.get('author', '')}/{repo.get('name', '')}"
        else:
            name = repo.get('full_name', '')
            url = repo.get('html_url', '')
            desc = repo.get('description', '') or ''
            stars = repo.get('stargazers_count', 0)
            language = repo.get('language', 'Unknown')
            repo_name = repo.get('full_name', '')
        
        # 如果描述为空或过短，尝试获取 README 摘要
        if not desc or len(desc) < 30:
            readme_summary = get_readme_summary(repo_name, GITHUB_TOKEN)
            if readme_summary:
                desc = readme_summary
        
        desc_display = (desc[:150] + '...' if len(desc) > 150 else desc) if desc else '暂无描述'
        
        lines.append(
            f'<div style="margin: 15px 0; padding: 12px; border-left: 4px solid #0366d6; background: #f6f8fa;">'
            f'<p style="margin: 0 0 8px 0;">'
            f'<b style="font-size: 16px; color: #24292e;">{i}. <a href="{url}" target="_blank" style="color: #0366d6; text-decoration: none;">{name}</a></b>'
            f'</p>'
            f'<p style="margin: 5px 0; color: #586069; font-size: 14px; line-height: 1.5;">'
            f' {desc_display}'
            f'</p>'
            f'<p style="margin: 8px 0 0 0; font-size: 13px; color: #666;">'
            f' <b style="color: #ffc107;">{stars}</b> stars |  {language}'
            f'</p>'
            f'</div>'
        )
    return ''.join(lines)


def send_pushplus(token: str, title: str, content: str) -> Dict:
    """通过 PushPlus 推送消息到微信。"""
    payload = {
        'token': token,
        'title': title,
        'content': content,
        'template': 'html'
    }
    try:
        r = requests.post(PUSHPLUS_API, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {'error': str(e)}


def main():
    token = os.getenv('PUSHPLUS_TOKEN')
    if not token:
        print('Error: Please set PUSHPLUS_TOKEN environment variable')
        sys.exit(2)

    count = int(os.getenv('TREND_COUNT', '10'))
    use_search = os.getenv('USE_SEARCH_API', 'false').lower() == 'true'
    keywords = os.getenv('KEYWORDS', '')

    print(f"Fetching {count} trending repositories...")
    if use_search:
        repos = fetch_trending_via_search(n=count + 5)
    else:
        repos = fetch_trending_from_api(since='daily', n=count + 5)

    if not repos:
        print('Error: No trending repos fetched')
        sys.exit(1)

    # 过滤（可选）
    if keywords:
        repos = filter_interesting(repos, keywords.split(','))
        print(f"Filtered to {len(repos)} repos with keywords")

    # 取前 N 个
    repos = repos[:count]

    if not repos:
        print('Error: No repos after filtering')
        sys.exit(1)

    title = f" GitHub 每日热门项目 ({len(repos)}个)  {datetime.now().date().isoformat()}"
    content = build_html(repos)

    print(f"Sending {len(repos)} repos to WeChat...")
    res = send_pushplus(token, title, content)

    if 'error' in res:
        print(f"Error sending: {res}")
        sys.exit(1)
    else:
        print(f" Successfully pushed to WeChat: {res}")


if __name__ == '__main__':
    main()
