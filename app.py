import streamlit as st
import psycopg2
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Danish Power - Enterprise Portal", layout="wide")

# --- EMBEDDED LOGO ---
LOGO_BASE64 = "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"

# --- POSTGRESQL DB CONNECTION & INIT ---
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        dbname=st.secrets["database"]["dbname"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"]
    )

def init_db():
    conn = init_connection()
    with conn.cursor() as c:
        # Core form (Unique Email for Drafts)
        cols = ["id SERIAL PRIMARY KEY", "supplier_email VARCHAR(255) UNIQUE", "submission_status VARCHAR(50)", 
                "timestamp TEXT", "supplier_name TEXT", "product_name TEXT", "audit_date TEXT"]
        for i in range(1, 9):
            for j in range(1, 6):
                cols.append(f"q_{i}_{j}_status TEXT")
                cols.append(f"q_{i}_{j}_comment TEXT")
        c.execute(f"CREATE TABLE IF NOT EXISTS core_assessment ({', '.join(cols)})")
        
        # Supporting tables with BYTEA for file storage
        c.execute("""CREATE TABLE IF NOT EXISTS doc_checklist (
            id SERIAL PRIMARY KEY, supplier_email VARCHAR(255), category TEXT, description TEXT, status TEXT, remarks TEXT, file_name TEXT, file_data BYTEA
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS machinery (
            id SERIAL PRIMARY KEY, supplier_email VARCHAR(255), description TEXT, unique_id TEXT, make_model TEXT, capacity TEXT, specification TEXT, installation_year TEXT, features TEXT, automation TEXT, remarks TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS instruments (
            id SERIAL PRIMARY KEY, supplier_email VARCHAR(255), category TEXT, name TEXT, make_model TEXT, test_name TEXT, range TEXT, accuracy TEXT, cal_date TEXT, nabl_detail TEXT, master_equip TEXT, certificate_no TEXT, remarks TEXT
        )""")
        
        # Plant photos now with custom_photo_name
        c.execute("""CREATE TABLE IF NOT EXISTS plant_photos (
            id SERIAL PRIMARY KEY, supplier_email VARCHAR(255), category_desc TEXT, custom_photo_name TEXT, remarks TEXT, file_name TEXT, file_data BYTEA
        )""")
    conn.commit()

init_db()

# --- DATA DICTIONARIES (Truncated for brevity, use your full lists here) ---
audit_points = {
    "1. Raw Material, Planning & Traceability": {
        "1.1": "Is raw material quality ensured through testing/ verifying test reports?",
        "1.2": "Do system exists to ensure that separate raw materials batches are prevented from mix-up?"
    } # Note: Add all your original 8.5 questions here
}

mandatory_docs = ["Company Profile / Brochure", "ISO 9001-2015 Certification"] # Add all here
later_docs = ["Quality Policy", "Factory License"] # Add all here
plant_photos_list = ["Factory Administrative Building", "Critical Machinery for component"] # Add all here

# --- HEADER ALIGNMENT ---
header_col1, header_col2, header_col3 = st.columns([1.5, 3.2, 2.3])
with header_col1:
    st.image(f"data:image/png;base64,{LOGO_BASE64}", use_container_width=True)
with header_col2:
    st.markdown("<h1 style='color: #E31E24; text-align: center; margin: 0;'>DANISH POWER LIMITED</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic;'>Supplier Quality System Audit</p>", unsafe_allow_html=True)
with header_col3:
    st.markdown("<div style='border: 2px solid #E31E24; padding: 10px; font-size: 13px;'><b>Format No.:</b> F-12<br><b>Rev. No.:</b> 03</div>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1.5px solid #E31E24; margin-bottom:25px;'>", unsafe_allow_html=True)


# --- DASHBOARD LOGIC ---
st.sidebar.markdown("<h3 style='color:#E31E24; font-weight:bold;'>PORTAL ACCESS</h3>", unsafe_allow_html=True)
portal_mode = st.sidebar.radio("Switch View", ["Supplier Gateway Form", "DPL Quality Admin View"])

