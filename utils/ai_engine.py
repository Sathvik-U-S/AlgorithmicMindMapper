import json
import re
from google import genai

def analyze_algorithm(algo_name, api_key, model="gemini-2.5-flash"):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an elite Data Structures and Algorithms instructor. 
    Analyze the algorithm: {algo_name}.
    
    CRITICAL INSTRUCTION: Return ONLY a raw, valid JSON object. No Markdown wrappers.
    
    ABSOLUTE FORMATTING RULES (FAILURE WILL BREAK THE UI):
    1. NEVER use Streamlit color syntax (e.g., :green[Pivot], :blue[Index], :red[...]) ANYWHERE in the JSON.
    2. The values for `graphviz_flowchart`, `graphviz_trace`, `call_stack`, `execution_trace_table`, and `flashcards` must be 100% plain text and standard characters. 
    3. Do NOT use markdown colors. Use standard text formatting.
    
    JSON SCHEMA REQUIRED:
    {{
        "explanation": "Detailed plain-text explanation of the core logic.",
        "edge_cases": ["Edge case 1 and how it handles it", "Edge case 2"],
        "graphviz_flowchart": {{
            "nodes": [{{"id": "A", "label": "Start"}}],
            "edges": [["A", "B", "Condition"]]
        }},
        "graphviz_trace": {{
            "nodes": [{{"id": "1", "label": "Array: [5,2,9]"}}],
            "edges": [["1", "2", "Swap 5 and 2"]]
        }},
        "call_stack": [
            {{
                "step_name": "Initial Call", 
                "explanation": "Detailed plain text explaining what is happening at this specific timeline step.",
                "stack": [
                    {{"frame": "mergeSort(0, 4)", "detail": "Targeting the full array from index 0 to 4"}}
                ]
            }}
        ],
        "tradeoffs": {{
            "Time Efficiency": 8, "Space Efficiency": 5, "Scalability": 9, "Simplicity": 4, "Adaptability": 6
        }},
        "execution_trace_table": "Raw Markdown table string. PLAIN TEXT ONLY. No colors. Pipe-separated string.",
        "time_complexity": "Markdown bullet points.",
        "space_complexity": "Markdown bullet points.",
        "primary_complexity": "Exactly one of: O(1), O(log N), O(N), O(N log N), O(N^2), O(2^N)",
        "real_world_apps": ["App 1", "App 2"],
        "limitations": ["Limitation 1"],
        "alternative": "Alternative algorithm"
    }}
    """
    
    response = client.models.generate_content(model=model, contents=prompt)
    raw = response.text.strip()
    clean = re.sub(r'^```json\s*|\s*```$', '', raw, flags=re.MULTILINE)
    return json.loads(clean, strict=False)

def generate_flashcards(algo_context, api_key, model="gemini-2.5-flash"):
    client = genai.Client(api_key=api_key)
    prompt = f"""
    Based on this algorithm context: {algo_context}
    Generate 5 Active-Recall Flashcards.
    
    ABSOLUTE FORMATTING RULES: 
    1. STRICTLY FORBIDDEN: Do NOT use Streamlit color syntax (e.g., :green[Pivot]).
    2. Use standard HTML tags ONLY: <b>bold</b>, <i>italic</i>, <code>code</code>.
    3. Ensure the text flows normally as cohesive paragraphs. Start at the top.
    
    Return ONLY valid JSON in this format:
    {{
        "cards": [
            {{"front": "Question?", "back": "Detailed, cohesive answer with <b>HTML</b> tags. No colors."}}
        ]
    }}
    """
    response = client.models.generate_content(model=model, contents=prompt)
    clean = re.sub(r'^```json\s*|\s*```$', '', response.text.strip(), flags=re.MULTILINE)
    return json.loads(clean, strict=False)

def answer_followup(question, context_data, api_key, model="gemini-2.5-flash"):
    client = genai.Client(api_key=api_key)
    prompt = f"""
    Context: {context_data}
    Student asks: {question}
    
    Provide a concise, direct answer in plain text. NO STREAMLIT COLORS.
    If the user asks to draw or trace a graph/flowchart, provide clean, basic Graphviz DOT syntax. 
    
    Return ONLY valid JSON in this format:
    {{
        "text": "Your plain-text response here.",
        "graphviz_code": "digraph G {{ ... }}" 
    }}
    """
    response = client.models.generate_content(model=model, contents=prompt)
    clean = re.sub(r'^```json\s*|\s*```$', '', response.text.strip(), flags=re.MULTILINE)
    try: return json.loads(clean, strict=False)
    except Exception: return {"text": response.text, "graphviz_code": ""}