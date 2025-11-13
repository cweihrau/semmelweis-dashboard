# app.py
# Some code snippets and text assisted by ChatGPT.

import streamlit as st
import pandas as pd
import altair as alt

# ---------- Data loading ----------
@st.cache_data
def load_data():
    # Make sure the CSV file is in the same folder as this app
    # and named exactly: yearly_deaths_by_clinic.csv
    df = pd.read_csv("yearly_deaths_by_clinic.csv")
    df["mortality_rate"] = df["Deaths"] / df["Birth"] * 100
    return df

df = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
clinic_options = ["All clinics"] + sorted(df["Clinic"].unique().tolist())
selected_clinic = st.sidebar.selectbox("Select clinic", clinic_options)

if selected_clinic == "All clinics":
    plot_df = df.copy()
else:
    plot_df = df[df["Clinic"] == selected_clinic].copy()

handwashing_year = 1847

# ---------- Title & description ----------
st.title("Handwashing and Childbed Fever: Semmelweis’s Data")

st.write(
    """
In the mid-19th century, Dr. Ignaz Semmelweis observed alarmingly high death rates from
childbed fever in maternity clinics. By introducing a simple intervention—hand-washing with a
chlorine solution—he dramatically reduced mortality. This dashboard visualizes yearly births,
deaths, and mortality rates in two clinics before and after hand-washing was introduced.
    """
)

st.caption("Data: Yearly births and deaths by clinic, including period before and after hand-washing (1847).")

# ---------- Births over time ----------
st.subheader("Births over time")

births_chart = (
    alt.Chart(plot_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Birth:Q", title="Number of births"),
        color=alt.Color("Clinic:N", title="Clinic"),
        tooltip=["Year", "Clinic", "Birth"]
    )
    .properties(height=300)
)

st.altair_chart(births_chart, use_container_width=True)


# ---------- Deaths over time ----------
st.subheader("Deaths over time")

deaths_chart = (
    alt.Chart(plot_df)
    .mark_line(point=True, color="red")
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Deaths:Q", title="Number of deaths"),
        color=alt.Color("Clinic:N", title="Clinic"),
        tooltip=["Year", "Clinic", "Deaths", alt.Tooltip("mortality_rate", format=".2f")]
    )
    .properties(height=300)
)

st.altair_chart(deaths_chart, use_container_width=True)

# ---------- Mortality rate chart ----------
st.subheader("Mortality rate (%) over time")

mortality_chart = alt.Chart(plot_df).mark_line(point=True).encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("mortality_rate:Q", title="Mortality rate (%)"),
    color=alt.Color("Clinic:N", title="Clinic"),
    tooltip=["Year", "Clinic", alt.Tooltip("mortality_rate", format=".2f", title="Mortality (%)")]
).properties(
    height=350
)

# Vertical rule for hand-washing introduction (now white)
handwashing_rule = (
    alt.Chart(pd.DataFrame({"Year": [handwashing_year]}))
    .mark_rule(strokeDash=[4, 4], color="white")
    .encode(x="Year:O")
)

mortality_chart = mortality_chart + handwashing_rule



st.altair_chart(mortality_chart, use_container_width=True)

# ---------- Summary statistics ----------
st.subheader("Before vs. after hand-washing")

before = df[df["Year"] < handwashing_year]
after = df[df["Year"] >= handwashing_year]

before_rate = before["mortality_rate"].mean()
after_rate = after["mortality_rate"].mean()

col1, col2 = st.columns(2)
col1.metric("Average mortality before hand-washing", f"{before_rate:.2f}%")
col2.metric("Average mortality after hand-washing", f"{after_rate:.2f}%", delta=f"{after_rate - before_rate:.2f} pts")

st.write(
    """
**Findings:**  
After hand-washing was introduced, the average mortality rate dropped sharply compared to the years before.
This suggests a strong relationship between basic hygiene practices and survival, supporting Semmelweis’s
conclusion that hand-washing was crucial in preventing childbed fever.
    """
)
