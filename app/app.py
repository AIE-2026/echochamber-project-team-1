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
import sys
from pathlib import Path
import html

import gradio as gr
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.agent import generate_agent_response
from core.graph import run_thread

# ─────────────────────────────────────────────────────────────────────────────


#Adaug funcția load_agent_choices()
def load_agent_choices():
    roles_path = PROJECT_ROOT / "assets" / "roles" / "roles.yaml"

    if not roles_path.exists():
        return []

    with open(roles_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    roles = data["agents"] if "agents" in data else data

    return list(roles.keys())

#Chat simplu minim
def chat(prompt):
    return f"Prompt primit:\n\n{prompt}"

#Funcția RAG
def rag_agent_response(agent_slug, stimulus, provider, k):
    if not agent_slug:
        return "Nu există agenți în roles.yaml.", ""

    if not stimulus.strip():
        return "Scrie un text politic.", ""

    try:
        result = generate_agent_response(
            agent_slug=agent_slug,
            stimulus=stimulus,
            provider=provider,
            k=int(k),
            temperature=0.3,
            roles_path="assets/roles/roles.yaml",
        )

        return result["response"], result["rag_text"]

    except Exception as e:
        return f"[Eroare: {type(e).__name__} — {e}]", ""
# Randare HTML pentru thread-ul multi-agent
# Randare HTML pentru thread-ul multi-agent
def render_thread_html(messages):
    cards = []

    for i, msg in enumerate(messages, start=1):
        agent = ""
        handle = ""
        text = ""
        turn = i

        if isinstance(msg, dict):
            turn = msg.get("turn", i)

            # Uneori core.graph pune rezultatul complet al agentului în msg["text"]
            raw_text = msg.get("text", "")

            if isinstance(raw_text, dict):
                agent = raw_text.get("agent_name", raw_text.get("agent_slug", "Agent"))
                handle = raw_text.get("agent_slug", msg.get("handle", msg.get("slug", "")))
                text = raw_text.get("response", "")
            else:
                agent = msg.get("agent", msg.get("agent_name", "Agent"))
                handle = msg.get("handle", msg.get("slug", msg.get("agent_slug", "")))
                text = raw_text or msg.get("response", "")
        else:
            agent = "Agent"
            handle = ""
            text = str(msg)

        agent = html.escape(str(agent))
        handle = html.escape(str(handle))
        text = html.escape(str(text))
        turn = html.escape(str(turn))

        cards.append(f"""
        <div style="border-left: 3px solid #e05a35; padding: .7rem 1rem; margin: .5rem 0; background: #f7f7f7; border-radius: 6px;">
            <div style="font-size: .8rem; color: #e05a35; font-weight: bold; text-transform: uppercase;">
                {agent}
            </div>
            <div style="font-size: .75rem; color: #666;">
                {handle} · #{turn}
            </div>
            <p style="color: #222; margin-top: .5rem;">
                {text}
            </p>
        </div>
        """)

    return "\n".join(cards)
# Funcție pentru rularea thread-ului multi-agent
def run_multi_agent_thread(
    stimulus,
    provider,
    total_turns,
    use_anti_sistem,
    use_conspirationist,
    use_anti_suveranist
):
    active_slugs = []

    if use_anti_sistem:
        active_slugs.append("anti_sistem")

    if use_conspirationist:
        active_slugs.append("conspirationist")

    if use_anti_suveranist:
        active_slugs.append("anti_suveranist")

    if not stimulus.strip():
        return "Scrie un text politic mai întâi."

    if not active_slugs:
        return "Selectează cel puțin un agent."

    try:
        messages = run_thread(
            stimulus=stimulus,
            active_slugs=active_slugs,
            total_turns=int(total_turns),
            provider=provider,
            k=3,
        )

        return render_thread_html(messages)

    except Exception as e:
        return f"[Eroare Multi-agent Thread: {type(e).__name__} — {e}]"    
#UI complet minim
#UI complet minim
agent_choices = load_agent_choices()

with gr.Blocks(title="EchoChamber") as demo:

    gr.Markdown("# EchoChamber")
    gr.Markdown("Aplicație minimă pentru testarea agenților RAG.")

    with gr.Tab("Chat simplu"):

        prompt_box = gr.Textbox(
            label="Prompt",
            lines=4,
            value="Explică ce este un LLM."
        )

        chat_button = gr.Button("Trimite")

        chat_output = gr.Textbox(
            label="Răspuns",
            lines=8
        )

        chat_button.click(
            fn=chat,
            inputs=prompt_box,
            outputs=chat_output
        )

    with gr.Tab("Agent RAG"):

        agent_dropdown = gr.Dropdown(
            choices=agent_choices,
            value=agent_choices[0] if agent_choices else None,
            label="Agent"
        )

        provider_dropdown = gr.Dropdown(
            choices=["gemini", "gemini-flash"],
            value="gemini-flash",
            label="Provider"
        )

        stimulus_box = gr.Textbox(
            label="Text politic",
            lines=4,
            value="CCR a decis anularea alegerilor după suspiciuni privind influențe externe."
        )

        k_slider = gr.Slider(
            minimum=1,
            maximum=10,
            value=5,
            step=1,
            label="Număr fragmente recuperate"
        )

        agent_button = gr.Button("Generează răspuns RAG")

        response_box = gr.Textbox(
            label="Răspuns agent",
            lines=8
        )

        context_box = gr.Textbox(
            label="Context recuperat",
            lines=12
        )

        agent_button.click(
            fn=rag_agent_response,
            inputs=[
                agent_dropdown,
                stimulus_box,
                provider_dropdown,
                k_slider
            ],
            outputs=[
                response_box,
                context_box
            ]
        )

    with gr.Tab("Multi-agent thread"):

        thread_stimulus = gr.Textbox(
            label="Text politic",
            value="CCR a decis anularea alegerilor după suspiciuni privind influențe externe.",
            lines=4
        )

        thread_provider = gr.Dropdown(
            choices=["gemini", "gemini-flash"],
            value="gemini-flash",
            label="Provider"
        )

        thread_turns = gr.Slider(
            minimum=2,
            maximum=8,
            value=4,
            step=1,
            label="Număr intervenții"
        )

        use_anti_sistem = gr.Checkbox(
            value=True,
            label="Anti-sistem"
        )

        use_conspirationist = gr.Checkbox(
            value=True,
            label="Conspiraționist"
        )

        use_anti_suveranist = gr.Checkbox(
            value=True,
            label="Anti-suveranist"
        )

        thread_button = gr.Button("Pornește thread")

        thread_output = gr.HTML(
            label="Thread generat"
        )

        thread_button.click(
            fn=run_multi_agent_thread,
            inputs=[
                thread_stimulus,
                thread_provider,
                thread_turns,
                use_anti_sistem,
                use_conspirationist,
                use_anti_suveranist
            ],
            outputs=thread_output
        )
if __name__ == "__main__":
    demo.launch()