# core/graph.py
# ==============
# LangGraph orchestration for the agentic debate (Tab 3).
#
# HOW THE DEBATE WORKS:
#   This is NOT a fixed round-robin. After each message, a "router" LLM call
#   decides who speaks next based on the thread content. Agents address each
#   other directly by @handle, agree or disagree with previous messages.
#
#   Flow:
#     START → [router] → [agent_X] → [router] → [agent_Y] → ... → END
#
#   The router picks the next agent based on who was just challenged,
#   who hasn't spoken recently, or who has the strongest reaction to give.
#
# Students: you don't need to modify this file.

from typing import TypedDict
import argparse

from langgraph.graph import StateGraph, START, END

from core.agent import generate_agent_response


# Handles folosite pentru afișarea thread-ului.
# Puteți păstra aceste valori sau le puteți adapta la agenții echipei.
HANDLES = {
    "anti_sistem": "@LibertateRO99",
    "conspirationist": "@AdevarulViu",
    "pro_european": "@EuroOptimistRO",
    "anti_suveranist": "@CetateanEU",
    "personalist_salvator": "@Marian_GS_Fan",
}


class ThreadState(TypedDict):
    stimulus: str       # textul politic inițial
    messages: list      # lista mesajelor produse până acum
    active_slugs: list  # agenții care participă
    total_turns: int    # numărul total de intervenții
    current_turn: int   # câte intervenții au fost produse
    next_slug: str      # agentul ales de router
    provider: str       # gemini / deepseek
    k: int              # numărul de fragmente recuperate din FAISS


def thread_to_text(messages):
    """
    Transformă lista de mesaje într-un text citibil.
    Acest text va fi trimis agentului ca THREAD ANTERIOR.
    """
    if not messages:
        return "(nu există mesaje anterioare)"

    lines = []

    for msg in messages:
        line = f'Turn {msg["turn"]} — {msg["handle"]}: {msg["text"]}'
        lines.append(line)

    return "\n".join(lines)


def pick_next_agent(active_slugs, current_turn):
    """
    Router simplu round-robin.
    Exemplu:
    anti_sistem → conspirationist → pro_european → anti_sistem ...
    """
    index = current_turn % len(active_slugs)
    return active_slugs[index]


def router_node(state: ThreadState):
    """
    Nodul router decide cine vorbește următorul
    sau oprește conversația dacă s-a ajuns la total_turns.
    """
    if state["current_turn"] >= state["total_turns"]:
        return {"next_slug": "__end__"}

    next_slug = pick_next_agent(
        state["active_slugs"],
        state["current_turn"]
    )

    return {"next_slug": next_slug}


def route_decision(state: ThreadState):
    """
    Funcția folosită de conditional edge.
    Returnează următorul nod către care merge graful.
    """
    return state["next_slug"]


def make_agent_node(slug):
    """
    Creează un nod pentru un agent.
    Fiecare nod:
    - citește stimulusul;
    - citește thread-ul anterior;
    - cheamă generate_agent_response();
    - adaugă mesajul nou în messages;
    - crește current_turn.
    """

    def agent_node(state: ThreadState):
        # TODO 1:
        # transformă state["messages"] în text folosind thread_to_text()
        thread_text = thread_to_text(state["messages"])

        # TODO 2:
        # ia handle-ul agentului curent din HANDLES
        my_handle = HANDLES.get(slug, f"@{slug}")

        # TODO 3:
        # dacă există mesaje anterioare, identifică ultimul vorbitor
        # și construiește o instrucțiune prin care agentul răspunde direct lui
        #
        # dacă nu există mesaje, agentul este primul și reacționează la stimulus
        if state["messages"]:
            last_message = state["messages"][-1]
            last_handle = last_message["handle"]

            task = (
                f"Răspunde direct lui {last_handle} "
                f"și continuă conversația într-un stil natural."
            )
        else:
            task = (
                "Ești primul care intervine în conversație. "
                "Reacționează la stimulus și exprimă-ți poziția."
            )

        # TODO 4:
        # construiește agent_input cu:
        # [STIMULUS]
        # [THREAD ANTERIOR]
        # [SARCINĂ]
        agent_input = f"""
[STIMULUS]
{state["stimulus"]}

[THREAD ANTERIOR]
{thread_text}

[SARCINĂ]
{task}
"""

        # TODO 5:
        # cheamă generate_agent_response()
        result = generate_agent_response(
            agent_slug=slug,
            stimulus=agent_input,
            provider=state["provider"],
            k=state["k"]
        )

        # TODO 6:
        # construiește new_message cu:
        # agent, slug, handle, text, turn
        new_message = {
            "agent": slug,
            "slug": slug,
            "handle": my_handle,
            "text": result,
            "turn": state["current_turn"] + 1
        }

        # TODO 7:
        # returnează update-ul pentru state:
        # messages + current_turn
        return {
            "messages": state["messages"] + [new_message],
            "current_turn": state["current_turn"] + 1
        }

    return agent_node


def build_graph(active_slugs):
    """
    Construiește graful LangGraph:
    START → router → agent_node → router → ... → END
    """
    workflow = StateGraph(ThreadState)

    # TODO 1:
    # adaugă nodul router
    workflow.add_node("router", router_node)

    # TODO 2:
    # adaugă câte un nod pentru fiecare agent din active_slugs
    for slug in active_slugs:
        workflow.add_node(slug, make_agent_node(slug))

    # TODO 3:
    # adaugă edge START → router
    workflow.add_edge(START, "router")

    # TODO 4:
    # construiește route_map:
    # fiecare slug merge către nodul lui
    # "__end__" merge către END
    route_map = {
        slug: slug for slug in active_slugs
    }

    route_map["__end__"] = END

    # TODO 5:
    # adaugă conditional edge din router
    workflow.add_conditional_edges(
        "router",
        route_decision,
        route_map
    )

    # TODO 6:
    # fiecare agent trebuie să revină la router
    for slug in active_slugs:
        workflow.add_edge(slug, "router")

    # TODO 7:
    # compilează și returnează graful
    return workflow.compile()


def run_thread(
    stimulus,
    active_slugs,
    total_turns=4,
    provider="gemini",
    k=3
):
    """
    Funcția principală folosită de notebook și aplicație.

    Returnează lista finală de mesaje.
    """
    # TODO 1:
    # construiește graful cu build_graph(active_slugs)
    graph = build_graph(active_slugs)

    # TODO 2:
    # creează initial_state
    initial_state = {
        "stimulus": stimulus,
        "messages": [],
        "active_slugs": active_slugs,
        "total_turns": total_turns,
        "current_turn": 0,
        "next_slug": "",
        "provider": provider,
        "k": k
    }

    # TODO 3:
    # rulează graph.invoke(initial_state)
    final_state = graph.invoke(initial_state)

    # TODO 4:
    # returnează final_state["messages"]
    return final_state["messages"]


def main():
    """
    Permite testarea din terminal:

    python -m core.graph --agents anti_sistem conspirationist pro_european --text "CCR a decis anularea alegerilor după suspiciuni privind influențe externe." --turns 4 --provider gemini
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--agents", nargs="+", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--turns", type=int, default=4)
    parser.add_argument("--provider", default="gemini")
    parser.add_argument("--k", type=int, default=3)

    args = parser.parse_args()

    messages = run_thread(
        stimulus=args.text,
        active_slugs=args.agents,
        total_turns=args.turns,
        provider=args.provider,
        k=args.k
    )

    print(thread_to_text(messages))


if __name__ == "__main__":
    main()