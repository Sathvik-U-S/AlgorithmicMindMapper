import re
import base64
import zlib

def process_markdown_colors(text):
    if not text: return ""
    text = str(text)
    text = re.sub(r':([a-zA-Z]+)\[(.*?)\]', r'<span style="color: \1; font-weight: bold;">\2</span>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    lines = text.split('\n')
    processed_lines = []
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|'):
            if not in_table:
                in_table = True
                processed_lines.append('<table style="width:100%; border-collapse:collapse; margin:20px 0; background-color:#161B22;">')
            
            if re.match(r'^\|[\s:-|]+$', stripped):
                continue
                
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            is_header = (processed_lines[-1].startswith('<table') or len(processed_lines) == 1)
            tag = 'th' if is_header else 'td'
            row_style = 'background-color:#21262D; color:#00FFAA; font-weight:bold;' if is_header else ''
            row_html = f'  <tr style="{row_style}">' + ''.join([f'<{tag} style="border:1px solid #30363D; padding:12px; font-family:sans-serif;">{c}</{tag}>' for c in cells]) + '</tr>'
            processed_lines.append(row_html)
        else:
            if in_table:
                in_table = False
                processed_lines.append('</table>')
            processed_lines.append(line + '<br>')
            
    if in_table:
        processed_lines.append('</table>')
        
    return '\n'.join(processed_lines)

def get_kroki_image_html(dot_object):
    if dot_object is None: return ""
    try:
        dot_string = dot_object.source
        compressed = zlib.compress(dot_string.encode('utf-8'), 9)
        b64_str = base64.urlsafe_b64encode(compressed).decode('utf-8').replace('=', '')
        kroki_url = f"https://kroki.io/graphviz/svg/{b64_str}"
        return f'<img src="{kroki_url}" style="max-width: 100%; height: auto; padding: 10px; border-radius: 8px;">'
    except Exception: return ""

def get_plotly_html(fig):
    """FIX: Embeds Plotly JS offline so the chart never disappears in the PDF print view."""
    if fig is None: return ""
    try: 
        html_snippet = fig.to_html(full_html=False, include_plotlyjs=True, config={'staticPlot': True})
        return f'<div style="max-width: 100%; width: 750px; margin: 0 auto; overflow: visible;">{html_snippet}</div>'
    except Exception: return ""

def build_call_stack_html(call_stack):
    if not call_stack:
        return "<p style='color: #8B949E;'><i>No recursive stack frames tracked for this algorithm.</i></p>"
    
    html = "<div style='display: flex; flex-direction: column; gap: 20px; padding-bottom: 15px;'>"
    for idx, step in enumerate(call_stack):
        html += f"<div style='background: #21262D; border: 1px solid #30363D; border-radius: 8px; padding: 20px;'>"
        html += f"<div style='color: #8B949E; font-size: 13px; margin-bottom: 5px; text-transform: uppercase; font-weight: bold;'>Step {idx + 1}</div>"
        html += f"<h4 style='color: #58A6FF; margin-top: 0; margin-bottom: 10px; font-size: 18px;'>{step.get('step_name', 'Action')}</h4>"
        html += f"<p style='font-size: 15px; color: #E6EDF3; margin-top: 0; margin-bottom: 15px; line-height: 1.5;'>{step.get('explanation', '')}</p>"
        
        html += "<div style='display: flex; flex-direction: column-reverse; gap: 8px;'>" 
        stack_frames = step.get('stack', [])
        
        if not stack_frames:
            html += "<div style='background: #161B22; border: 1px dashed #8B949E; padding: 12px; text-align: center; border-radius: 4px; color: #8B949E; font-size: 14px;'>[Empty / Resolved]</div>"
        else:
            for frame in stack_frames:
                if isinstance(frame, dict):
                    f_name = frame.get('frame', '')
                    f_det = frame.get('detail', '')
                else:
                    f_name, f_det = str(frame), ""
                    
                html += f"<div style='background: #161B22; border: 1px solid #ff4b4b; padding: 12px; text-align: center; border-radius: 6px;'>"
                html += f"<div style='font-family: monospace; font-size: 15px; color: #00FFAA; font-weight: bold;'>{f_name}</div>"
                html += f"<div style='font-size: 13px; color: #8B949E; margin-top: 4px;'>{f_det}</div>"
                html += "</div>"
        
        html += "</div></div>"
    html += "</div>"
    return html

def generate_beautiful_report(algo_name, data, dot_flow, dot_trace, fig_bar):
    html_flow = get_kroki_image_html(dot_flow)
    html_trace = get_kroki_image_html(dot_trace)
    html_bar = get_plotly_html(fig_bar)
    call_stack_html = build_call_stack_html(data.get("call_stack", []))
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Report - {algo_name}</title>
        <style>
            body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0D1117; color: #E6EDF3; line-height: 1.6; padding: 40px; max-width: 1000px; margin: auto; }}
            h1 {{ color: #00FFAA; border-bottom: 2px solid #161B22; padding-bottom: 10px; font-size: 2.5em; }}
            h2 {{ color: #58A6FF; margin-top: 40px; border-bottom: 1px solid #161B22; padding-bottom: 5px; }}
            h3 {{ color: #8B949E; }}
            .card {{ background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .img-container {{ margin: 20px 0; background-color: transparent; text-align: center; overflow: visible; }}
            
            ul {{ list-style-type: square; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #30363D; padding: 10px; text-align: left; }}
            th {{ background-color: #21262D; color: #00FFAA; }}
            
            /* -- BULLETPROOF PDF PRINT SETTINGS -- */
            @media print {{ 
                body {{ background-color: #fff !important; color: #000 !important; padding: 0; margin: 0; }} 
                h1, h2, h3, p, div, li, td, span {{ color: #000 !important; }}
                h1, h2 {{ border-color: #ccc; page-break-after: avoid; }} 
                
                .card, div, .img-container {{ overflow: visible !important; overflow-x: visible !important; page-break-inside: avoid; }}
                .card {{ background-color: #fff !important; border: 1px solid #ccc !important; box-shadow: none !important; margin-bottom: 20px; }} 
                th {{ background-color: #f0f0f0 !important; color: #000 !important; }} 
                
                table {{ width: 100% !important; table-layout: fixed !important; word-wrap: break-word !important; overflow-wrap: break-word !important; white-space: normal !important; }}
                td, th {{ white-space: normal !important; word-wrap: break-word !important; overflow-wrap: break-word !important; font-size: 10pt; padding: 4px; }}
                
                /* Invert charts for white backgrounds */
                img, .js-plotly-plot, .plotly-graph-div {{ max-width: 100%; page-break-inside: avoid; filter: invert(1) hue-rotate(180deg); }} 
            }}
        </style>
    </head>
    <body>
        <h1>Data Structures & Algorithms Report: {algo_name}</h1>
        
        <h2>1. Core Logic & Explanation</h2>
        <div class="card">{process_markdown_colors(data.get('explanation'))}</div>
        
        <h2>2. Architectural Flowchart</h2>
        <div class="img-container">
            {html_flow}
        </div>
        
        <h2>3. Execution Trace Data State</h2>
        <div class="img-container">
            {html_trace}
        </div>
        <div class="card" style="padding: 0; border: none; background: transparent; overflow: visible;">
            {process_markdown_colors(data.get('execution_trace_table'))}
        </div>
        
        <h2>4. Recursive Call Stack Timeline</h2>
        <div class="card" style="background-color: transparent; border: none; box-shadow: none; padding: 0;">
            {call_stack_html}
        </div>
        
        <h2>5. Space-Time Complexity</h2>
        <div class="card">
            <h3>Target Complexity: {data.get('primary_complexity')}</h3>
            <p><b>Time:</b><br>{process_markdown_colors(data.get('time_complexity'))}</p>
            <p><b>Space:</b><br>{process_markdown_colors(data.get('space_complexity'))}</p>
        </div>
        
        <h2>6. Trade-off Profile</h2>
        <div class="card img-container" style="background-color: transparent; border: none; box-shadow: none; overflow: visible;">
            {html_bar}
        </div>
        
        <h2>7. Edge Cases & Pathological Inputs</h2>
        <div class="card">
            <ul>
                {"".join([f"<li>{process_markdown_colors(ec)}</li>" for ec in data.get("edge_cases", [])])}
            </ul>
        </div>
        
        <h2>8. Limitations & Alternatives</h2>
        <div class="card">
            <p><b>Alternative:</b> {process_markdown_colors(data.get('alternative'))}</p>
            <ul>
                {"".join([f"<li>{process_markdown_colors(lim)}</li>" for lim in data.get("limitations", [])])}
            </ul>
        </div>
    </body>
    </html>
    """
    return html