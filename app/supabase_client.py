from supabase import create_client, Client

SUPABASE_URL = 'https://ysxfsmqemocaaaikneaa.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlzeGZzbXFlbW9jYWFhaWtuZWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcyOTY4NzIsImV4cCI6MjA2Mjg3Mjg3Mn0.r_NkccmZzxek-8NgXthntP2vYsjS6Mo0vk8LOv7ZwxU'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

result = supabase.table('akun').select('*').execute()
print(result.__dict__)