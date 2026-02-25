import os
import json
import requests
from pathlib import Path

# ==========================
# CONFIG
# ==========================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-r1"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================
# AI CALL
# ==========================
def call_ai(system_prompt, user_prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ==========================
# STEP 1: SITE STRUCTURE
# ==========================
def generate_structure(prompt):
    system = "You are a senior website architect."
    user = f"""
Generate a JSON website structure.

Rules:
- Header and footer must be global
- Pages must be independent
- Include pricing, login, signup, legal pages

Return ONLY valid JSON.

Prompt:
{prompt}
"""
    result = call_ai(system, user)
    return json.loads(result)

# ==========================
# STEP 2: GLOBAL COMPONENTS
# ==========================
def generate_header(prompt):
    return call_ai(
        "You create reusable website headers.",
        f"Create a clean global HTML header for this site:\n{prompt}",
    )

def generate_footer(prompt):
    return call_ai(
        "You create reusable website footers.",
        f"Create a clean global HTML footer with disclaimer:\n{prompt}",
    )

# ==========================
# STEP 3: PAGE GENERATOR
# ==========================
def generate_page(page_name, prompt):
    return call_ai(
        "You generate complete HTML pages.",
        f"""
Create a FULL HTML page for '{page_name}'.

Rules:
- Do NOT include header or footer
- Content only inside <main>
- SEO friendly
- Professional UI

Website prompt:
{prompt}
""",
    )

# ==========================
# STEP 4: CSS
# ==========================
def generate_css(prompt):
    return call_ai(
        "You generate production-ready CSS.",
        f"""
Create a modern fintech CSS stylesheet.
Dark & light friendly.
Mobile responsive.

Website prompt:
{prompt}
""",
    )

# ==========================
# ASSEMBLER
# ==========================
def assemble_page(body, header, footer):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link rel="stylesheet" href="main.css"/>
</head>
<body>
{header}
<main>
{body}
</main>
{footer}
</body>
</html>
"""

# ==========================
# MAIN
# ==========================
def main():
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    prompt = Path("prompt.txt").read_text()

    print("🔹 Generating site structure...")
    structure = generate_structure(prompt)

    print("🔹 Generating header & footer...")
    header = generate_header(prompt)
    footer = generate_footer(prompt)

    (OUTPUT_DIR / "header.html").write_text(header)
    (OUTPUT_DIR / "footer.html").write_text(footer)

    print("🔹 Generating CSS...")
    css = generate_css(prompt)
    (OUTPUT_DIR / "main.css").write_text(css)

    print("🔹 Generating pages...")
    for page in structure["pages"]:
        body = generate_page(page, prompt)
        full_html = assemble_page(body, header, footer)
        (OUTPUT_DIR / page).write_text(full_html)
        print(f"   ✔ {page}")

    print("✅ Site generation complete.")

if __name__ == "__main__":
    main()
