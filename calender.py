import requests
import time
from icalendar import Calendar

CANVAS_URL = "https://canvas.instructure.com"
API_TOKEN = "Your Access Token Here"  # ← Only change this
COURSE_ID = "Course ID here"

with open("calender file .ics", "rb") as f:
    cal = Calendar.from_ical(f.read())

for component in cal.walk():
    if component.name == "VEVENT":
        title = str(component.get("SUMMARY", "No Title"))
        start = component.get("DTSTART").dt
        end = component.get("DTEND").dt

        response = requests.post(
            f"{CANVAS_URL}/api/v1/calendar_events",
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            json={
                "calendar_event": {
                    "context_code": f"course_{COURSE_ID}",
                    "title": title,
                    "start_at": start.isoformat(),
                    "end_at": end.isoformat(),
                }
            }
        )
        
        if response.status_code == 201:
            print(f"✅ Imported: {title}")
        else:
            print(f"❌ Failed: {title} → {response.text}")
        
        time.sleep(0.5)

print("🎉 All Done! Check your Test course calendar on Canvas.")
