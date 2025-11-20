import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="MediInsight SaaS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Data Simulation (Matching Kaggle 'No-Show' Structure) ---
@st.cache_data
def load_data(count=200):
    neighbourhoods = ['JARDIM DA PENHA', 'MATA DA PRAIA', 'PONTAL DE CAMBURI', 'JARDIM CAMBURI', 'RESISTÊNCIA']
    data = []
    
    for i in range(count):
        is_no_show = np.random.choice(['Yes', 'No'], p=[0.3, 0.7]) # ~30% no-show
        has_sms = np.random.choice([0, 1], p=[0.5, 0.5])
        age = np.random.randint(5, 85)
        
        scheduled_date = datetime.now() - timedelta(days=np.random.randint(1, 30))
        lead_days = np.random.randint(0, 15)
        appointment_date = scheduled_date + timedelta(days=lead_days)
        
        # Correlations for risk factors
        diabetes = np.random.choice([0, 1], p=[0.9, 0.1])
        hipertension = np.random.choice([0, 1], p=[0.8, 0.2])
        
        row = {
            'PatientId': f'P-{10000 + i}',
            'AppointmentID': f'APT-{50000 + i}',
            'Gender': np.random.choice(['F', 'M']),
            'ScheduledDay': scheduled_date,
            'AppointmentDay': appointment_date,
            'Age': age,
            'Neighbourhood': np.random.choice(neighbourhoods),
            'Scholarship': np.random.choice([0, 1], p=[0.9, 0.1]),
            'Hipertension': hipertension,
            'Diabetes': diabetes,
            'Alcoholism': np.random.choice([0, 1], p=[0.95, 0.05]),
            'Handcap': np.random.choice([0, 1], p=[0.98, 0.02]),
            'SMS_received': has_sms,
            'No-show': is_no_show,
            'LeadDays': lead_days
        }
        data.append(row)
        
    return pd.DataFrame(data)

df = load_data(500)

# --- 2. Sidebar ---
with st.sidebar:
    st.title("🏥 MediInsight")
    
    page = st.radio("Navigation", ["Dashboard", "Patients", "Schedule", "Settings"])
    
    st.markdown("---")
    st.subheader("AI Prediction 🤖")
    st.info("Tomorrow's risk is **High (24%)**.")
    if st.button("Auto-Send SMS Reminders", type="primary"):
        st.toast("Sent 42 SMS reminders successfully!", icon="✅")
    
    st.markdown("---")
    st.caption("v1.2.0 • Connected to KaggleHub")

