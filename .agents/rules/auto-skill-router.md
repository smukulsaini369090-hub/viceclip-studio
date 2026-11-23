---
name: auto-skill-router
description: Permanent, self-updating Skill & Repository Routing System that automatically discovers, indexes, adopts, and chains skills with zero manual intervention.
trigger: always_on
---

# Self-Updating Skill & Repository Routing System (Permanent Always-On Rule)

This rule is **permanently active** across all sessions, conversations, and subagents in this environment. It ensures that the model automatically discovers available skills, keeps its index synchronized with the filesystem in real time, identifies user intent, resolves the exact skills needed, chains them logically, and executes them without requiring manual prompts.

---

## 1. Mandatory Response Header (Status Tag)

**EVERY** response that addresses a task, question, feature, bug, design, or implementation MUST begin with this exact header on Line 1:

```text
⚡ Active Skills: [Skill 1, Skill 2]
```

- When matching one or more skills: list the active skill names (e.g. `⚡ Active Skills: [brainstorming, writing-plans]` or `⚡ Active Skills: [ui-ux-pro-max, ui-styling]`).
- For purely casual chit-chat or trivial queries that require no engineering methodology: `⚡ Active Skills: None`.
- **When a new skill is auto-adopted during this turn:** Prepend a one-time notice immediately above or alongside the status line:
  ```text
  🆕 Auto-Adopted Skills: [New Skill Name]
  ⚡ Active Skills: [New Skill Name, ...]
  ```

---

## 2. Zero-Touch Auto-Adoption Protocol (Self-Healing & Auto-Update)

1. **Autonomous Filesystem Inspection:**
   At the start of every session—or whenever a user prompt refers to a domain/tool not currently covered in the table below—the agent MUST check the live directory contents of watched skill locations:
   - Workspace Skills: `.agents/skills/`, `.agent/skills/`
   - Global Config Skills: `~/.gemini/config/skills/`, `~/.gemini/config/plugins/`
   - Builtin Skills: `~/.gemini/antigravity/builtin/skills/`
   - Full Offline Library: `~/.agents/skills_library/skills/`

2. **Auto-Adopt New Skills (Zero Prompts Required):**
   - If a new skill directory containing `SKILL.md` (or repo containing `README.md`) exists that is **NOT** present in the Master Skill Index Table below:
     1. Read its `SKILL.md` or manifest frontmatter (name, description, instructions).
     2. Immediately append it to the Master Skill Index Table in `auto-skill-router.md` (and workspace `GEMINI.md` / `AGENTS.md`).
     3. Apply that newly discovered skill to the user's current task right away.
     4. Display `🆕 Auto-Adopted Skills: [New Skill Name]`.

3. **Auto-Purge Stale Skills:**
   - If an indexed skill folder has been deleted or moved from disk, automatically remove or update its row in the Master Table so the index never goes stale.

---

## 3. Strict Auto-Execution Protocol

1. **Intent-First Silent Matching:**
   Before writing any code or answering questions, silently analyze the user's intent against the live **Master Skill Index Table**. Match concepts, goals, tech stack, domain keywords, and file types.
2. **Auto-Enable & Full Adherence:**
   When a match is found, immediately adopt and strictly follow the skill's methodology, checklists, and scripts (e.g. Red-Green-Refactor for TDD, root-cause tracing for systematic debugging, local search for UI/UX Pro Max, 9-pass checklist for unslop).
3. **Multi-Skill Chaining Matrix:**
   When a task spans multiple disciplines, chain the skills in logical execution order:
   - **New Feature / Product Idea:** `brainstorming` ➔ `writing-plans` ➔ `ui-ux-pro-max` ➔ `test-driven-development` ➔ `verification-before-completion`.
   - **Bug / Error / Crash / Test Failure:** `systematic-debugging` ➔ `test-driven-development` ➔ `verification-before-completion`.
   - **UI / Frontend Polish / De-Slop:** `unslop` ➔ `ui-ux-pro-max` ➔ `ui-styling` ➔ `verification-before-completion`.
   - **Multi-Task / Complex Execution:** `writing-plans` ➔ `subagent-driven-development` ➔ `verification-before-completion`.
   - **Git Finalization / Branch Close:** `finishing-a-development-branch` ➔ `verification-before-completion`.
4. **Zero Unnecessary Prompts:**
   Never ask the user "Which skill should I use?" or "Do you want me to use TDD / UI-UX Pro Max?". Silently select the highest-affinity skills and proceed immediately.

---

## 4. Master Skill Index Table (Live Synced)

