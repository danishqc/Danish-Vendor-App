import streamlit as st
import sqlite3
import os
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# Page Config
st.set_page_config(page_title="Danish Power Limited - Enterprise Master Portal", layout="wide")

# --- NATIVE EMBEDDED LOGO ENCODING STRATEGY ---
LOGO_BASE64 = "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"

# --- DATABASE MANAGEMENT VAULT ---
def init_db():
    conn = sqlite3.connect('danish_power_enterprise.db')
    c = conn.cursor()
    
    # 1. Core Evaluation Table
    cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT", "timestamp TEXT", "supplier_name TEXT", "product_name TEXT", "audit_date TEXT"]
    for i in range(1, 9):
        for j in range(1, 6):
            cols.append(f"q_{i}_{j}_status TEXT")
            cols.append(f"q_{i}_{j}_comment TEXT")
    c.execute(f"CREATE TABLE IF NOT EXISTS core_assessment ({', '.join(cols)})")
    
    # 2. Documents Checklist Table
    c.execute("""CREATE TABLE IF NOT EXISTS doc_checklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_name TEXT, category TEXT, description TEXT, status TEXT, remarks TEXT, file_path TEXT
    )""")
    
    # 3. Production Machinery Table
    c.execute("""CREATE TABLE IF NOT EXISTS machinery (
        id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_name TEXT, description TEXT, unique_id TEXT, make_model TEXT, 
        capacity TEXT, specification TEXT, installation_year TEXT, features TEXT, automation TEXT, remarks TEXT
    )""")
    
    # 4. Calibration Registers Table
    c.execute("""CREATE TABLE IF NOT EXISTS instruments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_name TEXT, category TEXT, name TEXT, make_model TEXT, 
        test_name TEXT, range TEXT, accuracy TEXT, cal_date TEXT, nabl_detail TEXT, master_equip TEXT, certificate_no TEXT, remarks TEXT
    )""")
    
    # 5. 🆕 COMPREHENSIVE RE-ARCHITECTED PHOTO VENDOR TABLE (Stores Raw Binary Stream Base64 Strings)
    c.execute("""CREATE TABLE IF NOT EXISTS plant_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, supplier_name TEXT, description TEXT, file_path TEXT, base64_blob TEXT
    )""")
    
    conn.commit()
    conn.close()

init_db()

# --- 100% EXCEL-MAPPED PARAMETRIC DICTIONARY ---
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
    "List of Machinery & inhouse/outsource testing facilities", "MQP (Quality Plan) along with Incoming, Inprocess & Final Inspection Checklist (Related to Product)",
    "Calibration of measuring instruments and test equipment", "Approval letters of various consultants/ PSUs or major Private parties",
    "List of supply for major Private & government Sector Company", "Total area of the Factory (Covered  & Uncovered)"
]

