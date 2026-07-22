import re
import secrets as pysecrets
import smtplib
import ssl
from email.mime.text import MIMEText

import streamlit as st
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Danish Power Limited - Enterprise Master Portal", layout="wide")

# --- HIGH-CONTRAST INPUT STYLING (fixes washed-out/invisible form fields) ---
st.markdown("""
<style>
/* Text inputs, number inputs, date inputs, text areas */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    border: 1.8px solid #4A4A4A !important;
    border-radius: 6px !important;
    color: #111111 !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus,
.stTextArea textarea:focus {
    border: 2px solid #E31E24 !important;
    box-shadow: 0 0 0 1px #E31E24 !important;
}
/* Selectbox / dropdown */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1.8px solid #4A4A4A !important;
    border-radius: 6px !important;
    color: #111111 !important;
}
div[data-baseweb="select"] span {
    color: #111111 !important;
}
/* Placeholder text - keep visible but distinguishable */
input::placeholder, textarea::placeholder {
    color: #6B6B6B !important;
    opacity: 1 !important;
}
/* File uploader box */
[data-testid="stFileUploader"] section {
    background-color: #FAFAFA !important;
    border: 1.8px dashed #4A4A4A !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploader"] section > div {
    color: #111111 !important;
}
/* Field labels - make bold and dark so they don't fade into background */
label, .stTextInput label, .stSelectbox label, .stFileUploader label, .stDateInput label, .stTextArea label {
    color: #212121 !important;
    font-weight: 600 !important;
}
/* Radio buttons in sidebar */
[data-testid="stSidebar"] label {
    color: #212121 !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# --- NATIVE EMBEDDED LOGO ENCODING STRATEGY ---
LOGO_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAZcAAAB8CAMAAACSTA3KAAAAyVBMVEX////jHiThAAAAAADjGyH86OniEBj98/PiCxXjGR/97+/thofiAArjFRziAA71xsbrcnToVVnlOT7yrrD74uMODAn/+vr0uLnmQ0j40dL62tvrdnjvm5zlMzjxoqOKionpaWvjJSumpqZ9fX3pYmX1v8DujI7w8PDvk5Wzs7PpXF/zsbL4z9AaGBePjo4rKilhYWCbm5rCwsJWVVVubW3sf4HnTlIlJCM5ODfd3d3rbXDmQkYWFBPOzs4yMTBBQD/k4+NNTEx1dXSo7yhCAAAQPUlEQVR4nO1di1riOhAuaYEW24LQgnKTKjdRVkURV3HVff+HOukFSCaXtt6WPZv/+845QtJkMn8yM5mEHk1TUFBQUFBQUFBQUFBQUFBQUFBQUFBQUPincTmokRg2/7RA2dCmxX4sf7TBxiPV3sFnCPkRtFCJBPrwAL8HVSB25aMNLqkG3fpnCPkRtOwCib+HF1rsD/NyYJLtWUefIeRHoHiJoXj5FChe9hOKl/2E4mU/oXjZTyhe9hOKl/2E4mU/MUI0FC//Uyhe9hOKl/3En+OlXClzkvjv5aVSLHpesfKXHAuUi15RPrLv58UbdTtHvaBgmY4RBL37cb9a3JXm5qV43F/i5kzXRsg1jaBe614W0x5KR7nd7w6f6r3e0/2gS0n4MVSOu8MgcFxklwpBfdxvC+qJeQklG4SS1Z+G0+7I+4yp6PWHBay+kmUZhlHA/xiWY2IZe51RQkAuXsqjg17IBm4uqY8bLLkI1afb8RbqJIIW1cCgRxb2asnXxf6RiVzXsUI4JRe3GAxaMlGqAd2NoO5o5iLcrGEkspo2Khwc82oKeKk07h1khwqMRMO6Q8Zh35MpKRXFbh3ZjlHgwCoh8/EyrJSDl8uOg0yL11zBctFRwgCySKAG1cRhiSw0Z9GXxwNkW1DMUMIhV4MRqqAbbpw8LSCHEdUwUb3K1uXy0q7ZrAINvPieGu9eNcePyOUrMWm+hOqtHLy06qjE5XgzFNSLhktv+GzAC6UnZ4i/qjyikkBCBx1dCqTJsK8cBbZAXgsNGTvJ4aXcEUmGWzD62akg0J4J2yRb712OsvEy6iEZyUlzj83cvLRsSiEADhKc3KfyUp7JBC7ZcMmwvFRNmWQGqotclRjNDmcB84CZoecUnxdPOsgdzF4xJy8HSLYGwyZNrjFL48UryJQaqpV2fCwv0zTJLJR3yVQtuVCUgPRHLi+NDGsvhmMV8/Ay69C1uQJyh5/CS1tqwuNmaRMJeRmnS1ZAy1y0jNOYlnXF8tJ8zCDidkAB/VnKC3bumWTiECPnpZJKC+7booZK84Kjg0yS5SCmfJ9DjWxPDC+VnpunATAl5LxkFaoBhUrhpQ66wQGuWYJUmR0JL1kly2zKikFWm8PvCPLiOe9S5QafwksBMS5WykufLsROdDidDurQ5yIyKHSFuVlWgrikRtGun2DvBQlFiFLe5/Di9XLxYtLyWX2ktjLG9IPueOP82JluwBYNrgDD7dCeDcTBCZCtmBrmAyQ5qVicSsbJRshs9AzomZlcmfkxcKCITNs1eZukhh7IeNlRJU5h4TyKZNMsS3iJZLMdWyR4jg2loMjnhFzkHXYPfaKeHNR8byLg57tCic64AUa6ggmCjp9z8OqaBa9y+mTKdq/FbLxYrhufXrpecVy0fMaNe4mvZCDlw6pBKNEFgWUaklDxufFtXvjaiLZxTLgxKXsUuagw3HRDrofgWrFcUmkSpqXpc3WcO0OsPblfiCMADPwUnK7tNe+5EQucLsh44WKPZwZ+diUUhAiFMPjxUFjOi/QHrADRVC7LKrseAw05G5LGy4/PKB4uWTbc9CUlxkaibZx6bzYMzY07zMdRykb8VApXqiiEhV1gePn7q6Ew4t5xGZ3RowxKw14+iXRhEEqfshsCSqXh9xwmuKlxxhUdC9IpTZr/CWTyovb4TU3YoRD9HTIzAttZ8ptCsRTLC8mtdI2aDM+wE5LYY4ZK8abi1s0eJokeWFnLTnBIEbcVE0aL859xrGAgDQzLwU3209ZGF5EkVYLagWJcqsJygyTiDsXRWOLHyF4CaCioZGn4TE7t0I6L7boAIzZoNJ9y3gBER3K9Fsrhhd2z5TgCQzTTdlbMlPMrckfYKmneGFsiZwWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQnfyD/WXAGsq4oXi6YKNJFB2lJelineLeKiLeKiLeKl8iJyWTAwnzEvhxRRO5i4YjTmmijPHYxglNE5nBvIidhtQa2kOBnoDJ/2M+oCxfAQvQ6BDeyxpKQJnAabwgoQ5c7z807mB7Fw83JbQ2/G1dD+O/6/6//wO373f/jtw9tN/Nff/w8u+e519c73j09vXs/ebg/3D/9v7u8fn69/Pcf/APj+j/T15fXN1/mI6+Hh7ub6KuxG/e/1bXWz2T29fHl4SHWv6//D1XnF49XDfVwe+Lq4vr6Zz26/P9zeP/y/vb1/eLq/f59N3V/f3t7++PqF42T68l8Pq1Cvf/28CrvRD/Xz9erh8e3H1fXb6sXq6vFqdfPz6vXtNdbH8w2h02c2P728/rV6m89fV2/Pz//V8z+f/sL758vFf+K/Xj3hL9bHh6fT+erDqfV5/PPDy6t1ebp4ur7+D2D6n+XhX149wTev2vKvv5e381v1qfNn2uKnO/8G4/PjrOf/Wv3vXw5xXz18+vj93WzHBcqVx5if4b/pM5sXWb3h/w/5tBvVefD9EwAAAABJRU5ErkJggg=="

# ============================================================
#  CONFIG / CONSTANTS
# ============================================================
MAX_FILE_MB = 10
MAX_ADMIN_ATTEMPTS = 5
OTP_TTL_MINUTES = 10
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# OTP-based email verification is optional: it only turns on if an [email]
# section (smtp_host, smtp_port, smtp_user, smtp_password) exists in secrets.
OTP_ENABLED = "email" in st.secrets


def is_valid_email(addr: str) -> bool:
    return bool(EMAIL_RE.match(addr.strip())) if addr else False


def send_otp_email(to_addr: str, code: str) -> bool:
    """Sends a one-time verification code. Returns True on success."""
    try:
        cfg = st.secrets["email"]
        msg = MIMEText(f"Your Danish Power Limited portal verification code is: {code}\n"
                        f"This code expires in {OTP_TTL_MINUTES} minutes.")
        msg["Subject"] = "Danish Power Limited - Verification Code"
        msg["From"] = cfg["smtp_user"]
        msg["To"] = to_addr
        context = ssl.create_default_context()
        with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"])) as server:
            server.starttls(context=context)
            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.sendmail(cfg["smtp_user"], to_addr, msg.as_string())
        return True
    except Exception as e:
        st.error(f"⚠️ Could not send verification email: {e}")
        return False


# ============================================================
#  DATABASE
# ============================================================
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        dbname=st.secrets["database"]["dbname"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        sslmode="require",
    )


def get_connection():
    """Wraps init_connection with a friendly error instead of a hard crash.
    Also detects a stale/dead cached connection (idle timeout, DB restart,
    provider auto-pause) and transparently reconnects - this does not touch
    any stored data, it only manages the connection object."""
    try:
        conn = init_connection()
    except Exception as e:
        st.error(f"❌ Database connection failed. Please contact the portal administrator. ({e})")
        st.stop()

    try:
        with conn.cursor() as c:
            c.execute("SELECT 1")
        conn.rollback()  # close the transaction the ping opened (read-only, nothing to keep)
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        try:
            conn.close()
        except Exception:
            pass
        init_connection.clear()  # evict the dead cached connection
        try:
            conn = init_connection()
        except Exception as e:
            st.error(f"❌ Database connection failed. Please contact the portal administrator. ({e})")
            st.stop()
    return conn


def init_db():
    conn = get_connection()
    conn.autocommit = True
    with conn.cursor() as c:
        cols = ["id SERIAL PRIMARY KEY", "supplier_email VARCHAR(255) UNIQUE", "submission_status VARCHAR(50)",
                "timestamp TEXT", "supplier_name TEXT", "product_name TEXT", "audit_date TEXT",
                "gst_no TEXT", "pan_no TEXT", "cin_no TEXT", "msme_cert TEXT", "iso_cert TEXT", "approval_status TEXT"]
        for i in range(1, 9):
            for j in range(1, 6):
                cols.append(f"q_{i}_{j}_status TEXT")
                cols.append(f"q_{i}_{j}_comment TEXT")
        c.execute(f"CREATE TABLE IF NOT EXISTS core_assessment ({', '.join(cols)})")

        # Kept for backward compatibility with older deployments of this table.
        # NOTE: because every read below uses RealDictCursor (name-based access,
        # not column position), it no longer matters where ALTER TABLE physically
        # appends these columns - unlike the previous version of this app.
        for col in ["gst_no", "pan_no", "cin_no", "msme_cert", "iso_cert", "approval_status"]:
            try:
                c.execute(f"ALTER TABLE core_assessment ADD COLUMN IF NOT EXISTS {col} TEXT;")
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


def dict_cursor(conn):
    """All reads use a name-based cursor so column order in the DB never matters."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


try:
    init_db()
except SystemExit:
    raise
except Exception as e:
    st.error("⚠️ Database is temporarily unreachable. Please refresh the page in a few seconds.")
    st.caption(f"Technical detail: {e}")
    st.stop()

# ============================================================
#  AUDIT MATRIX / DOCUMENT LISTS  (text synced with Assessment_Master.xlsx)
# ============================================================
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
    "Company Profile  / Brochure",
    "ISO 9001-2015 ISO 14001:2015, ISO45001:2018 or equivalent third-party certification",
    "Organization Chart along with Manpower details",
    "Process Flow Chart / Diagram",
    "Source of Raw Material/Bought Out Item",
    "List of Machinery & inhouse/outsource testing facilities",
    "MQP (Quality Plan) along with Incoming, Inprocess & Final Inspection Checklist (Related to Product)",
    "Calibration of measuring instruments and test equipment",
    "Approval letters of various consultants/ PSUs or major Private parties",
    "List of supply for major Private & government Sector Company",
    "Total area of the Factory (Covered & Uncovered)"
]

