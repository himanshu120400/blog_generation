import os
import json
import re
import openai
from dotenv import load_dotenv

load_dotenv()

def _extract_text_from_response(resp):
    try:
        return resp.choices[0].message.content
    except Exception:
        pass
    try:
        return resp["choices"][0]["message"]["content"]
    except Exception:
        pass
    try:
        return resp.choices[0].text
    except Exception:
        pass
    return str(resp)

def _call_openai_chat(messages, model="gpt-4o", max_tokens=800, temperature=0.3):
    try:
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI()
            if hasattr(client, "chat") and hasattr(client.chat, "completions") and hasattr(client.chat.completions, "create"):
                resp = client.chat.completions.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature)
                return _extract_text_from_response(resp)
    except Exception:
        pass

    try:
        if hasattr(openai, "ChatCompletion"):
            resp = openai.ChatCompletion.create(model=model, messages=messages, max_tokens=max_tokens, temperature=temperature)
            return _extract_text_from_response(resp)
    except Exception:
        pass

    try:
        joined = "\n\n".join([m["content"] for m in messages if "content" in m])
        resp = openai.Completion.create(engine=model, prompt=joined, max_tokens=max_tokens, temperature=temperature)
        return _extract_text_from_response(resp)
    except Exception as e:
        raise RuntimeError(f"OpenAI call failed: {e}")

def _fallback_blog_post(industry, keywords, core_analysis_summary, competitors, customer_profile, word_count, references):
    title = f"{industry} Insights: Key Learnings and Opportunities"
    intro = f"In this article, we unpack recent findings relevant to {industry} and explain what they mean for {customer_profile}."
    kw_list = keywords if isinstance(keywords, (list, tuple)) else [k.strip() for k in (keywords or "").split(",") if k.strip()]

    sections = []
    sections.append("## Overview")
    sections.append(core_analysis_summary or "")
    sections.append("## What this means for businesses")
    sections.append(f"This section illustrates implications for {customer_profile} and highlights practical considerations.")
    sections.append("[TABLE_PLACEHOLDER]")
    sections.append("## Recommendations")
    sections.append("1. Prioritize initiatives that reduce downtime and operational costs.\n2. Invest in data collection and predictive tooling.\n3. Focus on measurable KPIs for the first 90 days.")
    sections.append("[GRAPH_PLACEHOLDER]")
    sections.append("## Competitor Notes")
    if competitors:
        if isinstance(competitors, str):
            comp_text = competitors
        elif isinstance(competitors, (list, tuple)):
            comp_text = ", ".join([c.get("name", str(c)) if isinstance(c, dict) else str(c) for c in competitors])
        else:
            comp_text = str(competitors)
        sections.append(f"Competitors mentioned: {comp_text}")
    else:
        sections.append("Competitor data not available.")

    refs_str = ""
    if references:
        refs_str = "\n\n## References\n" + "\n".join(f"- {r.get('title','Untitled')} ({r.get('source','')}): {r.get('link','')}" for r in references)

    seo_meta = "<!-- SEO Meta: keywords: " + ", ".join(kw_list[:8]) + " | industry: " + (industry or "General") + " -->\n\n"

    body = "\n\n".join([intro] + sections) + refs_str
    full = seo_meta + f"# {title}\n\n" + body
    return full

def generate_blog_post(
    industry,
    keywords,
    core_analysis_summary,
    competitors,
    customer_profile,
    word_count,
    references):
    kw_list = keywords if isinstance(keywords, (list, tuple)) else [k.strip() for k in (keywords or "").split(",") if k.strip()]
    kw_str = ", ".join(kw_list[:12])

    prompt = f"""
    You are an industry analyst writing a {word_count}-word SEO blog post for the {industry} industry.
    Your primary source is the following executive summary. Expand on its key points to create an engaging blog post.

    --- EXECUTIVE SUMMARY ---
    {core_analysis_summary}

    Instructions:
    1. Structure: Create a catchy headline, a short introduction, and 3-4 main sections with subheadings.
    2. Placeholders: Insert the placeholder `[TABLE_PLACEHOLDER]` once where a statistical KPI table would be appropriate. Insert `[GRAPH_PLACEHOLDER]` once where a visual graph would be appropriate. Do not write lead-in text like 'The following table:'.\n"
    3. Style: Write in a professional, data-driven, and engaging style. Include these keywords naturally: {kw_str}. Avoid generic fluff.
    4. Citations: Add citation numbers like [1] referencing the provided references. Use inline citations for claims.
    5. Output: Return only the blog post text (Markdown).
    References:
    {json.dumps(references) if references else "[]"}
    """
    messages = [{"role": "user", "content": prompt}]
    try:
        text = _call_openai_chat(messages, model="gpt-4o", max_tokens=min(4096, int(word_count * 2)), temperature=0.4)
        if text and text.strip():
            return text.strip()
        else:
            return _fallback_blog_post(industry, keywords, core_analysis_summary, competitors, customer_profile, word_count, references)
    except Exception as e:
        print(f"[Blog Gen ERROR] {e}")
        return _fallback_blog_post(industry, keywords, core_analysis_summary, competitors, customer_profile, word_count, references)