| Skill / Suite | Scope & Path | Core Capabilities & Deliverables | Auto-Trigger Keywords & User Intents |
| :--- | :--- | :--- | :--- |
| **`brainstorming`** | Superpowers (`skills/brainstorming/`) | Requirements elicitation, tradeoff analysis, architectural specs, alternative approaches before code. | `build`, `create`, `add feature`, `plan`, `new idea`, `design new`, `what should we do`, `concept` |
| **`test-driven-development`** | Superpowers (`skills/test-driven-development/`) | Red-Green-Refactor cycle, failing tests first, boundary testing, mock isolation. | `test`, `unit test`, `integration test`, `tdd`, `pytest`, `jest`, `vitest`, `write test`, `red-green` |
| **`systematic-debugging`** | Superpowers (`skills/systematic-debugging/`) | 4-phase root cause investigation, hypothesis testing, log tracing, regression isolation. | `bug`, `fix`, `error`, `exception`, `crash`, `broken`, `failed`, `500`, `timeout`, `doesn't work` |
| **`ui-ux-pro-max`** | UI/UX Pro Max (`skills/ui-ux-pro-max/`) | 80 UI styles, 194 color palettes, 74 font pairings, 141 UX rules, 25 chart types, 22 stacks. Local search: `scripts/search.py`. | `ui`, `ux`, `color palette`, `font`, `typography`, `theme`, `aesthetic`, `spacing`, `dark mode`, `accessibility` |
| **`unslop`** | Unslop Engine (`skills/unslop/`) | 9-pass anti-slop overhaul: removes rainbow gradients, glow blobs, shouty caps, emoji badges. | `unslop`, `polish ui`, `redesign`, `clean up ui`, `vibecoded`, `remove glow`, `professional look` |
| **`ui-styling`** | UI/UX Pro Max (`skills/ui-styling/`) | Component engineering with shadcn/ui + Tailwind CSS, accessible dialogs, forms, layout grids. | `tailwind`, `shadcn`, `css`, `responsive layout`, `button styling`, `modal style`, `component ui` |
| **`subagent-driven-development`** | Superpowers (`skills/subagent-driven-development/`) | Autonomous parallel execution of modular tasks via subagents with code reviews. | `parallel`, `autonomous subagent`, `execute plan`, `dispatch agents`, `large implementation` |
| **`writing-plans`** | Superpowers (`skills/writing-plans/`) | Structured, phased implementation plans with verification steps and file targets. | `spec`, `plan`, `roadmap`, `step by step plan`, `implementation outline`, `breakdown` |
| **`executing-plans`** | Superpowers (`skills/executing-plans/`) | Disciplined sequential execution of approved plans without drifting off-track. | `execute plan`, `implement plan`, `continue plan`, `next step` |
| **`verification-before-completion`** | Superpowers (`skills/verification-before-completion/`) | Evidence-first validation (build, lint, unit tests, live health checks) before asserting done. | `verify`, `done`, `finished`, `complete`, `check work`, `ready to ship` |
| **`finishing-a-development-branch`** | Superpowers (`skills/finishing-a-development-branch/`) | Git commit hygiene, branch squash, PR descriptions, merge verification. | `merge`, `git commit`, `git push`, `pr`, `pull request`, `close branch` |
| **`requesting-code-review`** | Superpowers (`skills/requesting-code-review/`) | Pre-merge architectural and safety review request against project standards. | `review code`, `code review`, `audit code`, `pre-merge check` |
| **`receiving-code-review`** | Superpowers (`skills/receiving-code-review/`) | Rigorous, non-defensive analysis and resolution of review comments. | `address feedback`, `review comments`, `incorporate feedback` |
| **`using-git-worktrees`** | Superpowers (`skills/using-git-worktrees/`) | Clean isolated workspaces for multi-branch concurrent development. | `worktree`, `isolated workspace`, `branch isolation` |
| **`banner-design`** | UI/UX Pro Max (`skills/banner-design/`) | Social banners, hero graphics, ad creatives, print assets. | `banner`, `hero section`, `thumbnail`, `marketing image`, `ad graphic` |
| **`design-system`** | UI/UX Pro Max (`skills/design-system/`) | 3-layer design tokens (primitive ➔ semantic ➔ component), CSS variables. | `design tokens`, `design system`, `token scale`, `color tokens` |
| **`brand`** | UI/UX Pro Max (`skills/brand/`) | Tone of voice, visual identity guidelines, asset management. | `brand`, `brand voice`, `tone`, `messaging`, `identity` |
| **`slides`** | UI/UX Pro Max (`skills/slides/`) | Interactive HTML presentation decks with Chart.js and token styling. | `slides`, `presentation`, `deck`, `pitch deck`, `chart presentation` |
| **`writing-skills`** | Superpowers (`skills/writing-skills/`) | Authoring, testing, and packaging new skills according to Antigravity standards. | `new skill`, `author skill`, `create skill`, `skill template` |
| **`diagnosing-superpowers`** | Superpowers (`skills/diagnosing-superpowers/`) | Diagnosing stalled sessions, ignored plans, or harness integration bugs. | `diagnose agent`, `agent stuck`, `session issue`, `bug in skill` |
| **`agentic-awesome-skills`** | AAS Library (`~/.agents/skills_library/`) | 3,131+ offline specialized playbooks (Security, DevOps, Mobile, API, Data). | `security audit`, `api platform`, `devops`, `specialized skill`, `activate skill` |
| **`mcp-app-development`** | Builtin (`builtin/skills/mcp-app-development`) | Interactive UI for MCP server tools in sidebar or modal panels. | `mcp app`, `mcp ui`, `interactive mcp`, `custom tool ui` |
| **`automation`** | Builtin (`builtin/skills/automation`) | Automated recurring cron or interval tasks in the background. | `schedule`, `recurring`, `cron`, `daily automation`, `timer` |
| **`generative_ui`** | Builtin (`builtin/skills/generative_ui`) | Rich interactive HTML widgets and data visualizers inside chat. | `interactive widget`, `visual calculator`, `diagram widget` |
| **`run-workflow`** | Builtin (`builtin/skills/run-workflow`) | Python workflow orchestration scripts with multi-agent stages. | `workflow script`, `fan out agents`, `agent pipeline` |
| **`antigravity_guide`** | Builtin (`builtin/skills/antigravity_guide`) | Quick reference and manual for Antigravity CLI, IDE, rules, and skills. | `antigravity`, `agy cli`, `antigravity guide`, `slash command` |
| **`agy-customizations`** | Builtin (`builtin/skills/agy-customizations`) | Customization loading priority, discovery mechanisms, rules & plugins guide. | `customizations`, `rules guide`, `plugin architecture`, `discovery priority` |

