import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO
from jinja2 import Template
from weasyprint import HTML
import base64
import openpyxl
import math

st.set_page_config(layout="wide")

# ---------------- IMAGE BASE64 ----------------
def image_to_base64(path):
    try:
        if pd.isna(path) or path == "":
            return ""

        path = str(path).strip()

        if path.startswith("http"):
            response = requests.get(path)
            img = Image.open(BytesIO(response.content))
        else:
            full_path = os.path.abspath(path)
            if not os.path.exists(full_path):
                return ""
            img = Image.open(full_path)

        img = img.convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format="PNG")

        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    except:
        return ""


# ---------------- LOAD EXCEL ----------------
df = pd.read_excel("products.xlsx")
df.columns = df.columns.str.strip().str.lower()

clients_df = pd.read_excel("clients.xlsx")
sales_df = pd.read_excel("sales.xlsx")

design_df = pd.read_excel("design.xlsx")
design_df.columns = design_df.columns.str.strip().str.lower()
  # Streamlit radio value #




# ---------------- CLIENT + SALES ----------------
st.subheader("Client & Sales Selection")

c1, c2 = st.columns(2)

with c1:
    client_names = clients_df["client_name"].tolist()
    selected_client = st.selectbox("Choose Client", client_names)

with c2:
    sales_names = sales_df["name"].tolist()
    selected_sales = st.selectbox("Choose Sales Person", sales_names)

client_logo_path = clients_df[
    clients_df["client_name"] == selected_client
]["logo_path"].values[0]

sales_info = sales_df[sales_df["name"] == selected_sales].iloc[0]


# ---------------- CLEAN COLUMNS ----------------
col_product = [c for c in df.columns if "product" in c][0]
col_price = [c for c in df.columns if "price" in c][0]
col_category = [c for c in df.columns if "category" in c][0]
col_brand = [c for c in df.columns if "brand" in c][0]
col_image = [c for c in df.columns if "image" in c][0]
col_desc = [c for c in df.columns if "description" in c][0] if "description" in df.columns else None
col_mrp = "mrp" if "mrp" in df.columns else None


# ---------------- FORMAT ----------------
df[col_product] = df[col_product].astype(str).str.title()
df[col_brand] = df[col_brand].astype(str).str.title()
df[col_category] = df[col_category].astype(str).str.title()

df[col_price] = pd.to_numeric(
    df[col_price].astype(str).str.replace(r"[^\d.]", "", regex=True),
    errors="coerce"
).fillna(0)

if col_mrp:
    df[col_mrp] = pd.to_numeric(
        df[col_mrp].astype(str).str.replace(r"[^\d.]", "", regex=True),
        errors="coerce"
    ).fillna(0)


def format_description(desc):
    if pd.isna(desc):
        return "No description available"
    points = str(desc).replace("\n", ",").split(",")
    points = [p.strip() for p in points if p.strip()]
    return "<ul>" + "".join([f"<li>{p}</li>" for p in points]) + "</ul>"


# ---------------- FILTERS ----------------
st.subheader("Filters")

f1, f2, f3 = st.columns(3)

with f1:
    min_price = st.number_input("Min Price", value=0)

with f2:
    max_price = st.number_input("Max Price", value=int(df[col_price].max()))

with f3:
    search = st.text_input("Search Product")


# ---------------- CATEGORY ----------------
st.subheader("Category")
categories = sorted(df[col_category].dropna().unique())
groups = {"A-E": [], "F-J": [], "K-O": [], "P-T": [], "U-Z": []}

for cat in categories:
    first = str(cat)[0].upper()
    if "A" <= first <= "E":
        groups["A-E"].append(cat)
    elif "F" <= first <= "J":
        groups["F-J"].append(cat)
    elif "K" <= first <= "O":
        groups["K-O"].append(cat)
    elif "P" <= first <= "T":
        groups["P-T"].append(cat)
    else:
        groups["U-Z"].append(cat)

cols = st.columns(5)
for i, (g, values) in enumerate(groups.items()):
    with cols[i]:
        st.markdown(f"**{g}**")
        with st.container(height=200):
            for cat in values:
                st.checkbox(cat, key=f"cat_{cat}")


# ---------------- BRAND ----------------
st.subheader("Brand")
brands = sorted(df[col_brand].dropna().unique())
groups = {"A-E": [], "F-J": [], "K-O": [], "P-T": [], "U-Z": []}

for br in brands:
    first = str(br)[0].upper()
    if "A" <= first <= "E":
        groups["A-E"].append(br)
    elif "F" <= first <= "J":
        groups["F-J"].append(br)
    elif "K" <= first <= "O":
        groups["K-O"].append(br)
    elif "P" <= first <= "T":
        groups["P-T"].append(br)
    else:
        groups["U-Z"].append(br)

