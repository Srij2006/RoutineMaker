import pandas as pd
from datetime import date

# --------------------------------
# SETTINGS
# --------------------------------

EXCEL_FILE = "Videos.xlsx"

# Your 32-day challenge starts here
START_DATE = date(2026, 9, 2)


# --------------------------------
# READ EXCEL
# --------------------------------

df = pd.read_excel(EXCEL_FILE, sheet_name="Videos")

# Make sure Completed is treated as True/False
df["Completed"] = df["Completed"].fillna(False).astype(bool)

# Convert schedule_date to Python dates
df["Schedule_date"] = pd.to_datetime(
    df["Schedule_date"]
).dt.date


# --------------------------------
# TODAY
# --------------------------------

today = date.today()

# Determine which challenge day today is
challenge_day = (today - START_DATE).days + 1


print("\n====================================")
print("          ROUTINE TRACKER")
print("====================================")

print(f"\nToday's Date : {today.strftime('%d-%b-%Y')}")
print(f"Challenge Day: {challenge_day}")


# --------------------------------
# TODAY'S VIDEOS
# --------------------------------

today_videos = df[df["Schedule_date"] == today]

print("\n------------------------------------")
print("          TODAY'S VIDEOS")
print("------------------------------------")

if today_videos.empty:

    if challenge_day < 1:
        print("Your challenge has not started yet.")

    elif challenge_day > 31:
        print("🎉 Your 31-day video schedule is complete!")

    else:
        print("No videos assigned for today.")

else:

    for _, video in today_videos.iterrows():

        if video["Completed"]:
            status = "✅ COMPLETED"
        else:
            status = "⬜ NOT COMPLETED"

        print(f"\nVideo {video['video_id']}")
        print(f"Title : {video['video_title']}")
        print(f"Status: {status}")
        print(f"URL   : {video['youtube_url']}")


# --------------------------------
# TODAY'S PROGRESS
# --------------------------------

if not today_videos.empty:

    total_today = len(today_videos)
    completed_today = today_videos["Completed"].sum()

    print("\n------------------------------------")
    print("          TODAY'S PROGRESS")
    print("------------------------------------")

    print(f"Completed : {completed_today}/{total_today}")

    if completed_today == total_today:
        print("🎉 TODAY COMPLETED!")

    else:
        print("📚 Keep going!")


# --------------------------------
# DAILY COMPLETION
# --------------------------------

daily_status = (
    df.groupby("Schedule_date")["Completed"]
    .agg(
        total="count",
        completed="sum"
    )
)

daily_status["day_completed"] = (
    daily_status["completed"] == daily_status["total"]
)


# --------------------------------
# CURRENT STREAK
# --------------------------------

streak = 0

current_date = today

while current_date in daily_status.index:

    if daily_status.loc[current_date, "day_completed"]:
        streak += 1
        current_date = current_date.fromordinal(
            current_date.toordinal() - 1
        )

    else:
        break


# --------------------------------
# OVERALL PROGRESS
# --------------------------------

total_videos = len(df)
completed_videos = int(df["Completed"].sum())

progress_percentage = (
    completed_videos / total_videos * 100
)


# --------------------------------
# SUMMARY
# --------------------------------

print("\n====================================")
print("             SUMMARY")
print("====================================")

print(f"\n🔥 Current Streak : {streak} day(s)")
print(
    f"📚 Overall        : "
    f"{completed_videos}/{total_videos} videos"
)

print(f"📈 Progress       : {progress_percentage:.1f}%")

print("\n====================================\n")