import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import date, timedelta


# ============================================================
# SETTINGS
# ============================================================

START_DATE = date(2026, 9, 2)
CHALLENGE_DAYS = 32

# Use Videos.xlsx if it exists.
# Otherwise use the corrected file from earlier.
if Path("Videos.xlsx").exists():
    EXCEL_FILE = "Videos.xlsx"
elif Path("Videos_Sequential.xlsx").exists():
    EXCEL_FILE = "Videos_Sequential.xlsx"
else:
    EXCEL_FILE = "Videos.xlsx"

PROGRESS_FILE = "progress.json"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Routine Streak",
    page_icon="🔥",
    layout="centered"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        color: #777;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .task-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        margin-bottom: 12px;
    }

    .complete-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #b7e4c7;
        background-color: #f0fff4;
        margin-bottom: 12px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .big-progress {
        font-size: 32px;
        font-weight: 800;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD EXCEL
# ============================================================

@st.cache_data
def load_videos():

    df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Videos"
    )

    # Completed column may exist in Excel,
    # but actual progress is stored separately.
    if "Completed" not in df.columns:
        df["Completed"] = False

    if "Schedule_date" in df.columns:
        df["Schedule_date"] = pd.to_datetime(
            df["Schedule_date"],
            errors="coerce"
        ).dt.date

    return df


df = load_videos()


# ============================================================
# PROGRESS STORAGE
# ============================================================

def load_progress():

    if not Path(PROGRESS_FILE).exists():
        return {
            "videos": {},
            "pyqs": {}
        }

    try:

        with open(
            PROGRESS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if "videos" not in data:
            data["videos"] = {}

        if "pyqs" not in data:
            data["pyqs"] = {}

        return data

    except Exception:

        return {
            "videos": {},
            "pyqs": {}
        }


def save_progress(data):

    with open(
        PROGRESS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


progress_data = load_progress()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def day_date(day_number):

    return START_DATE + timedelta(
        days=day_number - 1
    )


def get_day_videos(day_number):

    target_date = day_date(day_number)

    return df[
        df["Schedule_date"] == target_date
    ]


def video_key(video_id):

    return str(video_id)


def is_video_completed(video_id):

    return progress_data["videos"].get(
        video_key(video_id),
        False
    )


def is_pyq_completed(day_number):

    return progress_data["pyqs"].get(
        str(day_number),
        False
    )


def set_video_completed(video_id, value):

    progress_data["videos"][
        video_key(video_id)
    ] = value

    save_progress(progress_data)


def set_pyq_completed(day_number, value):

    progress_data["pyqs"][
        str(day_number)
    ] = value

    save_progress(progress_data)


def is_day_complete(day_number):

    day_videos = get_day_videos(day_number)

    # Need exactly all scheduled videos completed
    videos_done = all(
        is_video_completed(video["video_id"])
        for _, video in day_videos.iterrows()
    )

    pyq_done = is_pyq_completed(day_number)

    return videos_done and pyq_done


def calculate_streak():

    today = date.today()

    # Don't count days before challenge.
    if today < START_DATE:
        return 0

    current_day = (
        today - START_DATE
    ).days + 1

    streak = 0

    # Count backwards from today.
    for day_number in range(
        current_day,
        0,
        -1
    ):

        if is_day_complete(day_number):

            streak += 1

        else:

            break

    return streak


# ============================================================
# TODAY
# ============================================================

today = date.today()

challenge_day = (
    today - START_DATE
).days + 1


# Keep the challenge within 1-32.
if challenge_day < 1:
    challenge_day = 1

if challenge_day > CHALLENGE_DAYS:
    challenge_day = CHALLENGE_DAYS


today_videos = get_day_videos(
    challenge_day
)


# ============================================================
# GLOBAL STATISTICS
# ============================================================

completed_days = 0

for day_number in range(
    1,
    CHALLENGE_DAYS + 1
):

    if is_day_complete(day_number):
        completed_days += 1


streak = calculate_streak()

overall_progress = (
    completed_days / CHALLENGE_DAYS
    if CHALLENGE_DAYS > 0
    else 0
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔥 Routine Streak</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">32-Day Lecture + PYQ Challenge</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# TOP STATISTICS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "🎯 Challenge Day",
        f"{challenge_day}/{CHALLENGE_DAYS}"
    )

with col2:

    st.metric(
        "📈 Progress",
        f"{completed_days}/{CHALLENGE_DAYS}"
    )

with col3:

    st.metric(
        "🔥 Streak",
        f"{streak} days"
    )


st.progress(
    overall_progress
)


st.divider()


# ============================================================
# TODAY HEADER
# ============================================================

st.subheader(
    f"📅 Day {challenge_day}"
)

st.caption(
    day_date(challenge_day).strftime(
        "%d %B %Y"
    )
)


# ============================================================
# TODAY'S VIDEOS
# ============================================================
st.markdown(
    '<div class="section-title">📺 Videos</div>',
    unsafe_allow_html=True
)

if today_videos.empty:

    st.info("No videos scheduled for this day.")

else:

    for number, (_, video) in enumerate(
        today_videos.iterrows(),
        start=1
    ):

        vid_id = video["video_id"]

        checkbox_key = f"video_{vid_id}"

        current_value = is_video_completed(
            vid_id
        )

        completed = st.checkbox(
            f"Video {number}",
            value=current_value,
            key=checkbox_key
        )

        if completed != current_value:

            set_video_completed(
                vid_id,
                completed
            )

            st.rerun()


# ============================================================
# PYQ
# ============================================================

st.markdown(
    '<div class="section-title">📝 PYQs</div>',
    unsafe_allow_html=True
)

pyq_current = is_pyq_completed(
    challenge_day
)

pyq_done = st.checkbox(
    "PYQ",
    value=pyq_current,
    key=f"pyq_{challenge_day}"
)

st.caption(
    "Complete today's 30 PYQs."
)


if pyq_done != pyq_current:

    set_pyq_completed(
        challenge_day,
        pyq_done
    )

    st.rerun()


st.divider()


# ============================================================
# TODAY'S PROGRESS
# ============================================================

st.subheader(
    "📊 Today's Progress"
)


video_total = len(today_videos)

video_completed = sum(
    is_video_completed(video["video_id"])
    for _, video in today_videos.iterrows()
)


pyq_completed = (
    1
    if is_pyq_completed(challenge_day)
    else 0
)


total_tasks = video_total + 1

completed_tasks = (
    video_completed +
    pyq_completed
)


daily_progress = (
    completed_tasks / total_tasks
    if total_tasks > 0
    else 0
)


st.progress(
    daily_progress
)


st.markdown(
    f'<div class="big-progress">'
    f'{completed_tasks}/{total_tasks}'
    f'</div>',
    unsafe_allow_html=True
)


st.caption(
    f"Videos: {video_completed}/{video_total}  •  "
    f"PYQ: {pyq_completed}/1"
)


# ============================================================
# DAY COMPLETE
# ============================================================

if is_day_complete(challenge_day):

    st.success(
        f"🎉 Day {challenge_day} Complete!"
    )

    st.balloons()

else:

    remaining = (
        total_tasks -
        completed_tasks
    )

    st.info(
        f"{remaining} task(s) remaining for today."
    )


# ============================================================
# RESET OPTION
# ============================================================

st.divider()

with st.expander("⚙️ Settings"):

    st.write(
        "Your completion data is stored in "
        "`progress.json`."
    )

    if st.button(
        "Reset ALL progress"
    ):

        progress_data = {
            "videos": {},
            "pyqs": {}
        }

        save_progress(
            progress_data
        )

        st.success(
            "All progress has been reset."
        )

        st.rerun()