cols = st.columns(5)
for i, (g, values) in enumerate(groups.items()):
    with cols[i]:
        st.markdown(f"**{g}**")
        with st.container(height=200):
            for br in values:
                st.checkbox(br, key=f"brand_{br}")


# ---------------- FILTER APPLY ----------------
filtered = df[(df[col_price] >= min_price) & (df[col_price] <= max_price)]

selected_categories = [c for c in categories if st.session_state.get(f"cat_{c}", False)]
selected_brands = [b for b in brands if st.session_state.get(f"brand_{b}", False)]

if selected_categories:
    filtered = filtered[filtered[col_category].isin(selected_categories)]

if selected_brands:
    filtered = filtered[filtered[col_brand].isin(selected_brands)]

if search:
    filtered = filtered[filtered[col_product].str.contains(search, case=False, na=False)]


# ---------------- LAYOUT ----------------
design_option = st.radio(
    "Choose Catalogue Design",
    ["Design 1", "Design 2", "Design 3", "Design 4"],
    horizontal=True
)
selected_design = design_option
filtered_design = design_df[
    design_df["design_name"].str.strip().str.lower() ==
    selected_design.strip().lower()
]
pages = {}
for _, row in filtered_design.iterrows():
    pages[row["image_name"]] = image_to_base64(row["image_path"])




layout_option = st.radio(
    "Choose Layout",
    ["1 Image per Page", "2 Images per Page"],
    horizontal=True
)

col1, _ = st.columns([0.1, 0.9])

with col1:
    client_percent = st.number_input("Client Profit %", value=25)

# ---------------- PDF GENERATE ----------------
if st.button("Create Catalogue PDF", key="create_pdf_unique"):

    def logo_to_base64(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()

    ud_logo = logo_to_base64("logo.png")
    client_logo = logo_to_base64(client_logo_path)

    middle_page = pages.get("middle page2", "")
    first_page = pages.get("first page1", "")
    terms_page = pages.get("trems page3", "")
    last_page = pages.get("last page4", "")

    template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "single.html" if layout_option == "1 Image per Page" else "double.html"
    )

    with open(template_path, encoding="utf-8") as f:
        template = Template(f.read())

    # ---------------- FIXED PRODUCT SELECTION ----------------
    temp = []

    for index, row in filtered.iterrows():
        if st.session_state.get(f"product_{index}", False):

            base_price = row[col_price]
            final_price = int(base_price + (base_price * client_percent / 100) + 0.5)

        temp.append({
            "name": f"{row[col_brand]} - {row[col_product]}",
            "price": str(final_price),
            "mrp": str(int(row[col_mrp])) if col_mrp and pd.notna(row[col_mrp]) else "",
            "description": format_description(row[col_desc]) if col_desc else "",
            "image": image_to_base64(row[col_image])
        })

    if len(temp) == 0:
        st.error("Please select products first!")
        st.stop()

    page_size = 1 if layout_option == "1 Image per Page" else 2

    products_pdf = []
    for i in range(0, len(temp), page_size):
        products_pdf.append(temp[i:i+page_size])

    html = template.render(
    first_page=first_page,
    middle_page=middle_page,
    terms_page=terms_page,
    last_page=last_page,
    ud_logo=ud_logo,
    client_logo=client_logo,
    products=[item for sub in products_pdf for item in sub],  # 🔥 FIX
    sales_name=sales_info["name"],
    sales_phone=sales_info["phone"]
)

    st.download_button("Download Catalogue", html, file_name="catalog.html")

    with open("catalog.pdf", "rb") as f:
        st.download_button("Download Catalogue PDF", f, file_name="catalog.pdf")


# ---------------- PRODUCT LIST ----------------
st.subheader("Products")

if "select_all" not in st.session_state:
    st.session_state["select_all"] = False


def toggle_all():
    for i in filtered.index:
        st.session_state[f"product_{i}"] = st.session_state["select_all"]


st.checkbox("Select All", key="select_all", on_change=toggle_all)

cols_per_row = 6

for i in range(0, len(filtered), cols_per_row):
    row_items = filtered.iloc[i:i+cols_per_row]
    cols = st.columns(cols_per_row)

    for idx, (index, row) in enumerate(row_items.iterrows()):
        with cols[idx]:

            st.checkbox("Select", key=f"product_{index}")

            try:
                img_path = row[col_image]
                if isinstance(img_path, str) and img_path.startswith("http"):
                    response = requests.get(img_path)
                    img = Image.open(BytesIO(response.content))
                else:
                    img = Image.open(os.path.abspath(str(img_path)))

                st.image(img, width=150)

            except:
                st.warning("No image")

            st.write(f"{row[col_brand]} - {row[col_product]}")

            if col_mrp:
                st.markdown(f"**MRP:** ₹ {int(row[col_mrp])}")

            st.markdown(f"**Price:** ₹ {int(row[col_price])}")