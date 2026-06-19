import streamlit as st
import pandas as pd
import plotly.express as px
from graphviz import Digraph
from utils.ai_engine import analyze_algorithm, answer_followup
from utils.graph_renderer import render_graphviz, render_raw_dot, inject_theme_sync_js
from utils.report_generator import generate_beautiful_report
from database import save_user_state, get_user_state

st.set_page_config(page_title="DSA Visualizer", layout="wide")

st.html("""
<style>
/* Stable Table Width Container */
.scrollable-table-window {
    width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;
    border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 8px; padding: 10px; margin-bottom: 20px;
}
.scrollable-table-window table { width: 100%; white-space: nowrap !important; }
</style>
""")

if not st.session_state.get("api_key") or not st.session_state.get("user_id"):
    st.warning("Authentication Required: Please configure your Gemini API Key on the Profile page.", icon=":material/lock:")
    st.stop()

if "current_analysis" not in st.session_state:
    saved_state = get_user_state(st.session_state.user_id)
    if saved_state and saved_state["ai_data"]:
        st.session_state.current_analysis = saved_state["ai_data"]
        st.session_state.current_algo = saved_state["algo_name"]
        st.session_state.qna = saved_state["qna_history"]
    else:
        st.session_state.current_analysis = None
        st.session_state.current_algo = ""
        st.session_state.qna = []

st.markdown("### :material/account_tree: Logic Study Room")
c1, c2 = st.columns([3, 1])
algo_name = c1.text_input("Code Context / Algorithm Name", value=st.session_state.get("current_algo", ""), placeholder="E.g., 'Dijkstra's Algorithm' OR paste your raw Python function block here to visualize...", label_visibility="collapsed")

if c2.button("Deploy Mind-Map", type="secondary", width='stretch', icon=":material/play_arrow:"):
    if algo_name:
        with st.spinner("Synthesizing architecture, mapping execution trace, and evaluating trade-offs..."):
            try:
                data = analyze_algorithm(algo_name, st.session_state.api_key)
                st.session_state.current_analysis = data
                st.session_state.current_algo = algo_name
                st.session_state.qna = []
                save_user_state(st.session_state.user_id, algo_name, data, [])
            except Exception as e:
                st.error(f"Pipeline Compilation Failed: {e}", icon=":material/error:")

