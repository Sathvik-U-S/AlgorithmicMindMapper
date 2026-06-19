import streamlit as st
from graphviz import Digraph

def inject_theme_sync_js():
    """Unbreakable JS interval that survives Streamlit re-runs and instantly catches manual theme toggles."""
    js_code = """
    <script>
        (function() {
            function syncGraphvizColors() {
                try {
                    // Accurately find Streamlit's main background container
                    const appDiv = document.querySelector('[data-testid="stAppViewContainer"]') || document.querySelector('.stApp') || document.body;
                    const bgColor = window.getComputedStyle(appDiv).backgroundColor;
                    const rgb = bgColor.match(/\\d+/g);
                    if (!rgb) return;
                    
                    const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
                    const isLight = brightness > 128;
                    
                    let styleEl = document.getElementById('theme-sync-style');
                    if (!styleEl) {
                        styleEl = document.createElement('style');
                        styleEl.id = 'theme-sync-style';
                        document.head.appendChild(styleEl);
                    }
                    
                    if (isLight) {
                        styleEl.innerHTML = `
                            /* Graphviz Colors for Light Mode */
                            .stGraphVizChart svg path[fill="#161B22" i], 
                            .stGraphVizChart svg polygon[fill="#161B22" i] { fill: #FFFFFF !important; }
                            
                            .stGraphVizChart svg text { fill: #31333F !important; font-weight: bold !important; }
                            
                            .stGraphVizChart svg path[stroke="#00FFAA" i], 
                            .stGraphVizChart svg polygon[stroke="#00FFAA" i] { stroke: #FF007F !important; }
                            .stGraphVizChart svg polygon[fill="#00FFAA" i] { fill: #FF007F !important; }
                            
                            .stGraphVizChart svg path[stroke="#0099FF" i], 
                            .stGraphVizChart svg polygon[stroke="#0099FF" i] { stroke: #0099FF !important; }
                            .stGraphVizChart svg polygon[fill="#0099FF" i] { fill: #0099FF !important; }
                            
                            /* Recursive Frame Inspector Colors for Light Mode */
                            .cyber-box { background-color: #FFFFFF !important; border-color: #FF007F !important; box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important; }
                            .cyber-title { color: #31333F !important; }
                            .cyber-text { color: #555555 !important; }
                        `;
                    } else {
                        styleEl.innerHTML = ''; // Revert to pure Dark Mode
                    }
                } catch (e) {}
            }
            
            // CRITICAL FIX: Kill old ghost-timers before starting a new one on Streamlit re-run
            if (window.themeSyncTimer) clearInterval(window.themeSyncTimer);
            window.themeSyncTimer = setInterval(syncGraphvizColors, 200);
            syncGraphvizColors(); // Execute immediately
        })();
    </script>
    """
    st.html(js_code) 

def render_graphviz(graph_data, theme_color="#00FFAA", layout="TD"):
    if not graph_data or "nodes" not in graph_data:
        return
        
    dot = Digraph(node_attr={
        'shape': 'box', 
        'style': 'filled, rounded', 
        'fillcolor': '#161B22', 
        'color': theme_color, 
        'fontcolor': '#E6EDF3', 
        'fontname': 'sans-serif',
        'penwidth': '2'
    })
    
    dot.attr(bgcolor='transparent', rankdir=layout, pad='0.5', splines='spline')
    dot.edge_attr.update(color=theme_color, fontcolor='#E6EDF3', penwidth='1.5', fontname='sans-serif', fontsize='10')

    for node in graph_data.get("nodes", []):
        dot.node(str(node["id"]), str(node["label"]))

    for edge in graph_data.get("edges", []):
        if len(edge) == 3:
            dot.edge(str(edge[0]), str(edge[1]), label=f" {edge[2]} ")
        elif len(edge) >= 2:
            dot.edge(str(edge[0]), str(edge[1]))

    st.graphviz_chart(dot, width='stretch')
    inject_theme_sync_js()
    return dot