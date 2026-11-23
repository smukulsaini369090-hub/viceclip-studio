"""
VICECLIP STUDIO — GTA 6 Lore & Easter-Egg Dictionary
======================================================
Rich, structured reference data for prompt injection so the Viral Brain
understands GTA 6 context, can spot Easter eggs, and generate lore-aware
viral hooks that resonate with the GTA community.

This module is **pure data** — no I/O, no imports beyond the stdlib.
"""

from __future__ import annotations


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTERS
# ═══════════════════════════════════════════════════════════════════════════════

CHARACTERS: list[dict] = [
    {
        "name": "Lucia",
        "role": "Dual protagonist",
        "details": (
            "First female playable protagonist in GTA mainline history. "
            "Latina heritage. Shown in orange Leonida County Jail jumpsuit "
            "in Trailer 1. Bonnie-and-Clyde dynamic with Jason. "
            "Fan theories about her being ex-military or cartel-connected. "
            "Her hairstyle changes across trailers hinting at time progression."
        ),
        "viral_hooks": [
            "Lucia vs every other GTA protagonist",
            "Details you missed about Lucia",
            "Why Lucia might be the best GTA character ever",
        ],
    },
    {
        "name": "Jason",
        "role": "Dual protagonist",
        "details": (
            "Male protagonist partnered with Lucia. Bonnie-and-Clyde criminal "
            "duo storyline confirmed by Trailer 1 narration. Visually compared "
            "to a younger Tommy Vercetti by fans. Seen in armed robbery, "
            "nightclub, and car chase sequences."
        ),
        "viral_hooks": [
            "Is Jason related to Tommy Vercetti?",
            "Jason's secret backstory theory",
        ],
    },
    {
        "name": "Tommy Vercetti",
        "role": "GTA Vice City protagonist (legacy)",
        "details": (
            "Protagonist of GTA Vice City (2002). Set in 1986 Vice City. "
            "Hawaiian shirt icon. Fans speculate cameo or reference in GTA 6. "
            "Ray Liotta voiced him (RIP 2022). Any older man in a Hawaiian "
            "shirt in GTA 6 trailers triggers Tommy theories."
        ),
        "viral_hooks": ["Tommy Vercetti Easter egg FOUND"],
    },
    {
        "name": "NPC Citizens",
        "role": "Background detail",
        "details": (
            "GTA 6 NPCs show unprecedented AI — phone-filming crimes, "
            "reacting to player actions, social-media-style in-game posts, "
            "individual body types and behaviours. Rockstar confirmed "
            "next-gen NPC AI routines."
        ),
        "viral_hooks": [
            "GTA 6 NPC AI is INSANE — watch this",
            "NPCs in GTA 6 actually film you",
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# LOCATIONS & MAP
# ═══════════════════════════════════════════════════════════════════════════════

LOCATIONS: list[dict] = [
    {
        "name": "Leonida",
        "type": "State",
        "real_world": "Florida",
        "details": (
            "The GTA 6 state, Rockstar's fictionalised Florida. "
            "Includes Vice City, swamplands (Everglades analog), Keys-like "
            "islands, and suburban sprawl. The largest GTA map ever — "
            "rumoured to be larger than GTA V + RDR2 combined."
        ),
    },
    {
        "name": "Vice City",
        "type": "City",
        "real_world": "Miami / Miami Beach",
        "details": (
            "Neon-lit Art Deco oceanfront, Latin Quarter, luxury high-rises, "
            "nightclub strip. Returns from GTA Vice City (1986) now set in "
            "modern day. Ocean Drive analog visible in trailers."
        ),
    },
    {
        "name": "Vice Beach",
        "type": "District / Beach",
        "real_world": "South Beach / Miami Beach",
        "details": (
            "Iconic beach area with lifeguard towers, bikini NPCs, street "
            "performers, and neon signs. Major Trailer 1 setting. "
            "Spring-break chaos sequences filmed here."
        ),
    },
    {
        "name": "Vice Dale",
        "type": "Suburb / County",
        "real_world": "Fort Lauderdale / Broward County",
        "details": (
            "Suburban sprawl north of Vice City. Strip malls, trailer parks, "
            "Florida Man territory. Leaked map suggests it's a large playable "
            "area with its own mission hubs."
        ),
    },
    {
        "name": "Port Gellhorn",
        "type": "Industrial Port",
        "real_world": "Port of Miami / Port Everglades",
        "details": (
            "Shipping container yards, cruise ship terminal. Likely heist / "
            "smuggling mission location. Visible in leaked footage."
        ),
    },
    {
        "name": "Grassrivers / The Glades",
        "type": "Wetlands / Swamp",
        "real_world": "The Everglades",
        "details": (
            "Vast swampland with airboat traversal, alligators, hidden "
            "compounds. Fan-favourite exploration area. Drug lab / moonshine "
            "hideouts rumoured."
        ),
    },
    {
        "name": "Keys-like Islands",
        "type": "Island Chain",
        "real_world": "Florida Keys / Key West",
        "details": (
            "Southern island chain connected by bridges. Tropical paradise, "
            "diving, boat-based missions. Possibly an expansion area."
        ),
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# GAME ENGINE & TECHNOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

ENGINE_TECH: list[dict] = [
    {
        "feature": "RAGE 9 Engine",
        "details": (
            "Rockstar Advanced Game Engine version 9. Largest leap since "
            "RAGE 7 (RDR2). Powers GTA 6's open world, physics, lighting, "
            "and NPC AI. Built for PS5/Xbox Series X hardware."
        ),
        "viral_hooks": ["RAGE 9 is a generational leap"],
    },
    {
        "feature": "Water / Ocean Physics",
        "details": (
            "Most realistic water in any game. Dynamic wave systems, "
            "underwater currents, volumetric foam, real-time reflections. "
            "Boats react to individual waves. Trailer 1 beach shots showcase "
            "this. Fans compare every water shot frame-by-frame."
        ),
        "viral_hooks": [
            "GTA 6 water physics are UNREAL",
            "Zoom into the water — look at this detail",
        ],
    },
    {
        "feature": "Hair / Cloth Physics",
        "details": (
            "Strand-based hair simulation visible on Lucia. Dynamic cloth "
            "physics on all characters. Industry-leading character rendering."
        ),
        "viral_hooks": ["Look at Lucia's hair physics"],
    },
    {
        "feature": "NPC AI / Social Media System",
        "details": (
            "NPCs have individual routines, can call 911, film crimes on "
            "phones, post to in-game social media. Dynamic NPC population "
            "density based on time/location. The most alive open world ever."
        ),
        "viral_hooks": [
            "GTA 6 NPCs are smarter than GTA 5 players",
            "This NPC detail will blow your mind",
        ],
    },
    {
        "feature": "Vehicle Physics & Damage",
        "details": (
            "Soft-body-inspired deformation, individual panel damage, "
            "tire blowout physics, realistic suspension. Motorcycles and "
            "boats also overhauled. Vehicles seen in trailers show visible "
            "crumple zones."
        ),
        "viral_hooks": ["GTA 6 car damage is insane"],
    },
    {
        "feature": "Dynamic Weather & Time",
        "details": (
            "Hurricanes confirmed by leaked footage. Dynamic cloud systems, "
            "volumetric storms, flooding. Time-of-day affects NPC behaviour "
            "and mission availability. Florida hurricane season as gameplay."
        ),
        "viral_hooks": [
            "GTA 6 hurricane gameplay is TERRIFYING",
            "What happens during a hurricane in GTA 6",
        ],
    },
    {
        "feature": "Lighting / Global Illumination",
        "details": (
            "Path-traced global illumination on next-gen. Neon reflections "
            "on wet streets. Trailer 1 sunset shots are cinematic reference-"
            "quality. Ray-traced reflections on car paint and glass."
        ),
        "viral_hooks": ["This GTA 6 lighting is not real"],
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# TRAILER CALLBACKS & EASTER EGGS
# ═══════════════════════════════════════════════════════════════════════════════

TRAILER_REFERENCES: list[dict] = [
    {
        "source": "Trailer 1 (December 2023)",
        "moments": [
            "Opening shot: flamingos + Vice City skyline at golden hour",
            "Lucia in jail jumpsuit — first female protag reveal",
            "Bonnie-and-Clyde narration voiceover",
            "NPC filming a street fight on their phone",
            "Alligator walking through a parking lot",
            "Strip club / nightclub neon montage",
            "Armed robbery with Lucia and Jason",
            "Boat chase through the Glades",
            "Florida Man-style news ticker on in-game TV",
            "Mudding truck in swampland",
            "Lucia and Jason sitting on car hood watching sunset — final shot",
        ],
    },
    {
        "source": "Trailer 2 (anticipated)",
        "moments": [
            "Expected to reveal expanded map areas",
            "Gameplay mechanics showcase",
            "Possible heist mission preview",
            "New vehicle types and customisation",
            "In-game phone / social media system demo",
        ],
    },
    {
        "source": "Leaks (September 2022 Uber hack)",
        "moments": [
            "90+ clips of early development build leaked",
            "Showed Vice City restaurant robbery",
            "Lucia and Jason character models in early form",
            "Diner robbery mission prototype",
            "Weapon wheel and inventory UI glimpse",
            "NPC dialogue trees visible",
            "Swamp / Everglades area traversal",
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# PAST ROCKSTAR REFERENCES (cross-game Easter eggs to watch for)
# ═══════════════════════════════════════════════════════════════════════════════

ROCKSTAR_CALLBACKS: list[dict] = [
    {"game": "GTA Vice City", "elements": [
        "Tommy Vercetti's mansion / Diaz's mansion location",
        "Malibu Club / nightclub references",
        "Lance Vance callback potential",
        "Hyman Condo location",
        "Print Works / business ownership system",
    ]},
    {"game": "GTA San Andreas", "elements": [
        "CJ / Grove Street references",
        "Gym / body customisation system return",
        "Lowrider culture in Vice City's Latin Quarter",
    ]},
    {"game": "GTA IV", "elements": [
        "Liberty City News references",
        "Niko Bellic mention potential",
        "Brucie Kibbutz social media cameo theory",
    ]},
    {"game": "GTA V", "elements": [
        "Michael, Trevor, Franklin references",
        "LifeInvader → modern social media system evolution",
        "Maze Bank / finance system callbacks",
        "Dr. Dre / Franklin's story DLC connections",
    ]},
    {"game": "Red Dead Redemption 2", "elements": [
        "RAGE engine lineage visible in lighting/physics",
        "Horse → vehicle physics evolution comparison",
        "NPC interaction depth inherited and expanded",
    ]},
]

# ═══════════════════════════════════════════════════════════════════════════════
# FAN THEORIES & MAP RUMOURS
# ═══════════════════════════════════════════════════════════════════════════════

FAN_THEORIES: list[dict] = [
    {
        "theory": "Evolving Map",
        "details": (
            "The map may change over time via post-launch updates — "
            "new islands, construction projects completing, seasonal "
            "events tied to real holidays."
        ),
    },
    {
        "theory": "Multiple Time Periods",
        "details": (
            "Lucia's changing appearance across trailers suggests missions "
            "may span several years, possibly with flashback sequences "
            "to the 1980s Vice City era."
        ),
    },
    {
        "theory": "Crypto / In-Game Economy",
        "details": (
            "Leaked code referenced cryptocurrency and stock systems, "
            "possibly expanding GTA V's stock market mechanic. "
            "In-game phone app for trading rumoured."
        ),
    },
    {
        "theory": "Playable Prison Section",
        "details": (
            "Lucia's jail jumpsuit suggests a prison prologue or "
            "breakout mission sequence. Fans debate whether it's the "
            "opening mission."
        ),
    },
    {
        "theory": "Co-op / Partner Switching",
        "details": (
            "Bonnie-and-Clyde dynamic suggests seamless switching between "
            "Lucia and Jason during missions, similar to GTA V's character "
            "switching but more integrated."
        ),
    },
    {
        "theory": "Florida Man Random Events",
        "details": (
            "The in-game news ticker and Florida-inspired setting strongly "
            "suggests 'Florida Man'-style random encounters as a core "
            "open-world activity system."
        ),
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# EASTER EGG CATEGORIES (for auto-zoom classification)
# ═══════════════════════════════════════════════════════════════════════════════

EASTER_EGG_CATEGORIES: list[dict] = [
    {
        "category": "Background Details",
        "examples": [
            "Hidden text on billboards, licence plates, store signs",
            "Phone screen content visible on NPC devices",
            "Newspaper headlines referencing past GTA events",
            "Radio station posters with real Rockstar references",
        ],
    },
    {
        "category": "Map Secrets",
        "examples": [
            "Hidden interiors visible through windows",
            "Underwater objects (sunken ships, treasure)",
            "Mountain / rooftop hidden items",
            "Secret rooms in accessible buildings",
        ],
    },
    {
        "category": "Character References",
        "examples": [
            "NPCs resembling past GTA protagonists",
            "Clothing items referencing past games",
            "Tattoo parlour designs with lore references",
            "Voice lines referencing Liberty City or Los Santos",
        ],
    },
    {
        "category": "Vehicle Easter Eggs",
        "examples": [
            "Licence plates with hidden codes / dates",
            "Vehicle names parodying real car brands",
            "Special vehicle spawns at specific times",
            "Custom paint jobs referencing past GTA vehicles",
        ],
    },
    {
        "category": "Environmental Storytelling",
        "examples": [
            "Crime scene details telling mini-stories",
            "Graffiti with developer messages",
            "Abandoned locations with lore implications",
            "Time-sensitive environmental changes",
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# VIRAL TOPIC TRIGGERS (keywords that spike GTA 6 community engagement)
# ═══════════════════════════════════════════════════════════════════════════════

VIRAL_TRIGGERS: list[str] = [
    "GTA 6", "GTA VI", "Grand Theft Auto 6", "Grand Theft Auto VI",
    "Vice City", "Leonida", "Lucia", "Jason",
    "RAGE 9", "RAGE engine", "Rockstar Games", "Rockstar North",
    "Take-Two", "GTA Online 2",
    "Trailer 1", "Trailer 2", "release date",
    "map size", "map leak", "leaked footage",
    "Tommy Vercetti", "Vice City Stories",
    "Florida Man", "Everglades", "hurricane",
    "NPC AI", "water physics", "hair physics",
    "Easter egg", "hidden detail", "secret found",
    "comparison", "GTA 5 vs GTA 6", "evolution",
    "fan theory", "confirmed", "debunked",
]


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT INJECTION BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def build_lore_context() -> str:
    """
    Compile the full GTA 6 lore context into a formatted string
    ready for injection into the Gemini prompt.
    """
    sections: list[str] = []

    sections.append("=== GTA 6 LORE & CONTEXT DICTIONARY ===\n")

    # Characters
    sections.append("## KEY CHARACTERS")
    for char in CHARACTERS:
        sections.append(f"• {char['name']} ({char['role']}): {char['details']}")
        if char.get("viral_hooks"):
            sections.append(f"  Viral hook ideas: {', '.join(char['viral_hooks'])}")

    # Locations
    sections.append("\n## LOCATIONS & MAP")
    for loc in LOCATIONS:
        real = f" (real-world: {loc['real_world']})" if loc.get("real_world") else ""
        sections.append(f"• {loc['name']} [{loc['type']}]{real}: {loc['details']}")

    # Engine tech
    sections.append("\n## RAGE 9 ENGINE & TECHNOLOGY")
    for tech in ENGINE_TECH:
        sections.append(f"• {tech['feature']}: {tech['details']}")
        if tech.get("viral_hooks"):
            sections.append(f"  Viral hook ideas: {', '.join(tech['viral_hooks'])}")

    # Trailer references
    sections.append("\n## TRAILER & LEAK REFERENCE MOMENTS")
    for ref in TRAILER_REFERENCES:
        sections.append(f"### {ref['source']}")
        for moment in ref["moments"]:
            sections.append(f"  - {moment}")

    # Past game callbacks
    sections.append("\n## PAST ROCKSTAR GAME CALLBACKS")
    for cb in ROCKSTAR_CALLBACKS:
        sections.append(f"### {cb['game']}")
        for elem in cb["elements"]:
            sections.append(f"  - {elem}")

    # Fan theories
    sections.append("\n## ACTIVE FAN THEORIES")
    for theory in FAN_THEORIES:
        sections.append(f"• {theory['theory']}: {theory['details']}")

    # Easter egg categories
    sections.append("\n## EASTER EGG CATEGORIES (for auto-zoom detection)")
    for cat in EASTER_EGG_CATEGORIES:
        sections.append(f"### {cat['category']}")
        for ex in cat["examples"]:
            sections.append(f"  - {ex}")

    return "\n".join(sections)


def get_viral_triggers() -> list[str]:
    """Return the list of GTA 6 viral topic trigger keywords."""
    return VIRAL_TRIGGERS.copy()
