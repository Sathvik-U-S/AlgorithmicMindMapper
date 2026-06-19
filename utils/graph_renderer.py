import streamlit as st
import streamlit.components.v1 as components
import re
from graphviz import Digraph

def inject_theme_sync_js():
    js_code = """
    <script>
        (function() {
            function syncCyberBoxes() {
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
                    
                    let styleEl = parentDoc.getElementById('cyber-theme-sync');
                    if (!styleEl) {
                        styleEl = parentDoc.createElement('style');
                        styleEl.id = 'cyber-theme-sync';
                        parentDoc.head.appendChild(styleEl);
                    }
                    
                    if (isLight) {
                        styleEl.innerHTML = `
                            .cyber-box { background-color: #FFFFFF !important; border: 2px solid #FF007F !important; box-shadow: 0 0 10px rgba(255, 0, 127, 0.15) !important; }
                            .cyber-title { color: #31333F !important; font-weight: 800 !important; }
                            .cyber-text { color: #555555 !important; }
                        `;
                    } else {
                        styleEl.innerHTML = `
                            .cyber-box { background-color: #161B22 !important; border: 2px solid #0099FF !important; box-shadow: 0 0 10px rgba(0, 153, 255, 0.2) !important; }
                            .cyber-title { color: #00FFAA !important; font-weight: 800 !important; }
                            .cyber-text { color: #E6EDF3 !important; }
                        `;
                    }
                } catch (e) {}
            }
            syncCyberBoxes();
            setInterval(syncCyberBoxes, 500);
        })();
    </script>
    """
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

    try:
        raw_svg = dot.pipe(format='svg').decode('utf-8')
        # CRITICAL FIX: Strip hardcoded width/height so the zoom library can scale it!
        raw_svg = re.sub(r'(<svg[^>]*)(width="[^"]*")(.*?)', r'\1\3', raw_svg)
        raw_svg = re.sub(r'(<svg[^>]*)(height="[^"]*")(.*?)', r'\1\3', raw_svg)
        raw_svg = raw_svg.replace('<svg', '<svg id="scalable-svg" style="width:100%; height:100%; touch-action:none;"')
    except Exception:
        st.graphviz_chart(dot)
        return dot

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet" />
        <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
        <style>
            body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: transparent; }}
            #svg-container {{ width: 100%; height: 100%; position: relative; }}
            svg {{ cursor: grab; }}
            svg:active {{ cursor: grabbing; }}
            
            .toolbar {{ position: absolute; top: 10px; right: 10px; display: flex; gap: 8px; z-index: 100; }}
            .tool-btn {{
                background: rgba(22, 27, 34, 0.85); border: 1px solid {theme_color}; color: {theme_color};
                border-radius: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
                cursor: pointer; backdrop-filter: blur(4px); transition: all 0.2s;
            }}
            .tool-btn:active {{ background: {theme_color}; color: #161B22; transform: scale(0.95); }}
            
            svg path[fill="#161B22" i], svg polygon[fill="#161B22" i] {{ fill: #161B22; transition: fill 0.3s; }}
            svg text {{ fill: #E6EDF3; font-family: sans-serif; font-weight: bold; transition: fill 0.3s; }}
            svg path[stroke="{theme_color}" i], svg polygon[stroke="{theme_color}" i] {{ stroke: {theme_color}; transition: stroke 0.3s; }}
            svg polygon[fill="{theme_color}" i] {{ fill: {theme_color}; transition: fill 0.3s; }}
        </style>
    </head>
    <body>
        <div id="svg-container">
            <div class="toolbar">
                <button class="tool-btn" onclick="panZoom.zoomIn()"><span class="material-symbols-rounded">add</span></button>
                <button class="tool-btn" onclick="panZoom.zoomOut()"><span class="material-symbols-rounded">remove</span></button>
                <button class="tool-btn" onclick="panZoom.resetZoom(); panZoom.center();"><span class="material-symbols-rounded">refresh</span></button>
            </div>
            {raw_svg}
        </div>
        
        <script>
            var panZoom = svgPanZoom('#scalable-svg', {{
                zoomEnabled: true, controlIconsEnabled: false, fit: true, center: true, minZoom: 0.5, maxZoom: 10
            }});
            
            function syncTheme() {{
                try {{
                    const parentDoc = window.parent.document;
                    const appDiv = parentDoc.querySelector('.stApp') || parentDoc.body;
                    const bgColor = window.parent.getComputedStyle(appDiv).backgroundColor;
                    const rgb = bgColor.match(/\d+/g);
                    if (!rgb) return;
                    
                    const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
                    const isLight = brightness > 128;
                    
                    let styleEl = document.getElementById('dynamic-theme');
                    if (!styleEl) {{
                        styleEl = document.createElement('style');
                        styleEl.id = 'dynamic-theme';
                        document.head.appendChild(styleEl);
                    }}
                    
                    if (isLight) {{
                        let primary = "{theme_color}" === "#00FFAA" ? "#FF007F" : "#0099FF";
                        styleEl.innerHTML = `
                            svg path[fill="#161B22" i], svg polygon[fill="#161B22" i] {{ fill: #F0F2F6 !important; }}
                            svg text {{ fill: #31333F !important; }}
                            svg path[stroke="{theme_color}" i], svg polygon[stroke="{theme_color}" i] {{ stroke: ${{primary}} !important; }}
                            svg polygon[fill="{theme_color}" i] {{ fill: ${{primary}} !important; }}
                            .tool-btn {{ background: rgba(240, 242, 246, 0.9) !important; color: ${{primary}} !important; border-color: ${{primary}} !important; }}
                        `;
                    }} else {{ styleEl.innerHTML = ''; }}
                }} catch (e) {{}}
            }}
            syncTheme();
            setInterval(syncTheme, 500);
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=450)
    inject_theme_sync_js()
    return dot