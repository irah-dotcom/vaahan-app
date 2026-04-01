import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Config ---
st.set_page_config(page_title="Vaahan Manager", layout="wide")
FILE = "vaahan.csv"

# --- Initialize CSV ---
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["RegNo", "Fitness", "Tax", "Permit", "Contact", "Notes"])
    df.to_csv(FILE, index=False)

# --- Load CSV with session_state ---
if "df" not in st.session_state:
    df = pd.read_csv(FILE, dtype={"Contact": str})
    for col in ["Fitness", "Tax", "Permit"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["Contact"] = df["Contact"].fillna("")  # ensure contact not NaN
    df["Notes"] = df["Notes"].fillna("")
    st.session_state.df = df
else:
    df = st.session_state.df

today = pd.to_datetime(datetime.today().date())

# --- Sidebar ---
st.sidebar.title("🚗 Vaahan Manager")
menu = st.sidebar.selectbox("Menu", ["Home", "Vaahan"])

# --- Home ---
if menu == "Home":
    st.image("logo.png", width=200)
    st.subheader("Select Service")
    st.info("👉 Use the sidebar to go to Vaahan section")

# --- Vaahan Dashboard ---
elif menu == "Vaahan":
    st.header("🚗 Vaahan Dashboard")

    st.subheader("All Vehicles")
    st.dataframe(st.session_state.df.reset_index(drop=True), use_container_width=True)
    st.divider()

    option = st.selectbox("Choose Option", ["Add Data", "View / Search"])

    # --- Add Data ---
    if option == "Add Data":
        st.subheader("➕ Add Vehicle Data")
        reg = st.text_input("Registration Number", key="add_reg")
        fitness = st.date_input("Fitness Validity", key="add_fit")
        tax = st.date_input("Tax Validity", key="add_tax")
        permit = st.date_input("Permit Validity", key="add_permit")
        contact = st.text_input("Contact Number", key="add_contact", max_chars=10)
        notes = st.text_area("Notes", key="add_notes")

        if st.button("Save", key="add_save"):
            if not reg:
                st.warning("⚠️ Enter Registration Number")
            elif reg in st.session_state.df["RegNo"].values:
                st.error("❌ Registration Number already exists!")
            elif not contact.isdigit() or len(contact) > 10:
                st.error("❌ Contact must be a number with max 10 digits")
            else:
                new_row = {
                    "RegNo": reg,
                    "Fitness": pd.Timestamp(fitness),
                    "Tax": pd.Timestamp(tax),
                    "Permit": pd.Timestamp(permit),
                    "Contact": contact,
                    "Notes": notes
                }
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.df.to_csv(FILE, index=False)
                st.success("✅ Vehicle Added Successfully!")

    # --- View / Search ---
    elif option == "View / Search":
        st.subheader("🔍 Search & Manage Vehicles")

        search_reg = st.text_input("Search by Registration Number", key="search_reg")
        search_contact = st.text_input("Search by Contact Number", key="search_contact")
        month_filter = st.selectbox(
            "Filter by Month (Fitness)",
            ["All"] + [datetime(2000, m, 1).strftime("%B") for m in range(1, 13)],
            key="search_month"
        )

        temp_df = st.session_state.df.copy().reset_index(drop=False)

        # Apply filters
        if search_reg:
            temp_df = temp_df[temp_df["RegNo"].str.contains(search_reg, case=False, na=False)]
        if search_contact:
            temp_df = temp_df[temp_df["Contact"].str.contains(search_contact, na=False)]
        if month_filter != "All":
            month_number = datetime.strptime(month_filter, "%B").month
            temp_df = temp_df[temp_df["Fitness"].dt.month == month_number]

        st.dataframe(temp_df.drop(columns="index").reset_index(drop=True), use_container_width=True)
        st.divider()

        # --- Edit/Delete Section ---
        for _, row in temp_df.iterrows():
            original_index = row["index"]
            with st.expander(f"🚗 {row['RegNo']} | Contact: {row['Contact']}"):
                new_fitness = st.date_input("Edit Fitness", row["Fitness"], key=f"f{original_index}")
                new_tax = st.date_input("Edit Tax", row["Tax"], key=f"t{original_index}")
                new_permit = st.date_input("Edit Permit", row["Permit"], key=f"p{original_index}")
                new_contact = st.text_input("Edit Contact", str(row["Contact"]), max_chars=10, key=f"c{original_index}")
                new_notes = st.text_area("Edit Notes", row["Notes"], key=f"n{original_index}")

                # Update
                if st.button("Update", key=f"u{original_index}"):
                    try:
                        if not new_contact.isdigit() or len(new_contact) > 10:
                            st.error("❌ Contact must be a number with max 10 digits")
                        else:
                            st.session_state.df.at[original_index, "Fitness"] = pd.Timestamp(new_fitness)
                            st.session_state.df.at[original_index, "Tax"] = pd.Timestamp(new_tax)
                            st.session_state.df.at[original_index, "Permit"] = pd.Timestamp(new_permit)
                            st.session_state.df.at[original_index, "Contact"] = new_contact
                            st.session_state.df.at[original_index, "Notes"] = new_notes
                            st.session_state.df.to_csv(FILE, index=False)
                            st.success("✅ Vehicle Updated Successfully!")
                    except Exception as e:
                        st.error(f"❌ Error updating: {e}")

                # Delete
                if st.button("Delete", key=f"d{original_index}"):
                    st.session_state.df = st.session_state.df.drop(original_index).reset_index(drop=True)
                    st.session_state.df.to_csv(FILE, index=False)
                    st.warning("⚠️ Vehicle Deleted Successfully!")
