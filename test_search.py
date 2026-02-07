#!/usr/bin/env python3
"""测试案件搜索功能"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. 登录获取 token
print("1. 登录...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "testuser", "password": "123456"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
token = login_response.json()["access_token"]
print(f"[OK] 登录成功，Token: {token[:20]}...")

# 2. 搜索案件
print("\n2. 搜索案件...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

search_data = {
    "query": "房屋买卖",
    "page": 1,
    "page_size": 10
}

search_response = requests.post(
    f"{BASE_URL}/cases/search",
    headers=headers,
    json=search_data
)

print(f"状态码: {search_response.status_code}")
print(f"响应: {json.dumps(search_response.json(), ensure_ascii=False, indent=2)}")

if search_response.status_code == 200:
    result = search_response.json()
    print(f"\n[OK] 搜索成功！")
    print(f"  总数: {result['total']}")
    print(f"  当前页: {result['page']}")
    print(f"  每页数量: {result['page_size']}")
    print(f"\n案件列表:")
    for case in result['results']:
        print(f"  - [{case['id']}] {case['title']}")
        print(f"    法院: {case['court']}")
        print(f"    类型: {case['case_type']}")
        print()
