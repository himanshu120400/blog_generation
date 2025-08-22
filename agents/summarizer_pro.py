import os
import openai
from dotenv import load_dotenv

load_dotenv()

try:
    client = openai.OpenAI()
except openai.OpenAIError as e:
    print(f"[ERROR] Could not configure OpenAI client: {e}")
    exit()

def identify_competitors(website_content, keywords_and_industry):
    print("Step 1: Identifying competitors...")
    prompt = f"""You are a market analyst. Based on the provided company website content and keywords, identify 3 to 5 of the closest and most direct competitors.
    Provide only a comma-separated list of company names. Do not add any other text or explanation.
    ---
    Company Website Content:
    {website_content[:4000]}
    Extracted Industry/Keywords:
    {keywords_and_industry}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.2
        )
        competitors = response.choices[0].message.content.strip()
        print(f"Competitors identified: {competitors}")
        return competitors
    except Exception as e:
        print(f"[ERROR] OpenAI API call for competitor identification failed: {e}")
        return ""

def generate_benchmarking_report(website_content, keywords_and_industry, competitors, research_articles):
    print("Step 2: Generating the core benchmarking report...")
    
    research_snippets = []
    for article in research_articles:
        title = article.get("title", "Untitled")
        snippet = (article.get("content") or "")[:500]
        research_snippets.append(f"- {title}\n  {snippet}")
    
    prompt = f"""You are a senior business analyst preparing a competitor benchmarking report. Your goal is to uncover what the target company doesn't know.
    Core Task: Analyze the company against its competitors, using the provided articles to find novel insights and key metrics.
    Company's Identified Competitors: {competitors}
    
    Report Structure:
    1.  **Industry Overview & Emerging Trends:** Briefly describe the industry. Crucially, based on the 'Relevant Articles', identify 1-2 emerging technologies or novel trends the target company might be overlooking. This should address 'what they don't know'.
    2.  **Competitive Landscape & Strategy:** Analyze the strategies, strengths, and weaknesses of competitors ({competitors}). How are the leading companies different in their approach?
    3.  **Key Performance Indicators (KPIs) for Growth:** Market share, R&D spend, customer acquisition cost, uptime/downtime, defect rate. Compare the companies based on any metric data found in the articles.
    4.  **Strategic Gaps & Opportunities:** Based on the analysis, what is the target company lacking? Highlight what competitors are doing better and where the opportunities lie.
    5.  **Actionable Recommendations:** Invest in pilot projects to show ROI within 6 months. Improve data collection & sensors. Partner with specialist vendors to accelerate productization. Provide 3-5 concrete, strategic recommendations to address the identified gaps and capitalize on opportunities.
    ---
    INPUT DATA:
    1. Company Website Content: {website_content[:4000]}
    2. Extracted Industry/Keywords: {keywords_and_industry}
    3. Relevant Articles for Context: {"".join(research_snippets)}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages =
            [{"role": "system", "content": "You are a senior industry analyst and content strategist."},
            {"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.4
        )
        report = response.choices[0].message.content.strip()
        print("Core report generated.")
        return report
    except Exception as e:
        print(f"[ERROR] OpenAI API call for report generation failed: {e}")
        return ""

def generate_executive_summary(full_report):
    print("Step 3: Generating the executive summary...")
    
    prompt = f"""You are an assistant to a business analyst. Your task is to write a concise, hard-hitting executive summary (300-400 words) based on the detailed report provided below.

    The summary must:
    - Start with the company's current market position and the primary threat from competitors.
    - Mention the most critical KPIs (Key Performance Metrics) that determine success in this sector.
    - Distill the most important findings, including any emerging trends the company might be overlooking.
    - Conclude with the top 2-3 most impactful strategic recommendations from the report.
    ---
    FULL REPORT:
    {full_report}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        summary = response.choices[0].message.content.strip()
        print("Executive summary generated.")
        return summary
    except Exception as e:
        print(f"[ERROR] OpenAI API call for executive summary failed: {e}")
        return ""