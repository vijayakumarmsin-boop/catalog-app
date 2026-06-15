import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO
from jinja2 import Template

import base64
import openpyxl
import math
import mysql.connector
import smtplib
from email.mime.text import MIMEText
import urllib.parse
from login import check_login
import uuid
import tempfile
import webbrowser

st.set_page_config(layout="wide")

# ================= INIT SESSION STATE =================
if "selected_products" not in st.session_state:
    st.session_state["selected_products"] = set()
    
    
    
def get_delivery_text(value):
    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return "Not Provided"

    if value.isdigit():
        return f"{int(value) + 2} Working Days After Confirmation"

    return value


preview_id = st.query_params.get("preview_id")

if isinstance(preview_id, list):
    preview_id = preview_id[0]
    
if preview_id:

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="catalog123",
        database="catalogue_db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT html_content FROM preview_html WHERE order_id=%s",
        (preview_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        preview_html = row[0]

        st.components.v1.html(
        preview_html,
        height=900,
        scrolling=True
        )
    st.stop()

def get_delivery_text(delivery_value):
    delivery_value = str(delivery_value).strip()

    if delivery_value.isdigit():
        return f"Delivery Timeline*{int(delivery_value) + 2}* Working Days After Confirmation"

    return delivery_value

preview_owner = st.session_state.get("preview_owner", None)
role = st.session_state.get("role")
username = st.session_state.get("username")

# ✅ STEP 1: READ FROM URL FIRST
query_params = st.query_params

order_id_from_url = query_params.get("order_id", None)

if isinstance(order_id_from_url, list):
    order_id_from_url = order_id_from_url[0]

order_id_from_url = str(order_id_from_url).strip() if order_id_from_url else None

selected_categories = []
selected_brands = []

if order_id_from_url:

    conn = st.write("Database removed for cloud run")

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM order_filters WHERE order_id = %s
    """, (order_id_from_url,))

    data = cursor.fetchone()
    conn.close()

    if data:


        search = data["search_text"]

        selected_categories = data["categories"].split(",") if data["categories"] else []
        selected_brands = data["brands"].split(",") if data["brands"] else []
        saved_sales_person = data["sales_person"]

        st.session_state["restore_filters"] = True
        
        
# ✅ STEP 2: USE URL VALUE IF EXISTS, ELSE GENERATE NEW
if order_id_from_url:
    order_id = order_id_from_url
else:
    order_id = str(uuid.uuid4())


@st.cache_data
def load_product_image(path):
    try:
        if isinstance(path, str) and path.startswith("http"):
            response = requests.get(path)
            return Image.open(BytesIO(response.content))
        else:
            return Image.open(os.path.abspath(str(path)))
    except:
        return None
    
@st.cache_data
def load_data():
    df = pd.read_excel("products.xlsx")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

col_product = [c for c in df.columns if "product" in c][0]
col_price = [c for c in df.columns if "price" in c][0]
col_category = [c for c in df.columns if "category" in c][0]
col_brand = [c for c in df.columns if "brand" in c][0]
col_image = [c for c in df.columns if "image" in c][0]
col_desc = [c for c in df.columns if "description" in c][0] if "description" in df.columns else None
col_mrp = "mrp" if "mrp" in df.columns else None

df[col_brand] = df[col_brand].astype(str).str.lower().str.strip()
df[col_category] = df[col_category].astype(str).str.lower().str.strip()
df[col_product] = df[col_product].astype(str).str.lower().str.strip()

categories = sorted(df[col_category].dropna().unique())
brands = sorted(df[col_brand].dropna().unique())



def procurement_app():
    print("Procurement screen")


def sales_app():
    print("Sales screen")


def logo_to_base64(path):
    if path is None or path == "" or pd.isna(path):
        return ""

    if not os.path.exists(path):
        return ""

    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


check_login()

if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = {}

role = st.session_state.role
is_procurement = (role == "procurement")
is_sales = (role == "sales")

st.sidebar.title("User Info")
st.sidebar.write("User :", st.session_state.username)
st.sidebar.write("Role :", st.session_state.role)


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
clients_df = pd.read_excel("clients.xlsx")
sales_df = pd.read_excel("sales.xlsx")
design_df = pd.read_excel("design.xlsx")

client_list = clients_df["client_name"].dropna().tolist()
client_list.insert(0, "None")

df = df.where(pd.notnull(df), None)
clients_df = clients_df.where(pd.notnull(clients_df), None)
sales_df = sales_df.where(pd.notnull(sales_df), None)
design_df = design_df.where(pd.notnull(design_df), None)

design_df.columns = design_df.columns.str.strip().str.lower()


# ---------------- CLIENT + SALES ----------------
st.subheader("Client & Sales Selection")

c1, c2 = st.columns(2)

with c1:
    client_names = clients_df["client_name"].tolist()
    selected_client = st.selectbox("Choose Client", client_names)

with c2:

    sales_names = sales_df["name"].tolist()

    default_index = 0

    if order_id_from_url and data:
        saved_sales_person = data.get("sales_person")

        if saved_sales_person in sales_names:
            default_index = sales_names.index(saved_sales_person)

    selected_sales = st.selectbox(
        "Choose Sales Person",
        sales_names,
        index=default_index
    )

    match = clients_df[clients_df["client_name"] == selected_client]

    if len(match) > 0:
        client_logo_path = match["logo_path"].iloc[0]
    else:
        client_logo_path = None

sales_info = sales_df[sales_df["name"] == selected_sales].iloc[0]


# --------------- FORMAT ----------------
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

filter_type = st.radio(
    "Filter By",
    ["Price", "MRP"],
    horizontal=True
)

f1, f2, f3 = st.columns(3)

with f1:
    min_price = st.number_input("Min Price", value=1, min_value=1, step=1)

with f2:
    max_price = st.number_input(
        "Max Price",
        value=int(df[col_price].max()),
        max_value=int(df[col_price].max())
    )

with f3:
    search = st.text_input("Search Product")

if st.session_state.get("restore_filters"):

    for c in categories:
        key = str(c).strip().lower()
        st.session_state[f"cat_{key}"] = (key in selected_categories)

    for b in brands:
        key = str(b).strip().lower()
        st.session_state[f"brand_{key}"] = (key in selected_brands)


if st.button("➕ Add New Product"):

    @st.dialog("Add New Product")
    def add_product_dialog():

        new_image = st.text_input("Image URL")
        new_category = st.text_input("Category")
        new_brand = st.text_input("Brand")
        new_product = st.text_input("Product Name")
        new_price = st.number_input("Dealer Price", min_value=0, step=1)
        new_mrp = st.number_input("MRP", min_value=0, step=1)
        new_delivery = st.text_input("Delivery Timeline")

        if st.button("✅ Done"):

            new_row = {
                col_category: new_category,
                col_brand: new_brand,
                col_product: new_product,
                col_price: new_price,
                col_mrp: new_mrp,
                col_image: new_image,
                "delivery": new_delivery
            }

            df.loc[len(df)] = new_row
            df.to_excel("products.xlsx", index=False)

            st.cache_data.clear()
            st.rerun()

    add_product_dialog()
# ---------------- CATEGORY ----------------
st.subheader("Category")
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
              st.checkbox(cat.title(), key=f"cat_{str(cat).strip().lower()}")
              key=f"cat_{str(cat).strip().lower()}"


# ---------------- BRAND ----------------
st.subheader("Brand")
groups = {"A-E": [], "F-J": [], "K-O": [], "P-T": [], "U-Z": []}

for br in sorted(brands, key=lambda x: str(x).lower()):
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
                st.checkbox(
                    str(br).title(),
                    key=f"brand_{str(br).strip().lower()}"
                )



# ================= CLEAN FILTER ENGINE =================
df_full = df.copy()
df_filtered = df.copy()

search_text = (search or "").strip().lower()


# --- PRICE / MRP FILTER ---
if filter_type == "Price":
    df_filtered = df_filtered[
        (df_filtered[col_price] >= min_price) &
        (df_filtered[col_price] <= max_price)
    ]
else:
    if col_mrp:
        df_filtered = df_filtered[
            (df_filtered[col_mrp] >= min_price) &
            (df_filtered[col_mrp] <= max_price)
        ]

# --- CATEGORY FILTER (MULTI SELECT) ---
selected_categories = [
    c.lower().strip()
    for c in categories
    if st.session_state.get(f"cat_{str(c).strip().lower()}", False)
]

if selected_categories:
    df_filtered = df_filtered[
        df_filtered[col_category].isin(selected_categories)
    ]

# --- BRAND FILTER (MULTI SELECT) ---
selected_brands = [
    b.lower().strip()
    for b in brands
    if st.session_state.get(f"brand_{str(b).strip().lower()}", False)
]

if selected_brands:
    df_filtered = df_filtered[
        df_filtered[col_brand].isin(selected_brands)
    ]

# --- SEARCH FILTER ---
if search_text:

    search_col = (
        df_filtered[col_product].astype(str) + " " +
        df_filtered[col_brand].astype(str) + " " +
        df_filtered[col_category].astype(str)
    )

    df_filtered = df_filtered[
        search_col.str.contains(search_text, case=False, na=False)
    ]
selected_indexes = [
    i for i in df.index
    if st.session_state.get(f"product_{i}", False)
]

selected_rows = df.loc[selected_indexes]

remaining_rows = df_filtered.drop(selected_indexes, errors="ignore")

# Selected products sort
selected_rows = selected_rows.sort_values(
    by=[col_brand, col_price],
    ascending=[True, True]
)

# Remaining products sort
remaining_rows = remaining_rows.sort_values(
    by=[col_brand, col_price],
    ascending=[True, True]
)

# Selected first + remaining next
filtered = pd.concat([
    selected_rows,
    remaining_rows
])

filtered = filtered.sort_values(
    by=[col_brand, col_price],
    ascending=[True, True]
)

filtered = filtered.sort_values(
    by=[col_brand, col_price],
    ascending=[True, True]
)
# SALES TEAM FILTER
if order_id_from_url:

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="catalog123",
        database="catalogue_db"
    )

    selected_df = pd.read_sql(
        "SELECT product_name, delivery_time FROM selected_products WHERE order_id=%s",
        conn,
        params=[order_id_from_url]
    )

    conn.close()

    # normalize DB products
    selected_df["product_name"] = (
        selected_df["product_name"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    selected_list = selected_df["product_name"].tolist()

    # normalize excel products
    df_full[col_product] = (
        df_full[col_product]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # FINAL FILTER
    df_full[col_product] = df_full[col_product].astype(str).str.strip().str.lower()

    selected_list = selected_df["product_name"].astype(str).str.strip().str.lower().tolist()

    filtered = df_full[df_full[col_product].isin(selected_list)]

    selected_df["product_name"] = selected_df["product_name"].astype(str).str.strip().str.lower()
    selected_df["delivery_time"] = selected_df["delivery_time"].fillna("Not Provided")

    delivery_map = dict(zip(
        selected_df["product_name"],
        selected_df["delivery_time"]
    ))
    
    selected_list = selected_df["product_name"].astype(str).str.strip().str.lower()

    df_full[col_product] = df_full[col_product].astype(str).str.strip().str.lower()

    filtered = df_full[
        df_full[col_product].isin(selected_list)
    ]
# 🔥 SAVE FILTER STATE
st.session_state["filtered"] = filtered.copy()

# ---------------- LAYOUT ----------------
design_option = st.radio(
    "Choose Catalogue Design",
    ["Design 1", "Design 2", "Design 3", "Design 4"],
    horizontal=True
)

selected_design = design_option

filtered_design = design_df[
    design_df["design_name"].str.strip().str.lower()
    == selected_design.strip().lower()
]

pages = {}
for _, row in filtered_design.iterrows():
    pages[row["image_name"]] = image_to_base64(row["image_path"])


payment_option = st.radio(
    "Select Payment Terms",
    ["Advance Payment", "15 Days Credit", "30 Days Credit", "45 Days Credit"],
    horizontal=True
)

layout_option = st.radio(
    "Choose Layout",
    ["1 Image per Page", "2 Images per Page"],
    horizontal=True
)

col1, _ = st.columns([0.1, 0.9])

with col1:
    if is_sales:
        client_percent = st.number_input("Client Profit %", value=25)
    else:
        client_percent = 0


# ---------------- PDF GENERATE ----------------
# SALES TEAM ONLY
if is_sales:

  if st.button("Create Catalogue PDF", key="create_pdf_unique"):

    ud_logo = logo_to_base64("logo.png")
    client_logo = logo_to_base64(client_logo_path)

    middle_page = pages.get("middle page2", "")
    first_page = pages.get("first page1", "")

    if payment_option == "Advance Payment":
        terms_page = pages.get("terms_advance", "")
    elif payment_option == "15 Days Credit":
        terms_page = pages.get("terms_15", "")
    elif payment_option == "30 Days Credit":
        terms_page = pages.get("terms_30", "")
    elif payment_option == "45 Days Credit":
        terms_page = pages.get("terms_45", "")
    else:
        terms_page = ""

    last_page = pages.get("last page4", "")

    template_path = os.path.join(
        os.path.dirname(__file__),
        "templates",
        "single.html" if layout_option == "1 Image per Page" else "double.html"
    )

    with open(template_path, encoding="utf-8") as f:
        template = Template(f.read())

    temp = []
    selected_df = df.loc[
        list(st.session_state["selected_products"])
     ]
    for index, row in df.iterrows():

        if st.session_state.get(f"product_{index}", False):
            delivery_input = st.session_state.get(f"delivery_input_{index}", "").strip()
            
            delivery_text = get_delivery_text(delivery_input)
            
            base_price = row[col_price]

            final_price = int(base_price + (base_price * client_percent / 100) + 0.5)

            temp.append({
                "name": f"{str(row[col_brand]).title()} - {str(row[col_product]).title()}",
                "price": f"{final_price:,}",
                "mrp": f"{int(row[col_mrp]):,}" if col_mrp and pd.notna(row[col_mrp]) else "",
                "description": format_description(row[col_desc]) if col_desc else "",
                "image": image_to_base64(row[col_image]),
                "delivery": delivery_text
            })

    if len(temp) == 0:
        st.error("Please select products first!")
        st.stop()

    page_size = 1 if layout_option == "1 Image per Page" else 2

    products_pdf = []

    for i in range(0, len(temp), page_size):
        products_pdf.append(temp[i:i + page_size])

    html = template.render(
        first_page=first_page,
        middle_page=middle_page,
        terms_page=terms_page,
        last_page=last_page,
        ud_logo=ud_logo,
        client_logo=client_logo,
        products=[item for sub in products_pdf for item in sub],
        sales_name=sales_info["name"],
        sales_phone=str(sales_info["phone"]).replace("+", "").replace(" ", "").replace("-", ""),
        sales_email=str(sales_info["email"]).strip()
    )

    HTML(string=html).write_pdf("catalog.pdf")

    st.toast("✅ Catalogue Created Successfully!", icon="🎉")

    with open("catalog.pdf", "rb") as f:
        st.download_button(
            "Download Catalogue PDF",
            f,
            file_name="catalog.pdf",
            mime="application/pdf"
        )
# ---------------- PRODUCT LIST ----------------     
colA, colB = st.columns([1, 2])

with colA:
    st.markdown("## Products")   # same header style, clean

with colB:

    selected_count = sum(
        1 for i in filtered.index
        if st.session_state.get(f"product_{i}", False)
    )

    no_image_count = sum(
        1 for i, row in filtered.iterrows()
        if st.session_state.get(f"product_{i}", False)
        and not image_to_base64(row[col_image])
    )

    st.markdown(
        f"""
        <div style="display:flex; gap:25px; align-items:center; font-size:27px; font-weight:600;">
            <div>🛒 Selected: {selected_count}</div>
            <div>🖼️ No Image: {no_image_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
   
filtered_for_ui = filtered.copy()

# =================== PREVIEW ===================
if st.button("👀 Preview"):
    
    selected_indexes = sorted(
        st.session_state["selected_products"],
        key=lambda i: (
            str(df.loc[i, col_brand]).lower(),
            df.loc[i, col_price]
        )
    )

    selected_items = []
    for index in selected_indexes:
        row = df.loc[index]

        selected_items.append({
            "index": index,
            "brand": row[col_brand],
            "product": row[col_product],
            "price": row[col_price],
            "mrp": row[col_mrp] if col_mrp else "",
            "image": image_to_base64(row[col_image]),
            "delivery": st.session_state.get(f"delivery_input_{index}", "")
        })

    selected_items = [item for item in selected_items if item["image"]]

    if len(selected_items) == 0:
        st.warning("Please select products first")
        st.stop()

    html = """
<html>
<head>
<style>

html, body{
    margin:0;
    padding:0;
    width:100%;
    height:100%;
    overflow-x:hidden;
}

/* HEADER */
.header{
    background:#111827;
    color:white;
    padding:18px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}

.container{
    padding:0px;
    width:100vw;
    max-width:100vw;
}

.grid{
    display:grid;
    grid-template-columns:repeat(6, minmax(0, 1fr));
    gap:18px;
    width:100%;
    padding:10px;
    box-sizing:border-box;
}

/* CARD */
.card{
    background:white;
    border-radius:14px;
    padding:12px;
    box-shadow:0 5px 15px rgba(0,0,0,0.15);
    transition:0.3s;
}

.card:hover{
    transform:translateY(-5px);
}

/* IMAGE */
.card img{
    width:100%;
    height:170px;
    object-fit:contain;
    border-radius:10px;
}

/* TEXT */
.name{
    font-size:13px;
    font-weight:600;
    margin-top:8px;
    color:#111827;
    height:34px;
    overflow:hidden;
}

/* PRICE */
.price{
    color:#16a34a;
    font-weight:bold;
    font-size:16px;
    margin-top:5px;
}

/* MRP */
.mrp{
    color:#dc2626;
    font-size:12px;
    text-decoration:line-through;
}

/* DELIVERY */
.delivery{
    font-size:11px;
    color:#374151;
    margin-top:6px;
    font-weight:600;
}

/* RESPONSIVE */
@media(max-width:1100px){
    .grid{ grid-template-columns:repeat(3, 1fr); }
}

@media(max-width:700px){
    .grid{ grid-template-columns:repeat(2, 1fr); }
}

@media(max-width:450px){
    .grid{ grid-template-columns:repeat(1, 1fr); }
}

</style>
</head>

<body>

<div class="header">
🛍 Product Preview
</div>

<div class="container">
<div class="grid">
"""

    # ================= PRODUCT LOOP =================
    for item in selected_items:

        html += f"""
        <div class="card">

            <img src="{item['image']}">

            <div class="name">
                {item['brand']} - {item['product']}
            </div>

            <div class="price">
                Dealer price:₹ {int(item['price'])}
            </div>
        """

        # MRP
        if item["mrp"] and str(item["mrp"]) != "nan":
            html += f"""
            <div class="mrp">
                MRP:₹ {int(item['mrp'])}
            </div>
            """

        # DELIVERY
        delivery_value = str(item["delivery"]).strip()

        if delivery_value:
            if delivery_value.isdigit():
                html += f"""
                <div class="delivery">
                    🚚 Delivery Timeline *{int(delivery_value) + 2}* Working Days After Confirmation
                </div>
                """
            else:
                html += f"""
                <div class="delivery">
                    🚚 {delivery_value}
                </div>
                """

        html += """
        </div>
        """

    html += """
</div>
</div>

</body>
</html>
"""

    # ================= SAVE PREVIEW =================
    order_id = str(uuid.uuid4())

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="catalog123",
        database="catalogue_db"
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO preview_html (order_id, html_content)
        VALUES (%s, %s)
    """, (order_id, html))

    conn.commit()
    conn.close()

    APP_URL = "https://client-unbaked-violation.ngrok-free.dev"
    preview_url = f"{APP_URL}?preview_id={order_id}"

    st.markdown(
        f'<a href="{preview_url}" target="_blank">👀 Open Preview</a>',
        unsafe_allow_html=True
    )
   
# =================== SEND TO SALES TEAM ===================
if is_procurement:
    if st.button("📤 Send to Sales Team"):

        selected_categories = [c for c in categories if st.session_state.get(f"cat_{c}", False)]
        selected_brands = [b for b in brands if st.session_state.get(f"brand_{b}", False)]

        selected_indexes = st.session_state.get("selected_products", [])
        if isinstance(selected_indexes, set):
            selected_indexes = list(selected_indexes)
        selected_indexes = [
            i for i in st.session_state["selected_products"]
        ]
        selected_items = df.loc[selected_indexes]

        # Generate order_id
        order_id = str(uuid.uuid4())
        st.session_state["restore_filters"] = False

        APP_URL = "https://client-unbaked-violation.ngrok-free.dev"
        app_link = f"{APP_URL}?order_id={order_id}"

        sales_info = sales_df[sales_df["name"] == selected_sales].iloc[0]
        sales_email = sales_info["email"]

        # DB connection
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="catalog123",
            database="catalogue_db"
        )
        cursor = conn.cursor()

        # ================= INSERT FILTERS =================
        cursor.execute("""
            INSERT INTO order_filters
            (order_id, min_price, max_price, search_text, brands, categories, sales_person)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            order_id,
            min_price,
            max_price,
            search,
            ",".join(selected_brands),
            ",".join(selected_categories),
            selected_sales
        ))

        # ================= INSERT EACH PRODUCT =================
        for index in selected_indexes:

            row = df.loc[index]

            delivery_input = st.session_state.get(f"delivery_input_{index}", "").strip()

            if delivery_input == "":
                delivery_time = ""

            else:
                delivery_time = delivery_input

            cursor.execute("""
                INSERT INTO selected_products
                (order_id, product_name, price, mrp, delivery_time, user_email, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                order_id,
                str(row[col_product]).strip(),
                int(row[col_price]),
                int(row[col_mrp]) if col_mrp else 0,
                delivery_time,
                sales_email,
                "pending"
            ))

        # ================= NOTIFICATION =================
        cursor.execute("""
            INSERT INTO notifications
            (user_email, message)
            VALUES (%s, %s)
        """, (
            sales_email,
            f"New catalogue shared by {st.session_state.username}"
        ))

        conn.commit()
        conn.close()

        # ================= EMAIL =================
        subject = "New Catalogue Shared"
        body = f"""
Hello {selected_sales},

Products have been shared.

Client: {selected_client}

Open App:
{app_link}

Thanks
"""

        mailto_link = f"mailto:{sales_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

        st.markdown(f"👉 [Click here to open email app]({mailto_link})")
        st.toast(f"Mail opened for {selected_sales} 🚀", icon="🎉")
# ---------------- BRAND + PRICE ASCENDING SORT ----------------


if "select_all" not in st.session_state:
    st.session_state["select_all"] = False


def toggle_all():
    for i in filtered.index:
        st.session_state[f"product_{i}"] = st.session_state["select_all"]


st.checkbox("Select All", key="select_all", on_change=toggle_all)

cols_per_row = 6

for i in range(0, len(filtered), cols_per_row):

    row_items = filtered.iloc[i:i + cols_per_row]
    cols = st.columns(cols_per_row)

    for idx, (index, row) in enumerate(row_items.iterrows()):

     with cols[idx]:

        st.checkbox("Select", key=f"product_{index}")
        
        if st.session_state.get(f"product_{index}", False):
            st.session_state["selected_products"].add(index)
        else:
            st.session_state["selected_products"].discard(index)
        # IMAGE
        img_path = row[col_image]

        img = load_product_image(str(img_path))

        if img:
            st.image(img, width=150)

            if st.button("🔍 Fullscreen", key=f"fs_{index}"):

                @st.dialog("Image Preview")
                def show_full():
                    st.image(
                        img,
                        use_container_width=True
                )

                show_full()

        else:
            st.warning("No image")

        # TEXT
        st.write(
        f"{str(row[col_brand]).title()} - {str(row[col_product]).title()}"
        )

        if col_mrp:
            st.markdown(f"**MRP:** ₹ {int(row[col_mrp]):,}")

        st.markdown(f"**Dealer price:** ₹ {int(row[col_price]):,}")
        st.markdown(
            "<div style='margin-bottom:-10px;font-weight:600;'>🚚 Delivery Time</div>",
            unsafe_allow_html=True
            )
        product_name = str(row[col_product]).strip().lower()

        default_delivery = ""

        if order_id_from_url:
            default_delivery = delivery_map.get(product_name, "")

        if f"delivery_input_{index}" not in st.session_state:
            st.session_state[f"delivery_input_{index}"] = default_delivery

        d1, d2 = st.columns([0.45, 1])

        with d1:
            delivery_time = st.text_input(
                "",
                key=f"delivery_input_{index}"
            )

        st.session_state[f"delivery_store_{index}"] = delivery_time   # ✅ safe

        st.session_state[f"delivery_{index}"] = delivery_time
        # ================= EDIT BUTTON =================
        if is_procurement:
            if st.button("✏️ Edit", key=f"edit_{index}"):
                st.session_state[f"edit_mode_{index}"] = True

        # ================= EDIT MODE =================
        if st.session_state.get(f"edit_mode_{index}", False):

            st.markdown("### 🛠 Edit Mode")

            new_price = st.number_input(
                "Edit Dealer price",
                value=int(row[col_price]),
                key=f"price_{index}"
            )

            new_mrp = None
            if col_mrp:
                new_mrp = st.number_input(
                    "Edit MRP",
                    value=int(row[col_mrp]),
                    key=f"mrp_{index}"
                )

            if st.button("✅ Done", key=f"done_{index}"):

                df.loc[index, col_price] = new_price

                if col_mrp and new_mrp is not None:
                    df.loc[index, col_mrp] = new_mrp

                df.to_excel("products.xlsx", index=False)
                st.cache_data.clear()

                st.session_state[f"edit_mode_{index}"] = False

                st.success("Updated Successfully ✅")
                st.rerun()