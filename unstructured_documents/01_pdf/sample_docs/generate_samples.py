"""
Generate sample PDF documents for testing different extraction methods.

Creates 4 PDFs:
  1. simple_text.pdf   - Multi-page text with headings and paragraphs about AI
  2. tables.pdf        - Multiple tables (inventory, revenue, employees)
  3. multi_column.pdf  - Two-column layout (research-paper style)
  4. mixed_content.pdf - Text + table + bullet points + headers combined

Usage:
    uv run python unstructured_documents/01_pdf/sample_docs/generate_samples.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

SAMPLE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 1) simple_text.pdf
# ---------------------------------------------------------------------------


def generate_simple_text():
    """Create a multi-page document about Artificial Intelligence."""
    path = SAMPLE_DIR / "simple_text.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        topMargin=72,
        bottomMargin=72,
        leftMargin=72,
        rightMargin=72,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading1"],
        fontSize=16,
        spaceBefore=18,
        spaceAfter=10,
    )
    subheading_style = ParagraphStyle(
        "CustomSubheading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
    )

    story = []

    # Title
    story.append(Paragraph("Artificial Intelligence: A Comprehensive Overview", title_style))
    story.append(Spacer(1, 12))

    # ---- Section 1 ----
    story.append(Paragraph("1. Introduction to Artificial Intelligence", heading_style))
    story.append(
        Paragraph(
            "Artificial Intelligence (AI) is a branch of computer science that aims to create "
            "systems capable of performing tasks that normally require human intelligence. These "
            "tasks include visual perception, speech recognition, decision-making, and language "
            "translation. The field was founded on the claim that human intelligence can be so "
            "precisely described that a machine can be made to simulate it.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "The concept of artificial intelligence has been part of human imagination for "
            "centuries, but the formal field of AI research was established in 1956 at the "
            "Dartmouth Conference. Since then, AI has experienced several cycles of optimism "
            "and disappointment, known as AI winters, followed by renewed enthusiasm and "
            "funding. The current era of AI, driven by deep learning and big data, has "
            "achieved remarkable breakthroughs across numerous domains.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Modern AI systems are powered by machine learning algorithms that learn patterns "
            "from vast amounts of data. Unlike traditional software that follows explicit "
            "rules written by programmers, machine learning systems improve their performance "
            "through experience. This paradigm shift has enabled applications that were "
            "previously thought impossible, from self-driving cars to protein structure "
            "prediction.",
            body_style,
        )
    )

    # ---- Section 2 ----
    story.append(Paragraph("2. Machine Learning Fundamentals", heading_style))
    story.append(Paragraph("2.1 Supervised Learning", subheading_style))
    story.append(
        Paragraph(
            "Supervised learning is the most common form of machine learning. In this "
            "paradigm, the algorithm is trained on labeled data, where each input example "
            "is paired with the correct output. The model learns to map inputs to outputs "
            "by minimizing the difference between its predictions and the actual labels. "
            "Common supervised learning tasks include classification, where the goal is to "
            "assign inputs to discrete categories, and regression, where the goal is to "
            "predict continuous values.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Popular supervised learning algorithms include linear regression, logistic "
            "regression, support vector machines, decision trees, random forests, and "
            "neural networks. The choice of algorithm depends on the nature of the data, "
            "the complexity of the relationship between inputs and outputs, and the amount "
            "of available training data. Cross-validation and regularization techniques "
            "help prevent overfitting, where the model memorizes training data rather than "
            "learning generalizable patterns.",
            body_style,
        )
    )

    story.append(Paragraph("2.2 Unsupervised Learning", subheading_style))
    story.append(
        Paragraph(
            "Unsupervised learning works with unlabeled data, seeking to discover hidden "
            "patterns and structures. Clustering algorithms such as K-means, hierarchical "
            "clustering, and DBSCAN group similar data points together. Dimensionality "
            "reduction techniques like PCA and t-SNE help visualize high-dimensional data. "
            "Generative models learn the underlying distribution of data and can create "
            "new samples that resemble the training data.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Unsupervised learning is particularly valuable when labeled data is scarce or "
            "expensive to obtain. It is used extensively in customer segmentation, anomaly "
            "detection, topic modeling, and feature extraction. Auto-encoders and variational "
            "auto-encoders are neural network architectures commonly used for unsupervised "
            "representation learning.",
            body_style,
        )
    )

    story.append(Paragraph("2.3 Reinforcement Learning", subheading_style))
    story.append(
        Paragraph(
            "Reinforcement learning (RL) involves an agent that learns to make decisions by "
            "interacting with an environment. The agent receives rewards or penalties based on "
            "its actions and aims to maximize cumulative reward over time. RL has achieved "
            "impressive results in game playing, with systems like AlphaGo defeating world "
            "champions in Go, and AlphaStar reaching grandmaster level in StarCraft II.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Key concepts in reinforcement learning include the Markov Decision Process (MDP), "
            "value functions, policy gradients, and the exploration-exploitation trade-off. "
            "Deep reinforcement learning combines neural networks with RL algorithms, enabling "
            "agents to handle high-dimensional state spaces. Applications include robotics "
            "control, recommendation systems, resource management, and autonomous driving.",
            body_style,
        )
    )

    # ---- Section 3 ----
    story.append(Paragraph("3. Deep Learning and Neural Networks", heading_style))
    story.append(
        Paragraph(
            "Deep learning is a subset of machine learning based on artificial neural networks "
            "with multiple layers. These deep networks can learn hierarchical representations "
            "of data, with each layer capturing increasingly abstract features. The input layer "
            "receives raw data, hidden layers process and transform it, and the output layer "
            "produces the final result. Backpropagation is the primary algorithm for training "
            "deep neural networks, computing gradients of the loss function with respect to "
            "each weight through the chain rule of calculus.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Convolutional Neural Networks (CNNs) are specialized for processing grid-like data "
            "such as images. They use convolutional layers to automatically learn spatial "
            "hierarchies of features, from edges and textures to objects and scenes. Recurrent "
            "Neural Networks (RNNs) and their variants, Long Short-Term Memory (LSTM) and "
            "Gated Recurrent Unit (GRU), are designed for sequential data such as text and "
            "time series.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "The Transformer architecture, introduced in 2017, has revolutionized natural "
            "language processing and is increasingly used in computer vision and other domains. "
            "Transformers rely on self-attention mechanisms to capture long-range dependencies "
            "in data without the sequential processing limitations of RNNs. Large language "
            "models (LLMs) like GPT and BERT are based on the Transformer architecture and "
            "have demonstrated remarkable capabilities in text generation, translation, "
            "summarization, and question answering.",
            body_style,
        )
    )

    story.append(PageBreak())

    # ---- Section 4 ----
    story.append(Paragraph("4. Natural Language Processing", heading_style))
    story.append(
        Paragraph(
            "Natural Language Processing (NLP) is a field at the intersection of computer "
            "science, artificial intelligence, and linguistics. It focuses on enabling computers "
            "to understand, interpret, and generate human language. NLP encompasses a wide range "
            "of tasks, including text classification, named entity recognition, sentiment "
            "analysis, machine translation, text summarization, and question answering.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "The evolution of NLP has progressed from rule-based systems to statistical methods "
            "and finally to deep learning approaches. Word embeddings like Word2Vec, GloVe, and "
            "FastText represent words as dense vectors in a continuous space, capturing semantic "
            "relationships. Contextual embeddings from models like ELMo, BERT, and GPT provide "
            "word representations that vary based on context, significantly improving performance "
            "on downstream tasks.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Retrieval-Augmented Generation (RAG) is an emerging paradigm that combines the "
            "strengths of retrieval systems and generative models. In RAG, a retrieval component "
            "first finds relevant documents from a knowledge base, and then a generative model "
            "uses those documents as context to produce accurate, grounded responses. This "
            "approach helps mitigate hallucination in language models and enables them to access "
            "up-to-date information without retraining.",
            body_style,
        )
    )

    # ---- Section 5 ----
    story.append(Paragraph("5. Computer Vision", heading_style))
    story.append(
        Paragraph(
            "Computer vision is a field of AI that enables computers to interpret and understand "
            "visual information from the world. Key tasks include image classification, object "
            "detection, semantic segmentation, instance segmentation, and image generation. "
            "The field has been transformed by deep learning, particularly convolutional neural "
            "networks, which have achieved human-level or superhuman performance on many "
            "benchmark tasks.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Object detection algorithms such as YOLO, SSD, and Faster R-CNN can identify and "
            "localize multiple objects in an image in real time. Image segmentation models like "
            "U-Net and Mask R-CNN assign labels to every pixel in an image, enabling precise "
            "understanding of scene composition. Generative Adversarial Networks (GANs) and "
            "diffusion models can create photorealistic images from text descriptions, "
            "opening up new possibilities in creative applications.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Transfer learning has been crucial for computer vision, allowing models pre-trained "
            "on large datasets like ImageNet to be fine-tuned for specific tasks with limited "
            "data. Vision Transformers (ViTs) apply the Transformer architecture to images by "
            "treating image patches as tokens, achieving competitive or superior results "
            "compared to CNNs. Multi-modal models that combine vision and language understanding "
            "can perform tasks like visual question answering and image captioning.",
            body_style,
        )
    )

    # ---- Section 6 ----
    story.append(Paragraph("6. Ethics and Societal Impact", heading_style))
    story.append(
        Paragraph(
            "As AI systems become more powerful and pervasive, ethical considerations become "
            "increasingly important. Key concerns include algorithmic bias, where AI systems "
            "can perpetuate or amplify existing societal biases present in training data. "
            "Fairness, accountability, and transparency (FAT) are essential principles for "
            "responsible AI development. Privacy concerns arise from the massive data "
            "collection required to train AI models, and the potential for surveillance "
            "and tracking.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "The impact of AI on employment is a subject of ongoing debate. While AI automates "
            "certain tasks, it also creates new jobs and augments human capabilities. The "
            "challenge lies in managing the transition and ensuring that the benefits of AI "
            "are distributed equitably. Education and workforce development programs are "
            "essential to prepare workers for an AI-driven economy.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "AI safety research focuses on ensuring that advanced AI systems remain aligned "
            "with human values and intentions. This includes work on interpretability, making "
            "AI decisions understandable to humans; robustness, ensuring AI systems work "
            "reliably under various conditions; and alignment, ensuring AI goals match human "
            "goals. International cooperation and governance frameworks are being developed "
            "to address the global implications of AI technology.",
            body_style,
        )
    )

    # ---- Section 7 ----
    story.append(Paragraph("7. Future Directions", heading_style))
    story.append(
        Paragraph(
            "The future of AI holds tremendous promise across many fronts. Artificial General "
            "Intelligence (AGI), which would match or exceed human intelligence across all "
            "cognitive tasks, remains a long-term goal of the field. Neuro-symbolic AI aims "
            "to combine the pattern recognition strengths of neural networks with the "
            "reasoning capabilities of symbolic AI systems.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Edge AI brings intelligence to resource-constrained devices, enabling real-time "
            "processing without cloud connectivity. Quantum machine learning explores the "
            "intersection of quantum computing and AI, potentially offering exponential "
            "speedups for certain types of computations. Federated learning enables "
            "collaborative model training while keeping data decentralized, addressing "
            "privacy concerns in healthcare, finance, and other sensitive domains.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "AI for science is accelerating discoveries in physics, chemistry, biology, and "
            "materials science. Protein structure prediction by AlphaFold has transformed "
            "structural biology. Climate modeling, drug discovery, and mathematical reasoning "
            "are all areas where AI is making significant contributions. As these technologies "
            "mature, the integration of AI into every aspect of human activity will continue "
            "to deepen, making responsible development more important than ever.",
            body_style,
        )
    )

    doc.build(story)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# 2) tables.pdf
# ---------------------------------------------------------------------------


def generate_tables():
    """Create a document with multiple data tables."""
    path = SAMPLE_DIR / "tables.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        topMargin=72,
        bottomMargin=72,
        leftMargin=54,
        rightMargin=54,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TblTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=16,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "TblHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "TblBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
    )

    # Common table style
    def make_table_style():
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#D9E2F3")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#D9E2F3"), colors.white],
                ),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ]
        )

    story = []

    story.append(Paragraph("Business Data Report", title_style))
    story.append(Spacer(1, 6))

    # --- Table 1: Product Inventory ---
    story.append(Paragraph("Table 1: Product Inventory", heading_style))
    story.append(
        Paragraph(
            "Current inventory levels across warehouse locations as of Q4 2024.",
            body_style,
        )
    )

    inventory_data = [
        [
            "Product ID",
            "Product Name",
            "Category",
            "Quantity",
            "Unit Price",
            "Warehouse",
        ],
        ["PRD-001", "Wireless Mouse", "Electronics", "1,250", "$29.99", "Warehouse A"],
        [
            "PRD-002",
            "Mechanical Keyboard",
            "Electronics",
            "843",
            "$79.99",
            "Warehouse A",
        ],
        ["PRD-003", "USB-C Hub", "Accessories", "2,100", "$44.99", "Warehouse B"],
        ["PRD-004", "Monitor Stand", "Furniture", "567", "$54.99", "Warehouse C"],
        ["PRD-005", "Webcam HD", "Electronics", "1,890", "$64.99", "Warehouse A"],
        ["PRD-006", "Desk Lamp LED", "Lighting", "3,210", "$34.99", "Warehouse B"],
        ["PRD-007", "Ergonomic Chair", "Furniture", "245", "$349.99", "Warehouse C"],
        ["PRD-008", "Laptop Stand", "Accessories", "1,670", "$39.99", "Warehouse B"],
        [
            "PRD-009",
            "Noise-Canceling Headphones",
            "Electronics",
            "920",
            "$149.99",
            "Warehouse A",
        ],
        [
            "PRD-010",
            "Power Strip Surge Protector",
            "Accessories",
            "4,500",
            "$24.99",
            "Warehouse C",
        ],
    ]
    t1 = Table(inventory_data, repeatRows=1)
    t1.setStyle(make_table_style())
    story.append(t1)
    story.append(Spacer(1, 20))

    # --- Table 2: Quarterly Revenue ---
    story.append(Paragraph("Table 2: Quarterly Revenue by Region (in thousands USD)", heading_style))
    story.append(
        Paragraph(
            "Revenue figures for fiscal year 2024 across all operating regions.",
            body_style,
        )
    )

    revenue_data = [
        ["Region", "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "Annual Total"],
        ["North America", "$2,450", "$2,780", "$3,120", "$3,890", "$12,240"],
        ["Europe", "$1,890", "$2,100", "$2,340", "$2,870", "$9,200"],
        ["Asia Pacific", "$1,560", "$1,780", "$2,050", "$2,450", "$7,840"],
        ["Latin America", "$680", "$740", "$890", "$1,020", "$3,330"],
        ["Middle East & Africa", "$420", "$480", "$560", "$670", "$2,130"],
        ["Total", "$6,000", "$7,880", "$8,960", "$10,900", "$34,740"],
    ]
    t2 = Table(revenue_data, repeatRows=1)
    t2.setStyle(make_table_style())
    story.append(t2)

    story.append(PageBreak())

    # --- Table 3: Employee Records ---
    story.append(Paragraph("Table 3: Employee Directory", heading_style))
    story.append(
        Paragraph(
            "Key personnel across departments with their roles and contact information.",
            body_style,
        )
    )

    employee_data = [
        ["Emp ID", "Name", "Department", "Title", "Start Date", "Email"],
        [
            "E-101",
            "Sarah Johnson",
            "Engineering",
            "Senior Developer",
            "2019-03-15",
            "s.johnson@example.com",
        ],
        [
            "E-102",
            "Michael Chen",
            "Engineering",
            "Tech Lead",
            "2018-07-22",
            "m.chen@example.com",
        ],
        [
            "E-103",
            "Emily Rodriguez",
            "Marketing",
            "Marketing Manager",
            "2020-01-10",
            "e.rodriguez@example.com",
        ],
        [
            "E-104",
            "David Kim",
            "Data Science",
            "ML Engineer",
            "2021-05-18",
            "d.kim@example.com",
        ],
        [
            "E-105",
            "Jessica Patel",
            "Product",
            "Product Manager",
            "2019-11-03",
            "j.patel@example.com",
        ],
        [
            "E-106",
            "Robert Taylor",
            "Engineering",
            "DevOps Engineer",
            "2020-08-25",
            "r.taylor@example.com",
        ],
        [
            "E-107",
            "Amanda White",
            "HR",
            "HR Director",
            "2017-02-14",
            "a.white@example.com",
        ],
        [
            "E-108",
            "James Wilson",
            "Finance",
            "Financial Analyst",
            "2022-04-01",
            "j.wilson@example.com",
        ],
        [
            "E-109",
            "Lisa Brown",
            "Data Science",
            "Data Analyst",
            "2021-09-12",
            "l.brown@example.com",
        ],
        [
            "E-110",
            "Thomas Lee",
            "Engineering",
            "Frontend Developer",
            "2023-01-30",
            "t.lee@example.com",
        ],
    ]
    t3 = Table(employee_data, repeatRows=1)
    t3.setStyle(make_table_style())
    story.append(t3)
    story.append(Spacer(1, 20))

    # --- Table 4: Project Status ---
    story.append(Paragraph("Table 4: Project Status Overview", heading_style))
    story.append(
        Paragraph(
            "Active and upcoming projects with timeline and budget information.",
            body_style,
        )
    )

    project_data = [
        ["Project", "Lead", "Status", "Start", "Deadline", "Budget"],
        ["Platform Redesign", "M. Chen", "In Progress", "2024-01", "2024-06", "$450K"],
        ["Mobile App v3", "S. Johnson", "In Progress", "2024-02", "2024-08", "$320K"],
        ["Data Pipeline", "D. Kim", "Planning", "2024-04", "2024-09", "$280K"],
        ["Customer Portal", "T. Lee", "In Progress", "2024-03", "2024-07", "$190K"],
        ["ML Recommender", "L. Brown", "Testing", "2023-10", "2024-05", "$510K"],
        ["Security Audit", "R. Taylor", "Completed", "2024-01", "2024-03", "$120K"],
    ]
    t4 = Table(project_data, repeatRows=1)
    t4.setStyle(make_table_style())
    story.append(t4)

    doc.build(story)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# 3) multi_column.pdf
# ---------------------------------------------------------------------------


class ColumnBreak(Flowable):
    """Force a break to the next column / frame."""

    def __init__(self):
        super().__init__()
        self.width = 0
        self.height = 0

    def draw(self):
        pass

    def wrap(self, availWidth, availHeight):
        # Return zero size; the frame break is triggered by frameEnd
        return (0, 0)


def generate_multi_column():
    """Create a two-column document resembling a research paper."""
    path = SAMPLE_DIR / "multi_column.pdf"

    page_w, page_h = letter
    margin = 54
    gutter = 18
    col_w = (page_w - 2 * margin - gutter) / 2
    frame_h = page_h - 2 * margin

    left_frame = Frame(margin, margin, col_w, frame_h, id="left")
    right_frame = Frame(margin + col_w + gutter, margin, col_w, frame_h, id="right")

    two_col_template = PageTemplate(
        id="TwoCol",
        frames=[left_frame, right_frame],
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        topMargin=margin,
        bottomMargin=margin,
        leftMargin=margin,
        rightMargin=margin,
    )
    doc.addPageTemplates([two_col_template])

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ColTitle",
        parent=styles["Title"],
        fontSize=16,
        spaceAfter=8,
        alignment=TA_CENTER,
    )
    author_style = ParagraphStyle(
        "ColAuthor",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.grey,
    )
    heading_style = ParagraphStyle(
        "ColHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ColBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    )
    abstract_style = ParagraphStyle(
        "ColAbstract",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leftIndent=12,
        rightIndent=12,
    )

    story = []

    # Title and authors (span both columns via the left frame, will reflow)
    story.append(
        Paragraph(
            "Advances in Document Understanding for Retrieval-Augmented Generation Systems",
            title_style,
        )
    )
    story.append(
        Paragraph(
            "J. Smith, A. Kumar, L. Zhang &mdash; Institute of AI Research, 2024",
            author_style,
        )
    )
    story.append(Spacer(1, 6))

    # Abstract
    story.append(Paragraph("<b>Abstract</b>", heading_style))
    story.append(
        Paragraph(
            "This paper surveys recent advances in document understanding techniques that "
            "underpin modern Retrieval-Augmented Generation (RAG) pipelines. We examine "
            "methods for parsing unstructured documents including PDFs, web pages, and "
            "scanned images, and evaluate their effectiveness for downstream retrieval "
            "and generation tasks. Our analysis covers text extraction, layout analysis, "
            "table recognition, and multimodal approaches that combine vision and language "
            "models. We find that hybrid methods combining rule-based extraction with "
            "learned representations achieve the best results across diverse document types.",
            abstract_style,
        )
    )

    # Section 1
    story.append(Paragraph("1. Introduction", heading_style))
    story.append(
        Paragraph(
            "The explosion of digital documents in enterprise and academic settings has "
            "created an urgent need for robust document understanding systems. Organizations "
            "store vast quantities of knowledge in unstructured formats such as PDFs, Word "
            "documents, presentations, and scanned images. Unlocking this knowledge for "
            "AI-powered applications, particularly Retrieval-Augmented Generation (RAG), "
            "requires sophisticated parsing and extraction pipelines.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "RAG systems combine retrieval from a document corpus with generative language "
            "models to produce accurate, grounded responses. The quality of the retrieval "
            "step depends critically on how well source documents have been parsed, chunked, "
            "and indexed. Poor extraction leads to noisy passages that degrade both retrieval "
            "precision and generation quality.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "In this paper, we provide a comprehensive analysis of document understanding "
            "techniques relevant to RAG pipelines. We focus on PDF documents, which remain "
            "the most prevalent format for sharing structured knowledge in business and "
            "academia. We evaluate multiple extraction libraries and approaches, measuring "
            "their fidelity in preserving text content, layout structure, and tabular data.",
            body_style,
        )
    )

    # Section 2
    story.append(Paragraph("2. Related Work", heading_style))
    story.append(
        Paragraph(
            "Document understanding has a rich history in the document analysis and "
            "recognition community. Early systems relied on rule-based approaches with "
            "hand-crafted heuristics for layout segmentation. The introduction of deep "
            "learning brought significant improvements, with models like LayoutLM and "
            "DocFormer learning joint representations of text and layout.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Table extraction has received particular attention due to the structured "
            "nature of tabular data. Methods range from heuristic line detection to "
            "deep learning approaches such as TableNet and DETR-based table detectors. "
            "Recent multimodal models like Donut and Nougat can parse documents end-to-end "
            "without relying on OCR as an intermediate step.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "The RAG paradigm was introduced by Lewis et al. (2020) and has since become "
            "a standard approach for knowledge-intensive NLP tasks. Subsequent work has "
            "explored various aspects of RAG including retrieval strategies, chunk size "
            "optimization, and re-ranking methods. However, relatively little attention "
            "has been paid to the document parsing stage that precedes retrieval.",
            body_style,
        )
    )

    # Section 3
    story.append(Paragraph("3. Methodology", heading_style))
    story.append(
        Paragraph(
            "We evaluate five PDF extraction approaches: (1) PyPDF for basic text extraction, "
            "(2) pdfplumber for layout-aware extraction and table detection, (3) PyMuPDF for "
            "high-performance extraction with position information, (4) Tesseract OCR for "
            "scanned documents, and (5) a hybrid pipeline combining multiple methods.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Our evaluation corpus consists of 500 documents spanning four categories: "
            "academic papers, technical reports, financial statements, and product manuals. "
            "Each document was manually annotated with ground-truth text, table structures, "
            "and layout regions. We measure extraction quality using character error rate "
            "(CER), table structure recognition (TSR) accuracy, and reading order accuracy.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "For the RAG evaluation, we chunk extracted text using four strategies: "
            "fixed-size character windows, sentence-based splitting, recursive splitting "
            "with semantic boundaries, and heading-aware chunking. We then embed chunks "
            "using a sentence transformer model and evaluate retrieval quality on a set "
            "of 200 question-answer pairs derived from the document corpus.",
            body_style,
        )
    )

    # Section 4
    story.append(Paragraph("4. Results", heading_style))
    story.append(
        Paragraph(
            "Our experiments reveal significant differences between extraction methods "
            "across document categories. PyMuPDF consistently achieves the lowest character "
            "error rate, averaging 2.3% across all documents. pdfplumber provides the best "
            "table extraction with 87% TSR accuracy, compared to 45% for PyPDF and 76% for "
            "PyMuPDF. Tesseract OCR, while essential for scanned documents, introduces "
            "higher error rates of 5-8% on born-digital PDFs.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "The hybrid pipeline, which selects the best extraction method based on document "
            "characteristics, achieves the highest overall quality with 1.8% CER and 89% TSR "
            "accuracy. Documents are first classified as born-digital or scanned using image "
            "analysis, and then processed accordingly.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "For RAG retrieval quality, heading-aware chunking combined with PyMuPDF extraction "
            "yields the best results, with a mean reciprocal rank (MRR) of 0.82 and recall@5 "
            "of 0.91. Fixed-size chunking performs worst at MRR 0.68, while recursive splitting "
            "achieves MRR 0.79. These results underscore the importance of respecting document "
            "structure during chunking.",
            body_style,
        )
    )

    # Section 5
    story.append(Paragraph("5. Discussion", heading_style))
    story.append(
        Paragraph(
            "Our findings highlight several key insights for practitioners building RAG systems. "
            "First, no single extraction method dominates across all document types, suggesting "
            "that adaptive pipelines are necessary for production systems. Second, table "
            "extraction remains a significant challenge, and converting tables to natural "
            "language descriptions substantially improves retrieval performance.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Third, the choice of chunking strategy has a measurable impact on RAG quality, "
            "with structure-aware approaches outperforming naive splitting. Fourth, multi-column "
            "layouts require special handling to preserve reading order; without layout analysis, "
            "text from different columns may be interleaved, producing incoherent passages.",
            body_style,
        )
    )

    # Section 6
    story.append(Paragraph("6. Conclusion", heading_style))
    story.append(
        Paragraph(
            "We have presented a comprehensive evaluation of document understanding techniques "
            "for RAG systems. Our results demonstrate that careful attention to the parsing "
            "stage significantly impacts downstream retrieval and generation quality. We "
            "recommend a hybrid approach that combines multiple extraction methods with "
            "structure-aware chunking for optimal results. Future work should explore "
            "end-to-end learned parsing systems and their integration with RAG pipelines.",
            body_style,
        )
    )

    # References
    story.append(Paragraph("References", heading_style))
    refs = [
        "[1] Lewis, P. et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS.",
        "[2] Xu, Y. et al. (2020). LayoutLM: Pre-training of Text and Layout for Document Understanding. KDD.",
        "[3] Appalaraju, S. et al. (2021). DocFormer: End-to-End Transformer for Document Understanding. ICCV.",
        "[4] Kim, G. et al. (2022). Donut: Document Understanding Transformer without OCR. ECCV.",
        "[5] Blecher, L. et al. (2023). Nougat: Neural Optical Understanding for Academic Documents. arXiv.",
    ]
    for ref in refs:
        story.append(
            Paragraph(
                ref,
                ParagraphStyle(
                    "Ref",
                    parent=body_style,
                    fontSize=8,
                    leading=11,
                    spaceAfter=3,
                ),
            )
        )

    doc.build(story)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# 4) mixed_content.pdf
# ---------------------------------------------------------------------------


def generate_mixed_content():
    """Create a document mixing text, tables, bullet points, and headers."""
    path = SAMPLE_DIR / "mixed_content.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        topMargin=72,
        bottomMargin=72,
        leftMargin=72,
        rightMargin=72,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MixTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=16,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "MixHeading",
        parent=styles["Heading1"],
        fontSize=15,
        spaceBefore=18,
        spaceAfter=10,
    )
    subheading_style = ParagraphStyle(
        "MixSubheading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "MixBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
    )
    bullet_style = ParagraphStyle(
        "MixBullet",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        spaceAfter=4,
        leftIndent=36,
        bulletIndent=18,
        bulletFontSize=11,
    )

    def make_table_style():
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E75B6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#DAEEF3"), colors.white],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ]
        )

    story = []

    # Title
    story.append(Paragraph("2024 Technology Trends Report", title_style))
    story.append(Spacer(1, 8))

    # --- Introduction ---
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(
        Paragraph(
            "This report provides an analysis of the most significant technology trends "
            "shaping the industry in 2024. From the rapid adoption of generative AI to "
            "advances in quantum computing, these trends are reshaping how businesses "
            "operate and compete. Understanding these trends is essential for strategic "
            "planning and technology investment decisions.",
            body_style,
        )
    )

    # --- Key Findings (bullet points) ---
    story.append(Paragraph("Key Findings", heading_style))
    bullets = [
        "Generative AI adoption has increased by 340% year-over-year across enterprise organizations.",
        "Cloud-native architectures now power 78% of new application deployments.",
        "Cybersecurity spending has reached $188 billion globally, driven by increasing threat sophistication.",
        "Edge computing deployments grew 45% as organizations seek lower latency and data sovereignty.",
        "Sustainability-focused technology initiatives now represent 23% of IT budgets on average.",
        "Low-code and no-code platforms are used by 65% of organizations for at least some development.",
        "API-first strategies have been adopted by 82% of enterprises surveyed.",
    ]
    for b in bullets:
        story.append(Paragraph(f"\u2022 {b}", bullet_style))
    story.append(Spacer(1, 10))

    # --- Section with text ---
    story.append(Paragraph("Generative AI in the Enterprise", heading_style))
    story.append(
        Paragraph(
            "Generative AI has emerged as the defining technology of 2024. Large language "
            "models (LLMs) are being deployed across industries for tasks ranging from "
            "customer support automation to code generation and content creation. "
            "Retrieval-Augmented Generation (RAG) has become the preferred architecture "
            "for enterprise AI applications, combining the fluency of generative models "
            "with the accuracy of information retrieval.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Organizations are investing heavily in data infrastructure to support their "
            "AI initiatives. Vector databases, embedding pipelines, and document processing "
            "systems form the backbone of modern RAG deployments. The ability to accurately "
            "extract and structure information from unstructured documents is a critical "
            "capability that directly impacts AI application quality.",
            body_style,
        )
    )

    # --- Table: AI Adoption ---
    story.append(Paragraph("AI Adoption by Industry", subheading_style))
    ai_data = [
        ["Industry", "Adoption Rate", "Primary Use Case", "Avg. ROI"],
        ["Financial Services", "89%", "Fraud Detection & Risk Analysis", "340%"],
        ["Healthcare", "76%", "Diagnostic Assistance", "280%"],
        ["Manufacturing", "72%", "Predictive Maintenance", "310%"],
        ["Retail", "81%", "Personalization & Recommendations", "250%"],
        ["Technology", "94%", "Code Generation & Testing", "420%"],
        ["Education", "58%", "Personalized Learning", "180%"],
    ]
    t = Table(ai_data, repeatRows=1)
    t.setStyle(make_table_style())
    story.append(t)
    story.append(Spacer(1, 14))

    # --- Another text section ---
    story.append(Paragraph("Cloud and Infrastructure Trends", heading_style))
    story.append(
        Paragraph(
            "The cloud computing landscape continues to evolve rapidly. Multi-cloud and "
            "hybrid-cloud strategies have become the norm, with organizations distributing "
            "workloads across multiple providers to optimize cost, performance, and "
            "resilience. Kubernetes has solidified its position as the de facto standard "
            "for container orchestration.",
            body_style,
        )
    )

    # --- Bullet points for cloud ---
    story.append(Paragraph("Top Cloud Priorities for 2024", subheading_style))
    cloud_bullets = [
        "Cost optimization and FinOps practices to manage growing cloud spend.",
        "Multi-cloud governance and consistent security policies across providers.",
        "Serverless and event-driven architectures for new microservices.",
        "Infrastructure as Code (IaC) maturity using Terraform, Pulumi, and CDK.",
        "Green computing initiatives to reduce carbon footprint of cloud workloads.",
    ]
    for b in cloud_bullets:
        story.append(Paragraph(f"\u2022 {b}", bullet_style))
    story.append(Spacer(1, 10))

    # --- Table: Cloud Market Share ---
    story.append(Paragraph("Cloud Provider Market Share", subheading_style))
    cloud_data = [
        ["Provider", "Market Share", "YoY Growth", "Key Strength"],
        ["AWS", "31%", "+12%", "Breadth of services"],
        ["Microsoft Azure", "25%", "+18%", "Enterprise integration"],
        ["Google Cloud", "11%", "+22%", "AI/ML capabilities"],
        ["Others", "33%", "+8%", "Specialized offerings"],
    ]
    t2 = Table(cloud_data, repeatRows=1)
    t2.setStyle(make_table_style())
    story.append(t2)
    story.append(Spacer(1, 14))

    # --- Cybersecurity section ---
    story.append(Paragraph("Cybersecurity Landscape", heading_style))
    story.append(
        Paragraph(
            "The cybersecurity threat landscape has become increasingly complex. "
            "Ransomware attacks continue to rise in frequency and sophistication, while "
            "AI-powered threats present new challenges for defense teams. Zero-trust "
            "architecture has moved from concept to implementation, with organizations "
            "adopting identity-centric security models that verify every access request.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "Supply chain security has emerged as a critical concern following high-profile "
            "incidents. Software Bill of Materials (SBOM) requirements are becoming "
            "standard, and organizations are implementing stricter controls over "
            "third-party dependencies. AI is being used both offensively and defensively, "
            "creating an arms race between attackers and defenders.",
            body_style,
        )
    )

    # --- Conclusion ---
    story.append(Paragraph("Recommendations", heading_style))
    rec_bullets = [
        "Invest in RAG-based AI architectures for knowledge management applications.",
        "Establish robust document parsing pipelines to feed AI systems with high-quality data.",
        "Adopt a multi-cloud strategy with consistent governance and security policies.",
        "Prioritize cybersecurity investments, especially in zero-trust and supply chain security.",
        "Build internal AI literacy through training programs and centers of excellence.",
        "Evaluate sustainability metrics for all technology decisions and vendor selections.",
    ]
    for b in rec_bullets:
        story.append(Paragraph(f"\u2022 {b}", bullet_style))

    doc.build(story)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating sample PDF documents...")
    print()
    generate_simple_text()
    generate_tables()
    generate_multi_column()
    generate_mixed_content()
    print()
    print("All sample PDFs generated successfully.")
