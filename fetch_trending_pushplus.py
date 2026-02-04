#!/usr/bin/env python3
"""拉取 GitHub Trending 并通过 PushPlus 推送到微信。

使用方法：在环境变量 `PUSHPLUS_TOKEN` 中设置你的 PushPlus Token。
支持按语言、关键词筛选；也可推送 GitHub Search 热门项目。
"""
import os
import sys
import requests
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


def build_html(repos):
    lines = []
    for i, repo in enumerate(repos, 1):
        if 'author' in repo and 'name' in repo:
            name = f"{repo.get('author', '')}/{repo.get('name', '')}"
            url = repo.get('url', '')
            desc = repo.get('description', '')
            stars = repo.get('stars', 0)
            language = repo.get('language', 'Unknown')
        else:
            name = repo.get('full_name', '')
            url = repo.get('html_url', '')
            desc = repo.get('description', '') or '暂无描述'
            stars = repo.get('stargazers_count', 0)
            language = repo.get('language', 'Unknown')
        
        desc_display = (desc[:150] + '...' if len(desc) > 150 else desc) if desc else '暂无描述'
        
        lines.append(
            f'<div style="margin: 15px 0; padding: 12px; border-left: 4px solid #0366d6; background: #f6f8fa;">'
            f'<p style="margin: 0 0 8px 0;">'
            f'<b style="font-size: 16px; color: #24292e;">{i}. <a href="{url}" target="_blank" style="color: #0366d6; text-decoration: none;">{name}</a></b>'
            f'</p>'
            f'<p style="margin: 5px 0; color: #586069; font-size: 14px; line-height: 1.5;">'
            f'📝 {desc_display}'
            f'</p>'
            f'<p style="margin: 8px 0 0 0; font-size: 13px; color: #666;">'
            f'⭐ <b style="color: #ffc107;">{stars}</b> stars | 🔧 {language}'
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

    title = f"🔥 GitHub 每日热门项目 ({len(repos)}个) — {datetime.now().date().isoformat()}"
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
