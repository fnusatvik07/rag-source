"""Generate sample Markdown and plain text files for testing parsing and chunking."""

from pathlib import Path

SAMPLE_DIR = Path(__file__).parent


def generate_technical_doc():
    """A markdown document about Building REST APIs with rich formatting."""
    md = """\
# Building REST APIs: A Comprehensive Guide

## Introduction

REST (Representational State Transfer) is an architectural style for designing networked applications. RESTful APIs \
have become the standard way for web services to communicate, powering everything from mobile apps to microservices \
architectures. This guide covers the essential concepts, best practices, and implementation patterns for building \
robust REST APIs.

## Core Principles

REST is built on several fundamental principles that guide API design:

- **Statelessness**: Each request contains all the information needed to process it. The server does not store client \
session state between requests.
- **Client-Server Separation**: The client and server are independent. The client does not need to know about data \
storage, and the server does not need to know about the user interface.
- **Uniform Interface**: Resources are identified by URIs, manipulated through representations, and self-descriptive \
messages.
- **Cacheability**: Responses must define themselves as cacheable or non-cacheable to improve performance.
- **Layered System**: The architecture can be composed of hierarchical layers, with each layer only knowing about the \
layer it interacts with.

## HTTP Methods

RESTful APIs use standard HTTP methods to perform operations on resources:

| Method | Purpose | Idempotent | Safe | Example |
|--------|---------|------------|------|---------|
| GET | Retrieve a resource | Yes | Yes | `GET /api/users/123` |
| POST | Create a new resource | No | No | `POST /api/users` |
| PUT | Replace a resource entirely | Yes | No | `PUT /api/users/123` |
| PATCH | Partially update a resource | No | No | `PATCH /api/users/123` |
| DELETE | Remove a resource | Yes | No | `DELETE /api/users/123` |

### Idempotency

An operation is **idempotent** if performing it multiple times produces the same result as performing it once. GET, \
PUT, and DELETE are idempotent by design. POST is not, because calling it twice creates two resources.

## Resource Design

### URL Structure

Follow these conventions for clean, intuitive URLs:

1. Use nouns, not verbs: `/api/users` not `/api/getUsers`
2. Use plural names: `/api/users` not `/api/user`
3. Use hyphens for readability: `/api/user-profiles` not `/api/userProfiles`
4. Nest resources for relationships: `/api/users/123/orders`
5. Keep URLs shallow (max 2-3 levels deep)

### Request and Response Format

JSON is the standard format for REST API request and response bodies:

```json
{
    "id": 123,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "role": "admin",
    "created_at": "2025-01-15T10:30:00Z"
}
```

## Authentication and Authorization

### Common Authentication Methods

There are several approaches to securing REST APIs:

1. **API Keys**: Simple but limited. Pass a key in the header or query parameter.
2. **OAuth 2.0**: Industry standard for delegated authorization. Supports multiple grant types.
3. **JWT (JSON Web Tokens)**: Stateless tokens containing encoded claims. Popular for microservices.

```python
# Example: JWT authentication middleware
import jwt
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = payload
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401
        return f(*args, **kwargs)
    return decorated
```

## Error Handling

### Standard Error Response Format

Consistent error responses make APIs easier to consume:

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "The request body contains invalid fields.",
        "details": [
            {
                "field": "email",
                "message": "Must be a valid email address"
            }
        ]
    }
}
```

### HTTP Status Codes

Use appropriate status codes to communicate the result:

- **200 OK**: Successful GET, PUT, PATCH, or DELETE
- **201 Created**: Successful POST that created a resource
- **204 No Content**: Successful DELETE with no response body
- **400 Bad Request**: Invalid request syntax or parameters
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Request conflicts with current state
- **422 Unprocessable Entity**: Valid syntax but semantic errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server failure

## Pagination

### Offset-Based Pagination

The simplest approach, using `page` and `per_page` parameters:

```
GET /api/users?page=2&per_page=20
```

### Cursor-Based Pagination

More efficient for large datasets. Uses an opaque cursor to mark position:

```
GET /api/users?cursor=eyJpZCI6MTIzfQ&limit=20
```

## Best Practices Summary

1. Use consistent naming conventions across all endpoints
2. Version your API from day one (e.g., `/api/v1/users`)
3. Implement rate limiting to protect your service
4. Return appropriate HTTP status codes
5. Provide comprehensive error messages
6. Support filtering, sorting, and pagination for list endpoints
7. Use HATEOAS links to make the API discoverable
8. Document your API with OpenAPI/Swagger specifications
9. Implement request validation at the API boundary
10. Log all requests for debugging and auditing
"""
    (SAMPLE_DIR / "technical_doc.md").write_text(md)
    print("Generated: technical_doc.md")


