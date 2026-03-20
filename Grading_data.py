import requests
import csv
import time
import os

# ============================================================
#  CONFIGURATION — Fill these in
# ============================================================
CANVAS_URL = "https://canvas.instructure.com"
API_TOKEN  = "Insert Your Token here"
COURSE_ID  = "Insert COurse ID"
# ============================================================

headers = {"Authorization": f"Bearer {API_TOKEN}"}


# ============================================================
# STEP 1: GENERATE GRADE TEMPLATE FROM students.csv & assignments.csv
# ============================================================
def generate_grade_template():
    print("\n" + "="*55)
    print("📋 STEP 1: Generating Grade Template...")
    print("="*55)

    # Check files exist
    if not os.path.exists("students.csv"):
        print("❌ students.csv not found! Run fetch_canvas_data.py first.")
        return False
    if not os.path.exists("assignments.csv"):
        print("❌ assignments.csv not found! Run fetch_canvas_data.py first.")
        return False

    # Read students
    students = []
    with open("students.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students.append(row)

    # Read assignments
    assignments = []
    with open("assignments.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assignments.append(row)

    print(f"✅ Found {len(students)} students")
    print(f"✅ Found {len(assignments)} assignments\n")

    # Show assignments
    print("📝 Assignments found:")
    for a in assignments:
        print(f"   ID: {a['Assignment ID']} | {a['Name']} | Max: {a['Max Points']} pts")

    # Build grade template CSV
    fieldnames = ["Student ID", "Name"] + [a["Name"] for a in assignments]

    with open("grades_template.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            row = {
                "Student ID": s["Student ID"],
                "Name": s["Name"]
            }
            for a in assignments:
                row[a["Name"]] = ""  # Empty — to be filled
            writer.writerow(row)

    print("\n💾 Grade template saved to: grades_template.csv")
    print("👉 Open grades_template.csv, fill in the marks, save and run Step 2!")
    return True


# ============================================================
# STEP 2: UPLOAD GRADES FROM grades_template.csv TO CANVAS
# ============================================================
def upload_grades():
    print("\n" + "="*55)
    print("📤 STEP 2: Uploading Grades to Canvas...")
    print("="*55)

    if not os.path.exists("grades_template.csv"):
        print("❌ grades_template.csv not found! Run Step 1 first.")
        return

    # Read assignments to get IDs
    assignments = {}
    with open("assignments.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assignments[row["Name"]] = row["Assignment ID"]

    # Read filled grades
    grades = []
    with open("grades_template.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grades.append(row)

    print(f"✅ Found {len(grades)} students to grade")
    print(f"✅ Found {len(assignments)} assignments\n")

    success = 0
    failed  = 0

    for row in grades:
        student_id = row["Student ID"]
        student_name = row["Name"]

        for assignment_name, assignment_id in assignments.items():
            grade = row.get(assignment_name, "").strip()

            # Skip empty grades
            if not grade:
                print(f"⏭️  Skipping {student_name} - {assignment_name} (empty)")
                continue

            response = requests.put(
                f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/assignments/{assignment_id}/submissions/{student_id}",
                headers=headers,
                json={"submission": {"posted_grade": grade}}
            )

            if response.status_code in [200, 201]:
                print(f"✅ {student_name} | {assignment_name} | Grade: {grade}")
                success += 1
            else:
                print(f"❌ FAILED: {student_name} | {assignment_name} | {response.text}")
                failed += 1

            time.sleep(0.3)  # Avoid rate limiting

    print("\n" + "="*55)
    print(f"🎉 DONE! Uploaded: {success} | Failed: {failed}")
    print("="*55)


# ============================================================
# STEP 3: VERIFY GRADES (Optional)
# ============================================================
def verify_grades():
    print("\n" + "="*55)
    print("🔍 STEP 3: Verifying Uploaded Grades...")
    print("="*55)

    assignments = {}
    with open("assignments.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assignments[row["Name"]] = row["Assignment ID"]

    students = []
    with open("students.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students.append(row)

    print(f"{'Student':<25}", end="")
    for name in assignments:
        print(f"{name[:15]:<18}", end="")
    print()
    print("-" * (25 + 18 * len(assignments)))

    for s in students:
        student_id = s["Student ID"]
        print(f"{s['Name'][:24]:<25}", end="")

        for assignment_name, assignment_id in assignments.items():
            response = requests.get(
                f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/assignments/{assignment_id}/submissions/{student_id}",
                headers=headers
            )
            if response.status_code == 200:
                sub = response.json()
                grade = sub.get("grade", "-") or "-"
                print(f"{str(grade)[:15]:<18}", end="")
            else:
                print(f"{'ERR':<18}", end="")
            time.sleep(0.2)
        print()

    print("\n✅ Verification complete!")


# ============================================================
# MAIN MENU
# ============================================================
print("\n" + "="*55)
print("   🎓 CANVAS GRADE MANAGER")
print("="*55)
print("1. Generate Grade Template (Step 1)")
print("2. Upload Grades to Canvas (Step 2)")
print("3. Verify Uploaded Grades  (Step 3)")
print("="*55)

choice = input("Enter your choice (1/2/3): ").strip()

if choice == "1":
    generate_grade_template()
elif choice == "2":
    upload_grades()
elif choice == "3":
    verify_grades()
else:
    print("❌ Invalid choice! Enter 1, 2, or 3.")
