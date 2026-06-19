import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from database import get_user_state, get_flashcard_state, save_flashcard_state
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

fc_state = get_flashcard_state(st.session_state.user_id)
if fc_state and fc_state.get("algo_name") == algo_name:
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = fc_state["cards_data"]
        st.session_state.flashcard_algo = algo_name
        st.session_state.card_idx = fc_state["card_idx"]
        st.session_state.flash_stats = fc_state["stats"]

display_name = algo_name[:37] + "..." if len(algo_name) > 40 else algo_name

st.markdown(f"### :material/style: Active-Recall Deck: {display_name}")

# CRITICAL FIX: explicit `display: block` on the back of the card forces text to the top!
st.html("""
<style>
.flip-card { display: block; background-color: transparent; width: 100%; height: 280px; perspective: 1000px; margin-bottom: 20px; cursor: pointer; user-select: none; -webkit-tap-highlight-color: transparent; }
.flip-card input[type="checkbox"] { display: none; }
.flip-card-inner { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.5s cubic-bezier(0.4, 0.2, 0.2, 1); transform-style: preserve-3d; }
.flip-card input[type="checkbox"]:checked ~ .flip-card-inner { transform: rotateY(180deg); }
.flip-card-front, .flip-card-back { 
    position: absolute; width: 100%; height: 100%; -webkit-backface-visibility: hidden; backface-visibility: hidden; 
    border-radius: 12px; border: 2px solid #00FFAA; box-sizing: border-box; overflow-y: auto; 
}

.flip-card-front { 
    background-color: #161B22; color: #E6EDF3; font-size: 1.2rem; font-weight: bold; 
    display: flex; align-items: center; justify-content: center; text-align: center; padding: 25px;
}
.flip-card-back { 
    background-color: #00FFAA; color: #0D1117; transform: rotateY(180deg); 
    font-size: 1.1rem; line-height: 1.6; 
    display: block; text-align: left; padding: 25px; 
}
</style>
""")

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
                const rgb = bgColor.match(/\d+/g);
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
                        .flip-card-front { background-color: #F0F2F6 !important; color: #31333F !important; border-color: #FF007F !important; }
                        .flip-card-back { background-color: #FF007F !important; color: #FFFFFF !important; border-color: #FF007F !important; }
                    `;
                } else {
                    styleEl.innerHTML = ''; 
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
            save_flashcard_state(st.session_state.user_id, algo_name, st.session_state.flashcards, st.session_state.flash_stats, 0)
            st.rerun()

if st.session_state.get("flashcards"):
    cards = st.session_state.flashcards
    idx = st.session_state.card_idx
    
    if idx >= len(cards):
        st.success("Assessment completed successfully!", icon=":material/celebration:")
        
        st.markdown("#### :material/analytics: Session Performance Report")
        stats = st.session_state.flash_stats
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Hard Ratings", stats["Hard"])
        c2.metric("Good Ratings", stats["Good"])
        c3.metric("Easy Ratings", stats["Easy"])
        
        df = pd.DataFrame({"Rating": list(stats.keys()), "Count": list(stats.values())})
        fig = px.pie(df, values='Count', names='Rating', color='Rating', 
                     color_discrete_map={"Hard": "#ff4b4b", "Good": "#0099ff", "Easy": "#00FFAA"},
                     hole=0.4)
        
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch')
        
        if st.button("Restart Deck", icon=":material/restart_alt:", type="primary", width='stretch'):
            st.session_state.card_idx = 0
            st.session_state.flash_stats = {"Hard": 0, "Good": 0, "Easy": 0}
            save_flashcard_state(st.session_state.user_id, algo_name, st.session_state.flashcards, st.session_state.flash_stats, 0)
            st.rerun()
    else:
        st.progress((idx) / len(cards), text=f"Card {idx+1} of {len(cards)}")
        st.caption(":material/touch_app: *(Tap the card to reveal the technical explanation)*")
        
        card = cards[idx]
        card_html = f"""
        <label class="flip-card">
            <input type="checkbox">
            <div class="flip-card-inner">
                <div class="flip-card-front"><div>Q: {card.get('front', 'Question')}</div></div>
                <div class="flip-card-back"><div>{card.get('back', 'Answer')}</div></div>
            </div>
        </label>
        """
        st.html(card_html)
        
        c1, c2, c3 = st.columns(3)
        if c1.button("Hard :material/sentiment_dissatisfied:", width='stretch'):
            st.session_state.flash_stats["Hard"] += 1
            st.session_state.card_idx += 1
            save_flashcard_state(st.session_state.user_id, algo_name, st.session_state.flashcards, st.session_state.flash_stats, st.session_state.card_idx)
            st.rerun()
        if c2.button("Good :material/sentiment_satisfied:", width='stretch'):
            st.session_state.flash_stats["Good"] += 1
            st.session_state.card_idx += 1
            save_flashcard_state(st.session_state.user_id, algo_name, st.session_state.flashcards, st.session_state.flash_stats, st.session_state.card_idx)
            st.rerun()
        if c3.button("Easy :material/sentiment_very_satisfied:", width='stretch'):
            st.session_state.flash_stats["Easy"] += 1
            st.session_state.card_idx += 1
            save_flashcard_state(st.session_state.user_id, algo_name, st.session_state.flashcards, st.session_state.flash_stats, st.session_state.card_idx)
            st.rerun()