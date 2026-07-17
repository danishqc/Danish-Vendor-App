import streamlit as st
import psycopg2
import os
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Danish Power Limited - Enterprise Master Portal", layout="wide")

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
        # Creating columns for 8 sections, 5 questions each
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
        c.execute("""CREATE TABLE IF NOT EXISTS plant_photos (
            id SERIAL PRIMARY KEY, supplier_email VARCHAR(255), category_desc TEXT, custom_photo_name TEXT, remarks TEXT, file_name TEXT, file_data BYTEA
        )""")
    conn.commit()

init_db()

# --- COMPLETE COMPLIANCE DATA MATRIX ---
audit_points = {
    "1. Raw Material, Planning & Traceability": {
        "1.1": "Is raw material quality ensured through testing/ verifying test reports?",
        "1.2": "Do system exists to ensure that separate raw materials batches are prevented from mix-up? Is this demarcation extended up to delivery of finished goods?",
        "1.3": "To what extent the traceability of material is ensured? Can it be maintained even after delivery of the finished goods? Are records of traceability maintained?",
        "1.4": "How our requirements are taken care of during production planning viz. for delivery schedules, quantity, quality requirements etc.?",
        "1.5": "Sample Verification: Test few products for all related parameters and state results. If required, use additional sheets."
    },
    "2. Quality System & Document Control": {
        "2.1": "Is the company certified against some quality system standard e.g., ISO 9001:2015 etc and other?",
        "2.2": "Is there a system to ensure that the drawings and instruction received from us are properly preserved?",
        "2.3": "Are such documents made available to the concerned operators / people along with the explanation of the importance of adhering to these requirements?",
        "2.4": "Is it ensured that latest documents only are used for production purposes and obsolete documents are destroyed / returned?",
        "2.5": "When multiple documents e.g. drawings / instructions are issued, is proper control exercised to ensure that different documents are suitably used for its intended purpose?"
    },
    "3. Inspection Facilities & Calibration": {
        "3.1": "Are all required inspection facilities available with supplier?",
        "3.2": "Are all instruments calibrated / verified periodically? Attach calibration status of measuring equipment.",
        "3.3": "Are people aware of methods to use the instruments?",
        "3.4": "Are quality/control plans available and are they followed?",
        "3.5": "Are records of inspection kept?"
    },
    "4. Communication, Improvement & Ethics": {
        "4.1": "Are inspection reports sent to the customer?",
        "4.2": "Do you regularly interact with us regarding your status of quality and delivery performance?",
        "4.3": "If yes, do you communicate the status within the organization and do you take suitable measures to improve the situation?",
        "4.4": "Are plans available for up-gradation of technology / working conditions / process/products etc.?",
        "4.5": "What is the mechanism for protecting client's confidential information?"
    },
    "5. Labour Compliance & Human Rights": {
        "5.1": "Does a policy on Child Labor exists?",
        "5.2": "Compliance on working hours, minimum wages, worker benefits.",
        "5.3": "Workplace free of discrimination and harassment.",
        "5.4": "Does anti-corruption policy/procedure exist?",
        "5.5": "Whether workers and supervisors aware of anti-corruption policy/procedure?"
    },
    "6. Occupational Health & Safety": {
        "6.1": "Does the Supplier have Health and Safety Policy?",
        "6.2": "Does the Supplier have Health and Safety Procedures?",
        "6.3": "Are employees aware of Health and Safety Procedures?",
        "6.4": "Are employees aware of use of proper PPES?",
        "6.5": "Availability of a system to prevent, manage, track and report occupational injury and illness?"
    },
    "7. Workplace Infrastructure & Hygiene": {
        "7.1": "Suitable Machine safeguards and preventive maintenance of machines available?",
        "7.2": "Are all work areas and common spaces kept clean and hygienic?",
        "7.3": "Is there a documented cleaning schedule?",
        "7.4": "Are proper waste disposal and recycling procedures in place and followed?",
        "7.5": "Are washrooms and changing facilities clean, well-maintained, and adequately supplied?"
    },
    "8. Environment & Social Responsibility": {
        "8.1": "Environment Protection Policy and Procedures.",
        "8.2": "Consent to operate and its validity?",
        "8.3": "Whether mechanism for identification of hazardous material, labeling, handling reuse/recycling, disposal available?",
        "8.4": "Procedure for solid waste management?",
        "8.5": "Availability for Goal for reduction of energy consumption and GHG emission, energy efficiency?"
    }
}

