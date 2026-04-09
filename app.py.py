import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import numpy as np

# Page configuration
st.set_page_config(page_title="Malaria Analysis Kenya", layout="wide")

# Title
st.title("🦟 Bayesian Geospatial Analysis of Malaria Incidence in Kenya")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("kenya_malaria_clean.csv")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("📊 Filters")
selected_region = st.sidebar.multiselect(
    "Select Region(s)",
    options=df['Region'].unique(),
    default=df['Region'].unique()[:3]
)

# Filter data
if selected_region:
    filtered_df = df[df['Region'].isin(selected_region)]
else:
    filtered_df = df

# Main content - 2 columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Malaria Cases by Region")
    region_counts = filtered_df['Region'].value_counts()
    fig1 = px.bar(x=region_counts.index, y=region_counts.values, 
                  color=region_counts.values, 
                  title="Number of Cases per Region")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("👥 Age Distribution")
    fig2 = px.histogram(filtered_df, x='Age', nbins=30, 
                        title="Age Distribution of Patients",
                        color_discrete_sequence=['blue'])
    st.plotly_chart(fig2, use_container_width=True)

# Row 2
st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("💉 Symptoms Prevalence")
    symptoms = ['Fever', 'Headache', 'Chills', 'Sweats', 'Fatigue']
    symptom_counts = []
    for symptom in symptoms:
        if symptom in filtered_df.columns:
            count = (filtered_df[symptom] == 'Yes').sum()
            symptom_counts.append(count)
    
    fig3 = px.pie(values=symptom_counts, names=symptoms, title="Symptom Distribution")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🩸 Malaria Diagnosis by Region")
    if 'Diagnosis' in filtered_df.columns:
        # Assuming Diagnosis column has malaria positive/negative
        diagnosis_by_region = pd.crosstab(filtered_df['Region'], filtered_df['Diagnosis'])
        fig4 = px.bar(diagnosis_by_region, title="Diagnosis by Region", barmode='group')
        st.plotly_chart(fig4, use_container_width=True)

# Row 3 - Bayesian Analysis Section
st.markdown("---")
st.subheader("🧮 Bayesian Analysis Results")

col5, col6, col7 = st.columns(3)

with col5:
    # Calculate posterior probability (simplified)
    malaria_cases = len(filtered_df[filtered_df.get('Diagnosis', pd.Series()) == 'Malaria']) if 'Diagnosis' in filtered_df.columns else 0
    total_cases = len(filtered_df)
    prior = 0.1  # Prior probability of malaria
    likelihood = malaria_cases / total_cases if total_cases > 0 else 0
    posterior = (likelihood * prior) / ((likelihood * prior) + (1 - prior) * (1 - likelihood))
    
    st.metric("Prior Probability", f"{prior:.0%}")
    st.metric("Posterior Probability", f"{posterior:.1%}")

with col6:
    st.metric("Total Patients", total_cases)
    st.metric("Malaria Positive", malaria_cases)

with col7:
    infection_rate = (malaria_cases / total_cases * 100) if total_cases > 0 else 0
    st.metric("Infection Rate", f"{infection_rate:.1f}%")
    
    # Risk ratio by region
    if 'Region' in filtered_df.columns and 'Diagnosis' in filtered_df.columns:
        region_risk = filtered_df.groupby('Region').apply(
            lambda x: (x['Diagnosis'] == 'Malaria').mean()
        ).max()
        st.metric("Highest Risk Region", region_risk.nlargest(1).index[0] if len(region_risk) > 0 else "N/A")

# Footer
st.markdown("---")
st.caption("Data Source: Kenya DHS 2022 | Bayesian Geospatial Analysis")