later_docs = [
    "Product related special certification (If Applicable)",
    "Applicable type test reports (If Any)",
    "Quality Policy",
    "Factory License/ Registration certificate",
    "Pollution clearance certificate",
    "Standard operating Procedure (If any - Product Related)",
    "Copies of annual Balance Sheet for the last three years along with audit report",
    "Five major customer Un-priced purchase order for similar product",
    "Performance feedback certificate (Two customer)",
    "Detail of Outsourced Manufacturing activities (if any)",
    "Work Instruction for Storage, Handling etc.",
    "Maintenance facility & preventive maintenance",
    "Safety PPE and Firefighting guideline / Work instruction",
    "Internal Non-conformity of last one year and 8D analysis / CAPA report for any one of non-conformity",
    "Customer complaint handling records if any",
    "In-house training and learning development detail if any",
    "Jigs & fixtures Detail (List if available)",
    "Proof of time wise delivery with quality (Two customers)",
    "Electrical Power and alternative arrangement for power",
    "MTC & third-party test reports available for similar product (if any)",
    "Packing Guideline (Related to Product)",
    "Tool Manufacturing Facility (If Applicable)"
]

plant_photos = [
    "Factory Administrative Building", "Critical Machinery for component", "Display of Critical Machinery Maintenance",
    "Incoming Area (Store)", "In process Inspection", "Final Inspection Area", "5S Management", "Testing Facility",
    "Critical Equipment", "Lifting & Handling Facility", "Packing", "Galvanizing (If Applicable)",
    "Painting Area (If Applicable)", "Special Test Equipment", "House Keeping & PPE", "Factory Lux (Light) Check",
    "DG Set (If Applicable)", "Tool Room (If Applicable)", "Route card / Documents availability at Shop Floor",
    "ERP System (If Applicable)", "Display of Quality Policy & Objective", "Display of Safety Rules",
    "Display of Work Instruction", "Ready for Dispatch"
]