mandatory_docs = [
    "Company Profile  / Brochure", "ISO 9001-2015 ISO 14001:2015, ISO45001:2018 or equivalent third-party certification",
    "Organization Chart along with Manpower details", "Process Flow Chart / Diagram", "Source of Raw Material/Bought Out Item",
    "List of Machinery & inhouse/outsource testing facilities", "MQP (Quality Plan) along with Incoming, Inprocess & Final Inspection Checklist",
    "Calibration of measuring instruments and test equipment", "Approval letters of various consultants/ PSUs or major Private parties",
    "List of supply for major Private & government Sector Company", "Total area of the Factory (Covered  & Uncovered)"
]

later_docs = [
    "Product related special certification (If Applicable)", "Applicable type test reports (If Any)", "Quality Policy",
    "Factory License/ Registration certificate", "Pollution clearance certificate", "Standard operating Procedure",
    "Copies of annual Balance Sheet for the last three years", "Five major customer Un-priced purchase order",
    "Performance feedback certificate (Two customer)", "Detail of Outsourced Manufacturing activities",
    "Work Instruction for Storage, Handling etc.", "Maintenance facility & preventive maintenance",
    "Safety PPE and Firefighting guideline / Work instruction", "Internal Non – conformity of last one year",
    "Customer complaint handling records if any", "In-house training and learning development detail",
    "Jigs & fixtures Detail", "Proof of time wise delivery with quality", "Electrical Power and alternative arrangement",
    "MTC & third-party test reports available", "Packing Guideline", "Tool Manufacturing Facility"
]

plant_photos = [
    "Factory Administrative Building", "Critical Machinery for component", "Display of Critical Machinery Maintenance ",
    "Incoming Area (Store)", "In process Inspection ", "Final Inspection Area ", "5S Management ", "Testing Facility ",
    "Critical Equipment ", "Lifting & Handling Facility ", "Packing ", "Galvanizing (If Applicable)",
    "Painting Area (If Applicable)", "Special Test Equipment ", "House Keeping & PPE ", "Factory Lux (Light) Check  ",
    "DG Set (If Applicable)", "Tool Room (If Applicable)", "Route card  / Documents availability at Shop Floor",
    "ERP System (If Applicable)", "Display of Quality Policy  & Objective ", "Display of Safety Rules ",
    "Display of Work Instruction ", "Ready for Dispatch"
]

