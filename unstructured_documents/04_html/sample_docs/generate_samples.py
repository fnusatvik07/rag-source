"""Generate sample HTML files for testing extraction methods."""

from pathlib import Path

SAMPLE_DIR = Path(__file__).parent


def generate_article_page():
    """A typical blog/article page with navigation, content, sidebar, and footer."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="author" content="Jane Smith">
    <meta name="description" content="An introduction to natural language processing">
    <title>Understanding Natural Language Processing</title>
</head>
<body>
    <nav>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/blog">Blog</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>

    <main>
        <article>
            <h1>Understanding Natural Language Processing</h1>
            <p class="meta">Published on January 15, 2025 by Jane Smith | 8 min read</p>

            <h2>What is NLP?</h2>
            <p>Natural Language Processing (NLP) is a branch of artificial intelligence
            that focuses on the interaction between computers and humans through natural
            language. The ultimate goal of NLP is to enable computers to understand,
            interpret, and generate human language in a valuable way.</p>

            <p>NLP combines computational linguistics, machine learning, and deep learning
            models to process human language. It powers many applications we use daily,
            from search engines to virtual assistants.</p>

            <h2>Key NLP Tasks</h2>
            <ul>
                <li><strong>Tokenization</strong>: Breaking text into individual words or subwords</li>
                <li><strong>Named Entity Recognition</strong>: Identifying entities like people, organizations, \
and locations</li>
                <li><strong>Sentiment Analysis</strong>: Determining the emotional tone of text</li>
                <li><strong>Machine Translation</strong>: Converting text from one language to another</li>
                <li><strong>Text Summarization</strong>: Creating concise summaries of longer documents</li>
            </ul>

            <h2>Modern NLP Architecture</h2>
            <p>The transformer architecture, introduced in the paper "Attention Is All You Need"
            (2017), revolutionized NLP. Key developments include:</p>

            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Year</th>
                        <th>Parameters</th>
                        <th>Key Innovation</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>BERT</td><td>2018</td><td>340M</td><td>Bidirectional pre-training</td></tr>
                    <tr><td>GPT-2</td><td>2019</td><td>1.5B</td><td>Large-scale language modeling</td></tr>
                    <tr><td>T5</td><td>2019</td><td>11B</td><td>Text-to-text framework</td></tr>
                    <tr><td>GPT-3</td><td>2020</td><td>175B</td><td>Few-shot learning</td></tr>
                    <tr><td>PaLM</td><td>2022</td><td>540B</td><td>Scaling with pathways</td></tr>
                </tbody>
            </table>

            <h2>NLP in Practice</h2>
            <p>Modern NLP applications are everywhere. Chatbots handle customer service
            inquiries, email clients suggest replies, and search engines understand
            complex queries. The field continues to evolve rapidly with new models
            and techniques being developed regularly.</p>

            <blockquote>
                <p>"The development of full artificial intelligence could spell the end of
                the human race. It would take off on its own, and redesign itself at an
                ever-increasing rate." - Stephen Hawking</p>
            </blockquote>

            <h2>Conclusion</h2>
            <p>NLP has transformed how we interact with technology. As models become more
            sophisticated and training data more diverse, we can expect even more
            impressive capabilities in the years to come.</p>
        </article>
    </main>

    <aside>
        <h3>Related Articles</h3>
        <ul>
            <li><a href="/ml-basics">Machine Learning Basics</a></li>
            <li><a href="/deep-learning">Deep Learning Guide</a></li>
            <li><a href="/transformers">Transformer Architecture</a></li>
        </ul>
        <h3>Newsletter</h3>
        <p>Subscribe to our weekly AI newsletter for the latest updates.</p>
    </aside>

    <footer>
        <p>&copy; 2025 AI Blog. All rights reserved.</p>
        <nav>
            <a href="/privacy">Privacy Policy</a> |
            <a href="/terms">Terms of Service</a>
        </nav>
    </footer>
</body>
</html>"""
    (SAMPLE_DIR / "article_page.html").write_text(html)
    print("Generated: article_page.html")