later_docs = [
    "Product related special certification (If Applicable)", "Applicable type test reports (If Any)", "Quality Policy",
    "Factory License/ Registration certificate", "Pollution clearance certificate", "Standard operating Procedure (If any - Product Related)",
    "Copies of annual Balance Sheet for the last three years along with audit report", "Five major customer Un-priced purchase order for similar product",
    "Performance feedback certificate (Two customer)", "Detail of Outsourced Manufacturing activities (if any)",
    "Work Instruction for Storage, Handling etc.", "Maintenance facility & preventive maintenance", "Safety PPE and Firefighting guideline / Work instruction",
    "Internal Non – conformity of last one year and 8D analysis / CAPA report for any one of non-conformity", "Customer complaint handling records if any",
    "In-house training and learning development detail if any:", "Jigs & fixtures Detail (List if available):",
    "Proof of time wise delivery with quality (Two customers)", "Electrical Power and alternative arrangement for power",
    "MTC & third-party test reports available for similar product (if any)", "Packing Guideline ( Related to Product)", "Tool Manufacturing Facility (If Applicable)"
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

# --- NATIVE STABLE PDF GENERATOR (BUILDS COMPRESSED GRID DIRECT FROM DATABASE TEXT BLOB) ---
def generate_master_pdf(supplier):
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
    story.append(Paragraph("A unit of trust | Supplier Quality Audit Report | Format: F-12", sub_s))
    story.append(Spacer(1, 15))
    
    conn = sqlite3.connect('danish_power_enterprise.db')
    c = conn.cursor()
    c.execute("SELECT * FROM core_assessment WHERE supplier_name=?", (supplier,))
    core_data = c.fetchone()
    c.execute("SELECT description, status, remarks FROM doc_checklist WHERE supplier_name=?", (supplier,))
    docs_data = c.fetchall()
    c.execute("SELECT description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks FROM machinery WHERE supplier_name=?", (supplier,))
    mach_data = c.fetchall()
    c.execute("SELECT category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks FROM instruments WHERE supplier_name=?", (supplier,))
    inst_data = c.fetchall()
    # Pulling Base64 String Blobs directly from table mapping
    c.execute("SELECT description, base64_blob FROM plant_photos WHERE supplier_name=?", (supplier,))
    photos_data = c.fetchall()
    conn.close()

    if not core_data:
        return None

    meta_table = Table([
        [Paragraph(f"<b>Supplier Name:</b> {core_data[2]}", cell_s), Paragraph(f"<b>Audit Date:</b> {core_data[4]}", cell_s)],
        [Paragraph(f"<b>Product Supplied:</b> {core_data[3]}", cell_s), Paragraph(f"<b>Report Compiled:</b> {datetime.now().strftime('%d-%m-%Y')}", cell_s)]
    ], colWidths=[280, 280])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f5f7f8')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cfd8dc')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Core Compliance Questionnaire (Points 1.1 - 8.5)", sec_s))
    q_table_data = [[Paragraph("S.No", th_s), Paragraph("Checkpoints Description", th_s), Paragraph("Status", th_s), Paragraph("Auditor Remarks / Evidence", th_s)]]
    
    db_idx = 5
    for sec_name, questions in audit_points.items():
        q_table_data.append([Paragraph(f"<b>{sec_name}</b>", cell_b), "", "", ""])
        for q_num, q_text in questions.items():
            q_table_data.append([
                Paragraph(q_num, cell_s), Paragraph(q_text, cell_s),
                Paragraph(core_data[db_idx], cell_s), Paragraph(core_data[db_idx+1] if core_data[db_idx+1] else "-", cell_s)
            ])
            db_idx += 2
            
    q_table = Table(q_table_data, colWidths=[35, 275, 50, 200], repeatRows=1)
    q_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), brand_red),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    row_counter = 1
    for sec_name, questions in audit_points.items():
        q_table.setStyle(TableStyle([('SPAN', (0, row_counter), (3, row_counter)), ('BACKGROUND', (0, row_counter), (3, row_counter), colors.HexColor('#FFEBEE'))]))
        row_counter += len(questions) + 1
    story.append(q_table)
    
    story.append(PageBreak())
    
    story.append(Paragraph("2. Documents Submission Log Status", sec_s))
    doc_table_data = [[Paragraph("Documents Description", th_s), Paragraph("Status", th_s), Paragraph("Remarks / Reason", th_s)]]
    for d in docs_data:
        doc_table_data.append([Paragraph(d[0], cell_s), Paragraph(d[1], cell_s), Paragraph(d[2] if d[2] else "-", cell_s)])
    doc_table = Table(doc_table_data, colWidths=[280, 80, 200], repeatRows=1)
    doc_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_dark), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('PADDING', (0,0), (-1,-1), 5)]))
    story.append(doc_table)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Plant Machinery Deployed & Production Capacity", sec_s))
    mach_headers = ["Sr", "Description", "Unique ID", "Make/Model", "Capacity", "Specification", "Year", "Features", "Automation", "Remarks"]
    mach_table_data = [[Paragraph(h, th_s) for h in mach_headers]]
    for idx, m in enumerate(mach_data):
        mach_table_data.append([Paragraph(str(idx+1), cell_s)] + [Paragraph(str(val) if val else "-", cell_s) for val in m])
    mach_table = Table(mach_table_data, colWidths=[20, 80, 45, 55, 45, 55, 30, 80, 75, 75], repeatRows=1)
    mach_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_red), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('PADDING', (0,0), (-1,-1), 4)]))
    story.append(mach_table)
    
    story.append(PageBreak())
    
    story.append(Paragraph("4. Measuring Instruments & Testing Facility Calibration Logs", sec_s))
    inst_headers = ["Category", "Instrument Name", "Make/Model", "Test Performed", "Range", "Accuracy", "Cal Date", "NABL State", "Cert No", "Remarks"]
    inst_table_data = [[Paragraph(h, th_s) for h in inst_headers]]
    for row in inst_data:
        inst_table_data.append([
            Paragraph(row[0], cell_s), Paragraph(row[1], cell_s), Paragraph(row[2], cell_s), Paragraph(row[3], cell_s),
            Paragraph(row[4], cell_s), Paragraph(row[5], cell_s), Paragraph(row[6], cell_s), Paragraph(row[7], cell_s), Paragraph(row[9], cell_s), Paragraph(row[10] if row[10] else "-", cell_s)
        ])
    inst_table = Table(inst_table_data, colWidths=[65, 80, 55, 60, 45, 45, 50, 55, 55, 90], repeatRows=1)
    inst_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), brand_dark), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')), ('PADDING', (0,0), (-1,-1), 4)]))
    story.append(inst_table)
    
    story.append(PageBreak())
    
    # 🌟 FIXED SECTION 5: COMPRESSED NATIVE IMAGE FROM DIRECT BASE64 BLOB
    story.append(Paragraph("5. Factory Plant Photo Evidences (Direct Database Visual Vault)", sec_s))
    story.append(Spacer(1, 5))
    
    photo_grid = []
    current_row = []
    
    for p_desc, b64_str in photos_data:
        cell_elements = []
        cell_elements.append(Paragraph(f"<b>{p_desc}</b>", cell_b))
        cell_elements.append(Spacer(1, 4))
        
        # Decoding Base64 Stream text block directly back to memory image logic
        if b64_str and b64_str != "Empty":
            try:
                img_data = base64.b64decode(b64_str)
                img_buf = io.BytesIO(img_data)
                # Scaling photo dimension to 240x150 bounds natively inside cells
                img_flowable = Image(img_buf, width=240, height=150)
                cell_elements.append(img_flowable)
            except Exception:
                cell_elements.append(Paragraph("<font color='red'><i>Error decoding image block</i></font>", cell_s))
        else:
            cell_elements.append(Paragraph("<i>No Image Evidence Submitted</i>", cell_s))
            
        current_row.append(cell_elements)
        
        if len(current_row) == 2:
            photo_grid.append(current_row)
            current_row = []
            
    if current_row:
        current_row.append("")
        photo_grid.append(current_row)
        
    if photo_grid:
        t_photos = Table(photo_grid, colWidths=[270, 270])
        t_photos.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cfd8dc')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fafafa'))
        ]))
        story.append(t_photos)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS STYLING ENHANCEMENTS ---
