"""
Generate Publication-Quality Full VeriMem Architecture Diagram PNG.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def draw_architecture_diagram():
    base_dir = Path(__file__).resolve().parent
    charts_dir = base_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    output_png = charts_dir / "verimem_full_architecture.png"

    fig, ax = plt.subplots(figsize=(14, 18), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Scheme
    PRIMARY_BG = "#0f172a"
    BOX_BG_USER = "#e0f2fe"
    BOX_BORDER_USER = "#0284c7"
    
    BOX_BG_INGEST = "#f0fdf4"
    BOX_BORDER_INGEST = "#16a34a"
    
    BOX_BG_RECALL = "#faf5ff"
    BOX_BORDER_RECALL = "#9333ea"
    
    BOX_BG_STORE = "#fff7ed"
    BOX_BORDER_STORE = "#ea580c"

    TEXT_DARK = "#0f172a"

    def draw_box(x, y, w, h, text, bg, border, fontsize=9, bold=False):
        box = patches.FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.5,rounding_size=1.0",
            ec=border, fc=bg, lw=1.5
        )
        ax.add_patch(box)
        weight = 'bold' if bold else 'normal'
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, fontweight=weight, color=TEXT_DARK, wrap=True)

    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color="#475569", lw=1.5, mutation_scale=15)
        )
        if label:
            mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mid_x + 1.5, mid_y, label, fontsize=8, fontweight='bold', color="#0284c7", ha='left', va='center')

    # Title Banner
    ax.text(50, 98, "VeriMem Complete End-to-End System Architecture", ha='center', va='center', fontsize=16, fontweight='bold', color=PRIMARY_BG)
    ax.text(50, 96.5, "Fact Ingestion Pathway (Left) | Grounded Recall Pathway (Right) | Memory Persistence & Audit (Bottom)", ha='center', va='center', fontsize=10, color="#475569")

    # 1. Top Level Nodes
    draw_box(50, 93, 20, 3, "User", BOX_BG_USER, BOX_BORDER_USER, fontsize=10, bold=True)
    draw_arrow(50, 91.5, 50, 88.5)
    
    draw_box(50, 87, 28, 3.2, "Chat / Dashboard UI\n(React + Streamlit)", BOX_BG_USER, BOX_BORDER_USER, fontsize=10, bold=True)

    # Branching arrows from UI
    draw_arrow(40, 85.4, 25, 82.5) # Left to FastAPI Ingestion
    draw_arrow(60, 85.4, 75, 82.5) # Right to User Question

    # --- LEFT BRANCH: Fact Ingestion Pathway ---
    draw_box(25, 81, 28, 3, "FastAPI Backend Router", BOX_BG_INGEST, BOX_BORDER_INGEST, bold=True)
    draw_arrow(25, 79.5, 25, 76.5)

    draw_box(25, 75, 28, 3, "Session Parser & Dialogue State", BOX_BG_INGEST, BOX_BORDER_INGEST)
    draw_arrow(25, 73.5, 25, 70.5)

    draw_box(25, 69, 30, 3.2, "Memory Candidate Extractor\n(LLM API: Gemini 3.6 Flash)", BOX_BG_INGEST, BOX_BORDER_INGEST, bold=True)
    draw_arrow(25, 67.4, 25, 64.5)

    draw_box(25, 63, 30, 3.2, "Atomic Fact Decomposer\n(Subject-Predicate-Object Triples)", BOX_BG_INGEST, BOX_BORDER_INGEST)
    draw_arrow(25, 61.4, 25, 58.5)

    draw_box(25, 57, 30, 3.2, "Evidence Grounding Verifier\n(Rejects Assistant Assumptions)", BOX_BG_INGEST, BOX_BORDER_INGEST, bold=True)
    draw_arrow(25, 55.4, 25, 52.5)

    draw_box(25, 51, 30, 3.2, "Conflict & Update Detector\n(Preference / Goal Shift State Machine)", BOX_BG_INGEST, BOX_BORDER_INGEST, bold=True)
    draw_arrow(25, 49.4, 25, 46.5)

    draw_box(25, 45, 30, 3.2, "Natural Language Policy Engine\n(Evaluates NL User Rules)", BOX_BG_INGEST, BOX_BORDER_INGEST)
    draw_arrow(25, 43.4, 25, 40.5)

    draw_box(25, 39, 30, 3.2, "Memory Decision Controller\n(Commit / Retire / Reject Logic)", BOX_BG_INGEST, BOX_BORDER_INGEST, bold=True)

    # Decision Controller Outputs
    draw_arrow(25, 37.4, 25, 30.5, label="Store / Update / Reject")
    draw_arrow(36, 37.4, 48, 25.5) # To Audit Log

    # --- RIGHT BRANCH: Grounded Question Recall Pathway ---
    draw_box(75, 81, 28, 3, "User Question Input", BOX_BG_RECALL, BOX_BORDER_RECALL, bold=True)
    draw_arrow(75, 79.5, 75, 64.5)

    draw_box(75, 63, 32, 4, "Multi-Signal Hybrid Retriever\n(0.35*Semantic + 0.20*Entity +\n0.25*Recency + 0.10*Confidence)", BOX_BG_RECALL, BOX_BORDER_RECALL, bold=True)

    draw_arrow(75, 61, 75, 47.5)

    draw_box(75, 46, 30, 3.2, "Answer Agent\n(Generates Evidence-Cites Answers)", BOX_BG_RECALL, BOX_BORDER_RECALL, bold=True)
    draw_arrow(75, 44.4, 75, 40.5)

    draw_box(75, 39, 30, 3.2, "Answer Verifier\n(Checks Factuality against Evidence)", BOX_BG_RECALL, BOX_BORDER_RECALL)
    draw_arrow(75, 37.4, 75, 32.5)

    draw_box(75, 30, 32, 3.8, "Grounded Answer +\nCitations [mem_XXX] + Confidence", BOX_BG_RECALL, BOX_BORDER_RECALL, bold=True)
    
    # Loop back to UI
    ax.annotate(
        "", xy=(64, 87), xytext=(91, 30),
        arrowprops=dict(arrowstyle="->", color="#9333ea", lw=1.5, connectionstyle="arc3,rad=-0.4")
    )

    # --- BOTTOM LAYER: Memory Persistence & Audit ---
    draw_box(25, 29, 30, 3.2, "Versioned Memory Store\n(ACTIVE / UNCERTAIN / RETIRED)", BOX_BG_STORE, BOX_BORDER_STORE, bold=True)
    draw_box(50, 24, 20, 3.2, "Audit Log\n(Full Traceability)", BOX_BG_STORE, BOX_BORDER_STORE)

    # Connections between Retriever and Memory Store / Audit
    draw_arrow(60, 63, 40, 30) # Retriever scans Memory Store
    draw_arrow(62, 63, 52, 25.5) # Retriever checks Audit Log

    # Database Engines Layer
    draw_box(15, 14, 20, 3.5, "SQLite / PostgreSQL\n(Relational Metadata)", BOX_BG_STORE, BOX_BORDER_STORE)
    draw_box(38, 14, 20, 3.5, "Vector Store\n(Chroma / FAISS Embeddings)", BOX_BG_STORE, BOX_BORDER_STORE)
    draw_box(61, 14, 20, 3.5, "Optional Graph Memory\n(NetworkX / Neo4j Entities)", BOX_BG_STORE, BOX_BORDER_STORE)

    # Connect Versioned Memory Store to DB engines
    draw_arrow(20, 27.4, 15, 15.8)
    draw_arrow(25, 27.4, 38, 15.8)
    draw_arrow(30, 27.4, 61, 15.8)

    # Audit Log loop back to UI
    ax.annotate(
        "", xy=(45, 87), xytext=(50, 25.6),
        arrowprops=dict(arrowstyle="->", color="#ea580c", lw=1.5, connectionstyle="arc3,rad=0.3")
    )

    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Architecture diagram generated successfully at: {output_png}")

if __name__ == "__main__":
    draw_architecture_diagram()
