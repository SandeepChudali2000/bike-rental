import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------
# Page configuration
# -----------------------
st.set_page_config(
    page_title="DC Bike Rentals Dashboard",
    layout="wide"
)

# -----------------------
# Custom CSS
# -----------------------
st.markdown("""
<style>
/* Main app background */
.stApp {
    background-color: #1e1515;
    color: #f5f5f5;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #2a1b1b;
}

/* KPI Cards */
.kpi-card {
    background-color: #2b1f1f;
    padding: 24px 18px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 6px 14px rgba(0,0,0,0.6);
    border-left: 6px solid #c62828;
}

.kpi-title {
    font-size: 14px;
    color: #ffb3b3;
    text-transform: uppercase;
    margin-bottom: 6px;
    height: 45px;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

def kpi_card(title, value):
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

# -----------------------
# Title
# -----------------------
st.title("Washington D.C. Bike Rentals Demand Analysis Dashboard")
st.markdown("Interactive analysis of bike rental patterns (2011–2012)")
st.markdown("**Author:** Sandeep Chudali  \nAssignment 3: Data Visualization using Streamlit.")
st.markdown("---")

# -----------------------
# Load data
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df['datetime'] = pd.to_datetime(df['datetime'])

    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['hour'] = df['datetime'].dt.hour
    df['dayofweek'] = df['datetime'].dt.day_name()

    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    df['season_name'] = df['season'].map(season_map)

    def get_day_period(hour):
        if hour <= 5:
            return 'Night'
        elif hour <= 11:
            return 'Morning'
        elif hour <= 17:
            return 'Afternoon'
        else:
            return 'Evening'

    df['day_period'] = df['hour'].apply(get_day_period)
    return df

df = load_data()

# -----------------------
# Sidebar filters
# -----------------------
st.sidebar.header("🔧 Filters")

year_filter = st.sidebar.selectbox("Select Year", ["Both", 2011, 2012])
workingday_filter = st.sidebar.selectbox("Working Day", ["All", 0, 1])
season_filter = st.sidebar.multiselect(
    "Select Season",
    ['Spring', 'Summer', 'Fall', 'Winter'],
    default=['Spring', 'Summer', 'Fall', 'Winter']
)

filtered_df = df.copy()
if year_filter != "Both":
    filtered_df = filtered_df[filtered_df['year'] == year_filter]
if workingday_filter != "All":
    filtered_df = filtered_df[filtered_df['workingday'] == workingday_filter]
filtered_df = filtered_df[filtered_df['season_name'].isin(season_filter)]

# -----------------------
# KPI calculations
# -----------------------
total_casual = int(filtered_df['casual'].sum())
total_registered = int(filtered_df['registered'].sum())
total_rentals = int(filtered_df['count'].sum())
peak_hour = filtered_df.groupby('hour')['count'].mean().idxmax()
avg_hourly_rentals = int(filtered_df['count'].mean())

# -----------------------
# KPI Cards
# -----------------------
st.markdown("## 📌 Key Performance Indicators")
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(kpi_card("Total Rentals", f"{total_rentals:,}"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Casual Rentals", f"{total_casual:,}"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("Registered Rentals", f"{total_registered:,}"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Avg Hourly Rentals", avg_hourly_rentals), unsafe_allow_html=True)
with c5:
    st.markdown(kpi_card("Peak Hour", f"{peak_hour}:00"), unsafe_allow_html=True)

st.markdown("---")

# -----------------------
# Plot styling
# -----------------------
sns.set_style("darkgrid")
green = "#2e7d32"

# Plot 1: Hourly pattern
st.subheader("Mean Rentals by Hour of Day")
fig, ax = plt.subplots(figsize=(10,4))
hour_mean = filtered_df.groupby('hour')['count'].mean()
ax.plot(hour_mean.index, hour_mean.values, color=green, marker='o', linewidth=2)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Mean Rentals")
ax.set_xticks(range(24))
st.pyplot(fig)

# Plot 2: Day of week
st.subheader("Mean Rentals by Day of Week")
fig, ax = plt.subplots(figsize=(10,4))
order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
sns.barplot(
    data=filtered_df,
    x='dayofweek',
    y='count',
    order=order,
    estimator='mean',
    color=green,
    ax=ax
)
ax.set_ylabel("Mean Rentals")
plt.xticks(rotation=45)
st.pyplot(fig)

# Plot 3: Monthly pattern
st.subheader("Mean Rentals by Month")
fig, ax = plt.subplots(figsize=(10,4))
month_mean = filtered_df.groupby('month')['count'].mean()
ax.plot(month_mean.index, month_mean.values, color=green, marker='o', linewidth=2)
ax.set_xticks(range(1,13))
ax.set_ylabel("Mean Rentals")
st.pyplot(fig)

# Plot 4: Seasonal pattern
st.subheader(" Mean Rentals by Season")
fig, ax = plt.subplots(figsize=(8,4))
sns.barplot(
    data=filtered_df,
    x='season_name',
    y='count',
    estimator='mean',
    color=green,
    ax=ax
)
ax.set_ylabel("Mean Rentals")
st.pyplot(fig)

