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
    response = supabase.table("user_roles").select("*").eq("user_id", user_id).execute()
    data = response.data
    if data and len(data) > 0 and "role" in data[0]:
        return data[0]["role"]
    return "lite"  # fallback role



def add_user_role(user_id, role="lite"):
    """向 user_roles 表插入新用户的权限记录"""
    url = f"{SUPABASE_URL}/rest/v1/user_roles"
    data = {
        "user_id": user_id,
        "role": role
    }
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(url, json=data, headers=headers)
    return r.status_code == 201

