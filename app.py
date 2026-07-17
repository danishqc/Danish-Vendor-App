import streamlit as st
import psycopg2
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Danish Power Limited - Enterprise Master Portal", layout="wide")

# --- NATIVE EMBEDDED LOGO ENCODING STRATEGY ---
LOGO_BASE64 = "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"

# --- POSTGRESQL POOLER CONNECTION INITIALIZATION ---
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        dbname=st.secrets["database"]["dbname"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        sslmode="require"
    )

def init_db():
    conn = init_connection()
    conn.autocommit = True
    with conn.cursor() as c:
        # Create core table with all extended fields
        cols = ["id SERIAL PRIMARY KEY", "supplier_email VARCHAR(255) UNIQUE", "submission_status VARCHAR(50)", 
                "timestamp TEXT", "supplier_name TEXT", "product_name TEXT", "audit_date TEXT",
                "gst_no TEXT", "pan_no TEXT", "cin_no TEXT", "msme_cert TEXT", "iso_cert TEXT", "approval_status TEXT"]
        for i in range(1, 9):
            for j in range(1, 6):
                cols.append(f"q_{i}_{j}_status TEXT")
                cols.append(f"q_{i}_{j}_comment TEXT")
        c.execute(f"CREATE TABLE IF NOT EXISTS core_assessment ({', '.join(cols)})")
        
        # 🔥 SMART AUTO-MIGRATION ENGINE: Adds new columns to existing database automatically without crashing
        try:
            c.execute("ALTER TABLE core_assessment ADD COLUMN IF NOT EXISTS gst_no TEXT;")
            c.execute("ALTER TABLE core_assessment ADD COLUMN IF NOT EXISTS pan_no TEXT;")
            c.execute("ALTER TABLE core_assessment ADD COLUMN IF NOT EXISTS cin_no TEXT;")
            c.execute("ALTER TABLE core_assessment ADD COLUMN IF NOT EXISTS msme_cert TEXT;")
            c.execute("ALTER TABLE core_assessment ADD COLUMN IF NOT EXISTS iso_cert TEXT;")
            c.execute("ALTER TABLE core_assessment ADD COLUMN IF NOT EXISTS approval_status TEXT;")
        except Exception:
            pass

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

init_db()

