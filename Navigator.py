import requests
import time

# ============================================================
#  CONFIGURATION — Fill these in
# ============================================================
CANVAS_URL = "https://canvas.instructure.com"
API_TOKEN  = "paste_your_token_here"
COURSE_ID  = " Paste course ID"
# ============================================================

headers = {"Authorization": f"Bearer {API_TOKEN}"}

# ============================================================
# VISIBLE TABS — in exact order you want
# ============================================================
VISIBLE_ORDER = [
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
    "context_external_tool",  # Course Analytics
    "question_banks",         # Item Banks
]

# ============================================================
# HIDDEN TABS — will be pushed to bottom & hidden
# ============================================================
HIDDEN_NAMES = [
    "outcomes",
    "rubrics",
    "pages",
    "files",
    "attendance",
    "conferences",    # Big Blue Button
    "lucid",          # Lucid Whiteboard (partial match on label)
]

# ============================================================
# STEP 1: FETCH ALL TABS
# ============================================================
print("\n" + "="*55)
print("📋 Fetching current navigation tabs...")
print("="*55)

response = requests.get(
    f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs",
    headers=headers
)

if response.status_code != 200:
    print(f"❌ Error: {response.status_code} → {response.text}")
    exit()

all_tabs = response.json()
print(f"✅ Found {len(all_tabs)} tabs\n")

# Show all tabs found
print(f"{'ID':<35} {'Label':<30}")
print("-" * 65)
for t in all_tabs:
    print(f"{t.get('id',''):<35} {t.get('label','')}")

# ============================================================
# STEP 2: SORT TABS INTO TWO GROUPS
# ============================================================

def find_tab(tabs, identifier):
    """Find tab by ID match or partial label match."""
    match = next((t for t in tabs if t.get("id","").lower() == identifier.lower()), None)
    if match:
        return match
    match = next((t for t in tabs if identifier.lower() in t.get("label","").lower()), None)
    return match

# Build ordered visible list
visible_tabs = []
for tab_id in VISIBLE_ORDER:
    tab = find_tab(all_tabs, tab_id)
    if tab and tab not in visible_tabs:
        visible_tabs.append(tab)

# Build hidden list
hidden_tabs = []
for tab_id in HIDDEN_NAMES:
    tab = find_tab(all_tabs, tab_id)
    if tab and tab not in hidden_tabs and tab not in visible_tabs:
        hidden_tabs.append(tab)

# Any remaining tabs not in either list → push to bottom hidden
remaining = [t for t in all_tabs
             if t not in visible_tabs and t not in hidden_tabs]
hidden_tabs.extend(remaining)

print(f"\n✅ Visible tabs : {len(visible_tabs)}")
print(f"🚫 Hidden tabs  : {len(hidden_tabs)}")

# ============================================================
# STEP 3: ASSIGN POSITIONS
# Visible tabs → positions 1, 2, 3 ...
# Hidden tabs  → positions after visible, marked hidden
# ============================================================
print("\n" + "="*55)
print("🔄 Updating navigation order...")
print("="*55 + "\n")

success = 0
failed  = 0

# --- Visible tabs first ---
for position, tab in enumerate(visible_tabs, start=1):
    response = requests.put(
        f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs/{tab['id']}",
        headers=headers,
        json={
            "position": position,
            "hidden": False
        }
    )
    if response.status_code in [200, 201]:
        print(f"✅ Pos {position:02d} | Visible | {tab.get('label','')}")
        success += 1
    else:
        print(f"❌ Failed | {tab.get('label','')} → {response.status_code}: {response.text}")
        failed += 1
    time.sleep(0.3)

print()

# --- Hidden tabs pushed to bottom ---
hidden_start = len(visible_tabs) + 1
for position, tab in enumerate(hidden_tabs, start=hidden_start):
    response = requests.put(
        f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs/{tab['id']}",
        headers=headers,
        json={
            "position": position,
            "hidden": True
        }
    )
    if response.status_code in [200, 201]:
        print(f"🚫 Pos {position:02d} | Hidden  | {tab.get('label','')}")
        success += 1
    else:
        print(f"❌ Failed | {tab.get('label','')} → {response.status_code}: {response.text}")
        failed += 1
    time.sleep(0.3)

# ============================================================
# STEP 4: VERIFY FINAL STATE
# ============================================================
print("\n" + "="*55)
print("🔍 Final Navigation Order:")
print("="*55)

response = requests.get(
    f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/tabs",
    headers=headers
)

if response.status_code == 200:
    final_tabs = sorted(response.json(), key=lambda x: x.get("position", 999))
    print(f"\n{'Pos':<6} {'Label':<30} {'Status'}")
    print("-" * 50)
    for t in final_tabs:
        hidden = t.get("hidden", False)
        status = "🚫 Hidden (bottom)" if hidden else "✅ Visible"
        print(f"{str(t.get('position','')):<6} {t.get('label',''):<30} {status}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*55)
print(f"🎉 DONE! Updated: {success} | Failed: {failed}")
print("="*55)
print("\n👉 Visible tabs are on top, hidden tabs are dragged to the bottom!")
