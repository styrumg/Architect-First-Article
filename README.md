# Tell Your Coding Agent to Work as an Architect First

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21544417.svg)](https://doi.org/10.5281/zenodo.21544417)

![Architect First — declare intent, show the design, pass the gates, then code](assets/Architect-First-Banner.png)

**Let it declare intent, let it show the design, let both pass the gates — then, and only then, let it code.**

A position paper on making AI coding assistants produce inspectable intermediate representations — intent and design — and checking them with small, deterministic, opinion-free programs *before* any code is written.

## The idea in 30 seconds

Before writing code, the assistant fills in a short **questionnaire**: what parts the system has, how they talk to each other, what happens when something crashes, what it is *not sure about*. Then a small, boring, reliable program — **not another AI** — checks the answers against a checklist of mistakes that real systems have made in production. Missing or fishy answer → fix the plan first, then write code. A second AI judging the first can be sweet-talked; a smoke detector cannot.

## The pipeline

```
prose spec
  → thin spec? AI QUESTIONS YOU FIRST — and declines rather than guesses
  → AI DECLARES the questionnaire (intent)
  → deterministic CHECKER reviews it (Gate 1)
        ↑____ blocking findings go back to the AI ____↓
  → blueprint: typed messages, state machines, invariants (design)
  → SECOND boring checker validates it (Gate 2)
        ↑____ blocking findings go back ____↓
  → code that traceably implements the blueprint
  → existing code scanners check the code (Gate 3 — they already exist)
  → every decision logged to the project diary
```

Code-level checking is mature (SAST tools exist for every ecosystem). Checking at the *intent* and *design* levels today is a meeting. The paper argues that's the actual gap — and builds the two missing gates.

## What's in this repo

| Path | What it is |
|------|------------|
| `Tell-Your-Coding-Agent-to-Work-as-an-Architect-First.pdf` | The latest full paper with related work and references |
| `Architect-First-2pager.pdf` | The two-page summary — the whole argument in plain language |
| `examples/reference-run/` | A worked example: a payment worker taken through all three gates (thin requirements → blocked SIM → revised SIM → traceable FAM → vulnerable code blocked → fixed code passing) |
| `CITATION.cff` | Machine-readable citation metadata |
| `CHANGELOG.md` | Revision history |

New here? Read the two-pager first; the full paper is the detailed version of the same argument.

## Status and honest limits

**Claimed (engineering):** the assembly — questions first, declared intent, two deterministic gates, existing code scanners as the third, diary — is coherent, buildable, and built. A reference run shows the loop can improve a design in three rounds.

**Not claimed (science):** that it *reliably* improves software. That requires a blind A/B test: same AI, same real issues, with and without the gates — including whether the questionnaire tells the truth about the code, and whether the gates cry wolf often enough to get disabled. The experiment is designed to be able to fail.

The paper ends with an explicit limits section: what the gates cannot see, where false positives will come from, and which system types fit poorly.

## Discussing and contributing

- **Bugs in the argument** (wrong claims, broken logic, missing prior art): open an issue.
- **Prior art**: if you know of earlier work on machine-checkable intent/design representations for AI-generated code, that's the most valuable issue you can file.
- **Trying the gates on your own agent**: also welcome — report what they catch and, especially, what they get wrong.

## Citation

```bibtex
@misc{rumega2026architectfirst,
  author = {Rumega, Stanislav},
  title  = {Tell Your Coding Agent to Work as an Architect First:
            Let it declare intent, let it show the design,
            let both pass the gates — then, and only then, let it code},
  year   = {2026},
  howpublished = {\url{https://github.com/styrumg/Architect-First-Article}}
}
```

## License

The paper is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The worked-example artifacts in `examples/` are released under the same license. The full SIM/FAM schemas and gate implementations are held back until the cold-test validation runs (see the paper, Section 10) — see `CHANGELOG.md` and the release notes for scope.
