import streamlit as st
from streamlit_calendar import calendar
import pandas as pd
import datetime
import plotly.express as px
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="My Epic Life Calendar", page_icon="", layout="wide")
st.title("My Epic Life Calendar")
st.subheader("Track your wins, visualize your growth, and curate your year.")

# --- STATE MANAGEMENT & DATABASE ---
if "events" not in st.session_state:
    st.session_state.events = [
        {
            "title": "Hit a new PR at the gym!",
            "start": "2026-05-15",
            "end": "2026-05-15",
            "category": "Fitness/Health",
            "color": "#FF4B4B"
        },
        {
            "title": "Launched the backend alpha",
            "start": "2026-05-20",
            "end": "2026-05-20",
            "category": "Coding/Projects",
            "color": "#0068C9"
        }
    ]

if "month_images" not in st.session_state:
    st.session_state.month_images = {}

CATEGORIES = {
    "Coding/Projects": "#0068C9",
    "Fitness/Health": "#FF4B4B",
    "Learning/Books": "#29B5E8",
    "Life Milestone": "#F9A73E",
    "Social/Fun": "#27D8A1"
}

# --- SIDEBAR: MONTHLY VIBE CURATOR ---
st.sidebar.header("🖼️ Monthly Aesthetic")
current_month = st.sidebar.selectbox(
    "Choose Month to Style",
    ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    index=datetime.datetime.now().month - 1
)

uploaded_file = st.sidebar.file_uploader(f"Upload an amazing cover for {current_month}", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.session_state.month_images[current_month] = uploaded_file

# Display the month banner if it exists
if current_month in st.session_state.month_images:
    st.sidebar.image(st.session_state.month_images[current_month], caption=f"Vibe for {current_month}", use_column_width=True)
else:
    st.sidebar.info(f"No image set for {current_month} yet. Upload one to make it pop!")

# --- MAIN LAYOUT: CALENDAR & LOGGING ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Your Timeline")
    
    calendar_options = {
        "editable": True,
        "selectable": True,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek"
        },
        "initialView": "dayGridMonth",
    }
    
    state = calendar(events=st.session_state.events, options=calendar_options, key="epic_cal")
    
    if state.get("callback") == "select":
        st.session_state.selected_date = state["select"]["start"].split("T")[0]
        st.toast(f"Selected date: {st.session_state.selected_date} - Log your win in the right panel!", icon="📍")

with col2:
    st.markdown("###  Log an Amazing Thing")
    
    default_date = st.session_state.get("selected_date", str(datetime.date.today()))
    
    try:
        parsed_date = datetime.datetime.strptime(default_date, "%Y-%m-%d").date()
    except ValueError:
        parsed_date = datetime.date.today()
        
    log_date = st.date_input("Date of Achievement", value=parsed_date)
    win_title = st.text_input("What awesome thing did you do?", placeholder="e.g., Finished reading Atomic Habits")
    cat = st.selectbox("Category", list(CATEGORIES.keys()))
    
    if st.button("Lock It In", use_container_width=True):
        if win_title:
            new_event = {
                "title": f"✨ {win_title}",
                "start": str(log_date),
                "end": str(log_date),
                "category": cat,
                "color": CATEGORIES[cat]
            }
            st.session_state.events.append(new_event)
            st.success("Logged! Refreshing calendar...")
            st.rerun()
        else:
            st.error("Give your achievement a title first!")

# --- DASHBOARD: METRICS & ANALYTICS ---
st.markdown("---")
st.markdown("## 📊 Achievements Analytics")

if st.session_state.events:
    df = pd.DataFrame(st.session_state.events)
    
    total_wins = len(df)
    unique_days = df['start'].nunique()
    
    m1, m2 = st.columns(2)
    m1.metric("Total Epic Moments Logged", total_wins)
    m2.metric("Days with Wins", unique_days)
    
    st.markdown("### Category Breakdown")
    cat_counts = df['category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    
    fig = px.bar(
        cat_counts, 
        x='Category', 
        y='Count', 
        color='Category',
        color_discrete_map=CATEGORIES,
        text='Count'
    )
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Start logging items above to populate your metrics dashboard!")