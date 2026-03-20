import requests
import time

# ============================================================
#  CONFIGURATION — Fill these in
# ============================================================
CANVAS_URL = "https://canvas.instructure.com"
API_TOKEN  = "paste_your_token_here"
COURSE_ID  = "14437115"
# ============================================================

headers = {"Authorization": f"Bearer {API_TOKEN}"}


def create_assignment_group(name, weight):
    response = requests.post(
        f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/assignment_groups",
        headers=headers,
        json={"assignment_group": {"name": name, "group_weight": weight}}
    )
    if response.status_code in [200, 201]:
        return response.json()["id"]
    else:
        print(f"❌ Failed to create group '{name}': {response.text}")
        return None


def create_assignment(name, points, due_date, group_id, description, submission_type):
    data = {
        "assignment": {
            "name": name,
            "points_possible": points,
            "grading_type": "points",
            "published": True,
            "description": description,
            "submission_types": [submission_type],
            "assignment_group_id": group_id
        }
    }
    if due_date:
        data["assignment"]["due_at"] = f"{due_date}T23:59:00"

    response = requests.post(
        f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/assignments",
        headers=headers,
        json=data
    )
    if response.status_code in [200, 201]:
        return response.json()["id"]
    else:
        print(f"❌ Failed to create assignment '{name}': {response.text}")
        return None


def ask(prompt, default=None):
    """Helper to get input with optional default."""
    if default:
        value = input(f"{prompt} [{default}]: ").strip()
        return value if value else default
    return input(f"{prompt}: ").strip()


def ask_submission_type():
    print("     Submission Type:")
    print("       1. File Upload (online_upload)")
    print("       2. Text Entry (online_text_entry)")
    print("       3. URL Submission (online_url)")
    print("       4. No Submission (none)")
    choice = input("     Choose (1/2/3/4) [1]: ").strip() or "1"
    types = {"1": "online_upload", "2": "online_text_entry", "3": "online_url", "4": "none"}
    return types.get(choice, "online_upload")


# ============================================================
# MAIN INTERACTIVE FLOW
# ============================================================
print("\n" + "="*55)
print("   📝 CANVAS ASSIGNMENT CREATOR")
print("="*55)
print(f"   Course ID : {COURSE_ID}")
print(f"   Canvas URL: {CANVAS_URL}")
print("="*55)

# Step 1: Number of groups
print("\n📁 STEP 1: Assignment Groups")
print("-"*40)
num_groups = int(ask("How many assignment groups do you want to create"))

all_groups = []

# Step 2: For each group
for g in range(1, num_groups + 1):
    print(f"\n{'='*55}")
    print(f"  GROUP {g} of {num_groups}")
    print(f"{'='*55}")

    group_name   = ask(f"  Group {g} Name (e.g. Assignments, Test)")
    group_weight = int(ask(f"  Weightage % for '{group_name}'", "0"))
    num_assigns  = int(ask(f"  How many assignments in '{group_name}'"))

    assignments = []

    for a in range(1, num_assigns + 1):
        print(f"\n   📝 Assignment {a} of {num_assigns} in '{group_name}'")
        print("   " + "-"*40)

        name        = ask(f"   Name (e.g. Assignment {a})")
        points      = int(ask("   Max Points", "100"))
        due_date    = ask("   Due Date (YYYY-MM-DD) or press Enter to skip", "")
        description = ask("   Description (optional) or press Enter to skip", "")
        sub_type    = ask_submission_type()

        assignments.append({
            "name":        name,
            "points":      points,
            "due_date":    due_date,
            "description": description,
            "sub_type":    sub_type
        })

    all_groups.append({
        "name":        group_name,
        "weight":      group_weight,
        "assignments": assignments
    })

# Step 3: Summary before creating
print("\n\n" + "="*55)
print("   📋 SUMMARY — Review Before Creating")
print("="*55)

total_weight = 0
for g in all_groups:
    total_weight += g["weight"]
    print(f"\n📁 {g['name']} ({g['weight']}%)")
    print(f"   {len(g['assignments'])} assignment(s):")
    for a in g["assignments"]:
        due = a['due_date'] if a['due_date'] else "No due date"
        print(f"   ✏️  {a['name']} | {a['points']} pts | Due: {due}")

print(f"\n⚖️  Total Weight: {total_weight}%")
if total_weight != 100:
    print(f"⚠️  Warning: Total weight is {total_weight}%, not 100%!")

print("\n" + "="*55)
confirm = input("Type 'YES' to create all groups & assignments: ").strip()

if confirm != "YES":
    print("\n❌ Cancelled. Nothing was created.")
    exit()

# Step 4: Create everything in Canvas
print("\n" + "="*55)
print("🚀 Creating in Canvas...")
print("="*55)

total_success = 0
total_failed  = 0

for g in all_groups:
    print(f"\n📁 Creating group: {g['name']} ({g['weight']}%)...")
    group_id = create_assignment_group(g["name"], g["weight"])

    if not group_id:
        print(f"❌ Skipping assignments for '{g['name']}' — group creation failed.")
        total_failed += len(g["assignments"])
        continue

    print(f"✅ Group created! (ID: {group_id})")

    for a in g["assignments"]:
        result = create_assignment(
            name            = a["name"],
            points          = a["points"],
            due_date        = a["due_date"] if a["due_date"] else None,
            group_id        = group_id,
            description     = a["description"],
            submission_type = a["sub_type"]
        )
        if result:
            print(f"   ✅ Created: {a['name']} (ID: {result})")
            total_success += 1
        else:
            total_failed += 1

        time.sleep(0.5)

# Step 5: Final Summary
print("\n" + "="*55)
print("🎉 ALL DONE!")
print(f"   ✅ Successfully created : {total_success} assignments")
print(f"   ❌ Failed               : {total_failed} assignments")
print("="*55)
print("\n👉 Check your Canvas course to see all assignments!")
