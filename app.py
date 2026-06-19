import streamlit as st
import uuid
from database import init_db, save_user_data, get_user_data

st.set_page_config(page_title="Profile - Algorithmic Mind-Mapper", layout="wide")

init_db()

st.html("""
<style>
[data-testid="stMarkdownContainer"] table {
    display: block !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
}
</style>
""")

query_params = st.query_params
if "user_id" in query_params:
    st.session_state.user_id = query_params["user_id"]
    db_data = get_user_data(st.session_state.user_id)
    if db_data:
        st.session_state.profile_name = db_data["user_name"]
        st.session_state.api_key = db_data["api_key"]
elif "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
    st.session_state.profile_name = ""
    st.session_state.api_key = ""

st.markdown("### :material/account_circle: Engineer Profile & Settings")
st.markdown("**Algorithmic Mind-Mapper & Code-to-Flowchart Tracker** utilizes Google's Gemini API to generate intelligent, interactive algorithmic traces and architectural blueprints.")
st.info("Your API Key is securely encrypted locally and strictly tied to your unique Workspace ID.", icon=":material/lock:")

with st.container(border=True):
    name = st.text_input("Lead Engineer Name", value=st.session_state.get('profile_name', ''), placeholder="e.g., Alex Developer")
    api_key = st.text_input("Google Gemini API Key", type="password", value=st.session_state.get('api_key', ''), placeholder="AIzaSy...")

    if st.button("Save Workspace Configuration", type="primary", icon=":material/key:", width='stretch'):
        st.session_state.profile_name = name
        st.session_state.api_key = api_key
        save_user_data(st.session_state.user_id, name, api_key)
        st.success("Credentials secured! Proceed to the Algorithm Analysis tab to begin tracking.", icon=":material/check_circle:")

st.markdown("---")
st.subheader(":material/bookmark: Your Persistent Access Link")
st.info("Bookmark this exact URL. It will instantly restore your profile, API keys, and your last active execution trace across any device without a login portal:", icon=":material/info:")

# Production URL matched to your deployed application space
current_url = "https://algorithmicmindmappergit-h6bhwlhiqz5frnpksslcea.streamlit.app" 
personal_link = f"{current_url}/?user_id={st.session_state.user_id}"

st.code(personal_link, language="text")

st.markdown("---")
st.subheader(":material/delete: Storage Management")
st.warning("Executing a data reset will permanently purge your stored configurations and trace history from this environment.", icon=":material/warning:")
if st.button("Purge Local Data", icon=":material/restart_alt:"):
    save_user_data(st.session_state.user_id, "", "")
    from database import save_user_state
    save_user_state(st.session_state.user_id, "", {}, [])
    st.session_state.profile_name = ""
    st.session_state.api_key = ""
    st.success("Workspace environment successfully purged.", icon=":material/check:")