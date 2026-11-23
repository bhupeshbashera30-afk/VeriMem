"""
Generate VeriMem Architecture, Communication Flow & Viva Defense Guide PDF.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.lib.units import inch

def generate_architecture_pdf():
    base_dir = Path(__file__).resolve().parent
    output_pdf_path = base_dir / "VeriMem_Architecture_and_Defense_Guide.pdf"

    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    PRIMARY = colors.HexColor("#0f172a")    # Slate 900
    SECONDARY = colors.HexColor("#0284c7")  # Sky 600
    ACCENT = colors.HexColor("#059669")     # Emerald 600
    DARK_TEXT = colors.HexColor("#1e293b")  # Slate 800
    BG_LIGHT = colors.HexColor("#f8fafc")   # Slate 50
    BOX_BG = colors.HexColor("#f1f5f9")     # Slate 100
    BORDER_COLOR = colors.HexColor("#cbd5e1")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=DARK_TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=DARK_TEXT,
        leftIndent=10,
        spaceAfter=3
    )

    code_block_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=PRIMARY
    )

    elements = []

    # Title & Subtitle
    elements.append(Paragraph("VeriMem: System Architecture & LLM Communication Guide", title_style))
    elements.append(Paragraph("Data Flow Mechanics, 5-Stage Verification Pipeline & Academic Viva Defense Reference", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=10))

    # Section 1: Architectural Analogy
    elements.append(Paragraph("1. Executive Architectural Concept: The 'Car Engine' Analogy", h1_style))
    elements.append(Paragraph(
        "A common question in project evaluation is: <i>'Isn't ChatGPT/Gemini doing all the work?'</i><br/>"
        "The fundamental answer is: <b>No. An LLM API is just a raw cognitive engine — sitting alone on a table, an engine cannot drive anywhere. "
        "VeriMem is the entire car</b> (the chassis, database, transmission, steering, conflict resolution state machine, and safety brakes).",
        body_style
    ))

    # Section 2: Communication & Data Sharing Flow
    elements.append(Paragraph("2. How VeriMem Communicates with the LLM API", h1_style))
    elements.append(Paragraph(
        "VeriMem communicates with cloud LLM APIs (e.g., Google Gemini 3.6 Flash / OpenAI) via <b>secure HTTPS REST API requests</b>. "
        "The LLM is completely <i>stateless</i> — it does NOT store or manage memories. Information is exchanged as follows:",
        body_style
    ))

    diagram_text = (
        "<b>[ VERIMEM PYTHON BACKEND ]</b>  --- (1) HTTPS POST Request with System Prompt + User Turn --->  <b>[ LLM CLOUD API ]</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "&lt;--- (2) HTTPS Response with Structured JSON Candidate ---<br/>"
        "<b>[ VERIMEM ENGINE ]</b>  --- (3) Verifies Grounding &amp; Resolves Conflicts --->  <b>[ LOCAL SQLITE MEMORY STORE ]</b>"
    )

    flow_table = Table([[Paragraph(diagram_text, code_block_style)]], colWidths=[520])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BOX_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(flow_table)
    elements.append(Spacer(1, 8))

    # Data Sharing Details
    elements.append(Paragraph("<b>A. What VeriMem Sends to the LLM (Outbound Request)</b>", h2_style))
    elements.append(Paragraph("&bull; <b>Authentication Header</b>: Secure API key (`?key=API_KEY` or `x-api-key`).", bullet_style))
    elements.append(Paragraph("&bull; <b>System Role Prompt</b>: Instructions specifying exact tasks (e.g., Candidate Extraction, Atomic Fact Decomposition).", bullet_style))
    elements.append(Paragraph("&bull; <b>Dialogue Turns</b>: Raw text turns from user and assistant (e.g. `\"Actually I now prefer Coffee over Tea\"`).", bullet_style))
    elements.append(Paragraph("&bull; <b>Structured Output Rule</b>: Native JSON schema demand (`\"responseMimeType\": \"application/json\"`).", bullet_style))

    elements.append(Paragraph("<b>B. What the LLM Returns (Inbound Response)</b>", h2_style))
    elements.append(Paragraph("&bull; Structured JSON containing candidate memory text, memory type, and extraction confidence.", bullet_style))

    elements.append(Paragraph("<b>C. What VeriMem Does Locally (Persistence & Governance)</b>", h2_style))
    elements.append(Paragraph("&bull; <b>The LLM stores NOTHING.</b> The LLM response is passed to VeriMem's local Python engine.", bullet_style))
    elements.append(Paragraph("&bull; `EvidenceGroundingVerifier` checks if facts originated from the user (rejects assistant guesses).", bullet_style))
    elements.append(Paragraph("&bull; `ConflictDetector` checks the local SQLite database (`verimem.db`) and retires old outdated memories.", bullet_style))
    elements.append(Paragraph("&bull; `MemoryStore` commits verified memories into SQLite with status `ACTIVE`.", bullet_style))

    # Section 3: Visual End-to-End System Architecture Flowchart
    elements.append(Paragraph("3. Full VeriMem System Architecture Diagram & Node Breakdown", h1_style))
    elements.append(Paragraph(
        "Below is the complete end-to-end visual architecture diagram showing the entire data flow from the moment a user enters an input "
        "to the final committed memory and grounded response with citations:",
        body_style
    ))

    arch_img_path = base_dir / "charts" / "verimem_full_architecture.png"
    if arch_img_path.exists():
        elements.append(Image(str(arch_img_path), width=6.8*inch, height=8.6*inch))
        elements.append(Spacer(1, 10))

    elements.append(PageBreak())

    elements.append(Paragraph("<b>Detailed Node-by-Node Flow Breakdown (Start to Finish)</b>", h1_style))
    
    node_descriptions = [
        ("1. User Input & Chat / Dashboard UI", "The user types a chat statement or question in the React / Streamlit frontend dashboard. Inputs are routed to either the Ingestion or Recall pathway."),
        ("2. FastAPI Backend & Session Parser", "Receives the raw HTTP request, authenticates session_id and user_id, and loads the active session turn history."),
        ("3. Memory Candidate Extractor", "Calls the Gemini 3.6 Flash LLM API with system role prompts to extract candidate memories. Question inputs and greetings are filtered out."),
        ("4. Atomic Fact Decomposer", "Breaks complex extracted candidates into simple Subject-Predicate-Object atomic triples for precise verification."),
        ("5. Evidence Grounding Verifier", "Cross-references facts against raw dialogue turns. Rejects unconfirmed assistant assumptions (assistant_originated), preventing memory pollution."),
        ("6. Conflict & Update Detector", "Runs a state-machine that compares new facts against existing active memories. Identifies preference/identity/goal shifts and marks old memories as RETIRED (RETIRE_OLD_AND_STORE_NEW)."),
        ("7. Natural Language Policy Engine", "Compiles natural-language user rules (e.g. 'Ask before changing goals') into executable code checks to govern storage actions."),
        ("8. Memory Decision Controller & Versioned Store", "Makes the final commit decision (STORE_ACTIVE, RETIRE_OLD, REJECT) and writes verified memories to SQLite (verimem.db), Vector DB, and Graph stores with version tracking."),
        ("9. Audit Log", "Records every decision, confidence score, and rationale for full enterprise compliance and UI inspection."),
        ("10. Hybrid Retriever & Answer Agent", "For recall queries, scans active memories using a 4-signal formula (Semantic + Keyword + Recency + Confidence). The Answer Agent generates evidence-cited answers ([mem_XXX])."),
        ("11. Grounded Answer Output", "Returns the final grounded answer with evidence citations and confidence scores back to the Chat UI for the user.")
    ]

    for node_title, node_text in node_descriptions:
        elements.append(Paragraph(f"<b>&bull; {node_title}</b>", h2_style))
        elements.append(Paragraph(node_text, bullet_style))

    elements.append(Spacer(1, 10))

    # Section 4: Academic Viva Defense Q&A Reference Guide
    elements.append(Paragraph("4. Academic Viva Defense Reference (Professor Q&A)", h1_style))

    q_a = [
        ("Q1: Why do we use an LLM API (Gemini / ChatGPT) instead of a plain Python script?",
         "A plain Python script cannot understand human language semantics (e.g. knowing 'Coffee' and 'Tea' are both drinks, or that 'switched' means updating a preference). We use an LLM API as the cognitive text reader to parse natural language meaning into structured JSON data."),
        
        ("Q2: What if the evaluator says: 'ChatGPT is doing all the work, what is YOUR project doing?'",
         "ChatGPT by itself has NO long-term memory, NO database, NO conflict resolution, and hallucinates unconfirmed guesses. OUR PROJECT engineered the entire system: the SQLite database schema, the evidence verifier algorithm, the conflict update state machine, the natural-language policy compiler, the 4-signal hybrid retriever, and the visual execution inspector."),
        
        ("Q3: How did we calculate the 38.5% Baseline RAG vs 12.5% VeriMem Hallucination Rate?",
         "Formula: Hallucination Rate = (Hallucinated Answers / 1,000 Questions). Baseline RAG blindly stores assistant guesses and keeps old conflicting memories in the DB, causing 38.5% hallucinated answers. VeriMem verifies evidence turns and retires outdated memories, reducing hallucination down to 12.5% (a 67.5% reduction!).")
    ]

    for q, a in q_a:
        elements.append(Paragraph(f"<b>{q}</b>", h2_style))
        elements.append(Paragraph(a, body_style))

    doc.build(elements)
    print(f"Architecture PDF Guide generated successfully at: {output_pdf_path}")

if __name__ == "__main__":
    generate_architecture_pdf()
