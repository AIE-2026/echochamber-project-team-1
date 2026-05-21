# Ethics and limitations

EchoChamber is a teaching and research prototype for simulating discursive responses with AI agents.  
The goal is educational: to understand RAG, role prompts, LangGraph workflows, multi-agent interaction, and the risks of generated political discourse.  

EchoChamber must not be presented as a system that measures real public opinion, predicts political behavior, or represents real social groups.

---

## 1. What the agents are

The agents in this project are simulated discursive roles.  
They are not real people.  
They are not voters.  
They are not representatives of parties, communities, demographic groups, or social categories.

Each agent is created from:
- a YAML role prompt;
- retrieved fragments from a corpus;
- an LLM-generated response;
- workflow rules defined in the application.

Correct wording:  
> “The anti-system agent generated a simulated anti-system framing.”

Incorrect wording:  
> “Anti-system voters think this.”

---

## 2. What the outputs mean

Generated responses are not factual claims.  
They are synthetic comments produced by a model under a role constraint.

Even when RAG is used, retrieved context is only supporting material.  
Retrieved context does not automatically make the generated answer true.

All outputs must be interpreted critically by students, researchers, or instructors.

---

## 3. Main risks

| Risk | What it means | Minimum control |
|------|--------------|-----------------|
| Anthropomorphism | Users may treat agents as real people | Always label them as simulated agents |
| False factuality | Generated text may sound like verified information | Separate retrieved context from generated response |
| Corpus bias | Corpus may contain biased or unbalanced content | Document corpus source and known limits |
| Amplification | Multi-agent threads may intensify conflict or polarization | Limit number of turns and review outputs |
| Misrepresentation | A role may be confused with a real social group | Use “constructed discursive position,” not “group opinion” |
| Privacy | Data may include personal identifiers | Avoid unnecessary personal data and do not profile individuals |
| Political misuse | Outputs may be reused as persuasion material | Use only for education and analysis |

---

## 4. Data protection rules

Use only public or classroom-approved data.

Do not commit API keys, `.env` files, private documents, or personal data to GitHub.  
Avoid storing unnecessary identifiers such as usernames, names, contact details, or links to individual profiles.

If real comments are used, treat them as research material, not copyable content.  
Use short excerpts only when needed for analysis.

Do not build profiles of real users.  
Do not infer sensitive attributes (political identity, religion, ethnicity, health, etc.) from individual comments.

---

## 5. Responsible use

EchoChamber may be used to:
- test how role prompts shape generated responses;
- compare discursive framings;
- inspect how RAG affects generated text;
- study multi-agent interaction dynamics;
- support classroom discussion about AI, discourse, bias, and governance.

EchoChamber must not be used to:
- generate political persuasion material;
- imitate real citizens or groups;
- publish synthetic comments as authentic public opinion;
- target individuals or social groups;
- make factual claims about public events without verification;
- replace empirical social research.

---

## 6. Human oversight

Human interpretation is required.

Students must inspect:
- relevance of retrieved context;
- adherence of generated output to role;
- presence of unsupported claims;
- escalation or polarization in interactions;
- potential misleading interpretations.

No generated output should be used outside the classroom without human review.

---

## 7. Transparency in the application

The application should clearly indicate:
- which agent generated the response;
- input used;
- model/provider used;
- whether RAG context was retrieved;
- number of retrieved fragments;
- that outputs are synthetic.

Recommended disclaimer:
> EchoChamber generates simulated political-discourse responses. The agents are fictional analytical constructs, not real people and not representatives of real social groups. Outputs may contain bias, exaggeration, or unsupported claims. Use only for education and critical analysis.

---

## 8. How to present results

Recommended phrasing:
- “The agent generated a simulated framing.”
- “The thread shows possible escalation under this configuration.”
- “The response is based on retrieved corpus fragments, not verified facts.”
- “The result requires human interpretation.”

Avoid:
- “This group believes…”
- “The public thinks…”
- “The model proves…”
- “Voters would say…”

---

## 9. Minimal logging for reproducibility

Record:
- input text;
- agent slug;
- provider/model;
- retrieval parameter k;
- number of turns;
- routing strategy;
- observed issues.

Example:
```text
input: CCR a decis anularea alegerilor după suspiciuni privind influențe externe.
agents: anti_sistem, conspirationist, pro_european
provider: gemini
k: 3
turns: 4
router: round-robin
observed problem: mild repetition in turns 3–4

EchoChamber is a learning tool for studying simulated discourse systems.
It does not replace empirical research, factual verification, or human judgment.
Responsibility for interpretation lies with the researcher, not the system.