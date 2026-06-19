import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_user_state
from utils.ai_engine import generate_flashcards

st.set_page_config(page_title="Active Flashcards", layout="centered")

if not st.session_state.get("user_id"):
    st.warning("Authentication Required: Please configure your profile first.", icon=":material/lock:")
    st.stop()

saved_state = get_user_state(st.session_state.user_id)
if not saved_state or not saved_state.get("algo_name"):
    st.warning("No context loaded. Please compile a code block or algorithm on the Analysis page first!", icon=":material/search:")
    st.stop()

algo_name = saved_state["algo_name"]
algo_context = saved_state["ai_data"].get("explanation", algo_name)

display_name = algo_name[:37] + "..." if len(algo_name) > 40 else algo_name

st.markdown(f"### :material/style: Active-Recall Deck: :green[{display_name}]")

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

if "flashcards" not in st.session_state or st.session_state.get("flashcard_algo") != algo_name:
    if st.button("Generate Contextual Flashcard Deck", type="primary", width='stretch'):
        with st.spinner("Analyzing architectural logic and synthesizing active-recall assessments..."):
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
        st.success("🎉 Assessment completed successfully!", icon=":material/celebration:")
        
        st.markdown("#### :material/analytics: Session Performance Analytics")
        stats = st.session_state.flash_stats
        
        c1, c2, c3 = st.columns(3)
        c1.metric("High Difficulty Retentions", stats["Hard"])
        c2.metric("Standard Retentions", stats["Good"])
        c3.metric("Effortless Retentions", stats["Easy"])
        
        df = pd.DataFrame({"Rating": list(stats.keys()), "Count": list(stats.values())})
        fig = px.pie(df, values='Count', names='Rating', color='Rating', 
                     color_discrete_map={"Hard": "#ff4b4b", "Good": "#0099ff", "Easy": "#00FFAA"},
                     template="plotly_dark", hole=0.4)
        st.plotly_chart(fig, width='stretch')
        
        if st.button("Restart Active Recall Deck", icon=":material/restart_alt:", type="primary", width='stretch'):
            st.session_state.card_idx = 0
            st.session_state.flash_stats = {"Hard": 0, "Good": 0, "Easy": 0}
            st.rerun()
    else:
        st.progress((idx) / len(cards), text=f"Evaluating Card {idx+1} of {len(cards)}")
        st.caption("*(Press and hold the card to reveal the technical explanation)*")
        
        card = cards[idx]
        card_html = f"""
        <div class="flip-card"><div class="flip-card-inner">
            <div class="flip-card-front">Query: {card.get('front', 'Question')}</div>
            <div class="flip-card-back">{card.get('back', 'Answer')}</div>
        </div></div>
        """
        st.html(card_html)
        
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