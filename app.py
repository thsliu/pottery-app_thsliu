import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
h1, h2, h3 { text-align: center; }
.block-container { padding-top: 2rem; }
.card {
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏺 Suzie’s Pottery Studio")

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

# ---------- SIDEBAR FILTER ----------
st.sidebar.header("🔍 Filter")

type_filter = st.sidebar.multiselect(
    "Type", df["type"].dropna().unique(), default=df["type"].dropna().unique()
)

filtered_df = df[
    df["type"].isin(type_filter)
] if not df.empty else df

# ---------- ADD ENTRY ----------
st.subheader("➕ Add New Piece")

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
        images = st.file_uploader("Upload Images", accept_multiple_files=True)

    notes = st.text_area("Notes")

    submit = st.form_submit_button("Save")

if submit:
    img_id = len(df) + 1
    image_paths = []

    for i, img in enumerate(images):
        path = f"images/{img_id}_{i}.png"
        with open(path, "wb") as f:
            f.write(img.getbuffer())
        image_paths.append(path)

    # Calculate days
    days = (finish_date - start_date).days

    new_row = pd.DataFrame([[
        img_id, start_date, finish_date, days,
        piece_type, forming_method, clay, glaze,
        "|".join(image_paths), notes
    ]], columns=df.columns)

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("pottery_log.csv", index=False)

    st.success("Saved!")

# ---------- DELETE ----------
st.subheader("✏️ Manage Pieces")

if not df.empty:
    selected_id = st.selectbox("Select Piece ID", df["id"])

    if st.button("Delete"):
        df = df[df["id"] != selected_id]
        df.to_csv("pottery_log.csv", index=False)
        st.warning("Deleted. Refresh page.")

# ---------- GALLERY ----------
st.subheader("🎨 Gallery")

cols = st.columns(3)

for i, row in filtered_df.iterrows():
    with cols[i % 3]:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if pd.notna(row["images"]):
            for img_path in row["images"].split("|"):
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)

        st.markdown(f"### {row['type']}")
        st.write(f"**Method:** {row['forming_method']}")
        st.write(f"**Clay:** {row['clay']}")
        st.write(f"**Glaze:** {row['glaze']}")
        st.write(f"**Days:** {row['days']}")
        st.caption(row["notes"])

        st.markdown('</div>', unsafe_allow_html=True)