import re
import httpx

BASE = "http://127.0.0.1:8000"

c = httpx.Client(follow_redirects=False, base_url=BASE)
# get csrf
r = c.get("/login")
csrf_match = re.search(r'name="csrf_token" value="([^\"]+)"', r.text)
csrf = csrf_match.group(1) if csrf_match else ""
print('csrf:', bool(csrf))
# login
r2 = c.post("/login", data={"email":"hr@smartalloc.com","password":"hr123456","csrf_token":csrf})
print('login status:', r2.status_code)
cookies = dict(r2.cookies)
print('cookies:', cookies)
# get hr dashboard
r3 = c.get("/hr/dashboard", cookies=cookies)
print('hr dashboard status:', r3.status_code)
print('hr dashboard headers:', r3.headers.get('location'))
print('hr dashboard body snippet:', r3.text[:300])

c.close()
