# Algorithmic Mind-Mapper & Code-to-Flowchart Tracker 🧠🚀

A highly interactive, AI-driven educational tool designed to demystify Data Structures and Algorithms. By leveraging the Gemini AI API, this tool intercepts raw Python code or algorithm names and automatically compiles architectural Graphviz blueprints, execution trace tables, space-time matrices, and recursive memory call stacks.

## Features
- **Dynamic Graphviz Generation:** Translates complex code logic into instantly readable Flowcharts and Trace Matrices.
- **Cyber-Dark & Light Mode Integration:** UI actively detects Streamlit themes and applies robust CSS modifications.
- **Interactive Stack Inspector:** Step through recursive calls horizontally frame-by-frame.
- **PDF Report Generator:** Compiles your session into a beautifully formatted HTML document optimized perfectly for static PDF A4 printing.
- **Active Recall Deck:** Instantly converts the synthesized logic into a 3D-CSS Flashcard system for studying.

## Tech Stack
- **Frontend:** Streamlit, D3-Graphviz, Plotly Express
- **Backend AI Engine:** Google GenAI (`gemini-2.5-flash`)
- **Data Persistence:** SQLite3
- **Rendering Wrappers:** Kroki API (For bulletproof PDF image conversion)

## Installation 
1. Clone the repository.
2. Install requirements: `pip install -r requirements.txt`
3. Launch the app: `streamlit run app.py`
4. Enter your Gemini API Key directly in the UI.