---

| **`design`** | Auto-Adopted (`c:\Users\mukul\Downloads\ViceClip-Studio\.agents\skills\design\SKILL.md`) | Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, G | `design` |

| **`dispatching-parallel-agents`** | Auto-Adopted (`c:\Users\mukul\Downloads\ViceClip-Studio\.agents\skills\dispatching-parallel-agents\SKILL.md`) | Use when facing 2+ independent tasks that can be worked on without shared state or sequential depend | `dispatching-parallel-agents` |

| **`using-superpowers`** | Auto-Adopted (`c:\Users\mukul\Downloads\ViceClip-Studio\.agents\skills\using-superpowers\SKILL.md`) | Use when starting any conversation - establishes how to find and use skills, requiring skill invocat | `using-superpowers` |

| **`migrate-agent-settings`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\migrate-agent-settings\SKILL.md`) | Migrates the user's MCP servers, skills, slash commands, subagents, and instruction files from other | `migrate-agent-settings` |

| **`migrate-workflows`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\migrate-workflows\SKILL.md`) | Automatically migrate legacy workflows to modern skills across global and workspace configurations.  | `migrate-workflows` |

| **`native_swarm`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\native_swarm\SKILL.md`) | (Preview & Quota Heavy) Run a swarm: several agents working in parallel on | `native_swarm` |

| **`permissioned-github`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\permissioned-github\SKILL.md`) | Guidelines for interacting with GitHub and request permissions from the user when commands fail due  | `permissioned-github` |

| **`plugin`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\plugin\SKILL.md`) | How to manage and create plugins — namespaced bundles of skills, agents, rules, MCP servers and hook | `plugin` |

| **`swarm_monitor`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\swarm_monitor\SKILL.md`) | ONLY for the native-swarm worker whose brief says it is the monitor. On a | `swarm_monitor` |

| **`swarm_narrator`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\swarm_narrator\SKILL.md`) | ONLY for the native-swarm worker whose brief says it is the narrator. It | `swarm_narrator` |

| **`swarm_pane`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\swarm_pane\SKILL.md`) | What the coordinator writes so the Swarm UI's Overview can show the swarm's | `swarm_pane` |

| **`ui-plugin-navigation`** | Auto-Adopted (`C:\Users\mukul\.gemini\antigravity\builtin\skills\ui-plugin-navigation\SKILL.md`) | Discover UI plugin panels relevant to the current task and surface a one-click pill in chat to open  | `ui-plugin-navigation` |

## 5. Execution Examples

- **User:** *"I want to add a feature to let users export clips directly to TikTok."*  
  **Routing:** Matches `brainstorming` + `writing-plans` + `ui-ux-pro-max`.  
  **Output starts with:** `⚡ Active Skills: [brainstorming, writing-plans, ui-ux-pro-max]`

- **User:** *"The FastAPI backend crashes with a 500 error on video download."*  
  **Routing:** Matches `systematic-debugging` + `test-driven-development`.  
  **Output starts with:** `⚡ Active Skills: [systematic-debugging, test-driven-development]`

- **User:** *"The settings modal looks too flashy and AI-generated. Fix it."*  
  **Routing:** Matches `unslop` + `ui-ux-pro-max` + `ui-styling`.  
  **Output starts with:** `⚡ Active Skills: [unslop, ui-ux-pro-max, ui-styling]`

- **User adds a new skill:** *`git clone ...` into `.agents/skills/my-new-tool`*  
  **Routing:** Auto-detected on next prompt, added to table.  
  **Output starts with:**  
  `🆕 Auto-Adopted Skills: [my-new-tool]`  
  `⚡ Active Skills: [my-new-tool]`
