import streamlit as st
from graphviz import Digraph

def inject_theme_sync_js():
    """Invisible JS using st.html (Replaces deprecated components.v1.html) that perfectly converts SVG and HTML colors for Light Mode."""
    js_code = """
    <script>
        function syncGraphvizColors() {
            try {
                const parentDoc = window.parent.document;
                const appDiv = parentDoc.querySelector('.stApp');
                if (!appDiv) return;
                
                const bgColor = window.parent.getComputedStyle(appDiv).backgroundColor;
                const rgb = bgColor.match(/\\d+/g);
                if (!rgb) return;
                
                const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
                const isLight = brightness > 128;
                
                let styleEl = parentDoc.getElementById('theme-sync-style');
                if (!styleEl) {
                    styleEl = parentDoc.createElement('style');
                    styleEl.id = 'theme-sync-style';
                    parentDoc.head.appendChild(styleEl);
                }
                
                if (isLight) {
                    styleEl.innerHTML = `
                        .stGraphVizChart svg path[fill="#161B22" i], 
                        .stGraphVizChart svg polygon[fill="#161B22" i] { fill: #F0F2F6 !important; }
                        
                        .stGraphVizChart svg text { fill: #31333F !important; font-weight: bold !important; }
                        
                        .stGraphVizChart svg path[stroke="#00FFAA" i], 
                        .stGraphVizChart svg polygon[stroke="#00FFAA" i] { stroke: #31333F !important; }
                        .stGraphVizChart svg polygon[fill="#00FFAA" i] { fill: #31333F !important; }
                        
                        .stGraphVizChart svg path[stroke="#0099FF" i], 
                        .stGraphVizChart svg polygon[stroke="#0099FF" i] { stroke: #7A7A7A !important; }
                        .stGraphVizChart svg polygon[fill="#0099FF" i] { fill: #7A7A7A !important; }
                        
                        .cyber-box { background-color: #F0F2F6 !important; border-color: #FF007F !important; }
                        .cyber-title { color: #31333F !important; }
                        .cyber-text { color: #7A7A7A !important; }
                    `;
                } else {
                    styleEl.innerHTML = '';
                }
            } catch (e) {}
        }
        syncGraphvizColors();
        setInterval(syncGraphvizColors, 1000);
    </script>
    """
    st.html(js_code) # Modern replacement for components.html

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

    st.graphviz_chart(dot, width='stretch') # Fixed deprecation
    inject_theme_sync_js()
    return dot