def check_file_size(uploaded_file):
    """Returns True if the file is within the allowed size, else shows an error."""
    if uploaded_file is None:
        return True
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        st.error(f"⚠️ '{uploaded_file.name}' is {size_mb:.1f} MB — please upload a file under {MAX_FILE_MB} MB.")
        return False
    return True


# ============================================================
#  PDF GENERATION  (name-based access - immune to DB column order)
# ============================================================
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

    conn = get_connection()
    with dict_cursor(conn) as c:
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

    if not core_data:
        return None, None

    meta_table_data = [
        [Paragraph(f"<b>Supplier Name:</b> {core_data['supplier_name']}", cell_s), Paragraph(f"<b>Audit Date:</b> {core_data['audit_date']}", cell_s)],
        [Paragraph(f"<b>Product Supplied:</b> {core_data['product_name']}", cell_s), Paragraph(f"<b>GST No:</b> {core_data['gst_no']}", cell_s)],
        [Paragraph(f"<b>PAN No:</b> {core_data['pan_no']}", cell_s), Paragraph(f"<b>CIN / Reg No:</b> {core_data['cin_no']}", cell_s)],
        [Paragraph(f"<b>MSME Certificate:</b> {core_data['msme_cert']}", cell_s), Paragraph(f"<b>ISO Certificate:</b> {core_data['iso_cert']}", cell_s)],
        [Paragraph(f"<b>Approval Status:</b> {core_data['approval_status']}", cell_b), Paragraph(f"<b>Report Compiled:</b> {datetime.now().strftime('%d-%m-%Y')}", cell_s)]
    ]
    meta_table = Table(meta_table_data, colWidths=[281, 281])
    meta_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f7f8')), ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cfd8dc')), ('PADDING', (0, 0), (-1, -1), 8)]))
    story.append(meta_table)

    # Section 1: Core Matrix Table
    story.append(Paragraph("1. Core Compliance Evaluation Matrix (1.1 - 8.5)", sec_s))
    q_table_data = [[Paragraph("S.No", th_s), Paragraph("Checkpoints Description", th_s), Paragraph("Status", th_s), Paragraph("Auditor Remarks", th_s)]]
    for sec_name, questions in audit_points.items():
        q_table_data.append([Paragraph(f"<b>{sec_name}</b>", cell_b), "", "", ""])
        for q_num, q_text in questions.items():
            k_code = q_num.replace('.', '_')
            status_val = core_data.get(f"q_{k_code}_status") or "-"
            comment_val = core_data.get(f"q_{k_code}_comment") or "-"
            q_table_data.append([Paragraph(q_num, cell_s), Paragraph(q_text, cell_s), Paragraph(status_val, cell_s), Paragraph(comment_val, cell_s)])
    q_table = Table(q_table_data, colWidths=[35, 275, 50, 202], repeatRows=1)
    q_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), brand_red), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('PADDING', (0, 0), (-1, -1), 5)]))
    story.append(q_table)

    story.append(PageBreak())

    # Section 2: Document Table
    story.append(Paragraph("2. Document Checklist & Corporate Records Registry", sec_s))
    doc_table_data = [[Paragraph("Category", th_s), Paragraph("Document Description", th_s), Paragraph("Availability", th_s), Paragraph("Remarks Log", th_s), Paragraph("File Mapping", th_s)]]
    for row in docs_data:
        doc_table_data.append([Paragraph(row["category"], cell_s), Paragraph(row["description"], cell_s), Paragraph(row["status"], cell_s), Paragraph(row["remarks"] if row["remarks"] else "-", cell_s), Paragraph(row["file_name"] if row["file_name"] else "No File", cell_s)])
    doc_table = Table(doc_table_data, colWidths=[70, 180, 60, 130, 122], repeatRows=1)
    doc_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), brand_red), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('PADDING', (0, 0), (-1, -1), 5)]))
    story.append(doc_table)

    story.append(Spacer(1, 15))

    # Section 3: Machinery Table
    story.append(Paragraph("3. Plant Machinery Register & Structural Ledger", sec_s))
    mach_headers = ["Sr", "Description", "Unique ID", "Make/Model", "Capacity", "Specs", "Year", "Features", "Automation", "Remarks"]
    mach_table_data = [[Paragraph(h, th_s) for h in mach_headers]]
    for idx, m in enumerate(mach_data):
        mach_table_data.append([Paragraph(str(idx + 1), cell_s)] + [Paragraph(str(m[k]) if m[k] else "-", cell_s) for k in ["description", "unique_id", "make_model", "capacity", "specification", "installation_year", "features", "automation", "remarks"]])
    mach_table = Table(mach_table_data, colWidths=[20, 80, 45, 55, 45, 55, 30, 80, 75, 77], repeatRows=1)
    mach_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), brand_dark), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('PADDING', (0, 0), (-1, -1), 4)]))
    story.append(mach_table)

    story.append(Spacer(1, 15))

    # Section 4: Instruments Table
    story.append(Paragraph("4. Measuring Instruments & Metrological Testing Log", sec_s))
    inst_headers = ["Category", "Instrument Name", "Make/Model", "Test", "Range", "Accuracy", "Cal Date", "NABL", "Master Equip", "Cert No", "Remarks"]
    inst_table_data = [[Paragraph(h, th_s) for h in inst_headers]]
    for row in inst_data:
        inst_table_data.append([Paragraph(str(row[k]) if row[k] else "-", cell_s) for k in ["category", "name", "make_model", "test_name", "range", "accuracy", "cal_date", "nabl_detail", "master_equip", "certificate_no", "remarks"]])
    inst_table = Table(inst_table_data, colWidths=[48, 60, 45, 50, 35, 40, 45, 35, 55, 48, 71], repeatRows=1)
    inst_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), brand_dark), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('PADDING', (0, 0), (-1, -1), 4)]))
    story.append(inst_table)

    story.append(Spacer(1, 15))

    # Section 5: Plant Photo Registry Table
    story.append(Paragraph("5. Factory Physical Zone Image Submissions Register", sec_s))
    photo_headers = ["Target Evaluation Zone", "Uploaded Photo Custom Identify Name", "Technical Capture Remarks / Captions"]
    photo_table_data = [[Paragraph(ph, th_s) for ph in photo_headers]]
    for prow in photo_data:
        photo_table_data.append([Paragraph(prow["category_desc"], cell_s), Paragraph(prow["custom_photo_name"] if prow["custom_photo_name"] else "-", cell_s), Paragraph(prow["remarks"] if prow["remarks"] else "-", cell_s)])
    photo_table = Table(photo_table_data, colWidths=[162, 200, 200], repeatRows=1)
    photo_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), brand_dark), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cfd8dc')), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('PADDING', (0, 0), (-1, -1), 5)]))
    story.append(photo_table)

    doc.build(story)
    buffer.seek(0)
    return buffer, core_data["supplier_name"]