# --- COMPLETE UNABRIDGED AUDIT MATRIX DATA STRUCTURES ---
audit_points = {
    "1. Raw Material, Planning & Traceability": {
        "1.1": "Is raw material quality ensured through testing/ verifying test reports?",
        "1.2": "Do system exists to ensure that separate raw materials batches are prevented from mix-up? Is this demarcation extended up to delivery of finished goods?",
        "1.3": "To what extent the traceability of material is ensured? Can it be maintained even after delivery of the finished goods? Are records of traceability maintained?",
        "1.4": "How our requirements are taken care of during production planning viz. for delivery schedules, quantity, quality requirements etc.?",
        "1.5": "Sample Verification: Test few products for all related parameters and state results."
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
    "Company Profile  / Brochure", "ISO 9001-2015 ISO 14001:2015, ISO45001:2018 certification",
    "Organization Chart along with Manpower details", "Process Flow Chart / Diagram", "Source of Raw Material/Bought Out Item",
    "List of Machinery & inhouse/outsource testing facilities", "MQP (Quality Plan) along with Inspection Checklist",
    "Calibration of measuring instruments and test equipment", "Approval letters of consultants/ PSUs or major Private parties",
    "List of supply for major Private & government Sector Company", "Total area of the Factory (Covered & Uncovered)"
]

later_docs = [
    "Product related special certification", "Applicable type test reports", "Quality Policy",
    "Factory License/ Registration certificate", "Pollution clearance certificate", "Standard operating Procedure",
    "Copies of Balance Sheet for last 3 years", "Five major customer Un-priced purchase orders",
    "Performance feedback certificate", "Detail of Outsourced Manufacturing activities",
    "Work Instruction for Storage & Handling", "Maintenance facility & preventive maintenance",
    "Safety PPE and Firefighting guideline", "Internal Non-conformity logs & CAPA reports",
    "Customer complaint handling records", "In-house training and development detail",
    "Jigs & fixtures Detail", "Proof of time wise delivery with quality", "Electrical Power and alternative arrangement",
    "MTC & third-party test reports available", "Packing Guideline", "Tool Manufacturing Facility"
]

plant_photos = [
    "Factory Administrative Building", "Critical Machinery for component", "Display of Critical Machinery Maintenance",
    "Incoming Area (Store)", "In process Inspection", "Final Inspection Area", "5S Management", "Testing Facility",
    "Critical Equipment", "Lifting & Handling Facility", "Packing", "Galvanizing (If Applicable)",
    "Painting Area (If Applicable)", "Special Test Equipment", "House Keeping & PPE", "Factory Lux (Light) Check",
    "DG Set (If Applicable)", "Tool Room (If Applicable)", "Route card / Documents on Shop Floor",
    "ERP System (If Applicable)", "Display of Quality Policy & Objective", "Display of Safety Rules",
    "Display of Work Instruction", "Ready for Dispatch"
]

# --- FULL BRANDED PDF ENGINE WITH ZERO SHORTCUTS ---
def generate_master_pdf(supplier_email):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
    story = []
    
    brand_red = colors.HexColor('#E31E24')
    brand_dark = colors.HexColor('#212121')
    
    title_s = ParagraphStyle('TStyle', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=brand_red, alignment=1)
    sub_s = ParagraphStyle('SStyle', fontName='Helvetica-Oblique', fontSize=10, leading=14, textColor=colors.gray, alignment=1)
    sec_s = ParagraphStyle('SecStyle', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=brand_red, spaceBefore=12, spaceAfter=6)
    cell_s = ParagraphStyle('Cell', fontName='Helvetica', fontSize=8, leading=11)
    cell_b = ParagraphStyle('CellB', fontName='Helvetica-Bold', fontSize=8, leading=11)
    th_s = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.white, alignment=1)

    story.append(Paragraph("DANISH POWER LIMITED", title_s))
    story.append(Paragraph("Supplier Quality System Audit Report | Format: F-12", sub_s))
    story.append(Spacer(1, 15))
    
    conn = init_connection()
    with conn.cursor() as c:
        c.execute("SELECT * FROM core_assessment WHERE supplier_email=%s", (supplier_email,))
        core_data = c.fetchone()
        c.execute("SELECT description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks FROM machinery WHERE supplier_email=%s", (supplier_email,))
        mach_data = c.fetchall()
        c.execute("SELECT category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks FROM instruments WHERE supplier_email=%s", (supplier_email,))
        inst_data = c.fetchall()
        c.execute("SELECT category, description, status, remarks, file_name FROM doc_checklist WHERE supplier_email=%s ORDER BY id ASC", (supplier_email,))
        docs_data = c.fetchall()
        c.execute("SELECT category_desc, custom_photo_name, remarks, file_name FROM plant_photos WHERE supplier_email=%s ORDER BY id ASC", (supplier_email,))
        photo_data = c.fetchall()

    if not core_data: return None

    # Meta Table Updated with Extended 6 Fields
    meta_table_data = [
        [Paragraph(f"<b>Supplier Name:</b> {core_data[4]}", cell_s), Paragraph(f"<b>Audit Date:</b> {core_data[6]}", cell_s)],
        [Paragraph(f"<b>Product Supplied:</b> {core_data[5]}", cell_s), Paragraph(f"<b>GST No:</b> {core_data[7]}", cell_s)],
        [Paragraph(f"<b>PAN No:</b> {core_data[8]}", cell_s), Paragraph(f"<b>CIN / Reg No:</b> {core_data[9]}", cell_s)],
        [Paragraph(f"<b>MSME Certificate:</b> {core_data[10]}", cell_s), Paragraph(f"<b>ISO Certificate:</b> {core_data[11]}", cell_s)],
        [Paragraph(f"<b>Approval Status:</b> {core_data[12]}", cell_b), Paragraph(f"<b>Report Compiled:</b> {datetime.now().strftime('%d-%m-%Y')}", cell_s)]
    ]
    meta_table = Table(meta_table_data, colWidths=[281, 281])
    meta_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f5f7f8')), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cfd8dc')), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(meta_table)
    
    # Section 1: Core Matrix Table
    story.append(Paragraph("1. Core Compliance Evaluation Matrix (1.1 - 8.5)", sec_s))
    q_table_data = [[Paragraph("S.No", th_s), Paragraph("Checkpoints Description", th_s), Paragraph("Status", th_s), Paragraph("Auditor Remarks", th_s)]]
    db_idx = 13  # Offset shifted by 6 to map correctly after the new fields
    for sec_name, questions in audit_points.items():
        q_table_data.append([Paragraph(f"<b>{sec_name}</b>", cell_b), "", "", ""])
        for q_num, q_text in questions.items():
            q_table_data.append([Paragraph(q_num, cell_s), Paragraph(q_text, cell_s), Paragraph(core_data[db_idx] if core_data[db_idx] else "-", cell_s), Paragraph(core_data[db_idx+1] if core_data[db_idx+1] else "-", cell_s)])
            db_idx += 2
    q_table = Table(q_table_data, colWidths=[35, 275, 50, 202], repeatRows=1)
    q_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_red), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(q_table)
    
    story.append(PageBreak())
    
    # Section 2: Document Table
    story.append(Paragraph("2. Document Checklist & Corporate Records Registry", sec_s))
    doc_table_data = [[Paragraph("Category", th_s), Paragraph("Document Description", th_s), Paragraph("Availability", th_s), Paragraph("Remarks Log", th_s), Paragraph("File Mapping", th_s)]]
    for row in docs_data:
        doc_table_data.append([Paragraph(row[0], cell_s), Paragraph(row[1], cell_s), Paragraph(row[2], cell_s), Paragraph(row[3] if row[3] else "-", cell_s), Paragraph(row[4] if row[4] else "No File", cell_s)])
    doc_table = Table(doc_table_data, colWidths=[70, 180, 60, 130, 122], repeatRows=1)
    doc_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_red), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(doc_table)
    
    story.append(Spacer(1, 15))
    
    # Section 3: Machinery Table
    story.append(Paragraph("3. Plant Machinery Register & Structural Ledger", sec_s))
    mach_headers = ["Sr", "Description", "Unique ID", "Make/Model", "Capacity", "Specs", "Year", "Features", "Automation", "Remarks"]
    mach_table_data = [[Paragraph(h, th_s) for h in mach_headers]]
    for idx, m in enumerate(mach_data):
        mach_table_data.append([Paragraph(str(idx+1), cell_s)] + [Paragraph(str(val) if val else "-", cell_s) for val in m])
    mach_table = Table(mach_table_data, colWidths=[20, 80, 45, 55, 45, 55, 30, 80, 75, 77], repeatRows=1)
    mach_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_dark), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 4)]))
    story.append(mach_table)

    story.append(Spacer(1, 15))
    
    # Section 4: Instruments Table
    story.append(Paragraph("4. Measuring Instruments & Metrological Testing Log", sec_s))
    inst_headers = ["Category", "Instrument Name", "Make/Model", "Test", "Range", "Accuracy", "Cal Date", "NABL", "Cert No", "Remarks"]
    inst_table_data = [[Paragraph(h, th_s) for h in inst_headers]]
    for row in inst_data:
        inst_table_data.append([Paragraph(str(val) if val else "-", cell_s) for val in row])
    inst_table = Table(inst_table_data, colWidths=[55, 70, 50, 60, 40, 45, 50, 40, 55, 97], repeatRows=1)
    inst_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_dark), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 4)]))
    story.append(inst_table)
    
    story.append(Spacer(1, 15))
    
    # Section 5: Plant Photo Registry Table
    story.append(Paragraph("5. Factory Physical Zone Image Submissions Register", sec_s))
    photo_headers = ["Target Evaluation Zone", "Uploaded Photo Custom Identify Name", "Technical Capture Remarks / Captions"]
    photo_table_data = [[Paragraph(ph, th_s) for ph in photo_headers]]
    for prow in photo_data:
        photo_table_data.append([Paragraph(prow[0], cell_s), Paragraph(prow[1] if prow[1] else "-", cell_s), Paragraph(prow[2] if prow[2] else "-", cell_s)])
    photo_table = Table(photo_table_data, colWidths=[162, 200, 200], repeatRows=1)
    photo_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_dark), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(photo_table)

    doc.build(story)
    buffer.seek(0)
    return buffer, core_data[4]