def generate_research_paper():
    """A markdown document simulating a research paper."""
    md = """\
# Optimizing Chunk Size Selection for Retrieval-Augmented Generation Systems

## Abstract

Retrieval-Augmented Generation (RAG) systems rely on splitting documents into chunks for embedding and retrieval. The \
choice of chunk size significantly impacts retrieval accuracy, answer quality, and system latency. In this paper, we \
conduct a systematic evaluation of chunk sizes ranging from 128 to 2048 tokens across four domain-specific datasets. \
Our experiments reveal that the optimal chunk size is highly domain-dependent, with technical documentation benefiting \
from larger chunks (512-1024 tokens) while conversational datasets perform best with smaller chunks (128-256 tokens). \
We propose an adaptive chunking framework that selects chunk sizes based on document characteristics, achieving a \
15.3% \
improvement in answer accuracy over fixed-size approaches.

## Introduction

The emergence of large language models (LLMs) has transformed natural language processing, yet these models face \
fundamental limitations when dealing with knowledge that is not present in their training data. Retrieval-Augmented \
Generation addresses this limitation by augmenting LLM inputs with relevant information retrieved from external \
knowledge bases.

A critical but often overlooked component of RAG systems is the chunking strategy -- how source documents are divided \
into segments for embedding and retrieval. The chunk size directly affects multiple aspects of system performance. \
Chunks that are too small may lack sufficient context for meaningful retrieval, while chunks that are too large may \
introduce noise and exceed the context window limitations of embedding models.

Despite its importance, chunk size selection is typically treated as a hyperparameter to be tuned empirically, with \
little guidance available to practitioners. Most implementations default to arbitrary sizes (e.g., 512 or 1000 \
characters) without considering the characteristics of the source documents or the nature of expected queries.

This paper makes three contributions. First, we present a comprehensive empirical study of chunk size effects across \
diverse domains. Second, we identify document characteristics that correlate with optimal chunk sizes. Third, we \
propose an adaptive chunking framework that automatically selects appropriate chunk sizes based on document analysis.

## Methodology

### Datasets

We evaluate our approach on four datasets representing different document types commonly encountered in RAG \
applications:

1. **TechDocs**: 5,000 technical documentation pages from open-source software projects, containing code examples, API \
references, and tutorials.
2. **LegalCorpus**: 2,500 legal documents including contracts, regulations, and court opinions.
3. **MedicalQA**: 3,200 medical articles and clinical guidelines from PubMed.
4. **ConversationLogs**: 10,000 customer support conversations from an enterprise help desk system.

### Chunking Strategies

We evaluate five chunking strategies at each size:

1. **Fixed Character**: Splits text at exact character boundaries with configurable overlap.
2. **Sentence-Based**: Groups N sentences per chunk, respecting sentence boundaries.
3. **Paragraph-Based**: Uses paragraph breaks (double newlines) as natural chunk boundaries.
4. **Recursive**: Attempts progressively finer separators (paragraphs, newlines, sentences, characters).
5. **Semantic**: Groups sentences by topic similarity using sentence embeddings.

### Evaluation Metrics

We measure system performance using three metrics:

- **Retrieval Precision@5**: The fraction of top-5 retrieved chunks that are relevant to the query.
- **Answer Accuracy**: The correctness of the generated answer, evaluated by human annotators on a 1-5 scale.
- **Latency**: End-to-end response time from query submission to answer generation.

### Experimental Setup

All experiments use the same embedding model (text-embedding-3-small) and LLM (GPT-4) to isolate the effect of \
chunking. We use cosine similarity for retrieval with a FAISS index. Each configuration is evaluated on 500 queries \
per \
dataset, with three independent runs to account for variance.

## Results

### Chunk Size Effects

Our experiments reveal a clear relationship between chunk size and performance that varies by domain:

For TechDocs, retrieval precision peaks at 512 tokens (0.82) and remains stable up to 1024 tokens (0.80), dropping \
sharply at 2048 tokens (0.61). Answer accuracy follows a similar pattern, with the best scores at 512-768 tokens. The \
presence of code blocks in technical documentation means that smaller chunks often split code examples, losing \
critical \
context.

For LegalCorpus, larger chunks consistently outperform smaller ones. Precision at 1024 tokens (0.78) is significantly \
higher than at 128 tokens (0.52). Legal text relies heavily on cross-references within paragraphs, and splitting these \
references across chunks degrades retrieval quality.

MedicalQA shows optimal performance at 256-512 tokens. Medical text is information-dense, and smaller chunks allow \
more \
precise retrieval of specific facts. However, chunks below 128 tokens lose the clinical context needed for accurate \
answers.

ConversationLogs perform best at 128-256 tokens, reflecting the short, turn-based nature of support conversations. \
Each \
turn typically contains a discrete piece of information, and larger chunks introduce noise from unrelated conversation \
turns.

### Chunking Strategy Comparison

Across all datasets and sizes, recursive chunking consistently outperforms fixed-character chunking by 8-12% on \
retrieval precision. Sentence-based chunking performs comparably to recursive chunking for well-structured documents \
but falls behind for documents with inconsistent formatting. Semantic chunking achieves the best results on \
ConversationLogs but is computationally expensive, adding 200-400ms of preprocessing time per document.

## Conclusion

Our study demonstrates that chunk size selection is a critical design decision in RAG systems that should not be \
treated as a simple hyperparameter. The optimal chunk size depends on document type, content density, and query \
patterns. We recommend that practitioners begin with recursive chunking at 512 tokens as a reasonable default, then \
adjust based on domain-specific evaluation.

The adaptive chunking framework we propose provides an automated approach to chunk size selection that eliminates the \
need for manual tuning. By analyzing document characteristics such as average sentence length, paragraph structure, \
and \
vocabulary density, the framework selects an appropriate chunk size for each document, achieving consistent \
improvements across all evaluated domains.

Future work will explore dynamic chunk sizes within a single document, where different sections may benefit from \
different chunk sizes based on their content characteristics. We also plan to investigate the interaction between \
chunk \
size and different embedding models, as model architecture and training data may influence the optimal chunking \
strategy.
"""
    (SAMPLE_DIR / "research_paper.md").write_text(md)
    print("Generated: research_paper.md")


