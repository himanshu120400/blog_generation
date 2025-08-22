from agents.website_fetcher import fetch_website_content
from agents.keyword_extractor import extract_keywords_and_industry
from agents.news_fetcher import fetch_recent_news
from agents.paper_fetcher import fetch_articles_and_info
from agents.summarizer_pro import identify_competitors, generate_benchmarking_report, generate_executive_summary
from agents.blog_generator import generate_blog_post, generate_table_data, generate_graph_data
from agents.visualizer import create_kpi_graph
from agents.pdf_exporter import save_html_to_pdf
import re
from markdown import markdown

class CompanyBlogOrchestrator:
    def __init__(self, company_name, company_website):
        self.company_name = company_name
        self.company_website = company_website
        self.report_data = {}

    def run(self):
        print("\n1. Fetching website content & extracting industry-keywords.")
        self.report_data["website_content"] = fetch_website_content(self.company_website)
        if not self.report_data["website_content"]: return

        self.report_data["keywords_and_industry"] = extract_keywords_and_industry(self.company_name, self.report_data["website_content"])
        print(f"\n[Extracted Industry/Keywords]:\n{self.report_data['keywords_and_industry']}\n")

        print("\n2. Fetching recent news...")
        self.report_data["news_articles"] = fetch_recent_news(self.report_data["keywords_and_industry"], days=14, company=self.company_name)
        if not self.report_data["news_articles"]:
            self.report_data["news_articles"] = fetch_articles_and_info(self.report_data["keywords_and_industry"], self.company_name)

        print("\n3. Running Full Competitor and Benchmarking Analysis...")
        self.report_data["competitors"] = identify_competitors(self.report_data["website_content"], self.report_data["keywords_and_industry"])
        self.report_data["benchmarking_report"] = generate_benchmarking_report(self.report_data["website_content"], self.report_data["keywords_and_industry"], self.report_data["competitors"], self.report_data["news_articles"])
        if self.report_data["benchmarking_report"]:
            self.report_data["executive_summary"] = generate_executive_summary(self.report_data["benchmarking_report"])
        
        print("\n4. Generating Final Blog Post Components...")
        self.generate_blog_components()
        self.create_final_reports()

    def generate_blog_components(self):
        ind_match = re.search(
            r"Industry:\s*(.*)", self.report_data["keywords_and_industry"], re.I
        )
        kw_match = re.search(
            r"Keywords:\s*(.*)", self.report_data["keywords_and_industry"], re.I
        )
        self.report_data["industry"] = (
            ind_match.group(1).strip() if ind_match else "General"
        )
        self.report_data["keywords"] = (
            [k.strip() for k in kw_match.group(1).split(",")] if kw_match else []
        )

        self.report_data["core_content"] = self.report_data.get("executive_summary", "")
        if not self.report_data["core_content"]:
            print("[WARN] Executive summary is empty. Blog may lack depth.")
            self.report_data["core_content"] = "\n".join(
                [
                    f"{a.get('title','Untitled')}: {a.get('content','')[:200]}..."
                    for a in self.report_data["news_articles"][:4]
                ]
            )

        self.report_data["blog_prose"] = generate_blog_post(
            self.report_data["industry"],
            self.report_data["keywords"],
            self.report_data["core_content"],
            self.report_data.get("competitors", ""),
            self.report_data["industry"],
            1200,
            [
                {
                    "title": a.get("title"),
                    "link": a.get("link"),
                    "source": a.get("source"),
                }
                for a in self.report_data["news_articles"]
            ],
        )

        self.report_data["table_markdown"] = generate_table_data(
            self.report_data["core_content"]
        )
        self.report_data["graph_json"] = generate_graph_data(
            self.report_data["core_content"]
        )

    def create_final_reports(self):
        if not self.report_data.get("blog_prose"):
            print("[ERROR] Blog prose is empty. Cannot create reports.")
            return

        print("\n5. Assembling final reports.")

        final_content = self.report_data["blog_prose"]

        table_md = self.report_data.get("table_markdown", "")
        if table_md:
            final_content = final_content.replace("[TABLE_PLACEHOLDER]", table_md)
        else:
            final_content = final_content.replace(
                "[TABLE_PLACEHOLDER]", "<p><i>[Table could not be generated.]</i></p>"
            )

        json_str = self.report_data.get("graph_json", "")
        graph_base64 = create_kpi_graph(json_str) if json_str else None
        if graph_base64:
            graph_html = f'<img src="data:image/png;base64,{graph_base64}" alt="Statistical Graph" style="max-width: 100%; height: auto;">'
            final_content = final_content.replace("[GRAPH_PLACEHOLDER]", graph_html)
        else:
            final_content = final_content.replace(
                "[GRAPH_PLACEHOLDER]", "<p><i>[Graph could not be generated.]</i></p>"
            )

        html_body = markdown(final_content, extensions=["tables"])
        html_output_string = f"""
        <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{self.company_name} | Insight Digest</title>
        <style>body{{font-family:sans-serif;line-height:1.6;color:#333;max-width:800px;margin:40px auto;padding:20px;}}h1,h2,h3{{color:#2c3e50;}}table{{border-collapse:collapse;width:100%;margin-bottom:1em;}}th,td{{border:1px solid #ddd;padding:8px;text-align:left;}}th{{background-color:#f2f2f2;}}img{{max-width:100%;height:auto;border:1px solid #ddd;border-radius:4px;margin:1em 0;}}</style>
        </head><body>{html_body}</body></html>
        """

        safe_company_name = self.company_name.replace(" ", "_").replace("/", "_")
        html_filename = f"{safe_company_name}_Insight_Digest.html"
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_output_string)

        print(f"\n========== Final Report Generated ==========\n")
        print(f"HTML report saved to '{html_filename}'")

        pdf_filename = f"{safe_company_name}_Insight_Digest.pdf"
        save_html_to_pdf(html_filename, pdf_filename)