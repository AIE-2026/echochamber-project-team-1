"""
EchoChamber Studio — app.py
===========================
A simulation of discursive bubbles using Romanian political comments.
Each "agent" responds from the perspective of its own political community.
 
This file is intentionally kept simple and well-commented.
Sociology students: you don't need to understand every line —
focus on the functions that interest you and modify them freely.
 
Structure:
  1. IMPORTS & SETUP
  2. DESIGN CONSTANTS  (colors, fonts, HTML templates)
  3. HELPER FUNCTIONS  (fetch article, neutral summary, etc.)
  4. TAB 1 — Agents   (all agents respond to same stimulus)
  5. TAB 2 — News     (load article → summarize → chat)
  6. TAB 3 — Debate   (agentic thread with LLM router)
  7. BUILD UI          (assemble the Gradio interface)
  8. LAUNCH
"""
 
# ─────────────────────────────────────────────────────────────────────────────
# 1. IMPORTS & SETUP
import os
import sys
import traceback
from pathlib import Path
import html
from functools import wraps
from core.graph import run_thread
 
 
def safe_handler(fn):
    """Catch any exception in a Gradio handler and return it as text
    instead of letting it crash the websocket ('connection lost')."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            print(tb, file=sys.stderr)
            return f"[Error in {fn.__name__}: {type(e).__name__}: {e}]"
    return wrapper
 
import requests
from bs4 import BeautifulSoup
import gradio as gr
import yaml
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, APIError, AuthenticationError
 
# ENV SETUP
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
 
load_dotenv(PROJECT_ROOT / ".env")
 
BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "gemini-flash": "https://generativelanguage.googleapis.com/v1beta/openai/",
}
 
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "gemini-flash": os.getenv("GEMINI_API_KEY"),
}
 
from core.agent import generate_agent_response
from core.graph import run_thread
 
_CLIENT_CACHE = {}
 
 
def make_client(provider):
    if provider in _CLIENT_CACHE:
        return _CLIENT_CACHE[provider]
 
    client = OpenAI(
        api_key=API_KEYS.get(provider),
        base_url=BASE_URLS.get(provider),
    )
    _CLIENT_CACHE[provider] = client
    return client
 
 
def ask(provider, model, prompt, system=None, temperature=0.7):
    client = make_client(provider)
 
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
 
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        return f"[RateLimit: {model}]"
    except AuthenticationError:
        return "[Auth Error: check API key]"
    except APIError as e:
        return f"[API Error: {e}]"
    except Exception as e:
        return f"[Error: {type(e).__name__}: {e}]"
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 2. CONSTANTS
DEFAULT_K = 5
 
ALLOWED_AGENTS = {
    "anti_sistem",
    "conspirationist",
    "anti_suveranist",
}
 
 
def load_agent_choices():
    roles_path = PROJECT_ROOT / "assets" / "roles" / "roles.yaml"
    if not roles_path.exists():
        return []
 
    with open(roles_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
 
    roles = data["agents"] if isinstance(data, dict) and "agents" in data else data
    if not isinstance(roles, dict):
        return []
 
    return [k for k in roles.keys() if k in ALLOWED_AGENTS]
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 3. NEWS LOADING
def extract_article(url: str):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
 
        title = soup.title.text.strip() if soup.title else "Fără titlu"
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text())
 
        if len(text.strip()) < 200:
            return None, None
        return title, text
    except Exception:
        return None, None
 
 
@safe_handler
def load_news(url, manual_text):
    if url:
        title, text = extract_article(url)
        if title and text:
            preview = f"{title}\n\n{text[:800]}..."
            return preview, text
 
    if manual_text and manual_text.strip():
        preview = manual_text[:800] + ("..." if len(manual_text) > 800 else "")
        return preview, manual_text
 
    return "Nu s-a putut încărca articolul. Introdu text manual.", ""
 
 
@safe_handler
def summarize_article(article):
    if not article:
        return "Nu există articol încărcat."
    sentences = [s.strip() for s in article.split(".") if s.strip()]
    return ". ".join(sentences[:5]) + "."
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 4. CHAT
@safe_handler
def chat(prompt, article):
    if not article:
        return "Nu există articol încărcat."
    return f"{article}\n\nÎntrebare: {prompt}"
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 5. AGENT SINGLE
@safe_handler
def run_agent(agent_slug, source_text, article, manual_text, provider_val, temp_val):
    if not agent_slug:
        return "Selectează un agent."
 
    text = article if source_text == "article" else manual_text
    if not text or not text.strip():
        return "Nu există text de analizat."
 
    result = generate_agent_response(
        agent_slug=agent_slug,
        stimulus=text,
        provider=provider_val,
        k=DEFAULT_K,
        temperature=float(temp_val),
        roles_path="assets/roles/roles.yaml",
    )
    return result.get("response", "")
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 6. ALL AGENTS
@safe_handler
def run_all_agents(source_text, article, manual_text, provider_val, temp_val):
    text = article if source_text == "article" else manual_text
    if not text or not text.strip():
        return "Nu există text."
 
    outputs = []
    for slug in load_agent_choices():
        result = generate_agent_response(
            agent_slug=slug,
            stimulus=text,
            provider=provider_val,
            k=DEFAULT_K,
            temperature=float(temp_val),
            roles_path="assets/roles/roles.yaml",
        )
        outputs.append(f"### 🤖 {slug}\n{result.get('response','')}")
 
    return "\n\n---\n\n".join(outputs)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 7. DEBATE
@safe_handler
def run_debate(source_text, article, manual_text, agents, turns, provider_val, temp_val):
    text = article if source_text == "article" else manual_text
    if not text or not text.strip():
        return "Nu există text."
    if not agents:
        return "Selectează agenți."
 
    messages = run_thread(
        stimulus=text,
        active_slugs=agents,
        total_turns=int(turns),
        provider=provider_val,
        k=DEFAULT_K,
    )
 
    # Unique accent color per agent slug
    AGENT_COLORS = {
        "anti_sistem":          {"bg": "#fff4e5", "border": "#f4a01c", "badge": "#f4a01c", "text": "#7a4500"},
        "conspirationist":      {"bg": "#fdecea", "border": "#e53935", "badge": "#e53935", "text": "#7b1010"},
        "anti_suveranist":      {"bg": "#e8f5e9", "border": "#2e7d32", "badge": "#2e7d32", "text": "#1b4d1e"},
        "pro_european":         {"bg": "#e3f2fd", "border": "#1565c0", "badge": "#1565c0", "text": "#0d3572"},
        "personalist_salvator": {"bg": "#f3e5f5", "border": "#7b1fa2", "badge": "#7b1fa2", "text": "#4a0072"},
    }
    DEFAULT_COLOR = {"bg": "#f5f5f5", "border": "#9e9e9e", "badge": "#9e9e9e", "text": "#333"}
 
    cards = []
    for msg in messages:
        slug    = msg.get("slug", msg.get("agent", ""))
        agent   = html.escape(msg.get("agent", "Agent"))
        handle  = html.escape(msg.get("handle", agent))
        turn_num = msg.get("turn", "?")
        response = html.escape(msg.get("response", msg.get("text", "")))
 
        c = AGENT_COLORS.get(slug, DEFAULT_COLOR)
 
        cards.append(f"""
