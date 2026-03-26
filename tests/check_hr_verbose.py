import re
import httpx

BASE = "http://127.0.0.1:8000"

def run():
    c = httpx.Client(follow_redirects=False, base_url=BASE, timeout=10.0)
    # get csrf
    r = c.get("/login")
    print('GET /login', r.status_code)
    csrf_match = re.search(r'name="csrf_token" value="([^\"]+)"', r.text)
    csrf = csrf_match.group(1) if csrf_match else ""
    print('csrf token found:', bool(csrf))

    # login
    r2 = c.post("/login", data={"email":"hr@smartalloc.com","password":"hr123456","csrf_token":csrf})
    print('POST /login', r2.status_code)
    print('Set-Cookie header:', r2.headers.get('set-cookie'))
    cookies = dict(r2.cookies)
    print('cookies keys:', list(cookies.keys()))

    # get hr dashboard
    r3 = c.get("/hr/dashboard", cookies=cookies)
    print('GET /hr/dashboard status:', r3.status_code)
    print('Headers snippet:', {k:v for k,v in r3.headers.items() if k.lower() in ('content-type','location')})
    body = r3.text or ''
    print('Body length:', len(body))
    print('Body snippet (first 800 chars):')
    print(body[:800])

    c.close()

if __name__ == '__main__':
    run()
