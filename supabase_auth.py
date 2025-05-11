import requests

# Supabase 项目连接信息（Elliott 专属）
SUPABASE_URL = "https://zhlhqutkuvoxlxiiulrj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpobGhxdXRrdXZveGx4aWl1bHJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5MzEwNTQsImV4cCI6MjA2MjUwNzA1NH0.6IMR_vD9rYr3IAwsdfCznxlu5I2ATtIAqSJvZ_3TO3s"

def sign_up(email, password):
    """注册新用户（可选扩展）"""
    url = f"{SUPABASE_URL}/auth/v1/signup"
    data = {"email": email, "password": password}
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    r = requests.post(url, json=data, headers=headers)
    return r.json()

def sign_in(email, password):
    """用户登录，返回包含 user ID 的 token 对象"""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    data = {"email": email, "password": password}
    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    r = requests.post(url, json=data, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        return None

def get_user_role(user_id):
    """查询 user_roles 表，返回该用户权限：lite 或 pro"""
    url = f"{SUPABASE_URL}/rest/v1/user_roles?user_id=eq.{user_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    r = requests.get(url, headers=headers)
    data = r.json()
    if data:
        return data[0]["role"]
    else:
        return "lite"  # 默认角色