<div style="
    background: {c['bg']};
    border-left: 5px solid {c['border']};
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
">
    <div style="margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
        <span style="
            background: {c['badge']};
            color: #fff;
            font-weight: 700;
            font-size: 0.8em;
            padding: 2px 9px;
            border-radius: 20px;
            letter-spacing: 0.03em;
        ">Turn {turn_num}</span>
        <span style="font-weight: 700; font-size: 0.95em; color: {c['text']};">🗣 {handle}</span>
        <span style="font-size: 0.8em; color: #888;">· {agent}</span>
    </div>
    <div style="
        font-size: 0.95em;
        line-height: 1.65;
        color: #1a1f2c;
        white-space: pre-wrap;
    ">{response}</div>
</div>
""")
 
    return "\n".join(cards)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 8. UI STATE
agent_choices = load_agent_choices()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 9. UI
CUSTOM_CSS = """
body, .gradio-container {
    background-color: #e6f0f8 !important;
    font-family: Inter, sans-serif !important;
    color: #1a1f2c !important;
}
.sidebar-panel {
    background: #f0f4f8 !important;
    border: 1px solid #d1d9e6 !important;
    border-radius: 16px !important;
    padding: 20px !important;
}
button.primary {
    background: #ff4d4d !important;
    color: white !important;
}
"""
 
with gr.Blocks(
    title="EchoChamber Studio",
    css=CUSTOM_CSS,
    theme=gr.themes.Default(),
) as demo:
 
    article_state = gr.State("")
    full_article_text = gr.State("")
 
    with gr.Row(elem_classes=["title-container"]):
        with gr.Column():
            gr.Markdown("# 🧠 EchoChamber Studio")
            gr.Markdown("Simulare de bule ideologice și dezbatere multi-agent")
 
    with gr.Row():
        with gr.Column(scale=1, min_width=340, elem_classes=["sidebar-panel"]):
            gr.Markdown("### Control")
 
            provider = gr.Dropdown(
                ["gemini", "gemini-flash"],
                value="gemini-flash",
                label="Provider",
            )
            model = gr.Textbox(value="default", label="Model")
            temperature = gr.Slider(0, 1, value=0.7, step=0.1, label="Temperature")
 
            gr.Markdown("---")
            gr.Markdown("### News")
 
            news_url = gr.Textbox(label="News URL")
            manual_text = gr.Textbox(label="Manual text", lines=4)
 
            load_btn = gr.Button("Load news", variant="primary")
 
            gr.Markdown("---")
            news_preview = gr.Textbox(label="Preview", lines=6, interactive=False)
 
        with gr.Column(scale=3):
            with gr.Tab("Chat"):
                chat_input = gr.Textbox(label="Question")
                chat_btn = gr.Button("Send", variant="primary")
                summary_btn = gr.Button("Summarize article")
                chat_out = gr.Textbox(label="Response", lines=10)
 
            with gr.Tab("Agent"):
                agent_select = gr.Dropdown(choices=agent_choices, label="Agent")
                source_select = gr.Radio(["manual", "article"], value="article")
                agent_btn = gr.Button("Run agent", variant="primary")
                agent_out = gr.Textbox(lines=12)
 
            with gr.Tab("All agents"):
                source_all = gr.Radio(["manual", "article"], value="article")
                all_btn = gr.Button("Run all", variant="primary")
                all_out = gr.Markdown()
 
            with gr.Tab("Debate"):
                source_debate = gr.Radio(["manual", "article"], value="article")
                agents_multi = gr.Dropdown(
                    choices=agent_choices,
                    multiselect=True,
                    label="Agents",
                )
                turns = gr.Slider(2, 8, value=4, step=1)
                debate_btn = gr.Button("Start debate", variant="primary")
                debate_out = gr.HTML()
 
    # ───────────────── EVENTS ─────────────────
    load_btn.click(
        fn=load_news,
        inputs=[news_url, manual_text],
        outputs=[news_preview, full_article_text],
    )
 
    chat_btn.click(
        fn=chat,
        inputs=[chat_input, full_article_text],
        outputs=chat_out,
    )
 
    summary_btn.click(
        fn=summarize_article,
        inputs=[full_article_text],
        outputs=chat_out,
    )
 
    agent_btn.click(
        fn=run_agent,
        inputs=[agent_select, source_select, full_article_text, manual_text, provider, temperature],
        outputs=agent_out,
    )
 
    all_btn.click(
        fn=run_all_agents,
        inputs=[source_all, full_article_text, manual_text, provider, temperature],
        outputs=all_out,
    )
 
    debate_btn.click(
        fn=run_debate,
        inputs=[source_debate, full_article_text, manual_text, agents_multi, turns, provider, temperature],
        outputs=debate_out,
    )
 
 
if __name__ == "__main__":
    demo.queue().launch(show_error=True)
 