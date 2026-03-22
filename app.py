import streamlit as st
import pandas as pd
import os
from datetime import date

# Setup
st.set_page_config(layout="wide")
st.title("🏺 My Pottery Gallery")

# Ensure image folder exists
if not os.path.exists("images"):
    os.makedirs("images")

# Load data
if os.path.exists("pottery_log.csv"):
    df = pd.read_csv("pottery_log.csv")
else:
    df = pd.DataFrame(columns=[
        "id","date","type","clay","image","notes"
    ])

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter")

type_filter = st.sidebar.multiselect(
    "Type", options=df["type"].unique(), default=df["type"].unique()
)

filtered_df = df[df["type"].isin(type_filter)] if not df.empty else df

# --- Add New Piece ---
st.subheader("➕ Add New Piece")

with st.form("add_piece"):
    col1, col2 = st.columns(2)

    with col1:
        piece_type = st.selectbox("Type", ["Teapot","Mug","Bowl"])
        clay = st.text_input("Clay")

    with col2:
        entry_date = st.date_input("Date", date.today())
        image_file = st.file_uploader("Upload Image", type=["jpg","png"])

    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Save")

if submitted and image_file is not None:
    img_id = len(df) + 1
    image_path = f"images/{img_id}.png"

    with open(image_path, "wb") as f:
        f.write(image_file.getbuffer())

    new_row = pd.DataFrame([[
        img_id, entry_date, piece_type, clay, image_path, notes
    ]], columns=df.columns)

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("pottery_log.csv", index=False)

    st.success("Saved!")

# --- Gallery ---
st.subheader("🎨 Gallery")

cols = st.columns(3)

for i, row in filtered_df.iterrows():
    with cols[i % 3]:
        if os.path.exists(row["image"]):
            st.image(row["image"], use_container_width=True)
        st.write(f"**{row['type']}**")
        st.write(f"Clay: {row['clay']}")
        st.write(row["date"])
        st.caption(row["notes"])