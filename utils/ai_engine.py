import json
import re
from google import genai

def analyze_algorithm(algo_name, api_key, model="gemini-2.5-flash"):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an elite Data Structures and Algorithms instructor. 
    Analyze the algorithm: {algo_name}.
    
    CRITICAL INSTRUCTION: Return ONLY a raw, valid JSON object. No Markdown wrappers.
    
    CRITICAL FORMATTING RULES:
    1. NEVER color entire sentences or paragraphs.
    2. STRICT PROHIBITION: DO NOT use Streamlit color syntax (e.g., :green[...], :blue[...]) inside `graphviz_flowchart`, `graphviz_trace`, `call_stack`, or `execution_trace_table`. NEVER insert color blocks like ":green[Pivot]". Use plain text ONLY for these structures.
    3. You MAY use Streamlit colors ONLY in the `explanation`, `time_complexity`, `space_complexity`, and `alternative` fields to highlight technical keywords.
    
    JSON SCHEMA REQUIRED:
    {{
        "explanation": "Detailed Markdown explanation of the core logic.",
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
                "explanation": "Detailed text explaining what is happening at this specific timeline step.",
                "stack": [
                    {{"frame": "mergeSort(0, 4)", "detail": "Targeting the full array from index 0 to 4"}}
                ]
            }}
        ],
        "tradeoffs": {{
            "Time Efficiency": 8, "Space Efficiency": 5, "Scalability": 9, "Simplicity": 4, "Adaptability": 6
        }},
        "execution_trace_table": "Raw Markdown table string. DO NOT use color syntax here. Just return the pipe-separated string.",
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
    
    CRITICAL FORMATTING RULES: 
    1. Do NOT use markdown symbols or Streamlit color syntax (e.g., :green[...]). Use standard HTML tags ONLY: <b>bold</b>, <i>italic</i>, <code>code</code>.
    2. NEVER break sentences randomly. Ensure the text flows normally as cohesive paragraphs.
    
    Return ONLY valid JSON in this format:
    {{
        "cards": [
            {{"front": "Question?", "back": "Detailed, cohesive answer with <b>HTML</b> tags."}}
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
    
    Provide a concise, direct answer. 
    If the user asks to draw or trace a graph/flowchart, provide clean, basic Graphviz DOT syntax. 
    
    Return ONLY valid JSON in this format:
    {{
        "text": "Your response text here.",
        "graphviz_code": "digraph G {{ ... }}" 
    }}
    """
    response = client.models.generate_content(model=model, contents=prompt)
    clean = re.sub(r'^```json\s*|\s*```$', '', response.text.strip(), flags=re.MULTILINE)
    try: return json.loads(clean, strict=False)
    except Exception: return {"text": response.text, "graphviz_code": ""}