import os
import re
import logging
import subprocess
import httpx
import shutil

import google.generativeai as genai
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
_SOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sources")
TEMPLATE_TEX = os.path.join(_SOURCES_DIR, "Sanskar_Suri_Resume.tex")
OUTPUT_DIR = os.path.join(_SOURCES_DIR, "output")
OUTPUT_TEX = os.path.join(OUTPUT_DIR, "resume.tex")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "resume.pdf")

# ── Section markers ─────────────────────────────────────────────────────────
_EDITABLE_SECTIONS = [
    "Experience",
    "Projects",
    "Technical Skills",
    "Achivements",  # keep original typo from .tex
]

_SECTION_RE = re.compile(
    r"(\\section\*?\{(?:"
    + "|".join(re.escape(s) for s in _EDITABLE_SECTIONS)
    + r")\}.*?)(?=\\section|\Z)",
    re.DOTALL,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _read_template() -> str:
    with open(TEMPLATE_TEX, "r", encoding="utf-8") as f:
        return f.read()


def _extract_editable(tex: str) -> str:
    matches = _SECTION_RE.findall(tex)
    return "\n\n".join(matches)


def _replace_editable(original_tex: str, new_sections: str) -> str:
    first_match = _SECTION_RE.search(original_tex)
    if not first_match:
        logger.warning("No editable sections found – returning LLM output as-is.")
        return new_sections
    prefix = original_tex[: first_match.start()]
    all_matches = list(_SECTION_RE.finditer(original_tex))
    last_match = all_matches[-1]
    suffix = original_tex[last_match.end() :]
    return prefix + new_sections + suffix


def ensure_pdflatex():
    if shutil.which("pdflatex"):
        return True

    logger.warning("pdflatex not found. Attempting to install TeX Live...")

    try:
        subprocess.run(
            [
                "sudo",
                "apt-get",
                "install",
                "-y",
                "texlive-latex-base",
                "texlive-latex-extra",
            ],
            check=True,
        )

        return shutil.which("pdflatex") is not None

    except Exception as e:
        logger.error(f"Failed to install pdflatex: {e}")
        return False


def _compile_to_pdf(tex_path: str, output_dir: str) -> bool:
    if not ensure_pdflatex():
        logger.error("pdflatex is unavailable.")
        return False

    for _ in range(2):
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory",
                output_dir,
                tex_path,
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )

        if result.returncode != 0:
            logger.error(
                f"pdflatex failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
            )
            return False

    return True


def _send_file_to_telegram_sync(chat_id: int, file_path: str, caption: str = ""):
    """Synchronous helper – uses httpx directly, no asyncio needed."""
    bot_token = config.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    mime = "application/pdf" if file_path.endswith(".pdf") else "application/x-tex"
    resp = httpx.post(
        url,
        data={"chat_id": chat_id, "caption": caption},
        files={"document": (filename, file_bytes, mime)},
        timeout=30,
    )
    if resp.status_code == 200:
        logger.info(f"Telegram upload OK: {filename}")
    else:
        logger.error(f"Telegram upload failed: {resp.status_code} {resp.text[:300]}")
    return resp.status_code == 200


# ── Main public function ─────────────────────────────────────────────────────


def generate_resume(job_description: str, chat_id: int = 0) -> dict:
    """
    Modify the LaTeX resume for a given job description and compile to PDF.

    Args:
        chat_id: Telegram chat_id to upload the generated PDF (default: 0).

    Returns:
        dict with tex_path, pdf_path, telegram_sent.
    """

    # 1. Read template
    original_tex = _read_template()
    editable = _extract_editable(original_tex)

    # 2. Ask Gemini to rewrite only editable sections
    genai.configure(api_key=config.GEMINI_API_KEY)
    llm = genai.GenerativeModel(
        model_name=config.GEMINI_MODEL_NAME or "gemini-2.0-flash",
    )

    prompt = f"""You are an expert resume writer. Below are the EDITABLE LaTeX sections of a resume.
Rewrite ONLY these sections to better match the following job description / instructions.

STRICT RULES:
- Preserve every LaTeX command, macro, and formatting exactly (\\resumeItem, \\resumeSubheading, \\resumeProjectHeading, etc.).
- Do NOT change any personal information (name, email, phone, LinkedIn, GitHub).
- Do NOT add or remove \\section headings.
- Do NOT alter the preamble, packages, or document structure.
- Return ONLY the rewritten LaTeX sections — no markdown fences, no explanations.

JOB DESCRIPTION / INSTRUCTIONS:
{job_description}

EDITABLE SECTIONS:
{editable}
"""

    response = llm.generate_content(prompt)
    new_sections = response.text.strip()

    # Strip accidental markdown fences
    new_sections = re.sub(r"^```[a-z]*\n?", "", new_sections)
    new_sections = re.sub(r"\n?```$", "", new_sections)

    # 3. Splice back and write .tex
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    new_tex = _replace_editable(original_tex, new_sections)
    with open(OUTPUT_TEX, "w", encoding="utf-8") as f:
        f.write(new_tex)
    logger.info(f"Written tex to {OUTPUT_TEX}")

    # 4. Compile to PDF
    pdf_path = None
    try:
        ok = _compile_to_pdf(OUTPUT_TEX, OUTPUT_DIR)
        if ok and os.path.exists(OUTPUT_PDF):
            pdf_path = OUTPUT_PDF
            logger.info(f"PDF compiled: {OUTPUT_PDF}")
        else:
            logger.warning("pdflatex ran but PDF not found.")
    except FileNotFoundError:
        logger.warning("pdflatex not found on PATH; skipping PDF compilation.")
    except subprocess.TimeoutExpired:
        logger.error("pdflatex timed out.")
    except Exception as e:
        logger.error(f"pdflatex unexpected error: {e}")

    telegram_sent = False
    upload_path = pdf_path if pdf_path else OUTPUT_TEX
    upload_caption = (
        "📄 Your tailored resume is ready!"
        if pdf_path
        else "⚠️ PDF compilation unavailable — here is the .tex source. Compile with pdflatex to get the PDF."
    )
    telegram_sent = _send_file_to_telegram_sync(chat_id, upload_path, upload_caption)

    result = {
        "tex_path": OUTPUT_TEX,
        "pdf_path": pdf_path or "PDF compilation skipped (pdflatex not installed).",
        "telegram_sent": telegram_sent,
    }
    logger.info(f"generate_resume result: {result}")
    return result