if st.session_state.current_analysis:
    data = st.session_state.current_analysis
    
    col_viz, col_text = st.columns([1.2, 1])
    with col_viz:
        st.markdown("#### :material/schema: Logic Pathway")
        with st.container(border=True):
            dot_flow = render_graphviz(data.get("graphviz_flowchart"), "#00FFAA", "TD")
    with col_text:
        st.markdown("#### :material/description: How it Works")
        st.write(data.get("explanation", ""))

    st.divider()

    st.markdown("### :material/memory: Runtime Data State & Call Stack Tracker")
    c_trace, c_stack = st.columns([1.2, 1])
    with c_trace:
        st.markdown("**Execution Story**")
        with st.container(border=True):
            dot_trace = render_graphviz(data.get("graphviz_trace"), "#0099FF", "TD")
    
    st.markdown("**Execution Trace**")
    st.caption(":material/swipe_right: Swipe left or right inside the box below to view the complete table.")
    
    # Stable Implementation of Horizontal Scroll Table
    table_md = data.get("execution_trace_table", "")
    st.markdown(f'<div class="scrollable-table-window">\n\n{table_md}\n\n</div>', unsafe_allow_html=True)
    
    with c_stack:
        st.markdown("**Call Stack**")
        call_stack = data.get("call_stack", [])
        if call_stack:
            st.caption(":material/linear_scale: **Interactive Timeline:** Drag the slider below to step forward and backward through the frames.")
            step = st.slider("Execution Timeline Iteration", 0, len(call_stack)-1, 0, label_visibility="collapsed")
            current_frame = call_stack[step]
            
            st.markdown(f"#### :material/play_circle: {current_frame.get('step_name', 'System Action')}")
            st.info(current_frame.get('explanation', 'Resolving system operational state...'), icon=":material/info:")
            
            stack_items = current_frame.get('stack', [])
            if not stack_items:
                st.success("Call Stack Emptied (Execution Resolved)", icon=":material/check:")
            else:
                for frame in reversed(stack_items):
                    if isinstance(frame, dict):
                        f_name = frame.get('frame', 'Unknown Frame')
                        f_det = frame.get('detail', 'Awaiting context...')
                    else:
                        f_name, f_det = str(frame), ""
                    
                    st.markdown(f"""
                    <div class='cyber-box' style='padding:12px; margin-bottom:12px; border-radius:8px; text-align:center;'>
                        <div class='cyber-title' style='font-family:monospace; font-size: 1.1em;'>{f_name}</div>
                        <div class='cyber-text' style='font-size:0.9em; margin-top:5px;'>{f_det}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No linear or recursive frames recorded for this compilation.")

    st.divider()

    st.markdown("### :material/balance: Performance Trade-offs & Pathologies")    
    tradeoffs = data.get("tradeoffs", {})
    fig_bar = None
    st.markdown("##### Space-Time Structural Profile")
    if tradeoffs:
        st.caption(":material/touch_app: *Tip: Double-tap or double-click anywhere on the chart to reset the zoom/view.*")
        df_bar = pd.DataFrame({"Metric": list(tradeoffs.keys()), "Score": list(tradeoffs.values())})
        fig_bar = px.bar(df_bar, x="Score", y="Metric", orientation='h', template="plotly_dark", color="Score", color_continuous_scale="Tealgrn")
        fig_bar.update_layout(width=750, height=350, xaxis=dict(range=[0, 10]), margin=dict(l=150, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6EDF3", size=13))
        st.plotly_chart(fig_bar, width='stretch')
        
    st.divider()
    st.markdown(f"**Target Asymptotic Complexity:** \n\n {data.get('primary_complexity', 'O(N)')}")
    st.divider()
    st.markdown("**Time Cost:** \n" + data.get('time_complexity', ''))
    st.divider()
    st.markdown("**Space Allocation:** \n" + data.get('space_complexity', ''))
    st.divider()
    st.markdown("##### :material/warning: Identifiable Edge Cases")
    for ec in data.get("edge_cases", []): st.markdown(f"- {ec}")
    st.divider()
    st.markdown(f"**Structural Alternative:** \n\n {data.get('alternative', 'None suggested.')}")
    st.divider()
    
    st.markdown("#### :material/download: Download Report")
    st.info("Generate a formatted HTML technical document. Open the downloaded file in your browser and press **Ctrl+P** to convert it into a standardized PDF report.", icon=":material/lightbulb:")
    
    import re
    raw_name = st.session_state.current_algo
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', raw_name) 
    safe_name = re.sub(r'_+', '_', safe_name).strip('_') 
    safe_name = safe_name[:30] if len(safe_name) > 30 else (safe_name or "Algorithm")
    
    report_html = generate_beautiful_report(safe_name, data, dot_flow, dot_trace, fig_bar)
    st.download_button(label="Download Analytical Report (.html)", data=report_html, file_name=f"{safe_name}_Technical_Report.html", mime="text/html", type="secondary", icon=":material/picture_as_pdf:", width='stretch')
    st.divider()

    st.markdown("#### :material/forum: Ask Follow Up Questions")
    for msg in st.session_state.qna:
        with st.chat_message(msg["role"]):
            content = msg["content"]
            if isinstance(content, dict):
                st.write(content.get("text", ""))
                if content.get("graphviz_code"):
                    render_raw_dot(content["graphviz_code"], "#FF007F")
            else:
                st.write(content)
            
    q_input = st.chat_input("Request custom sub-graphs, syntax traces, or conceptual explanations to AI ...")
    if q_input:
        st.session_state.qna.append({"role": "user", "content": q_input})
        ans_payload = answer_followup(q_input, data.get("explanation", ""), st.session_state.api_key)
        st.session_state.qna.append({"role": "tutor", "content": ans_payload})
        save_user_state(st.session_state.user_id, st.session_state.current_algo, st.session_state.current_analysis, st.session_state.qna)
        st.rerun()