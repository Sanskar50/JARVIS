import os
import re
import logging
import subprocess
import shutil

from google import genai
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
_SOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sources")
TEMPLATE_TEX = os.path.join(_SOURCES_DIR, "Sanskar_Suri_Resume.tex")
OUTPUT_DIR = os.path.join(_SOURCES_DIR, "output")
OUTPUT_TEX = os.path.join(OUTPUT_DIR, "resume.tex")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "resume.pdf")
prompt_path = os.path.join(
    os.path.dirname(__file__), "prompts", "update_resume_prompt.txt"
)
with open(prompt_path, "r", encoding="utf-8") as f:
    update_resume_prompt = f.read().strip()

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
                "apt-get",
                "install",
                "-y",
                "texlive-latex-base",
                "texlive-latex-extra",
                "texlive-fonts-extra",
                "texlive-fonts-recommended",
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

    pdf_path = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(tex_path))[0] + ".pdf",
    )

    for i in range(2):
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
            # pdflatex may still produce a PDF despite non-zero exit (font warnings, etc.)
            if os.path.exists(pdf_path):
                logger.warning(
                    f"pdflatex pass {i+1} exited non-zero but PDF was produced (likely warnings only)."
                )
            else:
                logger.error(
                    f"pdflatex pass {i+1} failed — no PDF produced:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
                )
                return False

    return os.path.exists(pdf_path)


# ── Main public function ─────────────────────────────────────────────────────


def generate_resume(job_description: str) -> dict:
    """
    Modify the LaTeX resume for a given job description and compile to PDF.

    Returns:
        dict with tex_path and pdf_path.
    """

    # 1. Read template
    original_tex = _read_template()
    editable = _extract_editable(original_tex)

    # 2. Ask Gemini to rewrite only editable sections
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    model = config.GEMINI_MODEL_NAME

    prompt = f"""{update_resume_prompt}
                JOB DESCRIPTION / INSTRUCTIONS:
                {job_description}
                EDITABLE SECTIONS:
                {editable}
                """

    response = client.models.generate_content(model=model, contents=prompt)
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

    result = {
        "tex_path": OUTPUT_TEX,
        "pdf_path": pdf_path,
    }
    logger.info(f"generate_resume result: {result}")
    return result