def generate_table_heavy_page():
    """A data-heavy page with multiple tables."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Quarterly Sales Report - Q4 2024</title>
</head>
<body>
    <h1>Quarterly Sales Report - Q4 2024</h1>
    <p>This report covers sales performance across all regions for Q4 2024.</p>

    <h2>Regional Sales Summary</h2>
    <table border="1">
        <thead>
            <tr><th>Region</th><th>Q3 Revenue</th><th>Q4 Revenue</th><th>Growth</th></tr>
        </thead>
        <tbody>
            <tr><td>North America</td><td>$2.4M</td><td>$3.1M</td><td>+29%</td></tr>
            <tr><td>Europe</td><td>$1.8M</td><td>$2.2M</td><td>+22%</td></tr>
            <tr><td>Asia Pacific</td><td>$1.2M</td><td>$1.7M</td><td>+42%</td></tr>
            <tr><td>Latin America</td><td>$0.6M</td><td>$0.8M</td><td>+33%</td></tr>
            <tr><td><strong>Total</strong></td><td><strong>$6.0M</strong></td><td><strong>$7.8M</strong></td><td><strong>+30%</strong></td></tr>
        </tbody>
    </table>

    <h2>Top Products</h2>
    <table border="1">
        <thead>
            <tr><th>Product</th><th>Units Sold</th><th>Revenue</th><th>Margin</th></tr>
        </thead>
        <tbody>
            <tr><td>Enterprise Suite</td><td>145</td><td>$2.9M</td><td>72%</td></tr>
            <tr><td>Professional Plan</td><td>520</td><td>$2.6M</td><td>68%</td></tr>
            <tr><td>Starter Kit</td><td>1,230</td><td>$1.2M</td><td>55%</td></tr>
            <tr><td>Add-on Services</td><td>890</td><td>$1.1M</td><td>80%</td></tr>
        </tbody>
    </table>

    <h2>Key Metrics</h2>
    <ul>
        <li>Customer retention rate: 94%</li>
        <li>New customers acquired: 312</li>
        <li>Average deal size: $25,000</li>
        <li>Sales cycle length: 45 days</li>
    </ul>

    <h2>Regional Breakdown by Product</h2>
    <table border="1">
        <thead>
            <tr><th>Region</th><th>Enterprise</th><th>Professional</th><th>Starter</th><th>Add-ons</th></tr>
        </thead>
        <tbody>
            <tr><td>North America</td><td>$1.2M</td><td>$1.0M</td><td>$0.5M</td><td>$0.4M</td></tr>
            <tr><td>Europe</td><td>$0.9M</td><td>$0.7M</td><td>$0.3M</td><td>$0.3M</td></tr>
            <tr><td>Asia Pacific</td><td>$0.5M</td><td>$0.6M</td><td>$0.3M</td><td>$0.3M</td></tr>
            <tr><td>Latin America</td><td>$0.3M</td><td>$0.3M</td><td>$0.1M</td><td>$0.1M</td></tr>
        </tbody>
    </table>
</body>
</html>"""
    (SAMPLE_DIR / "table_heavy_page.html").write_text(html)
    print("Generated: table_heavy_page.html")


def generate_nested_structure():
    """A page with deeply nested HTML structure (documentation-style)."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>API Documentation - User Management</title>
</head>
<body>
    <div class="doc-wrapper">
        <div class="sidebar">
            <h3>Navigation</h3>
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#authentication">Authentication</a></li>
                <li><a href="#endpoints">Endpoints</a></li>
                <li><a href="#errors">Error Handling</a></li>
            </ul>
        </div>
        <div class="content">
            <h1 id="overview">User Management API</h1>
            <p>The User Management API allows you to create, read, update, and delete
            user accounts in your application.</p>

            <div class="section" id="authentication">
                <h2>Authentication</h2>
                <p>All API requests require a valid API key passed in the header:</p>
                <pre><code>Authorization: Bearer YOUR_API_KEY</code></pre>
                <p>API keys can be generated from the dashboard settings page.</p>

                <div class="warning">
                    <strong>Important:</strong> Never expose your API key in client-side code.
                    Always make API calls from your server.
                </div>
            </div>

            <div class="section" id="endpoints">
                <h2>Endpoints</h2>

                <div class="endpoint">
                    <h3>Create User</h3>
                    <p><code>POST /api/v1/users</code></p>
                    <p>Creates a new user account.</p>

                    <h4>Request Body</h4>
                    <pre><code>{
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
}</code></pre>

                    <h4>Response</h4>
                    <pre><code>{
    "id": "usr_123",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin",
    "created_at": "2025-01-15T10:30:00Z"
}</code></pre>
                </div>

                <div class="endpoint">
                    <h3>List Users</h3>
                    <p><code>GET /api/v1/users</code></p>
                    <p>Returns a paginated list of users.</p>

                    <h4>Query Parameters</h4>
                    <table border="1">
                        <thead>
                            <tr><th>Parameter</th><th>Type</th><th>Default</th><th>Description</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>page</td><td>integer</td><td>1</td><td>Page number</td></tr>
                            <tr><td>per_page</td><td>integer</td><td>20</td><td>Items per page (max 100)</td></tr>
                            <tr><td>role</td><td>string</td><td>-</td><td>Filter by role</td></tr>
                            <tr><td>search</td><td>string</td><td>-</td><td>Search by name or email</td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="endpoint">
                    <h3>Update User</h3>
                    <p><code>PUT /api/v1/users/{id}</code></p>
                    <p>Updates an existing user account. Only provided fields will be updated.</p>
                </div>

                <div class="endpoint">
                    <h3>Delete User</h3>
                    <p><code>DELETE /api/v1/users/{id}</code></p>
                    <p>Permanently deletes a user account. This action cannot be undone.</p>
                </div>
            </div>

            <div class="section" id="errors">
                <h2>Error Handling</h2>
                <p>The API uses standard HTTP status codes:</p>
                <table border="1">
                    <thead>
                        <tr><th>Code</th><th>Meaning</th><th>Description</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>200</td><td>OK</td><td>Request succeeded</td></tr>
                        <tr><td>201</td><td>Created</td><td>Resource created successfully</td></tr>
                        <tr><td>400</td><td>Bad Request</td><td>Invalid request body</td></tr>
                        <tr><td>401</td><td>Unauthorized</td><td>Missing or invalid API key</td></tr>
                        <tr><td>404</td><td>Not Found</td><td>Resource not found</td></tr>
                        <tr><td>429</td><td>Too Many Requests</td><td>Rate limit exceeded</td></tr>
                        <tr><td>500</td><td>Server Error</td><td>Internal server error</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <footer>
        <p>API Version 1.0 | Last updated: January 2025</p>
    </footer>
</body>
</html>"""
    (SAMPLE_DIR / "nested_structure.html").write_text(html)
    print("Generated: nested_structure.html")


if __name__ == "__main__":
    generate_article_page()
    generate_table_heavy_page()
    generate_nested_structure()
    print("\nAll HTML samples generated!")
