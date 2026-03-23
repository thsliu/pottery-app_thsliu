import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body { background-color: #fafafa; }
h1 { text-align: center; }
.card {
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 20px;
}
.portfolio-title {
    text-align: center;
    font-size: 24px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏺 Suzie’s Pottery")

view_mode = st.radio("View Mode", ["Portfolio", "Admin"], horizontal=True)

# ---------- SETUP ----------
if not os.path.exists("images"):
    os.makedirs("images")

if os.path.exists("pottery_log.csv"):
    df = pd.read_csv("pottery_log.csv")
else:
    df = pd.DataFrame(columns=[
        "id","start_date","finish_date","days",
        "type","forming_method","clay","glaze",
        "images","notes"
    ])

# =========================================================
# 🎨 PORTFOLIO VIEW
# =========================================================
if view_mode == "Portfolio":

    st.markdown("### Handmade Pottery Collection")

    cols = st.columns(3)

    for i, row in df.iterrows():
        with cols[i % 3]:

            if pd.notna(row["images"]):
                img_list = row["images"].split("|")
                if img_list and os.path.exists(img_list[0]):
                    st.image(img_list[0], use_container_width=True)

            st.markdown(f"<div class='portfolio-title'>{row['type']}</div>", unsafe_allow_html=True)
            st.caption(f"{row['forming_method']} • {row['clay']}")

# =========================================================
# ⚙️ ADMIN VIEW
# =========================================================
else:

    st.subheader("⚙️ Manage Your Pieces")

    mode = st.radio("Action", ["Add New", "Edit Existing"], horizontal=True)

    # ---------- ADD ----------
    if mode == "Add New":

        with st.form("add_form"):
            c1, c2 = st.columns(2)

            with c1:
                piece_type = st.selectbox("Type", ["Teapot","Mug","Bowl","Vase"])
                forming_method = st.selectbox(
                    "Forming Method",
                    ["Wheel thrown","Slab hand built","Coiled","Pinched","Thrown and altered"]
                )
                clay = st.text_input("Clay")
                glaze = st.text_input("Glaze")

            with c2:
                start_date = st.date_input("Start Date", date.today())
                finish_date = st.date_input("Finish Date", date.today())
                new_images = st.file_uploader("Upload Images", accept_multiple_files=True)

            notes = st.text_area("Notes")

            submit = st.form_submit_button("Save")

        if submit:
            img_id = len(df) + 1
            image_paths = []

            if new_images:
                for i, img in enumerate(new_images):
                    path = f"images/{img_id}_{i}.png"
                    with open(path, "wb") as f:
                        f.write(img.getbuffer())
                    image_paths.append(path)

            days = (finish_date - start_date).days

            new_row = pd.DataFrame([[
                img_id, start_date, finish_date, days,
                piece_type, forming_method, clay, glaze,
                "|".join(image_paths), notes
            ]], columns=df.columns)

            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv("pottery_log.csv", index=False)

            st.success("Added!")

    # ---------- EDIT ----------
    else:

        if not df.empty:

            selected_id = st.selectbox("Select Piece", df["id"])
            record = df[df["id"] == selected_id].iloc[0]

            existing_images = record["images"].split("|") if pd.notna(record["images"]) else []

            st.write("### Existing Images")
            for img in existing_images:
                if os.path.exists(img):
                    st.image(img, width=120)

            with st.form("edit_form"):
                c1, c2 = st.columns(2)

                types = ["Teapot","Mug","Bowl","Vase"]
                methods = ["Wheel thrown","Slab hand built","Coiled","Pinched","Thrown and altered"]

                with c1:
                    piece_type = st.selectbox("Type", types, index=types.index(record["type"]) if record["type"] in types else 0)
                    forming_method = st.selectbox("Forming Method", methods, index=methods.index(record["forming_method"]) if record["forming_method"] in methods else 0)
                    clay = st.text_input("Clay", record["clay"])
                    glaze = st.text_input("Glaze", record["glaze"])

                with c2:
                    start_date = st.date_input("Start Date", pd.to_datetime(record["start_date"]))
                    finish_date = st.date_input("Finish Date", pd.to_datetime(record["finish_date"]))
                    new_images = st.file_uploader("Add Images", accept_multiple_files=True)

                notes = st.text_area("Notes", record["notes"])

                update = st.form_submit_button("Update")

            if update:
                image_paths = existing_images.copy()

                if new_images:
                    for i, img in enumerate(new_images):
                        path = f"images/{selected_id}_new_{i}.png"
                        with open(path, "wb") as f:
                            f.write(img.getbuffer())
                        image_paths.append(path)

                days = (finish_date - start_date).days

                df.loc[df["id"] == selected_id] = [
                    selected_id, start_date, finish_date, days,
                    piece_type, forming_method, clay, glaze,
                    "|".join(image_paths), notes
                ]

                df.to_csv("pottery_log.csv", index=False)

                st.success("Updated!")

            if st.button("Delete"):
                df = df[df["id"] != selected_id]
                df.to_csv("pottery_log.csv", index=False)
                st.warning("Deleted. Refresh.")

    # ---------- GALLERY ----------
    st.subheader("📋 Full Gallery")

    cols = st.columns(3)

    for i, row in df.iterrows():
        with cols[i % 3]:

            if pd.notna(row["images"]):
                for img_path in row["images"].split("|"):
                    if os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)

            st.write(f"**{row['type']}**")
            st.write(row["forming_method"])
            st.write(f"Clay: {row['clay']}")
            st.write(f"Glaze: {row['glaze']}")
            st.write(f"Days: {row['days']}")
            st.caption(row["notes"])