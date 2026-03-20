import requests
import time

# ============================================================
#  CONFIGURATION — Fill these in
# ============================================================
CANVAS_URL = "https://canvas.instructure.com"
API_TOKEN  = "paste_your_token_here"
COURSE_ID  = "Course ID here"
# ============================================================

headers = {"Authorization": f"Bearer {API_TOKEN}"}

# ============================================================
# DESIRED NAVIGATION ORDER (visible to students)
# ============================================================
VISIBLE_TABS = [
    "home",
    "syllabus",
    "modules",
    "assignments",
    "quizzes",
    "discussions",
    "collaborations",
    "grades",
    "announcements",
    "people",
    "context_external_tool",   # Course Analytics
    "question_banks",          # Item Banks
]

# ============================================================
# TABS TO HIDE FROM STUDENTS
# ============================================================
HIDDEN_TABS = [
    "outcomes",
    "rubrics",
    "pages",
    "files",
    "attendance",
    "conferences",             # Big Blue Button
    "external_tools",          # Lucid (Whiteboard)
]

# ============================================================
# STEP 1: FETCH ALL CURRENT TABS
# ============================================================
print("\n" + "="*55)
print("📋 Fetching current navigation tabs...")
print("="*55)

response = requests.get(
    f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs",
    headers=headers
)

if response.status_code != 200:
    print(f"❌ Error fetching tabs: {response.status_code} → {response.text}")
    exit()

tabs = response.json()
print(f"✅ Found {len(tabs)} tabs\n")

# Show current tabs
print(f"{'ID':<30} {'Label':<30} {'Position':<10} {'Hidden'}")
print("-" * 80)
for t in tabs:
    print(f"{t.get('id',''):<30} {t.get('label',''):<30} {str(t.get('position','')):<10} {t.get('hidden', False)}")

# ============================================================
# STEP 2: UPDATE EACH TAB
# ============================================================
print("\n" + "="*55)
print("🔄 Updating navigation order...")
print("="*55 + "\n")

success = 0
failed  = 0

# Update visible tabs with correct position
for position, tab_id in enumerate(VISIBLE_TABS, start=1):
    # Find matching tab
    matched = next((t for t in tabs if t.get("id", "").lower() == tab_id.lower()), None)

    if not matched:
        print(f"⚠️  Tab not found: {tab_id} (skipping)")
        continue

    response = requests.put(
        f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs/{matched['id']}",
        headers=headers,
        json={
            "position": position,
            "hidden": False
        }
    )

    if response.status_code in [200, 201]:
        print(f"✅ Position {position:02d} | Visible  | {matched.get('label', tab_id)}")
        success += 1
    else:
        print(f"❌ Failed   | {matched.get('label', tab_id)} → {response.status_code}: {response.text}")
        failed += 1

    time.sleep(0.3)

# Hide unwanted tabs
print()
for tab_id in HIDDEN_TABS:
    matched = next((t for t in tabs if t.get("id", "").lower() == tab_id.lower()), None)

    if not matched:
        # Try partial match for external tools
        matched = next((t for t in tabs if tab_id.lower() in t.get("label", "").lower()), None)

    if not matched:
        print(f"⚠️  Tab not found: {tab_id} (skipping)")
        continue

    response = requests.put(
        f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs/{matched['id']}",
        headers=headers,
        json={"hidden": True}
    )

    if response.status_code in [200, 201]:
        print(f"🚫 Hidden            | {matched.get('label', tab_id)}")
        success += 1
    else:
        print(f"❌ Failed   | {matched.get('label', tab_id)} → {response.status_code}: {response.text}")
        failed += 1

    time.sleep(0.3)

# ============================================================
# STEP 3: VERIFY FINAL ORDER
# ============================================================
print("\n" + "="*55)
print("🔍 Final Navigation Order:")
print("="*55)

response = requests.get(
    f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs",
    headers=headers
)

if response.status_code == 200:
    updated_tabs = sorted(response.json(), key=lambda x: x.get("position", 999))
    print(f"\n{'Pos':<6} {'Label':<30} {'Visible to Students'}")
    print("-" * 55)
    for t in updated_tabs:
        hidden  = t.get("hidden", False)
        status  = "🚫 Hidden" if hidden else "✅ Visible"
        print(f"{str(t.get('position','')):<6} {t.get('label',''):<30} {status}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*55)
print(f"🎉 DONE! Updated: {success} | Failed: {failed}")
print("="*55)
print("\n👉 Check your Canvas course to see the updated navigation!")