def generate_plain_text():
    """A plain text document about the History of Computing (~1500 words)."""
    txt = """\
The History of Computing: From Mechanical Calculators to Artificial Intelligence

The story of computing stretches back thousands of years, beginning with the earliest counting devices and culminating \
in the powerful artificial intelligence systems we use today. Understanding this history provides essential context \
for \
appreciating how far the field has come and where it might be heading.

The earliest computing devices were simple mechanical tools designed to assist with arithmetic. The abacus, which \
originated in ancient Mesopotamia around 2400 BCE, was one of the first widely used calculating tools. It remained the \
primary computational aid for merchants and scholars for millennia, and variations of it are still used in some parts \
of the world today. The abacus demonstrated a fundamental principle that would persist throughout computing history: \
the use of physical representations to model abstract mathematical concepts.

The seventeenth century saw the first mechanical calculators. Blaise Pascal invented the Pascaline in 1642, a device \
that could perform addition and subtraction through a system of interlocking gears. A few decades later, Gottfried \
Wilhelm Leibniz improved upon Pascal's design with his Step Reckoner, which could also perform multiplication and \
division. These devices were remarkable engineering achievements, but they were expensive, fragile, and limited to \
basic arithmetic operations.

The conceptual foundations of modern computing were laid in the nineteenth century by Charles Babbage, an English \
mathematician and inventor. Babbage designed two groundbreaking machines: the Difference Engine, intended for \
computing \
mathematical tables, and the Analytical Engine, a general-purpose computing machine. The Analytical Engine, though \
never completed during Babbage's lifetime, contained many features found in modern computers, including a processing \
unit, memory, and the ability to be programmed using punched cards. Ada Lovelace, who worked with Babbage, wrote what \
is widely considered the first computer program -- an algorithm for the Analytical Engine to compute Bernoulli \
numbers. \
Her insight that the machine could manipulate symbols beyond mere numbers foreshadowed the versatility of modern \
computers.

The late nineteenth and early twentieth centuries brought the development of electromechanical computing devices. \
Herman Hollerith invented a tabulating machine that used punched cards to process data for the 1890 United States \
Census. His company eventually became IBM, which would dominate the computing industry for decades. The punched card \
system proved so effective that it remained in widespread use well into the 1970s.

The true dawn of electronic computing arrived during World War II. The war created an urgent need for rapid \
calculations -- breaking enemy codes, computing artillery firing tables, and designing nuclear weapons. The British \
Colossus machines, built at Bletchley Park starting in 1943, were among the first electronic digital computers, \
designed specifically for codebreaking. In the United States, the ENIAC (Electronic Numerical Integrator and Computer) \
became operational in 1945. ENIAC was a massive machine, weighing over 27 tons and containing more than 17,000 vacuum \
tubes. Despite its size, it could perform calculations thousands of times faster than any previous device.

The postwar period saw rapid advances in computing technology. The invention of the transistor at Bell Labs in 1947 by \
John Bardeen, Walter Brattain, and William Shockley transformed the field. Transistors were smaller, more reliable, \
and \
consumed far less power than vacuum tubes. By the late 1950s, transistor-based computers were replacing their \
vacuum-tube predecessors, making computing more accessible and affordable.

The development of integrated circuits in the late 1950s and early 1960s represented another quantum leap. Jack Kilby \
at Texas Instruments and Robert Noyce at Fairchild Semiconductor independently developed methods for fabricating \
multiple transistors on a single piece of semiconductor material. This innovation dramatically reduced the size and \
cost of computing components while increasing their speed and reliability. Gordon Moore, co-founder of Intel, observed \
in 1965 that the number of transistors on integrated circuits was doubling approximately every two years -- an \
observation that became known as Moore's Law and has held roughly true for over five decades.

The 1970s brought computing to the masses with the development of the microprocessor and the personal computer. The \
Intel 4004, released in 1971, was the first commercially available microprocessor, integrating the entire central \
processing unit of a computer onto a single chip. This development paved the way for personal computers. The Altair \
8800, introduced in 1975, is often considered the first commercially successful personal computer, though it required \
assembly and had limited capabilities. The Apple II, released in 1977, and the IBM PC, introduced in 1981, brought \
personal computing to homes and offices worldwide.

The 1980s and 1990s saw the rise of software as a driving force in computing. Operating systems like Microsoft Windows \
and Apple's Macintosh OS made computers accessible to non-technical users through graphical user interfaces. The \
development of the World Wide Web by Tim Berners-Lee in 1989, built on top of the Internet infrastructure that had \
been \
growing since the 1960s, transformed computing from a standalone activity into a connected experience. Email, web \
browsing, and online commerce changed how people communicated, accessed information, and conducted business.

The twenty-first century has been characterized by the explosion of mobile computing, cloud services, and artificial \
intelligence. The introduction of the iPhone in 2007 and subsequent smartphones put powerful computers in billions of \
pockets worldwide. Cloud computing, pioneered by companies like Amazon Web Services, Google Cloud, and Microsoft \
Azure, \
shifted computing resources from local machines to massive data centers, enabling on-demand access to virtually \
unlimited processing power and storage.

Perhaps the most significant development of recent years has been the rapid advancement of artificial intelligence and \
machine learning. Neural networks, a concept dating back to the 1940s, have experienced a renaissance thanks to \
increased computational power, vast amounts of training data, and algorithmic improvements. Deep learning techniques \
have achieved remarkable results in image recognition, natural language processing, game playing, and scientific \
discovery. The development of large language models, trained on enormous text corpora, has demonstrated capabilities \
that were considered science fiction just a decade ago.

The field of computing continues to evolve at a remarkable pace. Quantum computing promises to solve certain problems \
that are intractable for classical computers. Edge computing brings processing closer to data sources, reducing \
latency \
for real-time applications. Advances in hardware design, from specialized AI accelerators to neuromorphic chips that \
mimic brain architecture, continue to push the boundaries of what is computationally feasible.

Looking back over the history of computing, several themes emerge. First, the trend toward miniaturization and \
increased capability has been remarkably consistent, from room-sized machines to pocket-sized devices millions of \
times \
more powerful. Second, each major advance in hardware has enabled new categories of software applications that were \
previously impractical. Third, computing has progressively moved from being a specialized tool for scientists and \
engineers to being an integral part of everyday life for billions of people. Finally, the pace of change continues to \
accelerate, with each decade bringing transformations that would have seemed impossible to previous generations.

As we look toward the future, the history of computing reminds us that the most impactful developments often come from \
unexpected directions. The inventors of the transistor could not have imagined smartphones, and the creators of the \
Internet did not foresee social media. Whatever comes next in computing will likely be equally surprising and \
transformative.
"""
    (SAMPLE_DIR / "plain_text.txt").write_text(txt)
    print("Generated: plain_text.txt")


