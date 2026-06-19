import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from database import get_user_state
from utils.ai_engine import generate_flashcards

st.set_page_config(page_title="Active Flashcards", layout="centered")

if not st.session_state.get("user_id"):
    st.warning("Please configure your profile first.", icon=":material/lock:")
    st.stop()

saved_state = get_user_state(st.session_state.user_id)
if not saved_state or not saved_state.get("algo_name"):
    st.warning("No algorithm loaded. Compile an algorithm on the Analysis page first!", icon=":material/search:")
    st.stop()

algo_name = saved_state["algo_name"]
algo_context = saved_state["ai_data"].get("explanation", algo_name)

# Truncate long code blocks for the UI Display
display_name = algo_name[:37] + "..." if len(algo_name) > 40 else algo_name

st.markdown(f"### :material/style: Active-Recall Deck: :green[{display_name}]")

# 1. Base CSS (Cyber-Dark Default)
st.html("""
<style>
.flip-card { background-color: transparent; width: 100%; height: 250px; perspective: 1000px; margin-bottom: 20px; cursor: pointer; }
.flip-card-inner { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.6s; transform-style: preserve-3d; }
.flip-card:active .flip-card-inner { transform: rotateY(180deg); }
.flip-card-front, .flip-card-back { position: absolute; width: 100%; height: 100%; -webkit-backface-visibility: hidden; backface-visibility: hidden; display: flex; align-items: center; justify-content: center; padding: 20px; border-radius: 12px; border: 2px solid #00FFAA; box-sizing: border-box; }
.flip-card-front { background-color: #161B22; color: #E6EDF3; font-size: 1.2rem; font-weight: bold; }
.flip-card-back { background-color: #00FFAA; color: #0D1117; transform: rotateY(180deg); font-size: 1.1rem; line-height: 1.5; overflow-y: auto; }
</style>
""")

# 2. Dynamic Theme Watcher (Uses the exact same working logic as your Flowcharts)
js_code = """
<script>
    (function() {
        function syncFlashcardTheme() {
            try {
                const parentDoc = window.parent.document;
                if (!parentDoc) return;
                
                const appDiv = parentDoc.querySelector('.stApp') || parentDoc.body;
                if (!appDiv) return;
                
                const bgColor = window.parent.getComputedStyle(appDiv).backgroundColor;
                const rgb = bgColor.match(/\\d+/g);
                if (!rgb) return;
                
                const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
                const isLight = brightness > 128;
                
                let styleEl = parentDoc.getElementById('flashcard-theme-sync-style');
                if (!styleEl) {
                    styleEl = parentDoc.createElement('style');
                    styleEl.id = 'flashcard-theme-sync-style';
                    parentDoc.head.appendChild(styleEl);
                }
                
                if (isLight) {
                    styleEl.innerHTML = `
                        /* Flip to Light Mode styling with Pink accents */
                        .flip-card-front { background-color: #F0F2F6 !important; color: #31333F !important; border-color: #FF007F !important; }
                        .flip-card-back { background-color: #FF007F !important; color: #FFFFFF !important; border-color: #FF007F !important; }
                    `;
                } else {
                    styleEl.innerHTML = ''; // Restores default Cyber-Dark
                }
            } catch (e) {}
        }
        syncFlashcardTheme();
        setInterval(syncFlashcardTheme, 500);
    })();
</script>
"""
components.html(js_code, height=0, width=0)

if "flashcards" not in st.session_state or st.session_state.get("flashcard_algo") != algo_name:
    if st.button("Generate Flashcard Deck", type="primary", width='stretch'):
        with st.spinner("Analyzing context and generating active-recall questions..."):
            cards_data = generate_flashcards(algo_context, st.session_state.api_key)
            st.session_state.flashcards = cards_data.get("cards", [])
            st.session_state.flashcard_algo = algo_name
            st.session_state.card_idx = 0
            st.session_state.flash_stats = {"Hard": 0, "Good": 0, "Easy": 0}
            st.rerun()

if st.session_state.get("flashcards"):
    cards = st.session_state.flashcards
    idx = st.session_state.card_idx
    
    if idx >= len(cards):
        st.balloons()
        st.success("🎉 You've completed the deck!", icon=":material/celebration:")
        
        # --- FLASHCARD SESSION ANALYTICS REPORT ---
        st.markdown("#### :material/analytics: Session Performance Report")
        stats = st.session_state.flash_stats
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Hard Ratings", stats["Hard"])
        c2.metric("Good Ratings", stats["Good"])
        c3.metric("Easy Ratings", stats["Easy"])
        
        df = pd.DataFrame({"Rating": list(stats.keys()), "Count": list(stats.values())})
        
        # REMOVED template="plotly_dark" so Streamlit natively auto-themes the font colors!
        fig = px.pie(df, values='Count', names='Rating', color='Rating', 
                     color_discrete_map={"Hard": "#ff4b4b", "Good": "#0099ff", "Easy": "#00FFAA"},
                     hole=0.4)
        
        # Enforce transparent backgrounds so it never clashes with the UI 
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch')
        
        if st.button("Restart Deck", icon=":material/restart_alt:", type="primary", width='stretch'):
            st.session_state.card_idx = 0
            st.session_state.flash_stats = {"Hard": 0, "Good": 0, "Easy": 0}
            st.rerun()
    else:
        st.progress((idx) / len(cards), text=f"Card {idx+1} of {len(cards)}")
        st.markdown("*(Click and hold a card to reveal the answer)*")
        
        card = cards[idx]
        card_html = f"""
        <div class="flip-card"><div class="flip-card-inner">
            <div class="flip-card-front">Q: {card.get('front', 'Question')}</div>
            <div class="flip-card-back">{card.get('back', 'Answer')}</div>
        </div></div>
        """
        st.html(card_html)
        
        # Record Stats and Advance
        c1, c2, c3 = st.columns(3)
        if c1.button("Hard :material/sentiment_dissatisfied:", width='stretch'):
            st.session_state.flash_stats["Hard"] += 1
            st.session_state.card_idx += 1
            st.rerun()
        if c2.button("Good :material/sentiment_satisfied:", width='stretch'):
            st.session_state.flash_stats["Good"] += 1
            st.session_state.card_idx += 1
            st.rerun()
        if c3.button("Easy :material/sentiment_very_satisfied:", width='stretch'):
            st.session_state.flash_stats["Easy"] += 1
            st.session_state.card_idx += 1
            st.rerun()