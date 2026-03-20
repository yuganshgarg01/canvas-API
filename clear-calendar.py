import requests
import time

# ============================================================
#  CONFIGURATION — Fill these in
# ============================================================
CANVAS_URL = "https://canvas.instructure.com"
API_TOKEN = "7~MBH3uK97YzJE3VGrDkBYCe9PJ6KNt3Yu24vYaxTGNBHcWF2neL7cr7QYKZtn9vQL"  # ← Only change this
COURSE_ID = "12525952"
# ============================================================

headers = {"Authorization": f"Bearer {API_TOKEN}"}


def get_all_calendar_events():
    """Fetch all calendar events for the course with pagination."""
    print("\n" + "="*55)
    print("📅 Fetching all calendar events...")
    print("="*55)

    events = []
    url = f"{CANVAS_URL}/api/v1/calendar_events"
    params = {
        "context_codes[]": f"course_{COURSE_ID}",
        "all_events": True,
        "per_page": 50
    }

    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            break

        data = response.json()
        events.extend(data)

        # Handle pagination
        links = response.headers.get("Link", "")
        url = None
        params = {}  # Clear params for next page (already in URL)
        for part in links.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
                break

    print(f"✅ Found {len(events)} calendar events")
    return events


def display_events(events):
    """Display all fetched events."""
    if not events:
        print("⚠️  No events found for this course.")
        return

    print(f"\n{'ID':<12} {'Title':<40} {'Date'}")
    print("-" * 70)
    for e in events:
        date = e.get("start_at", "No date")
        if date and date != "No date":
            date = date[:10]
        title = e.get("title", "No title")[:38]
        print(f"{e.get('id',''):<12} {title:<40} {date}")


def delete_event(event_id, title):
    """Delete a single calendar event."""
    response = requests.delete(
        f"{CANVAS_URL}/api/v1/calendar_events/{event_id}",
        headers=headers,
        params={"cancel_reason": "Bulk delete"}
    )

    if response.status_code in [200, 201]:
        print(f"🗑️  Deleted: [{event_id}] {title}")
        return True
    else:
        print(f"❌ Failed: [{event_id}] {title} → {response.status_code}: {response.text}")
        return False


def delete_all_events():
    """Main function to fetch and delete all calendar events."""

    # Step 1: Fetch all events
    events = get_all_calendar_events()

    if not events:
        print("\n✅ No events to delete. Course calendar is already empty!")
        return

    # Step 2: Display events
    display_events(events)

    # Step 3: Confirm before deleting
    print("\n" + "="*55)
    print(f"⚠️  WARNING: You are about to delete {len(events)} events!")
    print(f"   Course ID : {COURSE_ID}")
    print(f"   Canvas URL: {CANVAS_URL}")
    print("="*55)
    confirm = input("\nType 'YES' to confirm deletion: ").strip()

    if confirm != "YES":
        print("\n❌ Deletion cancelled. No events were deleted.")
        return

    # Step 4: Delete all events
    print("\n" + "="*55)
    print("🗑️  Deleting all events...")
    print("="*55 + "\n")

    success = 0
    failed  = 0

    for event in events:
        event_id = event.get("id")
        title    = event.get("title", "No title")

        result = delete_event(event_id, title)
        if result:
            success += 1
        else:
            failed += 1

        time.sleep(0.3)  # Avoid rate limiting

    # Step 5: Summary
    print("\n" + "="*55)
    print("✅ DELETION COMPLETE!")
    print(f"   Successfully deleted : {success}")
    print(f"   Failed               : {failed}")
    print(f"   Total processed      : {len(events)}")
    print("="*55)

    if failed > 0:
        print("\n⚠️  Some events failed to delete. Try running the script again.")


# ============================================================
# MAIN
# ============================================================
print("\n" + "="*55)
print("   🗓️  CANVAS CALENDAR EVENT DELETER")
print("="*55)
print(f"   Course ID : {COURSE_ID}")
print(f"   Canvas URL: {CANVAS_URL}")
print("="*55)

delete_all_events()