def generate_structured_notes():
    """Plain text with some structure: Topic: labels, dashed lists, sections."""
    txt = """\
Topic: Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables systems to learn from data without being \
explicitly programmed. It has become one of the most important areas of computer science.

Key Concepts:
- Supervised learning uses labeled training data to learn a mapping function
- Unsupervised learning finds patterns in data without labeled examples
- Reinforcement learning trains agents through reward and punishment signals
- Semi-supervised learning combines small labeled datasets with large unlabeled ones

Common Algorithms:
- Linear regression for continuous value prediction
- Logistic regression for binary classification
- Decision trees for interpretable classification and regression
- Random forests for ensemble-based prediction
- Support vector machines for high-dimensional classification
- K-means clustering for unsupervised grouping
- Neural networks for complex pattern recognition

Topic: Data Preprocessing

Data preprocessing is a critical step that can significantly impact model performance. Raw data often contains noise, \
missing values, and inconsistencies that must be addressed before training.

Steps in Data Preprocessing:
- Data cleaning: handle missing values, remove duplicates, fix errors
- Feature scaling: normalize or standardize numeric features
- Encoding: convert categorical variables to numeric representations
- Feature selection: identify the most relevant features for the model
- Train-test split: divide data into training and evaluation sets

Common Pitfalls:
- Data leakage from using test data information during training
- Not handling class imbalance in classification problems
- Applying scaling after the train-test split incorrectly
- Ignoring outliers that can skew model performance

Topic: Model Evaluation

Evaluating model performance correctly is essential for building reliable systems. Different metrics are appropriate \
for different types of problems.

Classification Metrics:
- Accuracy: overall proportion of correct predictions
- Precision: proportion of positive predictions that are correct
- Recall: proportion of actual positives that are identified
- F1 Score: harmonic mean of precision and recall
- ROC-AUC: area under the receiver operating characteristic curve

Regression Metrics:
- Mean Absolute Error (MAE): average absolute difference between predicted and actual values
- Mean Squared Error (MSE): average squared difference between predicted and actual values
- Root Mean Squared Error (RMSE): square root of MSE, in original units
- R-squared: proportion of variance explained by the model

Validation Techniques:
- Hold-out validation: simple train-test split
- K-fold cross-validation: rotate through K train-test splits
- Stratified K-fold: preserves class distribution in each fold
- Time series split: respects temporal ordering of data

Topic: Deployment Considerations

Moving a model from development to production requires careful planning and infrastructure. Many models that perform \
well in testing fail to deliver value in production.

Key Challenges:
- Model serving: choosing between batch and real-time inference
- Monitoring: detecting model drift and performance degradation
- Scaling: handling increased load without sacrificing latency
- Versioning: managing multiple model versions simultaneously
- Retraining: establishing pipelines for regular model updates

Best Practices:
- Start with a simple baseline model before building complex ones
- Automate the training and deployment pipeline early
- Monitor model predictions and retrain on a regular schedule
- Document model assumptions, limitations, and expected behavior
- Plan for graceful degradation when the model is unavailable
"""
    (SAMPLE_DIR / "structured_notes.txt").write_text(txt)
    print("Generated: structured_notes.txt")


if __name__ == "__main__":
    generate_technical_doc()
    generate_research_paper()
    generate_plain_text()
    generate_structured_notes()
    print("\nAll markdown/text samples generated!")