# --- 3. Dashboard Logic ---
if page == "Dashboard":
    
    # Top Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Appointment Analytics")
        st.markdown("Real-time analysis of patient attendance and risk factors.")
    with col2:
        st.markdown("####") # Spacer
        st.download_button(
            label="📥 Export CSV",
            data=df.to_csv(index=False),
            file_name='appointments.csv',
            mime='text/csv',
        )

    st.divider()

    # --- KPI Metrics ---
    total_apts = len(df)
    no_shows = df[df['No-show'] == 'Yes']
    shows = df[df['No-show'] == 'No']
    rate = (len(no_shows) / total_apts) * 100
    
    # SMS Analysis logic
    sms_group = df[df['SMS_received'] == 1]
    no_sms_group = df[df['SMS_received'] == 0]
    
    sms_rate = (len(sms_group[sms_group['No-show'] == 'Yes']) / len(sms_group)) * 100
    no_sms_rate = (len(no_sms_group[no_sms_group['No-show'] == 'Yes']) / len(no_sms_group)) * 100
    sms_impact = no_sms_rate - sms_rate

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Appointments", f"{total_apts}", "+4.5%")
    k1.caption("vs last month")
    
    k2.metric("Overall No-Show Rate", f"{rate:.1f}%", f"{rate-20:.1f}%")
    k2.caption("Avg industry rate is 20%")
    
    est_loss = len(no_shows) * 150
    k3.metric("Est. Revenue Lost", f"${est_loss:,}", delta="-1.2%", delta_color="inverse")
    k3.caption("Based on $150/visit")
    
    k4.metric("SMS Success Rate", f"{(100 - sms_rate):.1f}%", f"+{sms_impact:.1f}% impact")
    k4.caption("Improvement over no-SMS")

    st.markdown("###")

    # --- Charts Section ---
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("The 'SMS Effect' Analysis")
        
        # Prepare data for bar chart
        sms_data = pd.DataFrame({
            'Category': ['No SMS Sent (Control)', 'SMS Received (Intervention)'],
            'No-Show Rate (%)': [no_sms_rate, sms_rate],
            'Color': ['#ef4444', '#0d9488'] # Red, Teal
        })
        
        fig_sms = px.bar(
            sms_data, 
            x='No-Show Rate (%)', 
            y='Category', 
            orientation='h',
            text='No-Show Rate (%)',
            color='Category',
            color_discrete_map={'No SMS Sent (Control)': '#ef4444', 'SMS Received (Intervention)': '#0d9488'}
        )
        fig_sms.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_sms.update_layout(showlegend=False, height=250, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_sms, use_container_width=True)
        
        st.info(f"🔥 **Insight:** SMS reminders reduced no-shows by **{sms_impact:.1f}%** in this cohort.")

    with c2:
        st.subheader("Risk Factors")
        
        # Simple breakdown
        gender_counts = no_shows['Gender'].value_counts()
        fig_pie = px.donut(
            values=gender_counts.values, 
            names=gender_counts.index, 
            title="No-Shows by Gender",
            color_discrete_sequence=['#60a5fa', '#f472b6'] # Blue, Pink
        )
        fig_pie.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- High Risk Queue & Data ---
    st.markdown("###")
    st.subheader("High Risk Queue & Patient Logs")
    
    tab1, tab2 = st.tabs(["📋 Detailed Log", "⚠️ High Risk Queue"])
    
    with tab1:
        # Search Filter
        search_term = st.text_input("Search Patient ID or Neighborhood", "")
        
        display_df = df.copy()
        if search_term:
            display_df = display_df[
                display_df['PatientId'].str.contains(search_term, case=False) | 
                display_df['Neighbourhood'].str.contains(search_term, case=False)
            ]
            
        # Styled Dataframe
        st.dataframe(
            display_df,
            column_config={
                "No-show": st.column_config.TextColumn(
                    "Status",
                    help="Did the patient show up?",
                    validate="^(Yes|No)$"
                ),
                "SMS_received": st.column_config.CheckboxColumn(
                    "SMS Sent",
                ),
                "ScheduledDay": st.column_config.DatetimeColumn(format="D MMM YYYY"),
                "AppointmentDay": st.column_config.DatetimeColumn(format="D MMM YYYY"),
            },
            use_container_width=True,
            hide_index=True,
            height=400
        )

    with tab2:
        # Filter for High Risk
        high_risk = df[(df['No-show'] == 'Yes') & (df['LeadDays'] > 5)]
        
        st.warning(f"Showing {len(high_risk)} patients who missed appointments booked >5 days in advance.")
        
        for index, row in high_risk.head(5).iterrows():
            with st.expander(f"⚠️ {row['PatientId']} - {row['Neighbourhood']}"):
                c_a, c_b = st.columns(2)
                c_a.write(f"**Age:** {row['Age']}")
                c_a.write(f"**Conditions:** {'Diabetes' if row['Diabetes'] else ''} {'Hypertension' if row['Hipertension'] else ''}")
                c_b.write(f"**Lead Time:** {row['LeadDays']} days")
                c_b.button("Call Patient", key=f"btn_{row['PatientId']}")

elif page == "Patients":
    st.title("Patient Directory")
    st.write("Patient list view placeholder.")
