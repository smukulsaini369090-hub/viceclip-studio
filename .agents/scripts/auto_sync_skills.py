"""
Self-Updating Skill & Repository Scanner for Antigravity
Scans workspace, global config, plugins, and AAS library.
Syncs entries with auto-skill-router.md automatically.
"""
import os
import re
import sys

ROUTER_PATHS = [
    r"c:\Users\mukul\Downloads\ViceClip-Studio\.agents\rules\auto-skill-router.md",
    r"c:\Users\mukul\Downloads\ViceClip-Studio\GEMINI.md",
    r"c:\Users\mukul\Downloads\ViceClip-Studio\AGENTS.md",
    os.path.expanduser(r"~\.gemini\config\rules\auto-skill-router.md"),
    os.path.expanduser(r"~\.gemini\config\AGENTS.md"),
]

WATCH_DIRS = [
    r"c:\Users\mukul\Downloads\ViceClip-Studio\.agents\skills",
    os.path.expanduser(r"~\.gemini\config\skills"),
    os.path.expanduser(r"~\.gemini\antigravity\builtin\skills"),
]

def scan_live_skills():
    live = {}
    for d in WATCH_DIRS:
        if not os.path.exists(d):
            continue
        for item in os.listdir(d):
            item_path = os.path.join(d, item)
            skill_md = os.path.join(item_path, "SKILL.md")
            if os.path.isdir(item_path) and os.path.exists(skill_md):
                if item not in live:
                    desc = "Specialized AI workflow"
                    try:
                        with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read(2048)
                        m = re.search(r"description:\s*(?:>-\s*|>\s*)?([^\n\r]+)", text)
                        if m:
                            desc = m.group(1).strip().strip('"').strip("'")
                    except Exception:
                        pass
                    live[item] = {
                        "name": item,
                        "path": skill_md,
                        "desc": desc
                    }
    return live

def sync():
    live_skills = scan_live_skills()
    if not os.path.exists(ROUTER_PATHS[0]):
        return
    with open(ROUTER_PATHS[0], "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    newly_adopted = []
    for name, data in live_skills.items():
        if f"**`{name}`**" not in content:
            newly_adopted.append(name)
            # Row format: | **`name`** | Scope (`path`) | Capabilities | Keywords |
            row = f"| **`{name}`** | Auto-Adopted (`{data['path']}`) | {data['desc'][:100]} | `{name}` |\n"
            content = content.replace("## 5. Execution Examples", f"{row}\n## 5. Execution Examples")

    if newly_adopted:
        for rp in ROUTER_PATHS:
            try:
                os.makedirs(os.path.dirname(rp), exist_ok=True)
                with open(rp, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception:
                pass
        print(f"🆕 Auto-Adopted Skills: [{', '.join(newly_adopted)}]")
    else:
        print("All skills synchronized. Zero drift detected.")

if __name__ == "__main__":
    sync()
