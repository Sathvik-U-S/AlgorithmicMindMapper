import streamlit as st
import streamlit.components.v1 as components
from graphviz import Digraph

def inject_theme_sync_js():
    """Uses the safe, sandboxed components.html iframe to protect the JS timer from Streamlit DOM wipes."""
    js_code = """
    <script>
        (function() {
            function syncGraphvizColors() {
                try {
                    // Reach up out of the iframe into the parent Streamlit application
                    const parentDoc = window.parent.document;
                    if (!parentDoc) return;
                    
                    // Locate the main background container
                    const appDiv = parentDoc.querySelector('[data-testid="stAppViewContainer"]') || parentDoc.querySelector('.stApp') || parentDoc.body;
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
                        // Light Mode: Apply bright theme colors instantly
                        styleEl.innerHTML = `
                            /* Graphviz Colors */
                            .stGraphVizChart svg path[fill="#161B22" i], 
                            .stGraphVizChart svg polygon[fill="#161B22" i] { fill: #F0F2F6 !important; }
                            
                            .stGraphVizChart svg text { fill: #31333F !important; font-weight: bold !important; }
                            
                            .stGraphVizChart svg path[stroke="#00FFAA" i], 
                            .stGraphVizChart svg polygon[stroke="#00FFAA" i] { stroke: #FF007F !important; }
                            .stGraphVizChart svg polygon[fill="#00FFAA" i] { fill: #FF007F !important; }
                            
                            .stGraphVizChart svg path[stroke="#0099FF" i], 
                            .stGraphVizChart svg polygon[stroke="#0099FF" i] { stroke: #0099FF !important; }
                            .stGraphVizChart svg polygon[fill="#0099FF" i] { fill: #0099FF !important; }
                            
                            /* Recursive Call Stack UI */
                            .cyber-box { background-color: #F0F2F6 !important; border-color: #FF007F !important; }
                            .cyber-title { color: #31333F !important; }
                            .cyber-text { color: #555555 !important; }
                        `;
                    } else {
                        // Dark Mode: Clear overrides to restore original Cyber-Dark styling
                        styleEl.innerHTML = ''; 
                    }
                } catch (e) {}
            }
            
            // Run instantly, then poll every 200ms to catch manual UI toggles flawlessly
            syncGraphvizColors();
            setInterval(syncGraphvizColors, 200);
        })();
    </script>
    """
    # Using the safe component wrapper with 0 size so it is invisible
    components.html(js_code, height=0, width=0) 

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

    # Using width='stretch' to prevent deprecation warnings while ensuring full container expansion
    st.graphviz_chart(dot, width='stretch')
    inject_theme_sync_js()
    return dot