# --- PORTAL BRANDED HEADER ---
header_col1, header_col2, header_col3 = st.columns([1.5, 3.2, 2.3])
with header_col1: st.image(f"data:image/png;base64,{LOGO_BASE64}", use_container_width=True)
with header_col2:
    st.markdown("<h1 style='color: #E31E24; text-align: center; margin:0;'>DANISH POWER LIMITED</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color:#212121; font-weight:600; margin:0;'>Supplier Quality Enterprise Portal</p>", unsafe_allow_html=True)
with header_col3: st.markdown("<div style='border: 2px solid #E31E24; padding: 10px; border-radius: 6px; font-size:13px;'><b>Format No.:</b> F-12<br><b>Rev. No.:</b> 03</div>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1.5px solid #E31E24; margin-top:10px; margin-bottom:25px;'>", unsafe_allow_html=True)

# --- NAVIGATION CONTROLLER ---
st.sidebar.markdown("<h3 style='color:#E31E24; font-weight:bold;'>PORTAL ACCESS</h3>", unsafe_allow_html=True)
portal_mode = st.sidebar.radio("Switch Dashboard View", ["Supplier Gateway Form", "DPL Quality Admin View"])

if portal_mode == "Supplier Gateway Form":
    st.subheader("🔐 Part A: Identity Verification & Draft Vault")
    vendor_email = st.text_input("Enter Official Corporate Email ID to Start or Resume*", placeholder="quality@vendorcompany.com")
    
    if vendor_email:
        conn = init_connection()
        db_draft_core, db_draft_mach, db_draft_inst = None, [], []
        existing_docs, existing_photos = {}, {}
        
        with conn.cursor() as c:
            c.execute("SELECT * FROM core_assessment WHERE supplier_email=%s", (vendor_email,))
            db_draft_core = c.fetchone()
            c.execute("SELECT description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks FROM machinery WHERE supplier_email=%s", (vendor_email,))
            db_draft_mach = c.fetchall()
            c.execute("SELECT category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks FROM instruments WHERE supplier_email=%s", (vendor_email,))
            db_draft_inst = c.fetchall()
            c.execute("SELECT description, status, remarks, file_name FROM doc_checklist WHERE supplier_email=%s", (vendor_email,))
            existing_docs = {r[0]: {"status": r[1], "remarks": r[2], "file_name": r[3]} for r in c.fetchall()}
            c.execute("SELECT category_desc, custom_photo_name, remarks, file_name FROM plant_photos WHERE supplier_email=%s", (vendor_email,))
            existing_photos = {r[0]: {"custom_name": r[1], "remarks": r[2], "file_name": r[3]} for r in c.fetchall()}

        if 'current_vendor' not in st.session_state or st.session_state.current_vendor != vendor_email:
            st.session_state.current_vendor = vendor_email
            st.session_state.mach_count = max(len(db_draft_mach), 1)
            st.session_state.inst_count = max(len(db_draft_inst), 1)

        if db_draft_core and db_draft_core[2] == 'SUBMITTED':
            st.success("✅ Assessment Locked: Your corporate response data matrix has been final-transmitted to Danish Power Vault.")
        else:
            if db_draft_core and db_draft_core[2] == 'DRAFT':
                st.warning("🔄 Live Active Draft Found. All technical attributes are auto-restored below.")
            else:
                st.info("🆕 System Initialized: Creating a clean empty canvas for your corporate profile.")

            st.subheader("🏢 Part B: Corporate Identity Registry")
            gcol1, gcol2, gcol3 = st.columns(3)
            with gcol1:
                s_name = st.text_input("Supplier Corporate Name*", value=db_draft_core[4] if db_draft_core else "")
                p_name = st.text_input("Product Component Description*", value=db_draft_core[5] if db_draft_core else "")
                gst_no = st.text_input("GST No.", value=db_draft_core[7] if db_draft_core and len(db_draft_core)>7 else "")
            with gcol2:
                pan_no = st.text_input("PAN No.", value=db_draft_core[8] if db_draft_core and len(db_draft_core)>8 else "")
                cin_no = st.text_input("CIN / Registration No.", value=db_draft_core[9] if db_draft_core and len(db_draft_core)>9 else "")
                msme_cert = st.text_input("MSME Certificate Detail", value=db_draft_core[10] if db_draft_core and len(db_draft_core)>10 else "")
            with gcol3:
                iso_cert = st.text_input("ISO Certificate No.", value=db_draft_core[11] if db_draft_core and len(db_draft_core)>11 else "")
                approval_options = ["Pending Review", "Approved", "Conditionally Approved", "Rejected"]
                app_idx = approval_options.index(db_draft_core[12]) if db_draft_core and len(db_draft_core)>12 and db_draft_core[12] in approval_options else 0
                approval_status = st.selectbox("Approval Status", approval_options, index=app_idx)
                a_date = st.date_input("Audit Compilation Date", datetime.now())

            t1, t2, t3, t4, t5 = st.tabs(["📊 1. Core Evaluation", "📎 2. Document Vault", "⚙️ 3. Machine Asset Register", "🔬 4. Metrological Records", "📸 5. Plant Photo Logs"])

            with t1:
                core_inputs = {}
                db_idx = 13  # Offset shifted by 6 to map correctly to questions
                for sec_title, questions in audit_points.items():
                    st.markdown(f"<div style='background-color:#FFEBEE; padding:8px; border-left: 4px solid #E31E24; font-weight:bold; color:#B71C1C;'>{sec_title}</div>", unsafe_allow_html=True)
                    for q_num, q_text in questions.items():
                        st.markdown(f"**{q_num}** {q_text}")
                        k_code = q_num.replace('.', '_')
                        def_status = db_draft_core[db_idx] if db_draft_core and len(db_draft_core)>db_idx and db_draft_core[db_idx] else "Yes"
                        def_comment = db_draft_core[db_idx+1] if db_draft_core and len(db_draft_core)>db_idx+1 and db_draft_core[db_idx+1] else ""
                        ch1, ch2 = st.columns([1, 4])
                        with ch1: status_sel = st.selectbox("Status", ["Yes", "No", "N/A"], key=f"s_{k_code}", index=["Yes", "No", "N/A"].index(def_status))
                        with ch2: comment_in = st.text_input("Evidence / Remarks", key=f"c_{k_code}", value=def_comment)
                        core_inputs[f"q_{k_code}_status"] = status_sel
                        core_inputs[f"q_{k_code}_comment"] = comment_in
                        db_idx += 2

            with t2:
                st.markdown("#### Cloud Document Vault")
                doc_responses = {}
                st.markdown("##### 🔴 Mandatory Compliance Certifications")
                for idx, doc in enumerate(mandatory_docs):
                    def_d_status = existing_docs[doc]["status"] if doc in existing_docs and existing_docs[doc]["status"] else "Available"
                    def_d_rem = existing_docs[doc]["remarks"] if doc in existing_docs and existing_docs[doc]["remarks"] else ""
                    if doc in existing_docs and existing_docs[doc]["file_name"]: st.caption(f"💾 *Saved Draft File:* `{existing_docs[doc]['file_name']}`")
                    dc1, dc2, dc3 = st.columns([2, 1, 2])
                    with dc1: st.write(f"**{idx+1}.** {doc}")
                    with dc2: st_v = st.selectbox("Status", ["Available", "Not Available"], key=f"m_s_{idx}", index=["Available", "Not Available"].index(def_d_status))
                    with dc3: fl_v = st.file_uploader("Upload", type=["pdf","png","jpg"], key=f"m_f_{idx}")
                    rm_v = st.text_input("Remarks", key=f"m_r_{idx}", value=def_d_rem)
                    doc_responses[doc] = {"status": st_v, "file": fl_v, "remarks": rm_v, "cat": "Mandatory"}

                st.markdown("##### 🟡 Auxiliary System Records")
                for idx, doc in enumerate(later_docs):
                    def_l_status = existing_docs[doc]["status"] if doc in existing_docs and existing_docs[doc]["status"] else "Available"
                    def_l_rem = existing_docs[doc]["remarks"] if doc in existing_docs and existing_docs[doc]["remarks"] else ""
                    if doc in existing_docs and existing_docs[doc]["file_name"]: st.caption(f"💾 *Saved Draft File:* `{existing_docs[doc]['file_name']}`")
                    dc1, dc2, dc3 = st.columns([2, 1, 2])
                    with dc1: st.write(f"**{idx+1}.** {doc}")
                    with dc2: st_v = st.selectbox("Status", ["Available", "Not Available"], key=f"l_s_{idx}", index=["Available", "Not Available"].index(def_l_status))
                    with dc3: fl_v = st.file_uploader("Upload", type=["pdf","png","jpg"], key=f"l_f_{idx}")
                    rm_v = st.text_input("Remarks", key=f"l_r_{idx}", value=def_l_rem)
                    doc_responses[doc] = {"status": st_v, "file": fl_v, "remarks": rm_v, "cat": "Auxiliary"}

            with t3:
                st.markdown("#### Dynamic Plant Machinery Capability Ledger")
                if st.button("➕ Add Plant Machinery Row Block"): st.session_state.mach_count += 1
                
                machinery_rows = []
                for m in range(st.session_state.mach_count):
                    d_desc, d_uid, d_make, d_cap, d_spec, d_year, d_feat, d_auto, d_rem = [""]*9
                    if db_draft_mach and m < len(db_draft_mach): d_desc, d_uid, d_make, d_cap, d_spec, d_year, d_feat, d_auto, d_rem = db_draft_mach[m]
                    
                    r1, r2, r3, r4 = st.columns(4)
                    with r1: mc_desc = st.text_input("Machine Description", key=f"m_ds_{m}", value=d_desc); mc_uid = st.text_input("Unique ID Code", key=f"m_ui_{m}", value=d_uid)
                    with r2: mc_make = st.text_input("Make/Model Specs", key=f"m_mk_{m}", value=d_make); mc_cap = st.text_input("Operating Capacity", key=f"m_cp_{m}", value=d_cap)
                    with r3: mc_spec = st.text_input("Technical Specs", key=f"m_sp_{m}", value=d_spec); mc_year = st.text_input("Installation Year", key=f"m_yr_{m}", value=d_year)
                    with r4: mc_feat = st.text_input("Core Features", key=f"m_ft_{m}", value=d_feat); mc_auto = st.selectbox("Automation Grade", ["Manual", "Semi-Automatic", "Fully-Automatic"], key=f"m_au_{m}", index=["Manual", "Semi-Automatic", "Fully-Automatic"].index(d_auto) if d_auto in ["Manual", "Semi-Automatic", "Fully-Automatic"] else 0)
                    mc_rem = st.text_input("Remarks Log", key=f"m_rm_{m}", value=d_rem)
                    machinery_rows.append([mc_desc, mc_uid, mc_make, mc_cap, mc_spec, mc_year, mc_feat, mc_auto, mc_rem])
                    st.markdown("---")

            with t4:
                st.markdown("#### Dynamic Metrological Traceability & Lab Register")
                if st.button("➕ Add Metrological Instrument Row"): st.session_state.inst_count += 1
                
                instrument_rows = []
                for r in range(st.session_state.inst_count):
                    d_cat, d_name, d_mm, d_test, d_rng, d_acc, d_cal, d_nabl, d_mst, d_cert, d_rem = [""]*11
                    if db_draft_inst and r < len(db_draft_inst): d_cat, d_name, d_mm, d_test, d_rng, d_acc, d_cal, d_nabl, d_mst, d_cert, d_rem = db_draft_inst[r]
                    
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: ins_cat = st.selectbox("Asset Category", ["Measuring Instrument", "Testing Facility"], key=f"i_ct_{r}", index=["Measuring Instrument", "Testing Facility"].index(d_cat) if d_cat in ["Measuring Instrument", "Testing Facility"] else 0); ins_name = st.text_input("Instrument Name", key=f"i_nm_{r}", value=d_name)
                    with c2: ins_mm = st.text_input("Make/Model No.", key=f"i_mm_{r}", value=d_mm); ins_test = st.text_input("Test Performed", key=f"i_ts_{r}", value=d_test)
                    with c3: ins_rng = st.text_input("Measurement Range", key=f"i_rg_{r}", value=d_rng); ins_acc = st.text_input("Accuracy/Least Count", key=f"i_ac_{r}", value=d_acc)
                    with c4: ins_cal = st.text_input("Last Calibration Date", key=f"i_cd_{r}", value=d_cal); ins_nabl = st.selectbox("NABL Facility?", ["Yes", "No"], key=f"i_nb_{r}", index=["Yes", "No"].index(d_nabl) if d_nabl in ["Yes", "No"] else 0)
                    ins_mst = st.text_input("Master Standard Details", key=f"i_ms_{r}", value=d_mst)
                    ins_cert = st.text_input("Calibration Certificate Ref No.", key=f"i_cr_{r}", value=d_cert)
                    ins_rem = st.text_input("Remarks Log", key=f"i_rm_{r}", value=d_rem)
                    instrument_rows.append([ins_cat, ins_name, ins_mm, ins_test, ins_rng, ins_acc, ins_cal, ins_nabl, ins_mst, ins_cert, ins_rem])
                    st.markdown("---")

            with t5:
                st.markdown("#### Factory Plant Physical Environment Image Evidences")
                photo_responses = []
                for idx, p_desc in enumerate(plant_photos):
                    def_p_name = existing_photos[p_desc]["custom_name"] if p_desc in existing_photos and existing_photos[p_desc]["custom_name"] else ""
                    def_p_rem = existing_photos[p_desc]["remarks"] if p_desc in existing_photos and existing_photos[p_desc]["remarks"] else ""
                    if p_desc in existing_photos and existing_photos[p_desc]["file_name"]: st.caption(f"📸 *Saved Photo:* `{existing_photos[p_desc]['file_name']}`")
                    st.markdown(f"📸 **{idx+1}. Target Metric Zone: {p_desc}**")
                    pc1, pc2 = st.columns([1, 1])
                    with pc1: img_file = st.file_uploader("Upload Image Frame", type=["jpg","png","jpeg"], key=f"p_f_{idx}")
                    with pc2:
                        photo_custom_name = st.text_input("Photo Frame Custom Name", key=f"p_n_{idx}", value=def_p_name)
                        photo_remarks = st.text_input("Technical Capture Captions", key=f"p_r_{idx}", value=def_p_rem)
                    photo_responses.append({"cat_desc": p_desc, "file": img_file, "custom_name": photo_custom_name, "remarks": photo_remarks})

            # --- SUBMISSION CONTROLS (VISIBLE AT ROOT SCOPE FOR STABILITY) ---
            st.markdown("<br><hr style='border: 1px solid #E31E24;'><h3 style='color:#E31E24;'>📥 Step C: Form Draft Vault & Submission Transmission</h3>", unsafe_allow_html=True)
            scol1, scol2 = st.columns(2)

            def commit_to_postgresql(status_string):
                try:
                    with conn.cursor() as c:
                        columns_string = "supplier_email, submission_status, timestamp, supplier_name, product_name, audit_date, gst_no, pan_no, cin_no, msme_cert, iso_cert, approval_status"
                        value_array = [vendor_email, status_string, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s_name, p_name, str(a_date), gst_no, pan_no, cin_no, msme_cert, iso_cert, approval_status]
                        conflict_update = "submission_status=EXCLUDED.submission_status, timestamp=EXCLUDED.timestamp, supplier_name=EXCLUDED.supplier_name, product_name=EXCLUDED.product_name, audit_date=EXCLUDED.audit_date, gst_no=EXCLUDED.gst_no, pan_no=EXCLUDED.pan_no, cin_no=EXCLUDED.cin_no, msme_cert=EXCLUDED.msme_cert, iso_cert=EXCLUDED.iso_cert, approval_status=EXCLUDED.approval_status"
                        
                        for key, val in core_inputs.items():
                            columns_string += f", {key}"
                            value_array.append(val)
                            conflict_update += f", {key}=EXCLUDED.{key}"
                        
                        placeholders = ", ".join(["%s"] * len(value_array))
                        c.execute(f"INSERT INTO core_assessment ({columns_string}) VALUES ({placeholders}) ON CONFLICT (supplier_email) DO UPDATE SET {conflict_update}", value_array)
                        
                        c.execute("DELETE FROM machinery WHERE supplier_email=%s", (vendor_email,))
                        for row in machinery_rows:
                            if row[0]: c.execute("INSERT INTO machinery (supplier_email, description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [vendor_email] + row)
                        
                        c.execute("DELETE FROM instruments WHERE supplier_email=%s", (vendor_email,))
                        for row in instrument_rows:
                            if row[1]: c.execute("INSERT INTO instruments (supplier_email, category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [vendor_email] + row)
                        
                        for d_title, d_val in doc_responses.items():
                            c.execute("SELECT id FROM doc_checklist WHERE supplier_email=%s AND description=%s", (vendor_email, d_title))
                            exists = c.fetchone()
                            if d_val["file"]:
                                binary_data = psycopg2.Binary(d_val["file"].read())
                                f_name = d_val["file"].name
                                if exists: c.execute("UPDATE doc_checklist SET status=%s, remarks=%s, file_name=%s, file_data=%s WHERE supplier_email=%s AND description=%s", (d_val["status"], d_val["remarks"], f_name, binary_data, vendor_email, d_title))
                                else: c.execute("INSERT INTO doc_checklist (supplier_email, category, description, status, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, %s, %s)", (vendor_email, d_val["cat"], d_title, d_val["status"], d_val["remarks"], f_name, binary_data))
                            else:
                                if exists: c.execute("UPDATE doc_checklist SET status=%s, remarks=%s WHERE supplier_email=%s AND description=%s", (d_val["status"], d_val["remarks"], vendor_email, d_title))
                                else: c.execute("INSERT INTO doc_checklist (supplier_email, category, description, status, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, NULL, NULL)", (vendor_email, d_val["cat"], d_title, d_val["status"], d_val["remarks"]))

                        for photo in photo_responses:
                            c.execute("SELECT id FROM plant_photos WHERE supplier_email=%s AND category_desc=%s", (vendor_email, photo["cat_desc"]))
                            exists = c.fetchone()
                            if photo["file"]:
                                photo_binary = psycopg2.Binary(photo["file"].read())
                                f_name = photo["file"].name
                                if exists: c.execute("UPDATE plant_photos SET custom_photo_name=%s, remarks=%s, file_name=%s, file_data=%s WHERE supplier_email=%s AND category_desc=%s", (photo["custom_name"], photo["remarks"], f_name, photo_binary, vendor_email, photo["cat_desc"]))
                                else: c.execute("INSERT INTO plant_photos (supplier_email, category_desc, custom_photo_name, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, %s)", (vendor_email, photo["cat_desc"], photo["custom_name"], photo["remarks"], f_name, photo_binary))
                            else:
                                if exists: c.execute("UPDATE plant_photos SET custom_photo_name=%s, remarks=%s WHERE supplier_email=%s AND category_desc=%s", (photo["custom_name"], photo["remarks"], vendor_email, photo["cat_desc"]))
                                else: c.execute("INSERT INTO plant_photos (supplier_email, category_desc, custom_photo_name, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, NULL, NULL)", (vendor_email, photo["cat_desc"], photo["custom_name"], photo["remarks"]))
                    conn.commit()
                    return True
                except Exception as db_err:
                    conn.rollback()
                    st.error(f"⚠️ Production Gatekeeper Halt: Transaction rolled back safely to prevent corruption. Reason: {str(db_err)}")
                    return False

            with scol1:
                if st.button("💾 SAVE AS DRAFT", use_container_width=True):
                    if not s_name: st.error("Validation Error: Supplier Corporate Name is required to commit a draft.")
                    else:
                        if commit_to_postgresql('DRAFT'):
                            st.success("💾 State Transmitted: Partial draft snapshot locked inside cloud database.")

            with scol2:
                if st.button("🚀 FINAL COMPLETED SUBMIT TO DANISH POWER", use_container_width=True):
                    if not s_name or not p_name: st.error("Validation Error: Corporate Registry data items are strictly required.")
                    else:
                        if commit_to_postgresql('SUBMITTED'):
                            st.success("🚀 Success! Compliance response locked down.")
                            st.balloons()

elif portal_mode == "DPL Quality Admin View":
    st.markdown("## 🛡️ Quality Assurance Verification Vault")
    admin_token = st.text_input("Enter Enterprise Operational Security Access Token", type="password")
    if admin_token == st.secrets["admin"]["password"]:
        st.success("🔑 Authorization Confirmed.")
        conn = init_connection()
        with conn.cursor() as c:
            c.execute("SELECT id, supplier_email, supplier_name, product_name, submission_status FROM core_assessment ORDER BY id DESC")
            records = c.fetchall()
        if not records: st.warning("No vendor records currently populate relational tables.")
        else:
            lookup_options = [f"ID: {r[0]} | Name: {r[2]} ({r[1]}) | State: {r[4]}" for r in records]
            target_selection = st.selectbox("Choose a Vendor Data Matrix Record for Analysis", lookup_options)
            selected_email = [row[1] for row in records if f"ID: {row[0]}" in target_selection][0]
            st.markdown("---")
            if st.button("📄 EXECUTE AND BUILD BRANDED OFFICIAL COMPLIANCE PDF REPORT", use_container_width=True):
                with st.spinner("Compiling structural entities into PDF layout..."):
                    pdf_stream, resolved_name = generate_master_pdf(selected_email)
                    if pdf_stream:
                        st.download_button(label=f"📥 DOWNLOAD OFFICIAL BRANDED AUDIT REPORT FOR {resolved_name.upper()}", data=pdf_stream, file_name=f"DPL_Audit_Report_{resolved_name.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
                    else: st.error("Compilation Fault: Empty or mismatched structure matrices encountered.")
    elif admin_token != "": st.error("Security Halt: Signature validation profile failed.")
