# EchoChamber Studio

EchoChamber Studio is a prototype AI application that simulates how different discursive agents respond to the same political or social news article.

## Project overview

EchoChamber Studio is a local Gradio-based prototype for exploring how different simulated discursive agents react to the same political or social text. The application can load or use a news article, summarize it, generate a response from one selected agent, compare responses from all available agents, and run a short multi-agent debate.

The system combines role definitions, retrieval from agent-specific comment corpora, and LLM generation. It is designed as a research and educational prototype for studying discursive framing, narrative variation, polarization, and the limits of automated interpretation in political communication.

## Why this project matters

Political and social communication often involves competing frames, emotional language, distrust, identity claims, and repeated narratives. EchoChamber Studio explores how AI agents can simulate different discursive positions around the same input text.

The project does not measure real public opinion. The agents generate simulated responses based on role definitions, retrieved examples, and model output.

## Main workflow

Single-agent workflow:

```text
news/text → selected agent role → retrieved similar comments → LLM → simulated response
```

Multi-agent debate workflow:

```text
news/text → selected agents → conversation state → multi-agent thread
```

The article or input text is the main object of the response. Retrieved comments are used as discursive context and style examples, not as factual evidence. The role file defines each agent's voice, worldview, and response rules.

## Repository structure

```text
app/                 Gradio user interface
core/                Backend logic for agents, retrieval, and multi-agent debate
assets/roles/        YAML definitions for simulated agents
assets/vectorstores/ FAISS indexes used for retrieval
data/bubbles/        Comment corpora grouped by agent/bubble
notebooks/           Development notebooks and individual work
docs/                Ethics, limitations, and project documentation
outputs/             Optional generated outputs
scripts/             Data processing and utility scripts
collector/           Collection utilities for public data sources
reports/             Project reports and documentation outputs
```

## How to run locally

Windows PowerShell:

```powershell
git pull
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python -m app.app
```

The application runs locally by default.

## Environment variables

Create a local `.env` file based on `.env.example`. Do not commit `.env` or API keys.

Example variables used by the project:

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_FLASH_MODEL=gemini-2.5-flash

DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-chat

OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openai/gpt-oss-120b:free
```

The exact provider used can be selected from the application interface. Provider availability depends on local API keys, provider quotas, and model rate limits.

## Application features

- **Chat**: ask the selected model a direct question about the loaded or manually provided article.
- **Summarize article**: generate a short summary of the loaded article.
- **Agent**: generate one response from a selected simulated agent.
- **All agents**: run all available agents on the same input and compare their responses.
- **Debate**: run a short multi-agent conversation between selected agents.

## Agents

Available agents are defined in `assets/roles/roles.yaml`.

Examples:

- `anti_sistem`
- `anti_suveranist`
- `conspirationist`
- `pro_european`
- `personalist_salvator`

Each agent is defined by a role, voice, worldview, and response rules. The agents are simulated discursive roles, not real people or real social groups.

## Technical components

```text
core/retriever.py    Searches the FAISS vectorstore for relevant comments
core/agent.py        Combines role, retrieved context, and LLM response
core/graph.py        Coordinates a multi-agent conversation
app/app.py           Exposes the system through a Gradio interface
```

The retrieval component uses FAISS vector indexes stored under `assets/vectorstores/`. These indexes are used to retrieve similar comments for each agent and provide discursive context to the language model.

## Ethics and limitations

- Agents are simulated roles, not real people or real social groups.
- Generated responses are not factual evidence.
- Retrieved comments are used as discursive context, not proof.
- The app may produce biased, generic, inaccurate, or harmful outputs.
- News extraction from URL may fail on some websites.
- The system should not be used to infer real public opinion.
- API keys and private data must never be committed.
- Outputs should be reviewed by humans before interpretation or reuse.
- The quality of responses depends on the corpus, vectorstores, prompts, and model provider.
- Simulated debates may amplify conflictual or polarizing language because agents are designed to reproduce specific discursive styles.

See also: `docs/ethics_checklist.md`

## Team contributions

| Name / GitHub handle | Main contribution |
|---|---|
| Osaci Cosmin / @osacicozmin | `anti_sistem` agent, anti-system bubble/vectorstore work, RAG testing, provider debugging, DeepSeek/OpenRouter integration |
| <Name / handle> | <Contribution> |
| <Name / handle> | <Contribution> |
| <Name / handle> | <Contribution> |
| <Name / handle> | <Contribution> |

## Known issues

- Some news websites block automatic article extraction.
- Some agents may respond too generically.
- The debate uses a simple routing logic.
- The app is a local prototype and is not deployed.
- The quality of responses depends on the corpus and model provider.
- Free provider models may return rate-limit errors.
- Provider quotas may affect live demonstrations.
- The system should not be interpreted as a real measurement of public opinion.

## License / usage note

This project is a research and educational prototype. Outputs should be reviewed by humans before interpretation or reuse.