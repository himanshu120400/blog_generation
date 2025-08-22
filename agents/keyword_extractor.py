import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    client = OpenAI()
except openai.OpenAIError as e:
    print(f"[ERROR] Could not configure OpenAI client: {e}")
    exit()

def extract_keywords_and_industry(company_name, website_content):
    prompt = (
        f"You are an expert industry analyst. Carefully read the following website content for the company '{company_name}'. "
        "Extract ONLY those keywords that precisely represent what the company actually DOES in 4-5 keywords and give a single line reason why you selected those, what it manufactures or provides—not general industry terms. "
        "For example, if the company manufactures automotive spare parts, do NOT use 'car manufacturer' as a keyword, but use terms like 'auto component manufacturing', 'OEM parts supplier', etc. "
        "Also infer and name the primary industry/domain.\n\n"
        "Output format:\nIndustry: <specific industry>\nKeywords: <comma-separated, highly specific and accurate keywords>\n\n"
        f"Website Content:\n{website_content[:3500]}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Keyword Extract ERROR] {e}")
        return "Industry: Unknown\nKeywords: "