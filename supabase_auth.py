from supabase import create_client

# Replace with your actual Supabase credentials
SUPABASE_URL = "https://zhlhqutkuvoxlxiiulrj.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def sign_up(email, password):
    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return result.user
    except Exception as e:
        print("Sign-up error:", e)
        return None

def sign_in(email, password):
    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return result.user
    except Exception as e:
        print("Login error:", e)
        return None

def add_user_role(user_id, role="lite"):
    try:
        supabase.table("user_roles").insert({
            "user_id": user_id,
            "role": role
        }).execute()
    except Exception as e:
        print("Insert role error:", e)

def get_user_role(user_id):
    try:
        response = supabase.table("user_roles").select("*").eq("user_id", user_id).execute()
        data = response.data
        if data and len(data) > 0 and "role" in data[0]:
            return data[0]["role"]
    except Exception as e:
        print("Role query error:", e)
    return "lite"