# ============================================================
#  PORTAL HEADER
# ============================================================
header_col1, header_col2, header_col3 = st.columns([1.5, 3.2, 2.3])
with header_col1:
    st.image(f"data:image/png;base64,{LOGO_BASE64}", use_container_width=True)
with header_col2:
    st.markdown("<h1 style='color: #E31E24; text-align: center; margin:0;'>DANISH POWER LIMITED</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color:#212121; font-weight:600; margin:0;'>Supplier Quality Enterprise Portal</p>", unsafe_allow_html=True)
with header_col3:
    st.markdown("<div style='border: 2px solid #E31E24; padding: 10px; border-radius: 6px; font-size:13px;'><b>Format No.:</b> F-12<br><b>Rev. No.:</b> 03</div>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1.5px solid #E31E24; margin-top:10px; margin-bottom:25px;'>", unsafe_allow_html=True)

# ============================================================
#  NAVIGATION
# ============================================================
st.sidebar.markdown("<h3 style='color:#E31E24; font-weight:bold;'>PORTAL ACCESS</h3>", unsafe_allow_html=True)
portal_mode = st.sidebar.radio("Switch Dashboard View", ["Supplier Gateway Form", "DPL Quality Admin View"])

# ============================================================
#  SUPPLIER GATEWAY
# ============================================================
if portal_mode == "Supplier Gateway Form":
    st.subheader("🔐 Part A: Identity Verification & Draft Vault")
    vendor_email_input = st.text_input("Enter Official Corporate Email ID to Start or Resume*", placeholder="quality@vendorcompany.com")

    vendor_email = None
    if vendor_email_input:
        if not is_valid_email(vendor_email_input):
            st.error("⚠️ Please enter a valid email address.")
        else:
            vendor_email_input = vendor_email_input.strip().lower()

            if not OTP_ENABLED:
                st.warning("⚠️ Email verification is not configured on this portal — anyone who enters this "
                           "email address can view and edit this vendor's data. Contact the administrator "
                           "to enable secure verification.")
                vendor_email = vendor_email_input
            else:
                # --- OTP verification flow ---
                if st.session_state.get("verified_email") == vendor_email_input:
                    vendor_email = vendor_email_input
                else:
                    st.info("🔑 A verification code is required to access or edit this vendor's data.")
                    if st.session_state.get("otp_target") != vendor_email_input:
                        st.session_state.otp_target = vendor_email_input
                        st.session_state.otp_code = None
                        st.session_state.otp_expiry = None

                    if st.button("📧 Send verification code"):
                        code = f"{pysecrets.randbelow(900000) + 100000}"
                        if send_otp_email(vendor_email_input, code):
                            st.session_state.otp_code = code
                            st.session_state.otp_expiry = datetime.now() + timedelta(minutes=OTP_TTL_MINUTES)
                            st.success("✅ Verification code sent. Please check the inbox.")

                    if st.session_state.get("otp_code"):
                        entered_code = st.text_input("Enter the 6-digit code sent to your email", max_chars=6)
                        if st.button("✅ Verify code"):
                            if datetime.now() > st.session_state.otp_expiry:
                                st.error("⚠️ Code expired. Please request a new one.")
                            elif entered_code == st.session_state.otp_code:
                                st.session_state.verified_email = vendor_email_input
                                st.success("✅ Verified! Loading your record...")
                                st.rerun()
                            else:
                                st.error("⚠️ Incorrect code.")

    if vendor_email:
        conn = get_connection()
        db_draft_core, db_draft_mach, db_draft_inst = None, [], []
        existing_docs, existing_photos = {}, {}

        try:
            with dict_cursor(conn) as c:
                c.execute("SELECT * FROM core_assessment WHERE supplier_email=%s", (vendor_email,))
                db_draft_core = c.fetchone()
                c.execute("SELECT description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks FROM machinery WHERE supplier_email=%s", (vendor_email,))
                db_draft_mach = c.fetchall()
                c.execute("SELECT category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks FROM instruments WHERE supplier_email=%s", (vendor_email,))
                db_draft_inst = c.fetchall()
                c.execute("SELECT description, status, remarks, file_name FROM doc_checklist WHERE supplier_email=%s", (vendor_email,))
                existing_docs = {r["description"]: {"status": r["status"], "remarks": r["remarks"], "file_name": r["file_name"]} for r in c.fetchall()}
                c.execute("SELECT category_desc, custom_photo_name, remarks, file_name FROM plant_photos WHERE supplier_email=%s", (vendor_email,))
                existing_photos = {r["category_desc"]: {"custom_name": r["custom_photo_name"], "remarks": r["remarks"], "file_name": r["file_name"]} for r in c.fetchall()}
        except Exception as e:
            st.error(f"❌ Could not load your record right now. Please try again shortly. ({e})")
            st.stop()

        if 'current_vendor' not in st.session_state or st.session_state.current_vendor != vendor_email:
            st.session_state.current_vendor = vendor_email
            st.session_state.mach_count = max(len(db_draft_mach), 1)
            st.session_state.inst_count = max(len(db_draft_inst), 1)

        if db_draft_core and db_draft_core["submission_status"] == 'SUBMITTED':
            st.success("✅ Assessment Locked: Your corporate response data matrix has been final-transmitted to Danish Power Vault.")
        else:
            if db_draft_core and db_draft_core["submission_status"] == 'DRAFT':
                st.warning("🔄 Live Active Draft Found. All technical attributes are auto-restored below.")
            else:
                st.info("🆕 System Initialized: Creating a clean empty canvas for your corporate profile.")

            st.subheader("🏢 Part B: Corporate Identity Registry")
            gcol1, gcol2, gcol3 = st.columns(3)
            with gcol1:
                s_name = st.text_input("Supplier Corporate Name*", value=db_draft_core["supplier_name"] if db_draft_core else "")
                p_name = st.text_input("Product Component Description*", value=db_draft_core["product_name"] if db_draft_core else "")
                gst_no = st.text_input("GST No.", value=db_draft_core["gst_no"] if db_draft_core and db_draft_core.get("gst_no") else "")
            with gcol2:
                pan_no = st.text_input("PAN No.", value=db_draft_core["pan_no"] if db_draft_core and db_draft_core.get("pan_no") else "")
                cin_no = st.text_input("CIN / Registration No.", value=db_draft_core["cin_no"] if db_draft_core and db_draft_core.get("cin_no") else "")
                msme_cert = st.text_input("MSME Certificate Detail", value=db_draft_core["msme_cert"] if db_draft_core and db_draft_core.get("msme_cert") else "")
            with gcol3:
                iso_cert = st.text_input("ISO Certificate No.", value=db_draft_core["iso_cert"] if db_draft_core and db_draft_core.get("iso_cert") else "")
                approval_options = ["Pending Review", "Approved", "Conditionally Approved", "Rejected"]
                app_idx = approval_options.index(db_draft_core["approval_status"]) if db_draft_core and db_draft_core.get("approval_status") in approval_options else 0
                approval_status = st.selectbox("Approval Status", approval_options, index=app_idx)
                a_date = st.date_input("Audit Compilation Date", datetime.now())

            t1, t2, t3, t4, t5 = st.tabs(["📊 1. Core Evaluation", "📎 2. Document Vault", "⚙️ 3. Machine Asset Register", "🔬 4. Metrological Records", "📸 5. Plant Photo Logs"])

            with t1:
                core_inputs = {}
                for sec_title, questions in audit_points.items():
                    st.markdown(f"<div style='background-color:#FFEBEE; padding:8px; border-left: 4px solid #E31E24; font-weight:bold; color:#B71C1C;'>{sec_title}</div>", unsafe_allow_html=True)
                    for q_num, q_text in questions.items():
                        st.markdown(f"**{q_num}** {q_text}")
                        k_code = q_num.replace('.', '_')
                        def_status = (db_draft_core.get(f"q_{k_code}_status") if db_draft_core else None) or "Yes"
                        def_comment = (db_draft_core.get(f"q_{k_code}_comment") if db_draft_core else None) or ""
                        ch1, ch2 = st.columns([1, 4])
                        with ch1:
                            status_sel = st.selectbox("Status", ["Yes", "No", "N/A"], key=f"s_{k_code}", index=["Yes", "No", "N/A"].index(def_status) if def_status in ["Yes", "No", "N/A"] else 0)
                        with ch2:
                            comment_in = st.text_input("Evidence / Remarks", key=f"c_{k_code}", value=def_comment)
                        core_inputs[f"q_{k_code}_status"] = status_sel
                        core_inputs[f"q_{k_code}_comment"] = comment_in

            with t2:
                st.markdown("#### Cloud Document Vault")
                st.caption(f"Files up to {MAX_FILE_MB} MB accepted (pdf, png, jpg).")
                doc_responses = {}
                st.markdown("##### 🔴 Mandatory Compliance Certifications")
                for idx, doc in enumerate(mandatory_docs):
                    def_d_status = existing_docs[doc]["status"] if doc in existing_docs and existing_docs[doc]["status"] else "Available"
                    def_d_rem = existing_docs[doc]["remarks"] if doc in existing_docs and existing_docs[doc]["remarks"] else ""
                    if doc in existing_docs and existing_docs[doc]["file_name"]:
                        st.caption(f"💾 *Saved Draft File:* `{existing_docs[doc]['file_name']}`")
                    dc1, dc2, dc3 = st.columns([2, 1, 2])
                    with dc1:
                        st.write(f"**{idx + 1}.** {doc}")
                    with dc2:
                        st_v = st.selectbox("Status", ["Available", "Not Available"], key=f"m_s_{idx}", index=["Available", "Not Available"].index(def_d_status))
                    with dc3:
                        fl_v = st.file_uploader("Upload", type=["pdf", "png", "jpg"], key=f"m_f_{idx}")
                        if not check_file_size(fl_v):
                            fl_v = None
                    rm_v = st.text_input("Remarks", key=f"m_r_{idx}", value=def_d_rem)
                    doc_responses[doc] = {"status": st_v, "file": fl_v, "remarks": rm_v, "cat": "Mandatory"}

                st.markdown("##### 🟡 Auxiliary System Records")
                for idx, doc in enumerate(later_docs):
                    def_l_status = existing_docs[doc]["status"] if doc in existing_docs and existing_docs[doc]["status"] else "Available"
                    def_l_rem = existing_docs[doc]["remarks"] if doc in existing_docs and existing_docs[doc]["remarks"] else ""
                    if doc in existing_docs and existing_docs[doc]["file_name"]:
                        st.caption(f"💾 *Saved Draft File:* `{existing_docs[doc]['file_name']}`")
                    dc1, dc2, dc3 = st.columns([2, 1, 2])
                    with dc1:
                        st.write(f"**{idx + 1}.** {doc}")
                    with dc2:
                        st_v = st.selectbox("Status", ["Available", "Not Available"], key=f"l_s_{idx}", index=["Available", "Not Available"].index(def_l_status))
                    with dc3:
                        fl_v = st.file_uploader("Upload", type=["pdf", "png", "jpg"], key=f"l_f_{idx}")
                        if not check_file_size(fl_v):
                            fl_v = None
                    rm_v = st.text_input("Remarks", key=f"l_r_{idx}", value=def_l_rem)
                    doc_responses[doc] = {"status": st_v, "file": fl_v, "remarks": rm_v, "cat": "Auxiliary"}

            with t3:
                st.markdown("#### Dynamic Plant Machinery Capability Ledger")
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("➕ Add Plant Machinery Row Block"):
                        st.session_state.mach_count += 1
                        st.rerun()
                with bcol2:
                    if st.session_state.mach_count > 1 and st.button("🗑️ Remove Last Machinery Row"):
                        last_idx = st.session_state.mach_count - 1
                        for prefix in ["m_ds_", "m_ui_", "m_mk_", "m_cp_", "m_sp_", "m_yr_", "m_ft_", "m_au_", "m_rm_"]:
                            st.session_state.pop(f"{prefix}{last_idx}", None)
                        st.session_state.mach_count -= 1
                        st.rerun()

                machinery_rows = []
                for m in range(st.session_state.mach_count):
                    d_desc = d_uid = d_make = d_cap = d_spec = d_year = d_feat = d_auto = d_rem = ""
                    if db_draft_mach and m < len(db_draft_mach):
                        row = db_draft_mach[m]
                        d_desc, d_uid, d_make, d_cap, d_spec, d_year, d_feat, d_auto, d_rem = (
                            row["description"], row["unique_id"], row["make_model"], row["capacity"],
                            row["specification"], row["installation_year"], row["features"], row["automation"], row["remarks"]
                        )

                    r1, r2, r3, r4 = st.columns(4)
                    with r1:
                        mc_desc = st.text_input("Machine Description", key=f"m_ds_{m}", value=d_desc)
                        mc_uid = st.text_input("Unique ID Code", key=f"m_ui_{m}", value=d_uid)
                    with r2:
                        mc_make = st.text_input("Make/Model Specs", key=f"m_mk_{m}", value=d_make)
                        mc_cap = st.text_input("Operating Capacity", key=f"m_cp_{m}", value=d_cap)
                    with r3:
                        mc_spec = st.text_input("Technical Specs", key=f"m_sp_{m}", value=d_spec)
                        mc_year = st.text_input("Installation Year", key=f"m_yr_{m}", value=d_year)
                    with r4:
                        mc_feat = st.text_input("Core Features", key=f"m_ft_{m}", value=d_feat)
                        mc_auto = st.selectbox("Automation Grade", ["Manual", "Semi-Automatic", "Fully-Automatic"], key=f"m_au_{m}", index=["Manual", "Semi-Automatic", "Fully-Automatic"].index(d_auto) if d_auto in ["Manual", "Semi-Automatic", "Fully-Automatic"] else 0)
                    mc_rem = st.text_input("Remarks Log", key=f"m_rm_{m}", value=d_rem)
                    machinery_rows.append([mc_desc, mc_uid, mc_make, mc_cap, mc_spec, mc_year, mc_feat, mc_auto, mc_rem])
                    st.markdown("---")

            with t4:
                st.markdown("#### Dynamic Metrological Traceability & Lab Register")
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("➕ Add Metrological Instrument Row"):
                        st.session_state.inst_count += 1
                        st.rerun()
                with bcol2:
                    if st.session_state.inst_count > 1 and st.button("🗑️ Remove Last Instrument Row"):
                        last_idx = st.session_state.inst_count - 1
                        for prefix in ["i_ct_", "i_nm_", "i_mm_", "i_ts_", "i_rg_", "i_ac_", "i_cd_", "i_nb_", "i_ms_", "i_cr_", "i_rm_"]:
                            st.session_state.pop(f"{prefix}{last_idx}", None)
                        st.session_state.inst_count -= 1
                        st.rerun()

                instrument_rows = []
                for r in range(st.session_state.inst_count):
                    d_cat = d_name = d_mm = d_test = d_rng = d_acc = d_cal = d_nabl = d_mst = d_cert = d_rem = ""
                    if db_draft_inst and r < len(db_draft_inst):
                        row = db_draft_inst[r]
                        d_cat, d_name, d_mm, d_test, d_rng, d_acc, d_cal, d_nabl, d_mst, d_cert, d_rem = (
                            row["category"], row["name"], row["make_model"], row["test_name"], row["range"],
                            row["accuracy"], row["cal_date"], row["nabl_detail"], row["master_equip"], row["certificate_no"], row["remarks"]
                        )

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        ins_cat = st.selectbox("Asset Category", ["Measuring Instrument", "Testing Facility"], key=f"i_ct_{r}", index=["Measuring Instrument", "Testing Facility"].index(d_cat) if d_cat in ["Measuring Instrument", "Testing Facility"] else 0)
                        ins_name = st.text_input("Instrument Name", key=f"i_nm_{r}", value=d_name)
                    with c2:
                        ins_mm = st.text_input("Make/Model No.", key=f"i_mm_{r}", value=d_mm)
                        ins_test = st.text_input("Test Performed", key=f"i_ts_{r}", value=d_test)
                    with c3:
                        ins_rng = st.text_input("Measurement Range", key=f"i_rg_{r}", value=d_rng)
                        ins_acc = st.text_input("Accuracy/Least Count", key=f"i_ac_{r}", value=d_acc)
                    with c4:
                        ins_cal = st.text_input("Last Calibration Date", key=f"i_cd_{r}", value=d_cal)
                        ins_nabl = st.selectbox("NABL Facility?", ["Yes", "No"], key=f"i_nb_{r}", index=["Yes", "No"].index(d_nabl) if d_nabl in ["Yes", "No"] else 0)
                    ins_mst = st.text_input("Master Standard Details", key=f"i_ms_{r}", value=d_mst)
                    ins_cert = st.text_input("Calibration Certificate Ref No.", key=f"i_cr_{r}", value=d_cert)
                    ins_rem = st.text_input("Remarks Log", key=f"i_rm_{r}", value=d_rem)
                    instrument_rows.append([ins_cat, ins_name, ins_mm, ins_test, ins_rng, ins_acc, ins_cal, ins_nabl, ins_mst, ins_cert, ins_rem])
                    st.markdown("---")

            with t5:
                st.markdown("#### Factory Plant Physical Environment Image Evidences")
                st.caption(f"Files up to {MAX_FILE_MB} MB accepted (jpg, png, jpeg).")
                photo_responses = []
                for idx, p_desc in enumerate(plant_photos):
                    def_p_name = existing_photos[p_desc]["custom_name"] if p_desc in existing_photos and existing_photos[p_desc]["custom_name"] else ""
                    def_p_rem = existing_photos[p_desc]["remarks"] if p_desc in existing_photos and existing_photos[p_desc]["remarks"] else ""
                    if p_desc in existing_photos and existing_photos[p_desc]["file_name"]:
                        st.caption(f"📸 *Saved Photo:* `{existing_photos[p_desc]['file_name']}`")
                    st.markdown(f"📸 **{idx + 1}. Target Metric Zone: {p_desc}**")
                    pc1, pc2 = st.columns([1, 1])
                    with pc1:
                        img_file = st.file_uploader("Upload Image Frame", type=["jpg", "png", "jpeg"], key=f"p_f_{idx}")
                        if not check_file_size(img_file):
                            img_file = None
                    with pc2:
                        photo_custom_name = st.text_input("Photo Frame Custom Name", key=f"p_n_{idx}", value=def_p_name)
                        photo_remarks = st.text_input("Technical Capture Captions", key=f"p_r_{idx}", value=def_p_rem)
                    photo_responses.append({"cat_desc": p_desc, "file": img_file, "custom_name": photo_custom_name, "remarks": photo_remarks})

            # --- SUBMISSION CONTROLS ---
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
                            if row[0]:
                                c.execute("INSERT INTO machinery (supplier_email, description, unique_id, make_model, capacity, specification, installation_year, features, automation, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [vendor_email] + row)

                        c.execute("DELETE FROM instruments WHERE supplier_email=%s", (vendor_email,))
                        for row in instrument_rows:
                            if row[1]:
                                c.execute("INSERT INTO instruments (supplier_email, category, name, make_model, test_name, range, accuracy, cal_date, nabl_detail, master_equip, certificate_no, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [vendor_email] + row)

                        for d_title, d_val in doc_responses.items():
                            c.execute("SELECT id FROM doc_checklist WHERE supplier_email=%s AND description=%s", (vendor_email, d_title))
                            exists = c.fetchone()
                            if d_val["file"]:
                                binary_data = psycopg2.Binary(d_val["file"].read())
                                f_name = d_val["file"].name
                                if exists:
                                    c.execute("UPDATE doc_checklist SET status=%s, remarks=%s, file_name=%s, file_data=%s WHERE supplier_email=%s AND description=%s", (d_val["status"], d_val["remarks"], f_name, binary_data, vendor_email, d_title))
                                else:
                                    c.execute("INSERT INTO doc_checklist (supplier_email, category, description, status, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, %s, %s)", (vendor_email, d_val["cat"], d_title, d_val["status"], d_val["remarks"], f_name, binary_data))
                            else:
                                if exists:
                                    c.execute("UPDATE doc_checklist SET status=%s, remarks=%s WHERE supplier_email=%s AND description=%s", (d_val["status"], d_val["remarks"], vendor_email, d_title))
                                else:
                                    c.execute("INSERT INTO doc_checklist (supplier_email, category, description, status, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, NULL, NULL)", (vendor_email, d_val["cat"], d_title, d_val["status"], d_val["remarks"]))

                        for photo in photo_responses:
                            c.execute("SELECT id FROM plant_photos WHERE supplier_email=%s AND category_desc=%s", (vendor_email, photo["cat_desc"]))
                            exists = c.fetchone()
                            if photo["file"]:
                                photo_binary = psycopg2.Binary(photo["file"].read())
                                f_name = photo["file"].name
                                if exists:
                                    c.execute("UPDATE plant_photos SET custom_photo_name=%s, remarks=%s, file_name=%s, file_data=%s WHERE supplier_email=%s AND category_desc=%s", (photo["custom_name"], photo["remarks"], f_name, photo_binary, vendor_email, photo["cat_desc"]))
                                else:
                                    c.execute("INSERT INTO plant_photos (supplier_email, category_desc, custom_photo_name, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, %s, %s)", (vendor_email, photo["cat_desc"], photo["custom_name"], photo["remarks"], f_name, photo_binary))
                            else:
                                if exists:
                                    c.execute("UPDATE plant_photos SET custom_photo_name=%s, remarks=%s WHERE supplier_email=%s AND category_desc=%s", (photo["custom_name"], photo["remarks"], vendor_email, photo["cat_desc"]))
                                else:
                                    c.execute("INSERT INTO plant_photos (supplier_email, category_desc, custom_photo_name, remarks, file_name, file_data) VALUES (%s, %s, %s, %s, NULL, NULL)", (vendor_email, photo["cat_desc"], photo["custom_name"], photo["remarks"]))
                    conn.commit()
                    return True
                except Exception as db_err:
                    conn.rollback()
                    st.error(f"⚠️ Production Gatekeeper Halt: Transaction rolled back safely to prevent corruption. Reason: {str(db_err)}")
                    return False

            with scol1:
                if st.button("💾 SAVE AS DRAFT", use_container_width=True):
                    if not s_name:
                        st.error("Validation Error: Supplier Corporate Name is required to commit a draft.")
                    else:
                        if commit_to_postgresql('DRAFT'):
                            st.success("💾 State Transmitted: Partial draft snapshot locked inside cloud database.")

            with scol2:
                if st.button("🚀 FINAL COMPLETED SUBMIT TO DANISH POWER", use_container_width=True):
                    if not s_name or not p_name:
                        st.error("Validation Error: Corporate Registry data items are strictly required.")
                    else:
                        if commit_to_postgresql('SUBMITTED'):
                            st.success("🚀 Success! Compliance response locked down.")
                            st.balloons()

# ============================================================
#  ADMIN VIEW
# ============================================================
elif portal_mode == "DPL Quality Admin View":
    st.markdown("## 🛡️ Quality Assurance Verification Vault")

    if "admin_attempts" not in st.session_state:
        st.session_state.admin_attempts = 0
    if "admin_verified" not in st.session_state:
        st.session_state.admin_verified = False

    if st.session_state.admin_attempts >= MAX_ADMIN_ATTEMPTS and not st.session_state.admin_verified:
        st.error("🔒 Too many incorrect attempts. Please refresh the page and try again later.")
    elif st.session_state.admin_verified:
        logout_col1, logout_col2 = st.columns([5, 1])
        with logout_col1:
            st.success("🔑 Authorization Confirmed.")
        with logout_col2:
            if st.button("🔒 Logout"):
                st.session_state.admin_verified = False
                st.session_state.admin_attempts = 0
                st.rerun()
        conn = get_connection()
        try:
            with dict_cursor(conn) as c:
                c.execute("SELECT id, supplier_email, supplier_name, product_name, submission_status FROM core_assessment ORDER BY id DESC")
                records = c.fetchall()
        except Exception as e:
            st.error(f"❌ Could not load vendor records. ({e})")
            records = []

        if not records:
            st.warning("No vendor records currently populate relational tables.")
        else:
            lookup_options = [f"ID: {r['id']} | Name: {r['supplier_name']} ({r['supplier_email']}) | State: {r['submission_status']}" for r in records]
            target_selection = st.selectbox("Choose a Vendor Data Matrix Record for Analysis", lookup_options)
            selected_email = [r["supplier_email"] for r in records if f"ID: {r['id']}" in target_selection][0]
            st.markdown("---")
            if st.button("📄 EXECUTE AND BUILD BRANDED OFFICIAL COMPLIANCE PDF REPORT", use_container_width=True):
                with st.spinner("Compiling structural entities into PDF layout..."):
                    pdf_stream, resolved_name = generate_master_pdf(selected_email)
                    if pdf_stream:
                        st.download_button(label=f"📥 DOWNLOAD OFFICIAL BRANDED AUDIT REPORT FOR {resolved_name.upper()}", data=pdf_stream, file_name=f"DPL_Audit_Report_{resolved_name.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
                    else:
                        st.error("Compilation Fault: Empty or mismatched structure matrices encountered.")
    else:
        # Uses a form + submit button so the password is only checked once,
        # on submit - NOT on every keystroke (which previously could exhaust
        # the attempt limit while the correct password was still being typed).
        with st.form("admin_login_form", clear_on_submit=False):
            admin_token = st.text_input("Enter Enterprise Operational Security Access Token", type="password")
            submitted = st.form_submit_button("🔓 Verify Access Token")
        if submitted:
            correct_password = st.secrets.get("admin", {}).get("password", None)
            if admin_token and correct_password and pysecrets.compare_digest(admin_token, correct_password):
                st.session_state.admin_verified = True
                st.rerun()
            else:
                st.session_state.admin_attempts += 1
                st.error("Security Halt: Signature validation profile failed.")