# --- BRANDED PDF REPORT GENERATOR (UPDATED FOR POSTGRES) ---
def generate_master_pdf(supplier_email):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    brand_red = colors.HexColor('#E31E24')
    brand_dark = colors.HexColor('#212121')
    
    title_s = ParagraphStyle('TStyle', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=brand_red, alignment=1)
    sub_s = ParagraphStyle('SStyle', fontName='Helvetica-Oblique', fontSize=10, leading=14, textColor=colors.gray, alignment=1)
    sec_s = ParagraphStyle('SecStyle', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=brand_red, spaceBefore=12, spaceAfter=6)
    cell_s = ParagraphStyle('Cell', fontName='Helvetica', fontSize=8, leading=11)
    cell_b = ParagraphStyle('CellB', fontName='Helvetica-Bold', fontSize=8, leading=11)
    th_s = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.white, alignment=1)

    story.append(Paragraph("DANISH POWER LIMITED", title_s))
    story.append(Paragraph("Supplier Quality Audit Report | Format: F-12", sub_s))
    story.append(Spacer(1, 15))
    
    conn = init_connection()
    with conn.cursor() as c:
        c.execute("SELECT * FROM core_assessment WHERE supplier_email=%s", (supplier_email,))
        core_data = c.fetchone()
        c.execute("SELECT description, status, remarks FROM doc_checklist WHERE supplier_email=%s", (supplier_email,))
        docs_data = c.fetchall()
        c.execute("SELECT description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks FROM machinery WHERE supplier_email=%s", (supplier_email,))
        mach_data = c.fetchall()
        c.execute("SELECT category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks FROM instruments WHERE supplier_email=%s", (supplier_email,))
        inst_data = c.fetchall()
        c.execute("SELECT category_desc, custom_photo_name, remarks FROM plant_photos WHERE supplier_email=%s", (supplier_email,))
        photo_data = c.fetchall()

    if not core_data:
        return None

    # Database indices mapping: 
    # id(0), email(1), status(2), timestamp(3), s_name(4), p_name(5), audit_date(6), q_1_1_status(7)...
    supplier_name_val = core_data[4]
    product_name_val = core_data[5]
    audit_date_val = core_data[6]

    meta_table = Table([
        [Paragraph(f"<b>Supplier Name:</b> {supplier_name_val}", cell_s), Paragraph(f"<b>Audit Date:</b> {audit_date_val}", cell_s)],
        [Paragraph(f"<b>Product Supplied:</b> {product_name_val}", cell_s), Paragraph(f"<b>Report Compiled:</b> {datetime.now().strftime('%d-%m-%Y')}", cell_s)]
    ], colWidths=[280, 280])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f5f7f8')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cfd8dc')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Core Compliance Questionnaire", sec_s))
    q_table_data = [[Paragraph("S.No", th_s), Paragraph("Checkpoints Description", th_s), Paragraph("Status", th_s), Paragraph("Auditor Remarks", th_s)]]
    
    db_idx = 7 # Starting index for Q1.1 Status in Postgres
    for sec_name, questions in audit_points.items():
        q_table_data.append([Paragraph(f"<b>{sec_name}</b>", cell_b), "", "", ""])
        for q_num, q_text in questions.items():
            status_val = core_data[db_idx] if core_data[db_idx] else "-"
            remark_val = core_data[db_idx+1] if core_data[db_idx+1] else "-"
            q_table_data.append([
                Paragraph(q_num, cell_s), Paragraph(q_text, cell_s),
                Paragraph(status_val, cell_s), Paragraph(remark_val, cell_s)
            ])
            db_idx += 2
            
    q_table = Table(q_table_data, colWidths=[35, 275, 50, 200], repeatRows=1)
    q_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), brand_red),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(q_table)
    story.append(PageBreak())
    
    # Machinery Table
    story.append(Paragraph("2. Plant Machinery Deployed", sec_s))
    mach_headers = ["Sr", "Description", "Unique ID", "Make/Model", "Capacity", "Specification", "Year", "Features", "Automation", "Remarks"]
    mach_table_data = [[Paragraph(h, th_s) for h in mach_headers]]
    for idx, m in enumerate(mach_data):
        mach_table_data.append([Paragraph(str(idx+1), cell_s)] + [Paragraph(str(val) if val else "-", cell_s) for val in m])
    mach_table = Table(mach_table_data, colWidths=[20, 80, 45, 55, 45, 55, 30, 80, 75, 75], repeatRows=1)
    mach_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_red), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('PADDING', (0,0), (-1,-1), 4)]))
    story.append(mach_table)

    # Photo Logs Table (New)
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Plant Photo Logs Submitted", sec_s))
    photo_headers = ["Category", "Photo Caption / Name", "Remarks"]
    photo_table_data = [[Paragraph(h, th_s) for h in photo_headers]]
    for row in photo_data:
        photo_table_data.append([Paragraph(row[0], cell_s), Paragraph(row[1] if row[1] else "-", cell_s), Paragraph(row[2] if row[2] else "-", cell_s)])
    photo_table = Table(photo_table_data, colWidths=[200, 180, 180], repeatRows=1)
    photo_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_dark), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(photo_table)

    doc.build(story)
    buffer.seek(0)
    return buffer, supplier_name_val

# --- NATIVE UI HEADER ---
header_col1, header_col2, header_col3 = st.columns([1.5, 3.2, 2.3])
with header_col1:
    st.image(f"data:image/png;base64,{LOGO_BASE64}", use_container_width=True)
with header_col2:
    st.markdown("<h1 style='color: #E31E24; text-align: center; margin: 0; font-size: 28px; font-weight: 800;'>DANISH POWER LIMITED</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #212121; font-weight:600; margin: 2px 0 0 0;'>Supplier Quality System Audit</p>", unsafe_allow_html=True)
with header_col3:
    st.markdown("""
    <div style='border: 2px solid #E31E24; padding: 10px; border-radius: 6px; font-size: 13px;'>
        <b>Format No.:</b> F-12<br><b>Rev. No.:</b> 03
    </div>
    """, unsafe_allow_html=True)
