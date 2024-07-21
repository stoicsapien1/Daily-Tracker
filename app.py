import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Function to load the data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('study_hours.csv')
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'person', 'hours'])
        df.to_csv('study_hours.csv', index=False)
    return df

# Function to save the data
def save_data(df):
    df.to_csv('study_hours.csv', index=False)

# Load the data
if 'data' not in st.session_state:
    st.session_state['data'] = load_data()

# Function to add new data
def add_data(new_data):
    new_df = pd.DataFrame(new_data)
    new_df['date'] = pd.to_datetime(new_df['date'], format='%Y-%m-%d', errors='coerce')
    updated_df = pd.concat([st.session_state['data'], new_df], ignore_index=True)
    save_data(updated_df)
    st.session_state['data'] = updated_df

# Title of the app
st.title("Study Hours Comparison")

# Form to add new study hours
st.write("## Add New Study Hours")
with st.form("add_hours_form"):
    person = st.selectbox("Person", ["Belal Ahmed Siddiqui", "Shahzeb Uddin", "Abdul Rahman"])
    hours = st.number_input("Hours", min_value=0, max_value=24, step=1)
    date_input = st.date_input("Date", value=date.today())
    submitted = st.form_submit_button("Add Hours")
    
    if submitted:
        new_entry = {'date': [date_input.strftime('%Y-%m-%d')], 'person': [person], 'hours': [hours]}
        add_data(new_entry)
        st.success("New study hours added!")
        st.experimental_rerun()

# Display the raw data
st.write("## Raw Data")
st.write(st.session_state['data'])

# Plot the data
fig = px.line(
    st.session_state['data'],
    x='date',
    y='hours',
    color='person',
    title='Study Hours Per Day',
    labels={'date': 'Date', 'hours': 'Hours Studied'},
    line_shape='linear'
)

# Add data labels and improve the layout
fig.update_traces(mode='lines+markers', line=dict(width=2), marker=dict(size=8))
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Hours Studied',
    xaxis=dict(showline=True, linewidth=2, linecolor='black'),
    yaxis=dict(showline=True, linewidth=2, linecolor='black'),
    title_font_size=24,
    legend_title_text='Person'
)

# Display the plot
st.plotly_chart(fig)

# Calculate total hours per week
st.session_state['data']['date'] = pd.to_datetime(st.session_state['data']['date'], format='%Y-%m-%d', errors='coerce')
st.session_state['data']['week'] = st.session_state['data']['date'].dt.isocalendar().week

weekly_hours = st.session_state['data'].groupby(['week', 'person'])['hours'].sum().reset_index()

# Determine who studied the most each week
most_studied = weekly_hours.loc[weekly_hours.groupby('week')['hours'].idxmax()]

st.write("## Most Studied Each Week")
st.write(most_studied)

# Plot weekly comparison
fig_weekly = px.bar(
    weekly_hours,
    x='week',
    y='hours',
    color='person',
    title='Study Hours Per Week',
    labels={'week': 'Week Number', 'hours': 'Hours Studied'},
    barmode='group'
)

# Add details to the weekly bar chart
fig_weekly.update_layout(
    xaxis_title='Week Number',
    yaxis_title='Hours Studied',
    xaxis=dict(showline=True, linewidth=2, linecolor='black'),
    yaxis=dict(showline=True, linewidth=2, linecolor='black'),
    title_font_size=24
)

# Display the plot
st.plotly_chart(fig_weekly)
