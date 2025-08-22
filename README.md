# AI-Powered Company Blog & Insight Generator

This project is an **AI-driven blog and report generator** that creates polished **Insight Digest Reports** for any company.  
It automatically fetches website content, extracts keywords and industry, gathers recent news, identifies competitors, and produces a **data-enriched blog post** with tables, graphs, and references — exported in both **HTML** and **PDF**.

---

## Features
- **Website & Industry Analysis** – Extracts keywords and industry from a company website.
- **News & Research Gathering** – Fetches recent news and fallback research papers if needed.
- **Competitor & Benchmarking Analysis** – Identifies competitors and generates an executive summary.
- **AI Blog Generation** – Produces a 1200-word SEO blog post with sections, insights, and references.
- **Table & Graph Generation** – Inserts KPI tables and auto-generated graphs.
- **Final Reports** – Outputs a clean, styled **HTML report** and exports to **PDF**.

---

## Tech Stack
- **Python 3.9+**
- **OpenAI API** (GPT models)
- **Markdown → HTML** conversion
- **PDF Export** utilities
- Custom agents for data fetching & summarization

---

## Project Structure
project-root/
│── app_main.py # Main orchestrator (runs the full pipeline)
│── blog_generator.py # Blog, table, and graph generation logic
│── agents/ # Supporting modules
│ ├── website_fetcher.py
│ ├── keyword_extractor.py
│ ├── news_fetcher.py
│ ├── paper_fetcher.py
│ ├── summarizer_pro.py
│ ├── visualizer.py
│ └── pdf_exporter.py

---

## Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>

2. **Set up environment**
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows

3. **Install dependencies**
   pip install -r requirements.txt

## Notes

Sensitive files like .env, __pycache__/, and virtual environments are ignored via .gitignore.
Requires an OpenAI API key.
Designed for extensibility — you can plug in new agents (e.g., different data sources).
