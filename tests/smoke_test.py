"""Quick smoke test for the app."""
import re
import httpx

BASE = "http://127.0.0.1:8000"

def test(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    return condition

def login(email, password):
    """Login helper — creates a fresh client, logs in, returns cookies."""
    c = httpx.Client(follow_redirects=False, base_url=BASE)
    r = c.get("/login")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', r.text)
    csrf = csrf_match.group(1) if csrf_match else ""
    r = c.post("/login", data={"email": email, "password": password, "csrf_token": csrf})
    cookies = dict(r.cookies)
    c.close()
    return r.status_code, cookies

print("=== Smart-Alloc Smoke Tests ===\n")

client = httpx.Client(follow_redirects=False, base_url=BASE)

# 1. Landing page
r = client.get("/")
test("Landing page loads (200)", r.status_code == 200)
test("Landing has hero text", "Smart Project Allocation" in r.text or "Smart-Alloc" in r.text)

# 2. Login page
r = client.get("/login")
test("Login page loads", r.status_code == 200)
test("Login has CSRF token", 'csrf_token' in r.text)

# 3. Register page
r = client.get("/register")
test("Register page loads", r.status_code == 200)

# 4. Dashboard redirect (unauthenticated)
r = client.get("/dashboard")
test("Unauthenticated → redirect to login", r.status_code == 302 and "/login" in r.headers.get("location", ""))

# 5. Login as admin
status, admin_cookies = login("admin@smartalloc.com", "admin123")
test("Admin login succeeds (302 to dashboard)", status == 302)
test("Got access_token cookie", "access_token" in admin_cookies)

# 6. Admin dashboard
r = client.get("/admin/dashboard", cookies=admin_cookies)
test("Admin dashboard loads (200)", r.status_code == 200)
test("Dashboard has stat cards", "card" in r.text and "Total Users" in r.text)
test("Dashboard has users table", "users" in r.text.lower())

# 7. Login as employee
status, emp_cookies = login("alice@smartalloc.com", "employee123")
test("Employee login succeeds", status == 302 and "access_token" in emp_cookies)

# 8. RBAC - employee can't access admin
r = client.get("/admin/dashboard", cookies=emp_cookies)
test("Employee blocked from admin (403)", r.status_code == 403)

# 9. Employee dashboard
r = client.get("/employee/dashboard", cookies=emp_cookies)
test("Employee dashboard loads", r.status_code == 200)

# 10. Employee skills page
r = client.get("/employee/skills", cookies=emp_cookies)
test("Employee skills page loads", r.status_code == 200)

# 11. Login as HR
status, hr_cookies = login("hr@smartalloc.com", "hr123456")
test("HR login succeeds", status == 302 and "access_token" in hr_cookies)

# 12. HR dashboard
r = client.get("/hr/dashboard", cookies=hr_cookies)
test("HR dashboard loads", r.status_code == 200)

# 13. Login as manager
status, mgr_cookies = login("manager1@smartalloc.com", "manager123")
test("Manager login succeeds", status == 302 and "access_token" in mgr_cookies)

# 14. Manager dashboard
r = client.get("/manager/dashboard", cookies=mgr_cookies)
test("Manager dashboard loads", r.status_code == 200)

# 15. Login as client
status, client_cookies = login("client1@example.com", "client123")
test("Client login succeeds", status == 302 and "access_token" in client_cookies)

# 16. Client dashboard
r = client.get("/client/dashboard", cookies=client_cookies)
test("Client dashboard loads", r.status_code == 200)
test("Client sees their projects", "E-Commerce" in r.text or "project" in r.text.lower())

# 17. Client submit project page
r = client.get("/client/submit", cookies=client_cookies)
test("Submit project page loads", r.status_code == 200)
test("Submit form has skill checkboxes", "skill_ids" in r.text)

# 18. Notifications API
r = client.get("/api/notifications/count", cookies=emp_cookies)
test("Notification count API works", r.status_code == 200 and "count" in r.json())

# 19. Logout
r = client.get("/logout", cookies=admin_cookies)
test("Logout clears cookie", r.status_code == 302)

print("\n=== Tests Complete ===")
client.close()
