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
        # CRITICAL FIX: Strip hardcoded dimensions so our custom wrapper can scale it dynamically
        raw_svg = re.sub(r'(<svg[^>]*)(width="[^"]*")(.*?)', r'\1\3', raw_svg)
        raw_svg = re.sub(r'(<svg[^>]*)(height="[^"]*")(.*?)', r'\1\3', raw_svg)
    except Exception:
        st.graphviz_chart(dot)
        return dot

    # Pure Native HTML Scrolling with Custom Multi-Touch Pan/Zoom Logic
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <style>
            :root {{
                --text-color: #E6EDF3;
                --bg-color: transparent;
                --border-color: rgba(128, 128, 128, 0.2);
                --btn-bg: rgba(22, 27, 34, 0.85);
                --container-bg: transparent;
                --primary: {theme_color};
            }}
            body {{ margin: 0; background-color: var(--bg-color); color: var(--text-color); font-family: sans-serif; overflow: hidden; }}
            
            .controls {{ 
                position: sticky; top: 0; z-index: 100; display: flex; gap: 12px; background-color: var(--bg-color); 
                padding: 10px; align-items: center; border-bottom: 1px solid var(--border-color); backdrop-filter: blur(8px);
            }}
            button {{ 
                display: flex; align-items: center; gap: 5px; padding: 6px 12px; cursor: pointer; border-radius: 6px; 
                border: 1px solid var(--primary); background: var(--btn-bg); color: var(--primary); font-weight: bold; 
                font-size: 13px; transition: all 0.2s; 
            }}
            button .material-icons {{ font-size: 18px; }}
            button:hover, button:active {{ background: var(--primary); color: #161B22; }}
            
            #wrapper {{ 
                width: 100%; height: calc(100vh - 60px); overflow: auto; background: var(--container-bg); 
                cursor: grab; position: relative; -webkit-overflow-scrolling: touch;
            }}
            #wrapper:active {{ cursor: grabbing; }}
            #wrapper::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            #wrapper::-webkit-scrollbar-track {{ background: transparent; }}
            #wrapper::-webkit-scrollbar-thumb {{ background-color: var(--border-color); border-radius: 8px; }}
            #wrapper::-webkit-scrollbar-thumb:hover {{ background-color: var(--primary); }}
            
            #container {{ 
                transform-origin: 0 0; transition: transform 0.1s ease-out; display: inline-block; 
                min-width: 100%; min-height: 100%; user-select: none; padding: 20px; box-sizing: border-box;
            }}
            
            svg {{ width: 100%; height: auto; pointer-events: none; }}
            
            /* The dynamic theme overrides will be injected here by JS */
        </style>
    </head>
    <body>
        <div class="controls">
            <button type="button" onclick="zoom(1.2)"><span class="material-icons">zoom_in</span> Zoom In</button>
            <button type="button" onclick="zoom(0.8)"><span class="material-icons">zoom_out</span> Zoom Out</button>
            <button type="button" onclick="resetZoom()"><span class="material-icons">restart_alt</span> Reset</button>
            <span id="zoom-level" style="margin-left: 10px; font-weight: 500; font-family: monospace;">100%</span>
        </div>
        
        <div id="wrapper">
            <div id="container">
                {raw_svg}
            </div>
        </div>
        
        <script>
            function syncTheme() {{
                try {{
                    const parentDoc = window.parent.document;
                    const appDiv = parentDoc.querySelector('.stApp') || parentDoc.body;
                    const bgColor = window.parent.getComputedStyle(appDiv).backgroundColor;
                    const rgb = bgColor.match(/\d+/g);
                    let isLight = false;
                    
                    if (rgb && rgb.length >= 3) {{
                        const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;
                        isLight = brightness > 128;
                    }}
                    
                    let styleEl = document.getElementById('dynamic-theme');
                    if (!styleEl) {{ 
                        styleEl = document.createElement('style'); 
                        styleEl.id = 'dynamic-theme'; 
                        document.head.appendChild(styleEl); 
                    }}
                    
                    if (isLight) {{
                        let primary = "{theme_color}" === "#00FFAA" ? "#FF007F" : "#0099FF";
                        styleEl.innerHTML = `
                            :root {{
                                --primary: ${{primary}};
                                --text-color: #31333F;
                                --bg-color: #FFFFFF;
                                --btn-bg: rgba(240, 242, 246, 0.95);
                                --container-bg: rgba(240, 242, 246, 0.5);
                                --border-color: rgba(49, 51, 63, 0.2);
                            }}
                            svg path[fill="#161B22" i], svg polygon[fill="#161B22" i] {{ fill: #F0F2F6 !important; }}
                            svg text {{ fill: #31333F !important; font-weight: bold !important; }}
                            svg path[stroke="{theme_color}" i], svg polygon[stroke="{theme_color}" i] {{ stroke: ${{primary}} !important; }}
                            svg polygon[fill="{theme_color}" i] {{ fill: ${{primary}} !important; }}
                        `;
                    }} else {{ 
                        styleEl.innerHTML = `
                            :root {{
                                --primary: {theme_color};
                                --text-color: #E6EDF3;
                                --bg-color: transparent;
                                --btn-bg: rgba(22, 27, 34, 0.85);
                                --container-bg: transparent;
                                --border-color: rgba(128, 128, 128, 0.2);
                            }}
                            svg path[fill="#161B22" i], svg polygon[fill="#161B22" i] {{ fill: #161B22 !important; }}
                            svg text {{ fill: #E6EDF3 !important; font-weight: bold !important; }}
                            svg path[stroke="{theme_color}" i], svg polygon[stroke="{theme_color}" i] {{ stroke: {theme_color} !important; }}
                            svg polygon[fill="{theme_color}" i] {{ fill: {theme_color} !important; }}
                        `;
                    }}
                }} catch (e) {{ console.log("Theme sync fallback."); }}
            }}
            syncTheme(); setInterval(syncTheme, 1000);
            
            // --- Custom Zoom Engine ---
            let scale = 1.0;
            const container = document.getElementById('container');
            const zoomLevel = document.getElementById('zoom-level');
            const wrapper = document.getElementById('wrapper');
            
            function zoom(factor) {{
                scale *= factor;
                if (scale < 0.2) scale = 0.2;
                if (scale > 10.0) scale = 10.0;
                container.style.transform = `scale(${{scale}})`;
                zoomLevel.innerText = Math.round(scale * 100) + "%";
            }}
            function resetZoom() {{
                scale = 1.0;
                container.style.transform = 'scale(1)';
                zoomLevel.innerText = "100%";
            }}
            
            // --- Custom Pan Engine ---
            let isDown = false;
            let startX, startY, scrollLeft, scrollTop;
            
            wrapper.addEventListener('mousedown', (e) => {{
                isDown = true;
                startX = e.pageX - wrapper.offsetLeft; startY = e.pageY - wrapper.offsetTop;
                scrollLeft = wrapper.scrollLeft; scrollTop = wrapper.scrollTop;
            }});
            wrapper.addEventListener('mouseleave', () => {{ isDown = false; }});
            wrapper.addEventListener('mouseup', () => {{ isDown = false; }});
            wrapper.addEventListener('mousemove', (e) => {{
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - wrapper.offsetLeft; const y = e.pageY - wrapper.offsetTop;
                wrapper.scrollLeft = scrollLeft - (x - startX) * 1.5; 
                wrapper.scrollTop = scrollTop - (y - startY) * 1.5;
            }});
            
            wrapper.addEventListener('touchstart', (e) => {{
                isDown = true;
                startX = e.touches[0].pageX - wrapper.offsetLeft; startY = e.touches[0].pageY - wrapper.offsetTop;
                scrollLeft = wrapper.scrollLeft; scrollTop = wrapper.scrollTop;
            }});
            wrapper.addEventListener('touchend', () => {{ isDown = false; }});
            wrapper.addEventListener('touchmove', (e) => {{
                if (!isDown) return;
                e.preventDefault(); 
                const x = e.touches[0].pageX - wrapper.offsetLeft; const y = e.touches[0].pageY - wrapper.offsetTop;
                wrapper.scrollLeft = scrollLeft - (x - startX) * 1.5;
                wrapper.scrollTop = scrollTop - (y - startY) * 1.5;
            }}, {{ passive: false }});
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=600)
    inject_theme_sync_js()
    return dot