if portal_mode == "Supplier Gateway Form":
    st.subheader("🔐 Verification & Draft System")
    vendor_email = st.text_input("Enter your official Email ID to Start or Resume Assessment*", placeholder="supplier@company.com")
    
    if vendor_email:
        conn = init_connection()
        with conn.cursor() as c:
            c.execute("SELECT submission_status FROM core_assessment WHERE supplier_email=%s", (vendor_email,))
            record = c.fetchone()
        
        if record and record[0] == 'SUBMITTED':
            st.success("✅ Your Assessment has already been submitted to Danish Power Limited. You cannot edit it anymore.")
        else:
            if record and record[0] == 'DRAFT':
                st.info("🔄 We found a saved draft for this email. You can continue filling.")
            else:
                st.info("🆕 Starting a new assessment. You can save your progress anytime.")
                
            # Form UI Start
            st.subheader("🏢 Part A: Corporate Registration Identity")
            gcol1, gcol2 = st.columns(2)
            with gcol1:
                s_name_input = st.text_input("Supplier Corporate Name*")
                p_name_input = st.text_input("Product Component Description*")
            with gcol2:
                a_date_input = st.date_input("Audit Compilation Date", datetime.now())
                
            t1, t2, t3, t4, t5 = st.tabs(["📊 Core Evaluation", "📎 Documents", "⚙️ Machinery", "🔬 Lab", "📸 Plant Photos"])
            
            with t1:
                core_inputs = {}
                for sec_title, questions in audit_points.items():
                    st.markdown(f"**{sec_title}**")
                    for q_num, q_text in questions.items():
                        k_code = q_num.replace('.', '_')
                        colA, colB = st.columns([1, 4])
                        with colA: status_select = st.selectbox(q_text, ["Yes", "No", "N/A"], key=f"s_{k_code}")
                        with colB: comment_input = st.text_input("Remarks", key=f"c_{k_code}")
                        core_inputs[f"q_{k_code}_status"] = status_select
                        core_inputs[f"q_{k_code}_comment"] = comment_input

            with t5:
                st.markdown("#### Factory Plant Image Evidences")
                plant_photos_entries = []
                for idx, p_desc in enumerate(plant_photos_list):
                    st.markdown(f"**📸 {idx+1}. {p_desc}**")
                    pc1, pc2 = st.columns([1, 1])
                    with pc1: img_file = st.file_uploader("Upload Image", type=["jpg","png"], key=f"ph_f_{idx}")
                    with pc2: 
                        ph_name = st.text_input("Photo Caption/Name", placeholder="e.g. Unit 1 CNC", key=f"ph_n_{idx}")
                        ph_rem = st.text_input("Remarks", key=f"ph_r_{idx}")
                    plant_photos_entries.append({"category": p_desc, "file": img_file, "name": ph_name, "rem": ph_rem})
                    st.markdown("---")

            # SAVE OR SUBMIT BUTTONS
            st.markdown("<br>", unsafe_allow_html=True)
            scol1, scol2 = st.columns(2)
            
            def save_data_to_db(status_flag):
                with conn.cursor() as c:
                    # Upsert Core Data
                    db_cols = "supplier_email, submission_status, timestamp, supplier_name, product_name, audit_date"
                    db_vals = [vendor_email, status_flag, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s_name_input, p_name_input, str(a_date_input)]
                    
                    update_set = "submission_status=EXCLUDED.submission_status, timestamp=EXCLUDED.timestamp, supplier_name=EXCLUDED.supplier_name, product_name=EXCLUDED.product_name, audit_date=EXCLUDED.audit_date"
                    
                    for key, val in core_inputs.items():
                        db_cols += f", {key}"
                        db_vals.append(val)
                        update_set += f", {key}=EXCLUDED.{key}"
                    
                    placeholders = ", ".join(["%s"] * len(db_vals))
                    query = f"INSERT INTO core_assessment ({db_cols}) VALUES ({placeholders}) ON CONFLICT (supplier_email) DO UPDATE SET {update_set}"
                    c.execute(query, db_vals)
                    
                    # Delete old photos for this email to prevent duplicates on re-save
                    c.execute("DELETE FROM plant_photos WHERE supplier_email=%s", (vendor_email,))
                    for photo in plant_photos_entries:
                        if photo["file"]:
                            file_bytes = psycopg2.Binary(photo["file"].read())
                            c.execute("INSERT INTO plant_photos (supplier_email, category_desc, custom_photo_name, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, %s)",
                                      (vendor_email, photo["category"], photo["name"], photo["rem"], photo["file"].name, file_bytes))
                conn.commit()

            with scol1:
                if st.button("💾 Save as Draft (Complete Later)", use_container_width=True):
                    save_data_to_db('DRAFT')
                    st.success("Draft saved! You can close this tab and return later using your email.")
            with scol2:
                if st.button("🚀 FINAL SUBMIT (Cannot be undone)", use_container_width=True):
                    if not s_name_input:
                        st.error("Supplier Name is mandatory for Final Submission!")
                    else:
                        save_data_to_db('SUBMITTED')
                        st.success("Successfully submitted to Danish Power Limited!")
                        st.balloons()


elif portal_mode == "DPL Quality Admin View":
    st.markdown("## 🛡️ Quality Assurance Verification Vault")
    passkey = st.text_input("Enter Admin Password", type="password")
    
    if passkey == st.secrets["admin"]["password"]:
        st.success("Access Granted.")
        
        conn = init_connection()
        with conn.cursor() as c:
            c.execute("SELECT id, supplier_name, product_name, submission_status FROM core_assessment ORDER BY id DESC")
            entries = c.fetchall()
            
        if entries:
            st.markdown("### Submitted Evaluations")
            df_entries = [f"ID: {r[0]} | {r[1]} | Status: {r[3]}" for r in entries]
            selection = st.selectbox("Select a Supplier to Generate PDF", df_entries)
            
            # NOTE: Include your reportlab logic here as before. 
            # To show images in PDF, you can fetch BYTEA from `plant_photos` table, 
            # save temporarily using io.BytesIO(), and pass to reportlab Image class.
            
    elif passkey != "":
        st.error("Invalid Password")
