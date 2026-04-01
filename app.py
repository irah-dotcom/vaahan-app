import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Vaahan Manager", layout="wide")

FILE = "vaahan.csv"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=[
        "RegNo", "Fitness", "Tax", "Permit", "Contact", "Notes"
    ])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

for col in ["Fitness", "Tax", "Permit"]:
    df[col] = pd.to_datetime(df[col], errors='coerce')

today = pd.to_datetime(datetime.today().date())

st.title("🚗 Vehicle Management System")

menu = st.sidebar.selectbox("Menu", ["Home", "Vaahan"])

if menu == "Home":
    st.image("logo.png", width=200)
    st.subheader("Select Service")
    st.info("👉 Use sidebar to go to Vaahan section")

elif menu == "Vaahan":

    st.header("🚗 Vaahan Dashboard")

    total = len(df)

    expired = df[
        (df["Fitness"] < today) |
        (df["Tax"] < today) |
        (df["Permit"] < today)
    ]

    st.metric("Total Vehicles", total)
    st.metric("Expired / Issues", len(expired))

    st.divider()

    option = st.selectbox("Choose Option", ["Add Data", "View / Search"])

    if option == "Add Data":
        st.subheader("➕ Add Vehicle Data")

        reg = st.text_input("Registration Number")
        fitness = st.date_input("Fitness Validity")
        tax = st.date_input("Tax Validity")
        permit = st.date_input("Permit Validity")
        contact = st.text_input("Contact Number")
        notes = st.text_area("Notes")

        if st.button("Save"):
            if reg:
                if reg in df["RegNo"].values:
                    st.error("❌ Reg No already exists!")
                else:
                    new = pd.DataFrame([[reg, fitness, tax, permit, contact, notes]],
                                       columns=df.columns)
                    new.to_csv(FILE, mode='a', header=False, index=False)
                    st.success("✅ Data Saved! Refresh page.")
            else:
                st.warning("⚠️ Enter Reg No")

    elif option == "View / Search":
        st.subheader("🔍 Search & Manage")

        search = st.text_input("Search by Reg No")

mobile_search = st.text_input("Search by Mobile Number")

month_filter = st.selectbox(
    "Filter by Month (Fitness Date)",
    ["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
)

temp_df = df.copy()

if search:
    temp_df = temp_df[temp_df["RegNo"].str.contains(search, case=False)]

if mobile_search:
    temp_df = temp_df[temp_df["Contact"].astype(str).str.contains(mobile_search)]

month_map = {
    "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
    "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12
}

if month_filter != "All":
    temp_df = temp_df[temp_df["Fitness"].dt.month == month_map[month_filter]]
            with st.expander(f"{status} 🚗 {row['RegNo']}"):

                st.write(f"Fitness: {row['Fitness'].date()}")
                st.write(f"Tax: {row['Tax'].date()}")
                st.write(f"Permit: {row['Permit'].date()}")
                st.write(f"Contact: {row['Contact']}")
                st.write(f"Notes: {row['Notes']}")

                new_fitness = st.date_input("Edit Fitness", row["Fitness"], key=f"f{i}")
                new_tax = st.date_input("Edit Tax", row["Tax"], key=f"t{i}")
                new_permit = st.date_input("Edit Permit", row["Permit"], key=f"p{i}")
                new_contact = st.text_input("Edit Contact", row["Contact"], key=f"c{i}")
                new_notes = st.text_area("Edit Notes", row["Notes"], key=f"n{i}")

                if st.button("Update", key=f"u{i}"):
                    df.loc[i, ["Fitness","Tax","Permit","Contact","Notes"]] = [
                        new_fitness, new_tax, new_permit, new_contact, new_notes
                    ]
                    df.to_csv(FILE, index=False)
                    st.success("Updated! Refresh page.")

                if st.button("Delete", key=f"d{i}"):
                    df = df.drop(i)
                    df.to_csv(FILE, index=False)
                    st.warning("Deleted! Refresh page.")
