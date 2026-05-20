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

import gradio as gr
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.agent import generate_agent_response

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

if __name__ == "__main__":
    demo.launch()