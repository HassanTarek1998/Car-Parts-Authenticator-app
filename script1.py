import streamlit as st
import re
from pyairtable import Api
from datetime import datetime
#change website name and icon
st.set_page_config(
    page_title="HTA Car Part Authenticator",
    page_icon="🚗"
)
st.markdown("""
<style>
/* Hide default Streamlit header */
header[data-testid="stHeader"] {
    background: none;
}

/* Custom navbar */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 65px;
    background-color: #191970;
    display: flex;
    align-items: center;
    padding-left: 20px;
    color: white;
    font-size: 20px;
    font-weight: 600;
    z-index: 9999;
    border-bottom: 2px solid rgba(0,212,255,0.6);
}
</style>

<div class="navbar" style="padding-left: 5%;">HTA Car Part Authenticator</div>
""", unsafe_allow_html=True)

#make top header transparent
st.markdown("""
<style>
/* Make the top header fully transparent */
header[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
    box-shadow: none !important;
}

/* Do NOT hide the inner div — keep sidebar toggle visible */
</style>
""", unsafe_allow_html=True)


#CHNAGE THE BACKGROUND OF all notification boxs
st.markdown("""
                    <style>
                        /* Target all info box containers */
                        div[data-testid="stNotification"],
                        div.stAlert,
                        div[data-baseweb="notification"] {
                            background-color: rgba(0, 20, 60, 0.85) !important; /* Dark navy, 85% opacity */
                            color: #ffffff !important; /* White text */
                            border-left: 4px solid rgba(0, 212, 255, 1) !important; /* Cyan accent */
                            padding: 12px 16px !important;
                            border-radius: 6px !important;
                        }
                    </style>
                """, unsafe_allow_html=True)
#change the top header background
st.markdown("""
    <style>
        header[data-testid="stHeader"] {
            background-color: #191970;
        }
    </style>
""", unsafe_allow_html=True)

#change the main background
st.markdown("""
    <style>
        .stApp {
           background: #020024;
background: linear-gradient(268deg, rgba(2, 0, 36, 1) 0%, rgba(9, 9, 121, 1) 35%, rgba(0, 212, 255, 1) 100%);
        }
    </style>
""", unsafe_allow_html=True)
#change the sidebar background
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #191970;
        }
    </style>
""", unsafe_allow_html=True)
# 1. Get the username from secrets
kofi_user = st.secrets["kofi"]
# Replace 'your_username' with your actual Ko-fi handle
kofi_button_html = f"""
<div style="display: flex; justify-content: center;">
    <a href='https://ko-fi.com/{kofi_user}' target='_blank'>
        <img height='36' style='border:0px;height:36px;' 
             src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' 
             border='0' alt='Buy Me a Coffee at ko-fi.com' />
    </a>
</div>
"""
def show_affiliates(table):
    st.sidebar.markdown("### 🛠️ Trusted Parts Sellers")
    st.sidebar.write("Avoid fakes by buying from verified retailers:")

    # Fetch records from your new 'Sponsors' table
    sponsors = table.all()

    for sponsor in sponsors:
        fields = sponsor['fields']
        name = fields.get('Sponsor Name')
        link = fields.get('Affiliate Link')
        code = fields.get('Discount Code', 'No code needed')

        # Displaying a neat card for each sponsor
        with st.sidebar.expander(f"Shop at {name}"):
            st.write(f"**Promo:** {code}")
            st.link_button(f"Visit {name} ↗️", link, use_container_width=True)

# 1. Airtable Configuration (Enter your IDs here)
TOKEN = st.secrets["AIRTABLE_TOKEN"]
BASE_ID = st.secrets["BASE_ID"]
TABLE_NAME = st.secrets["PartsTABLE"]

# 2. Connect to Airtable
api = Api(TOKEN)
table = api.table(BASE_ID, TABLE_NAME)
linkTable = api.table(BASE_ID, st.secrets["LinksTABLE"])
SponsorTable = api.table(BASE_ID, st.secrets["SponsorTABLE"])
# 3. The Web Interface
st.header("Stop Counterfeits. Drive with Confidence.")
st.subheader("The Smart Part Verifier uses official OEM data and Manufacturer analysis to ensure your car parts are 100% genuine before they ever touch your engine.")
st.write("Enter the details below to check if your part is genuine.")
# This injects the floating bubble into the page
st.markdown(kofi_button_html, unsafe_allow_html=True)
# 2.3 call Sponsor function
show_affiliates(SponsorTable)
#list the manufacturers from airtable
records=table.all()
manufacturers = sorted(
    {
        record["fields"].get("Manufacturer")
        for record in records
        if "Manufacturer" in record["fields"]
    }
)
brand = st.selectbox("Select Manufacturer", manufacturers)
serial = st.text_input("Enter Part Number")

if st.button("Verify Part"):
    if serial:
        # Fetch data from your Airtable
        records = table.all()
        found = False

        for record in records:
            fields = record['fields']
            if fields.get('Manufacturer') == brand:
                found = True
                pattern = fields.get('Official Serial Format')

                # Use Regex to check the format
                if re.match(pattern, serial):
                    st.success(f"✅ The format for {brand} is correct!")
                    st.info("Visual Tip: Genuine parts often have holograms, unique serial numbers, or scannable QR codes.")
                    st.info("Visual Tip: OEM Part Number Stamped, engraved, or molded directly onto the part")
                else:
                    st.error(f"❌ Fake detected: {brand} part number do not follow this format.")
                    st.error("⚠️ This part appears to be COUNTERFEIT.")
                    st.warning(
                            "Running fake parts can damage your engine. Buy a genuine replacement from our verified partner:")
                    st.link_button("View Genuine Part on FCP Euro", "https://www.fcpeuro.com/")

        if not found:
            st.warning("Manufacturer not found in database.")
    else:
        st.error("⚠️ Enter the part number")
# 3.1 Fetch records
records = linkTable.all()

# 3.1.2 Display as buttons
st.subheader("Official Links")
for record in records:
    fields = record['fields']
    name = fields.get('Manufacturer')
    url = fields.get('Website')  # Ensure this column exists in Airtable

    if name and url:
        st.link_button(f"Verify {name}", url, use_container_width=True)
# This injects the floating bubble into the sidebar
st.sidebar.markdown(kofi_button_html, unsafe_allow_html=True)

# The Footer Container
footer = st.container()
with footer:
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"© {datetime.now().year} Hassan Tarek Abdelhamid | All Rights Reserved")
    with col2:
        # You can put your Ko-fi link here too!
        st.write(f"[Contact](mailto:{st.secrets['Email']})")
