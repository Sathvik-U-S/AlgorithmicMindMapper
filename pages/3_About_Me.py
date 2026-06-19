import streamlit as st

st.set_page_config(
    page_title="About Sathvik",
    page_icon=":material/person:",
    layout="wide"
)

# --- DYNAMIC THEME ENGINE ---
st.html("""
<style>
    .glass {
        background: rgba(128, 128, 128, 0.08);
        backdrop-filter: blur(16px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(128, 128, 128, 0.15);
        font-size: 1.1rem;
        line-height: 1.8;
        transition: all 0.3s ease;
    }

    .glass ul { margin: 0; padding-left: 25px; }
    .glass li { margin-bottom: 12px; }
    .glass li::marker { color: #00FFAA; transition: color 0.3s ease; }
</style>

<script>
    function syncPageTheme() {
        try {
            const parentDoc = window.parent.document;
            const appDiv = parentDoc.querySelector('.stApp');
            if (!appDiv) return;
            
            const bgColor = window.parent.getComputedStyle(appDiv).backgroundColor;
            const rgb = bgColor.match(/\\d+/g);
            if (!rgb) return;
            
            const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
            const isLight = brightness > 128;
            
            let styleEl = parentDoc.getElementById('about-theme-sync-style');
            if (!styleEl) {
                styleEl = parentDoc.createElement('style');
                styleEl.id = 'about-theme-sync-style';
                parentDoc.head.appendChild(styleEl);
            }
            
            if (isLight) {
                styleEl.innerHTML = `
                    .glass { background: #F0F2F6 !important; border-color: #E0E2E6 !important; color: #31333F !important; }
                    .glass li::marker { color: #FF007F !important; } /* Fun Pink for Light Mode */
                `;
            } else {
                styleEl.innerHTML = '';
            }
        } catch (e) {}
    }
    syncPageTheme();
    setInterval(syncPageTheme, 1000);
</script>
""")

col1, col2 = st.columns([1, 2])

with col1:
    st.image(
        "https://api.dicebear.com/7.x/initials/svg?seed=Sathvik&backgroundColor=00FFAA",
        width=220
    )

with col2:
    st.markdown("## :material/person: Sathvik U S")
    st.markdown("### AIML Student | BS Data Science @ IIT Madras")

    st.markdown("""
    <div class='glass'>
        <ul>
            <li><b>B.E. in Artificial Intelligence & Machine Learning</b> — JNNCE, Shivamogga</li>
            <li><b>B.S. in Data Science & Applications</b> — IIT Madras</li>
            <li><b>Interests:</b> Artificial Intelligence, Machine Learning, Data Science, Software Engineering</li>
            <li><b>Strengths:</b> Problem Solving, Data Structures & Algorithms, Complexity Analysis</li>
            <li><b>Core Skills:</b> Python, SQL, Flask, Streamlit, Web Development</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.header("Connect & Collaborate", divider="green", anchor=False)

colA, colB = st.columns(2)

with colA:
    st.link_button(
        ":material/code: GitHub Space",
        "https://github.com/sathvikus",
        width='stretch'
    )

with colB:
    st.link_button(
        ":material/work: LinkedIn Network",
        "https://linkedin.com/in/sathvik-u-s",
        width='stretch'
    )

st.divider()

st.info(
    "Open to AI, ML, Data Science, and Full-Stack internship opportunities and technical project collaborations.",
    icon=":material/lightbulb:"
)