st.markdown("""
<style>
    .main { background-color: #FAFAFA; }
    div.stButton > button:first-child {
        background-color: #E31E24 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
    }
    div.stButton > button:first-child:hover { background-color: #B71C1C !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #E31E24 !important; border-bottom-color: #E31E24 !important; }
</style>
""", unsafe_allow_html=True)

# --- BRANDED GRID HEADER ALIGNMENT ---
header_col1, header_col2, header_col3 = st.columns([1.5, 3.2, 2.3])
with header_col1:
    st.image(f"data:image/png;base64,{LOGO_BASE64}", use_container_width=True)
with header_col2:
    st.markdown("<h1 style='color: #E31E24; text-align: center; margin: 0; font-size: 28px; font-weight: 800;'>DANISH POWER LIMITED</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #212121; font-weight:600; margin: 2px 0 0 0;'>Supplier Quality System Audit</p>", unsafe_allow_html=True)
with header_col3:
    st.markdown("""
    <div style='border: 2px solid #E31E24; padding: 10px; border-radius: 6px; background-color: #FFFFFF; font-size: 13px; color:#212121;'>
        <b>Format No.:</b> F-12<br><b>Date:</b> 01.09.2025<br><b>Rev. No.:</b> 03
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 1.5px solid #E31E24; margin-top:10px; margin-bottom:25px;'>", unsafe_allow_html=True)

# --- SIDEMENU CONTROL DASHBOARD ---
st.sidebar.markdown("<h3 style='color:#E31E24; font-weight:bold;'>PORTAL ACCESS</h3>", unsafe_allow_html=True)
portal_mode = st.sidebar.radio("Switch Dashboard View", ["Supplier Gateway Form", "DPL Quality Admin View"])

if portal_mode == "Supplier Gateway Form":
    st.subheader("🏢 Part A: Corporate Registration Identity")
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        s_name_input = st.text_input("Supplier Corporate Name*")
        p_name_input = st.text_input("Product Component Description*")
    with gcol2:
        a_date_input = st.date_input("Audit Compilation Date", datetime.now())
        
    t1, t2, t3, t4, t5 = st.tabs([
        "📊 1. Core Form", "📎 2. Document Vault", "⚙️ 3. Machinery Register", "🔬 4. Calibration Records", "📸 5. Plant Images"
    ])
    
    with t1:
        core_inputs = {}
        for sec_title, questions in audit_points.items():
            st.markdown(f"<div style='background-color:#FFEBEE; padding:8px; border-left: 4px solid #E31E24; border-radius:4px; font-weight:bold; color:#B71C1C;'>{sec_title}</div>", unsafe_allow_html=True)
            for q_num, q_text in questions.items():
                st.markdown(f"**{q_num}** {q_text}")
                ch_col1, ch_col2 = st.columns([1, 4])
                k_code = q_num.replace('.', '_')
                with ch_col1: status_select = st.selectbox("Status", ["Yes", "No", "N/A"], key=f"core_s_{k_code}")
                with ch_col2: comment_input = st.text_input("Auditor Remarks", key=f"core_c_{k_code}")
                core_inputs[f"q_{k_code}_status"] = status_select
                core_inputs[f"q_{k_code}_comment"] = comment_input

    with t2:
        m_doc_responses = {}
        for idx, doc in enumerate(mandatory_docs):
            dc1, dc2, dc3 = st.columns([2, 1, 2])
            with dc1: st.write(f"**{idx+1}.** {doc}")
            with dc2: st_val = st.selectbox("Status", ["Available", "Not Available"], key=f"m_ds_{idx}")
            with dc3: fl_val = st.file_uploader("Upload Copy", type=["pdf","jpg","png"], key=f"m_fl_{idx}")
            rem_val = st.text_input("Remarks", key=f"m_rm_{idx}")
            m_doc_responses[doc] = {"status": st_val, "file": fl_val, "remarks": rem_val}
            
        l_doc_responses = {}
        for idx, doc in enumerate(later_docs):
            dc1, dc2, dc3 = st.columns([2, 1, 2])
            with dc1: st.write(f"**{idx+1}.** {doc}")
            with dc2: st_val = st.selectbox("Status", ["Available", "Not Available"], key=f"l_ds_{idx}")
            with dc3: fl_val = st.file_uploader("Upload Copy", type=["pdf","jpg","png"], key=f"l_fl_{idx}")
            rem_val = st.text_input("Remarks Stage 2", key=f"l_rm_{idx}")
            l_doc_responses[doc] = {"status": st_val, "file": fl_val, "remarks": rem_val}

    with t3:
        if 'mach_rows_count' not in st.session_state: st.session_state.mach_rows_count = 1
        if st.button("➕ Add Machinery Row"): st.session_state.mach_rows_count += 1
        machinery_rows_entries = []
        for m in range(st.session_state.mach_rows_count):
            r1, r2, r3, r4 = st.columns(4)
            with r1: m_desc = st.text_input("Machine Name", key=f"md_ds_{m}"); m_uid = st.text_input("ID No.", key=f"md_ui_{m}")
            with r2: m_make = st.text_input("Make/Model", key=f"md_mk_{m}"); m_cap = st.text_input("Capacity", key=f"md_cp_{m}")
            with r3: m_spec = st.text_input("Specification", key=f"md_sp_{m}"); m_year = st.text_input("Year", key=f"md_yr_{m}")
            with r4: m_feat = st.text_input("Features", key=f"md_ft_{m}"); m_auto = st.selectbox("Automation", ["Manual", "Semi-Automatic", "Fully-Automatic"], key=f"md_au_{m}")
            m_rem = st.text_input("Remarks Log", key=f"md_rm_{m}")
            machinery_rows_entries.append([m_desc, m_uid, m_make, m_cap, m_spec, m_year, m_feat, m_auto, m_rem])

    with t4:
        if 'me_count' not in st.session_state: st.session_state.me_count = 1
        if st.button("➕ Add Equipment Row"): st.session_state.me_count += 1
        measuring_entries = []
        for r in range(st.session_state.me_count):
            c1, c2, c3, c4 = st.columns(4)
            with c1: name = st.text_input("Instrument Name", key=f"me_n_{r}"); mm = st.text_input("Model No.", key=f"me_m_{r}")
            with c2: t_name = st.text_input("Test Performed", key=f"me_t_{r}"); rng = st.text_input("Range", key=f"me_r_{r}")
            with c3: acc = st.text_input("Accuracy", key=f"me_a_{r}"); c_dt = st.text_input("Cal Date", key=f"me_d_{r}")
            with c4: nabl = st.selectbox("NABL Facility?", ["Yes", "No"], key=f"me_nb_{r}"); cert = st.text_input("Cert No.", key=f"me_c_{r}")
            mst = st.text_input("Master standard Traceability", key=f"me_ms_{r}")
            remk = st.text_input("Remarks Instrument", key=f"me_rmk_{r}")
            measuring_entries.append(["Measuring Instrument", name, mm, t_name, rng, acc, c_dt, nabl, mst, cert, remk])

    with t5:
        st.markdown("#### Upload Factory Images")
        plant_photos_entries = {}
        for idx, p_desc in enumerate(plant_photos):
            pc1, pc2 = st.columns([2, 3])
            with pc1: st.markdown(f"📸 **{p_desc}**")
            with pc2: img_file = st.file_uploader(f"Choose file for {p_desc}", type=["jpg","jpeg","png"], key=f"ph_fl_{idx}")
            plant_photos_entries[p_desc] = img_file

    master_submit = st.button("🔥 TRANSMIT VENDOR REGISTRATION TO DANISH POWER DATA VAULT", use_container_width=True)
    
    if master_submit:
        if not s_name_input or not p_name_input:
            st.error("Error: Corporate Name & Product Description fields are mandatory.")
        else:
            conn = sqlite3.connect('danish_power_enterprise.db')
            c = conn.cursor()
            
            # 1. Save Core Form
            db_cols = "timestamp, supplier_name, product_name, audit_date"
            db_placeholders = "?, ?, ?, ?"
            db_vals = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s_name_input, p_name_input, str(a_date_input)]
            for key, val in core_inputs.items():
                db_cols += f", {key}"
                db_placeholders += ", ?"
                db_vals.append(val)
            c.execute(f"INSERT INTO core_assessment ({db_cols}) VALUES ({db_placeholders})", db_vals)
            
            # 2. Save Documents
            for d_title, d_data in {**m_doc_responses, **l_doc_responses}.items():
                c.execute("INSERT INTO doc_checklist (supplier_name, category, description, status, remarks, file_path) VALUES (?, ?, ?, ?, ?, ?)",
                          (s_name_input, "Audit Doc", d_title, d_data["status"], d_data["remarks"], "Stored In Cloud"))
                          
            # 3. Save Machinery & Instruments
            for mach in machinery_rows_entries:
                if mach[0]: c.execute("INSERT INTO machinery (supplier_name, description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (s_name_input, *mach))
            for inst in measuring_entries:
                if inst[1]: c.execute("INSERT INTO instruments (supplier_name, category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (s_name_input, *inst))
                                 
            # 4. 🌟 FIXED IMAGE CONVERSION STRATEGY: Converting uploaded image stream to secure text block Base64
            for p_title, p_obj in plant_photos_entries.items():
                if p_obj is not None:
                    # Direct reading the image binary data and converting to clean ASCII text string
                    bytes_data = p_obj.read()
                    b64_string = base64.b64encode(bytes_data).decode('utf-8')
                else:
                    b64_string = "Empty"
                c.execute("INSERT INTO plant_photos (supplier_name, description, file_path, base64_blob) VALUES (?, ?, ?, ?)", (s_name_input, p_title, "Cloud Blob", b64_string))
                
            conn.commit()
            conn.close()
            st.success(f"🚀 Success! Form data for '{s_name_input}' has been safely uploaded inside database cloud system.")
            st.balloons()

elif portal_mode == "DPL Quality Admin View":
    st.markdown("<h2 style='color:#E31E24;'>🛡️ Quality Assurance Verification Vault</h2>", unsafe_allow_html=True)
    passkey = st.text_input("Enter Enterprise Security Access Token Key", type="password")
    
    if passkey == "danish123":
        st.success("Authorization Confirmed.")
        conn = sqlite3.connect('danish_power_enterprise.db')
        c = conn.cursor()
        c.execute("SELECT id, supplier_name, product_name, timestamp FROM core_assessment ORDER BY id DESC")
        entries = c.fetchall()
        conn.close()
        
        if not entries:
            st.warning("Database State: No entries found.")
        else:
            lookup_map = [f"ID: {row[0]} | {row[1]} ({row[2]}) - Filed: {row[3]}" for row in entries]
            selection = st.selectbox("Choose a Supplier to build PDF Report", lookup_map)
            selected_supplier_name = selection.split(" | ")[1].split(" (")[0]
            
            compiled_pdf_stream = generate_master_pdf(selected_supplier_name)
            if compiled_pdf_stream:
                st.download_button(
                    label=f"📥 DOWNLOAD BRANDED AUDIT PDF WITH IMAGES FOR {selected_supplier_name.upper()}",
                    data=compiled_pdf_stream,
                    file_name=f"DPL_Audit_Report_{selected_supplier_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
