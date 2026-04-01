import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Config ---
st.set_page_config(page_title="Vaahan Manager", layout="wide")
FILE = "vaahan.csv"

# --- Create CSV if not exists ---
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["RegNo", "Fitness", "Tax", "Permit", "Contact", "Notes"])
    df.to_csv(FILE, index=False)

df = pd.read_csv(FILE)

# Convert dates
for col in ["Fitness", "Tax", "Permit"]:
    df[col] = pd.to_datetime(df[col], errors='coerce')

today = pd.to_datetime(datetime.today().date())

# --- Sidebar ---
st.sidebar.title("🚗 Vaahan Manager")
menu = st.sidebar.selectbox("Menu", ["Home", "Vaahan"])

# --- Home Page ---
if menu == "Home":
    st.image("logo.png", width=200)
    st.subheader("Select Service")
    st.info("👉 Use the sidebar to go to Vaahan section")

# --- Vaahan Page ---
elif menu == "Vaahan":
    st.header("🚗 Vaahan Dashboard")
    
    st.subheader("All Vehicles")
    st.dataframe(df, use_container_width=True)  # Table view for all vehicles

    st.divider()
    
    option = st.selectbox("Choose Option", ["Add Data", "View / Search"])

    # --- Add Data ---
    if option == "Add Data":
        st.subheader("➕ Add Vehicle Data")
        reg = st.text_input("Registration Number")
        fitness = st.date_input("Fitness Validity")
        tax = st.date_input("Tax Validity")
        permit = st.date_input("Permit Validity")
        contact = st.text_input("Contact Number")
        notes = st.text_area("Notes")

        if st.button("Save"):
            if not reg:
                st.warning("⚠️ Enter Registration Number")
            elif reg in df["RegNo"].values:
                st.error("❌ Registration Number already exists!")
            elif not contact.isdigit() or len(contact) > 10:
                st.error("❌ Contact must be a number with max 10 digits")
            else:
                new = pd.DataFrame([[reg, fitness, tax, permit, contact, notes]], columns=df.columns)
                new.to_csv(FILE, mode='a', header=False, index=False)
                st.success("✅ Data Saved!")
                st.experimental_rerun()  # Auto refresh

    # --- View / Search ---
    elif option == "View / Search":
        st.subheader("🔍 Search & Manage Vehicles")

        search_reg = st.text_input("Search by Registration Number")
        search_contact = st.text_input("Search by Contact Number")
        month_filter = st.selectbox("Filter by Month", ["All"] + [datetime(2000, m, 1).strftime('%B') for m in range(1, 13)])

        temp_df = df.copy()

        # Filter by RegNo
        if search_reg:
            temp_df = temp_df[temp_df["RegNo"].str.contains(search_reg, case=False)]

        # Filter by Contact
        if search_contact:
            temp_df = temp_df[temp_df["Contact"].astype(str).str.contains(search_contact)]

        # Filter by month (Fitness)
        if month_filter != "All":
            month_number = datetime.strptime(month_filter, "%B").month
            temp_df = temp_df[temp_df["Fitness"].dt.month == month_number]

        st.dataframe(temp_df, use_container_width=True)

        st.divider()

        for i, row in temp_df.iterrows():
            with st.expander(f"🚗 {row['RegNo']} | Contact: {row['Contact']}"):
                new_fitness = st.date_input("Edit Fitness", row["Fitness"], key=f"f{i}")
                new_tax = st.date_input("Edit Tax", row["Tax"], key=f"t{i}")
                new_permit = st.date_input("Edit Permit", row["Permit"], key=f"p{i}")
                new_contact = st.text_input("Edit Contact", row["Contact"], key=f"c{i}", max_chars=10)
                new_notes = st.text_area("Edit Notes", row["Notes"], key=f"n{i}")

                # Update button
                if st.button("Update", key=f"u{i}"):
                    if not new_contact.isdigit() or len(new_contact) > 10:
                        st.error("❌ Contact must be a number with max 10 digits")
                    else:
                        df.loc[i, ["Fitness","Tax","Permit","Contact","Notes"]] = [
                            new_fitness, new_tax, new_permit, new_contact, new_notes
                        ]
                        df.to_csv(FILE, index=False)
                        st.success("✅ Updated!")
                        st.experimental_rerun()  # Auto refresh

                # Delete button
                if st.button("Delete", key=f"d{i}"):
                    df = df.drop(i)
                    df.to_csv(FILE, index=False)
                    st.warning("⚠️ Deleted!")
                    st.experimental_rerun()  # Auto refresh