st.markdown("<hr style='border: 1.5px solid #E31E24; margin-top:10px; margin-bottom:25px;'>", unsafe_allow_html=True)

# --- PORTAL LOGIC ---
st.sidebar.markdown("<h3 style='color:#E31E24; font-weight:bold;'>PORTAL ACCESS</h3>", unsafe_allow_html=True)
portal_mode = st.sidebar.radio("Switch Dashboard View", ["Supplier Gateway Form", "DPL Quality Admin View"])

if portal_mode == "Supplier Gateway Form":
    st.subheader("🔐 Verification & Draft System")
    vendor_email = st.text_input("Enter your official Email ID to Start or Resume Assessment*", placeholder="supplier@company.com")
    
    if vendor_email:
        conn = init_connection()
        with conn.cursor() as c:
            c.execute("SELECT submission_status FROM core_assessment WHERE supplier_email=%s", (vendor_email,))
            record = c.fetchone()
        
        if record and record[0] == 'SUBMITTED':
            st.success("✅ Your Assessment has already been submitted. It is now locked for review.")
        else:
            if record and record[0] == 'DRAFT':
                st.info("🔄 Found a saved draft. Please continue filling.")
            else:
                st.info("🆕 Starting a new assessment. You can save your progress anytime.")
                
            st.subheader("🏢 Part A: Corporate Registration Identity")
            gcol1, gcol2 = st.columns(2)
            with gcol1:
                s_name_input = st.text_input("Supplier Corporate Name*")
                p_name_input = st.text_input("Product Component Description*")
            with gcol2:
                a_date_input = st.date_input("Audit Compilation Date", datetime.now())
                
            t1, t2, t3, t4, t5 = st.tabs([
                "📊 1. Core Evaluation", "📎 2. Documents Vault", 
                "⚙️ 3. Machine Asset", "🔬 4. Lab Records", "📸 5. Plant Image Records"
            ])
            
            with t1:
                core_inputs = {}
                for sec_title, questions in audit_points.items():
                    st.markdown(f"<div style='background-color:#FFEBEE; padding:8px; border-left: 4px solid #E31E24; font-weight:bold;'>{sec_title}</div>", unsafe_allow_html=True)
                    for q_num, q_text in questions.items():
                        st.markdown(f"**{q_num}** {q_text}")
                        k_code = q_num.replace('.', '_')
                        ch_col1, ch_col2 = st.columns([1, 4])
                        with ch_col1: status_select = st.selectbox("Status", ["Yes", "No", "N/A"], key=f"s_{k_code}")
                        with ch_col2: comment_input = st.text_input("Remarks", key=f"c_{k_code}")
                        core_inputs[f"q_{k_code}_status"] = status_select
                        core_inputs[f"q_{k_code}_comment"] = comment_input
                    st.markdown("---")

            with t2:
                st.markdown("#### Document Vault (PDF/JPG/PNG only)")
                # (You can implement the file upload logic here similarly using BYTEA format like we do for photos below)
                st.info("Document upload section reserved for implementation. Proceed to Tab 5 for Photo Uploads demo.")

            with t3:
                st.markdown("#### Production Machinery Log")
                if 'mach_rows' not in st.session_state: st.session_state.mach_rows = 1
                if st.button("➕ Add Plant Machinery Row"): st.session_state.mach_rows += 1
                machinery_rows = []
                for m in range(st.session_state.mach_rows):
                    r1, r2, r3, r4 = st.columns(4)
                    with r1: m_desc = st.text_input("Machine Description", key=f"md_ds_{m}"); m_uid = st.text_input("Unique ID", key=f"md_ui_{m}")
                    with r2: m_make = st.text_input("Make/Model", key=f"md_mk_{m}"); m_cap = st.text_input("Capacity", key=f"md_cp_{m}")
                    with r3: m_spec = st.text_input("Specification", key=f"md_sp_{m}"); m_year = st.text_input("Year", key=f"md_yr_{m}")
                    with r4: m_feat = st.text_input("Features", key=f"md_ft_{m}"); m_auto = st.selectbox("Automation", ["Manual", "Semi", "Full"], key=f"md_au_{m}")
                    m_rem = st.text_input("Remarks", key=f"md_rm_{m}")
                    machinery_rows.append([m_desc, m_uid, m_make, m_cap, m_spec, m_year, m_feat, m_auto, m_rem])
                    st.markdown("---")

            with t4:
                st.markdown("#### Metrological & Lab Testing Records")
                st.info("Lab equipment records section reserved for implementation.")

            with t5:
                st.markdown("#### Factory Plant Image Evidences")
                plant_photos_entries = []
                for idx, p_desc in enumerate(plant_photos):
                    st.markdown(f"**📸 {idx+1}. {p_desc}**")
                    pc1, pc2 = st.columns([1, 1])
                    with pc1: img_file = st.file_uploader(f"Upload Image", type=["jpg","png"], key=f"ph_f_{idx}")
                    with pc2: 
                        ph_name = st.text_input("Photo Caption / Exact Name", placeholder="e.g. Unit 1 CNC", key=f"ph_n_{idx}")
                        ph_rem = st.text_input("Additional Remarks", key=f"ph_r_{idx}")
                    plant_photos_entries.append({"category": p_desc, "file": img_file, "name": ph_name, "rem": ph_rem})
                    st.markdown("---")

            # --- SUBMISSION LOGIC ---
            st.markdown("<br>", unsafe_allow_html=True)
            scol1, scol2 = st.columns(2)
            
            def save_data(status_flag):
                with conn.cursor() as c:
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
                    
                    # Store Machines
                    c.execute("DELETE FROM machinery WHERE supplier_email=%s", (vendor_email,))
                    for mach in machinery_rows:
                        if mach[0]: 
                            c.execute("""INSERT INTO machinery (supplier_email, description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks) 
                                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (vendor_email, *mach))
                    
                    # Store Photos (BYTEA format)
                    c.execute("DELETE FROM plant_photos WHERE supplier_email=%s", (vendor_email,))
                    for photo in plant_photos_entries:
                        if photo["file"]:
                            file_bytes = psycopg2.Binary(photo["file"].read())
                            c.execute("INSERT INTO plant_photos (supplier_email, category_desc, custom_photo_name, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, %s)",
                                      (vendor_email, photo["category"], photo["name"], photo["rem"], photo["file"].name, file_bytes))
                conn.commit()

            with scol1:
                if st.button("💾 SAVE AS DRAFT", use_container_width=True):
                    if not s_name_input:
                        st.warning("Please enter Supplier Name before saving.")
                    else:
                        save_data('DRAFT')
                        st.success("Draft saved! Return later using your email ID.")
            with scol2:
                if st.button("🚀 FINAL SUBMIT", use_container_width=True):
                    if not s_name_input or not p_name_input:
                        st.error("Supplier Name & Product Description are mandatory!")
                    else:
                        save_data('SUBMITTED')
                        st.success("Successfully submitted to Danish Power Limited!")
                        st.balloons()

elif portal_mode == "DPL Quality Admin View":
    st.markdown("## 🛡️ Quality Assurance Verification Vault")
    passkey = st.text_input("Enter Enterprise Access Token", type="password")
    
    # Read admin password from secrets
    if passkey == st.secrets["admin"]["password"]:
        st.success("Authorization Confirmed.")
        
        conn = init_connection()
        with conn.cursor() as c:
            c.execute("SELECT id, supplier_email, supplier_name, product_name, submission_status FROM core_assessment ORDER BY id DESC")
            entries = c.fetchall()
            
        if not entries:
            st.warning("No evaluations submitted yet.")
        else:
            st.markdown("### 📑 Submitted Supplier Evaluations")
            lookup_map = [f"ID: {r[0]} | {r[2]} ({r[1]}) - Status: {r[4]}" for r in entries]
            selection = st.selectbox("Choose a Record to Generate PDF", lookup_map)
            
            selected_email = [row[1] for row in entries if f"ID: {row[0]}" in selection][0]
            
            if st.button("📄 Generate Final PDF Report"):
                pdf_data, s_name = generate_master_pdf(selected_email)
                if pdf_data:
                    st.download_button(
                        label=f"📥 DOWNLOAD AUDIT REPORT FOR {s_name.upper()}",
                        data=pdf_data,
                        file_name=f"DPL_Audit_{s_name.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    elif passkey != "":
        st.error("Invalid access token.")
