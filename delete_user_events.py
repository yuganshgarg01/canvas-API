import requests
import time

# ============================================================
#  CONFIGURATION — Fill these in
# ============================================================
CANVAS_URL = "https://canvas.instructure.com"
API_TOKEN  = "paste_your_token_here"
# ============================================================

headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Step 1: Get User ID
print("🔍 Fetching user info...")
user = requests.get(f"{CANVAS_URL}/api/v1/users/self", headers=headers).json()
USER_ID = user["id"]
print(f"✅ Logged in as: {user['name']} (ID: {USER_ID})")

# Step 2: Fetch all events
print("\n📅 Fetching all calendar events...")
events = []
url = f"{CANVAS_URL}/api/v1/calendar_events"
params = {"context_codes[]": f"user_{USER_ID}", "all_events": True, "per_page": 50}

while url:
    response = requests.get(url, headers=headers, params=params)
    events.extend(response.json())
    links = response.headers.get("Link", "")
    url = None
    params = {}
    for part in links.split(","):
        if 'rel="next"' in part:
            url = part.split(";")[0].strip().strip("<>")

print(f"✅ Found {len(events)} events")

if not events:
    print("\n✅ No events to delete. Calendar is already empty!")
    exit()

# Step 3: Confirm
confirm = input(f"\n⚠️  Delete ALL {len(events)} events? Type YES: ").strip()
if confirm != "YES":
    print("❌ Cancelled.")
    exit()

# Step 4: Delete
print("\n🗑️  Deleting...\n")
success = 0
failed  = 0

for e in events:
    r = requests.delete(
        f"{CANVAS_URL}/api/v1/calendar_events/{e['id']}",
        headers=headers,
        params={"cancel_reason": "Bulk delete"}
    )
    if r.status_code in [200, 201]:
        print(f"✅ Deleted: {e.get('title', 'No title')}")
        success += 1
    else:
        print(f"❌ Failed : {e.get('title', 'No title')} → {r.text}")
        failed += 1
    time.sleep(0.3)

print(f"\n🎉 Done! Deleted: {success} | Failed: {failed}")