def generate_table_data(core_analysis_summary):
    prompt = f"""
    Based on the following executive summary, generate ONLY a Markdown table for a 'Profit & Loss Impact Analysis'.
    Columns must be: Impact Area | Description | Recommended Action
    Return only the Markdown table (no explanation).

    --- SUMMARY ---
    {core_analysis_summary}
    """
    messages = [{"role":"user","content":prompt}]
    try:
        text = _call_openai_chat(messages, model="gpt-4o-mini", max_tokens=400, temperature=0.1)
        if text:
            if "|" in text and ("---" in text or "\n| " in text or "\n---" in text):
                start = text.find("|")
                table_text = text[start:].strip()
                header_line = table_text.splitlines()[0] if table_text.splitlines() else ""
                cols = header_line.count("|")
                if cols >= 2:
                    return table_text
    except Exception as e:
        print(f"[Table Gen ERROR] {e}")

    import re
    sentences = [s.strip() for s in re.split(r'[.\n]', core_analysis_summary or "") if s.strip()]
    rows = []
    keywords_map = [
        ("Revenue impact", ["revenue", "sales", "growth", "acquisition"]),
        ("Cost impact", ["cost", "expense", "opex", "capex"]),
        ("Operational efficiency", ["downtime", "throughput", "efficiency", "maintenance"]),
        ("Quality & Risk", ["quality", "defect", "risk", "compliance"]),
    ]
    used = set()
    for area, kws in keywords_map:
        matched = next((s for s in sentences if any(k in s.lower() for k in kws) and s not in used), None)
        if matched:
            used.add(matched)
            rows.append((area, matched[:120], "Investigate and prioritize initiatives that address this area."))

    for s in sentences:
        if s not in used and len(rows) < 6:
            rows.append(("Observation", s[:120], "Review and contextualize with internal KPIs."))

    while len(rows) < 3:
        rows.append(("Other", "No clear point found in summary.", "Manual review required."))

    table = "| Impact Area | Description | Recommended Action |\n|---|---|---|\n"
    for r in rows:
        desc = r[1].replace("|", "¦")
        action = r[2].replace("|", "¦")
        table += f"| {r[0]} | {desc} | {action} |\n"
    return table


def generate_graph_data(core_analysis_summary):
    prompt = f"""
    Based on the following summary, generate ONLY a JSON object for a small bar graph with keys:
    {{
    "title": "<short title>",
    "data": {{ "<label>": <numeric_value>, ... }}
    }}
    Do NOT include explanation or Markdown. Values must be numeric (integers or floats).
    --- SUMMARY ---
    {core_analysis_summary}
    """
    messages = [{"role":"user","content":prompt}]
    try:
        text = _call_openai_chat(messages, model="gpt-4o-mini", max_tokens=300, temperature=0.1)
        if text:
            import re, json
            m = re.search(r'(\{[\s\S]*\})', text)
            js_txt = m.group(1) if m else text
            try:
                parsed = json.loads(js_txt)
                if isinstance(parsed, dict) and "data" in parsed and isinstance(parsed["data"], dict):
                    good = True
                    for k,v in parsed["data"].items():
                        try:
                            parsed["data"][k] = float(v)
                        except Exception:
                            good = False
                            break
                    if good:
                        return json.dumps(parsed)
            except Exception:
                pass
    except Exception as e:
        print(f"[Graph JSON Gen ERROR] {e}")

    import re, json
    tokens = re.findall(r'\b[a-z]{3,}\b', (core_analysis_summary or "").lower())
    from collections import Counter
    c = Counter([t for t in tokens if t not in ("the","and","for","that","this","with","from","are","have","has","were","was")])
    top = c.most_common(6)
    data = {k: int(v) for k, v in top} if top else {"no_data": 1}
    obj = {"title": "Top tokens", "data": data}
    return json.dumps(obj)