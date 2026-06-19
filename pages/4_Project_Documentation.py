import streamlit as st

st.set_page_config(
    page_title="Project Documentation",
    page_icon=":material/description:",
    layout="wide"
)

# --- DYNAMIC THEME ENGINE ---
st.html("""
<style>
    .hero {
        padding: 34px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(0,255,170,0.12), rgba(88,166,255,0.08));
        border: 1px solid rgba(0,255,170,0.18);
        margin-bottom: 25px;
        transition: all 0.3s ease;
    }

    .card {
        background: rgba(128,128,128,0.08);
        backdrop-filter: blur(18px);
        padding: 26px;
        border-radius: 20px;
        border: 1px solid rgba(0,255,170,0.15);
        margin-bottom: 18px;
        transition: all 0.3s ease;
    }

    .feature {
        padding: 20px;
        border-radius: 16px;
        border-left: 4px solid #00FFAA;
        background: rgba(128,128,128,0.05);
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
</style>

<script>
    function syncDocsTheme() {
        try {
            const parentDoc = window.parent.document;
            const appDiv = parentDoc.querySelector('.stApp');
            if (!appDiv) return;
            
            const bgColor = window.parent.getComputedStyle(appDiv).backgroundColor;
            const rgb = bgColor.match(/\\d+/g);
            if (!rgb) return;
            
            const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
            const isLight = brightness > 128;
            
            let styleEl = parentDoc.getElementById('docs-theme-sync-style');
            if (!styleEl) {
                styleEl = parentDoc.createElement('style');
                styleEl.id = 'docs-theme-sync-style';
                parentDoc.head.appendChild(styleEl);
            }
            
            if (isLight) {
                // Instantly flips all custom UI to clean Streamlit Light-Mode colors
                styleEl.innerHTML = `
                    .hero { background: linear-gradient(135deg, #E0E2E6, #F0F2F6) !important; border-color: #D0D2D6 !important; color: #31333F !important; }
                    .hero h1, .hero p { color: #31333F !important; }
                    .card, .feature { background: #F0F2F6 !important; border-color: #D0D2D6 !important; color: #31333F !important; }
                    .card h4, .feature h4 { color: #31333F !important; }
                    .feature { border-left: 4px solid #FF007F !important; } /* Pink Accent for Light Mode Features */
                `;
            } else {
                styleEl.innerHTML = ''; // Restores Cyber-Dark Default
            }
        } catch (e) {}
    }
    syncDocsTheme();
    setInterval(syncDocsTheme, 1000);
</script>
""")

# --- DOCUMENTATION CONTENT ---
st.markdown("""
<div class='hero'>
<h1 style='margin-top:0;'>Algorithmic Mind-Mapper & Code-to-Flowchart Tracker </h1>
<p style='font-size:1.1rem; margin-bottom:0;'>
A highly interactive, AI-driven educational tool designed to demystify Data Structures and Algorithms. By leveraging the Gemini AI API, this tool intercepts raw Python code or algorithm names and automatically compiles architectural Graphviz blueprints, execution trace tables, space-time matrices, and recursive memory call stacks.
</p>
</div>
""", unsafe_allow_html=True)

st.header("Features", divider="green")

features = [
    ("", "Dynamic Graphviz Generation", "Translates complex code logic into instantly readable Flowcharts and Trace Matrices."),
    ("", "Cyber-Dark & Light Mode Integration", "UI actively detects Streamlit themes and applies robust CSS modifications."),
    ("", "Interactive Stack Inspector", "Step through recursive calls horizontally frame-by-frame."),
    ("", "PDF Report Generator", "Compiles your session into a beautifully formatted HTML document optimized perfectly for static PDF A4 printing."),
    ("", "Active Recall Deck", "Instantly converts the synthesized logic into a 3D-CSS Flashcard system for studying.")
]

for icon, title, desc in features:
    st.markdown(f"""
    <div class='feature'>
    <h4 style='margin:0;'>{icon} {title}</h4>
    <p style='margin: 5px 0 0 0;'>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

st.header("Tech Stack", divider="green")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='card'>
    <h4 style='margin-top:0;'> Frontend Components</h4>
    <ul>
        <li><b>Streamlit</b> (UI Framework)</li>
        <li><b>D3-Graphviz</b> (Browser-Native Rendering)</li>
        <li><b>Plotly Express</b> (Trade-off Matrices)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='card'>
    <h4 style='margin-top:0;'> Backend & Data</h4>
    <ul>
        <li><b>Google GenAI</b> (<code>gemini-2.5-flash</code>)</li>
        <li><b>SQLite3</b> (Data Persistence & Caching)</li>
        <li><b>Kroki API</b> (PDF Image Compilation)</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.header("Installation", divider="green")

st.markdown("""
<div class='card'>
<ol style='margin-bottom:0;'>
<li>Clone the repository to your local machine.</li>
<li>Install requirements: <code>pip install -r requirements.txt</code></li>
<li>Launch the app: <code>streamlit run app.py</code></li>
<li>Enter your Gemini API Key directly in the UI Configuration tab.</li>
</ol>
</div>
""", unsafe_allow_html=True)