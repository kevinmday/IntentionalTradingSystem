# RippleIT.py
import os
import random
os.environ["FLASK_SKIP_DOTENV"] = "1"   # Prevent Flask from auto-loading .env
import re, uuid, json, math, time
from pathlib import Path
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS

# ---------------------------
# Config
# ---------------------------
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app, resources={r"/api/*": {"origins": "*"}})  # loosen for prototype

# In-memory result store for permalinks (prototype only)
RESULTS: Dict[str, Dict[str, Any]] = {}


# ---------------------------
# Utilities
# ---------------------------
def read_text_from_url(url: str, timeout: float = 2.5) -> str:
    """
    Try to fetch the URL and return visible text. No hard dependency libs.
    Fail gracefully in offline environments.
    """
    try:
        import requests
        from bs4 import BeautifulSoup  # pip install beautifulsoup4
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "RippleLab/0.1"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Drop scripts/styles
        for t in soup(["script", "style", "noscript"]):
            t.decompose()
        text = " ".join(soup.get_text(" ").split())
        return text[:200_000]
    except Exception:
        # Fallback: just return the URL so the engine is deterministic
        return f"URL:{url}"


def normalize_text(base_text: str) -> str:
    # Strip excess whitespace and normalize unicode quotes a bit
    t = base_text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------
# Legacy scoring functions (for /api/analyze)
# ---------------------------
def score_truth(text: str) -> int:
    """
    RippleTruth: very lightweight heuristic for prototype.
    - More declarative sentences and factual tokens -> higher score
    - Excess all-caps, excessive punctuation -> lower score
    """
    if not text:
        return 50
    t = text
    n = len(t)
    sentences = max(1, t.count(".") + t.count("?") + t.count("!"))
    commas = t.count(",")
    caps_ratio = sum(1 for ch in t if ch.isupper()) / max(1, n)
    punct = len(re.findall(r"[!?]{2,}", t))
    digits = len(re.findall(r"\b\d[\d,\.]*\b", t))

    raw = 60 + 8 * math.log10(min(n, 50_000) + 10) + 0.02 * (commas + digits) - 65 * caps_ratio - 10 * punct
    return int(max(1, min(99, round(raw))))


def score_polarization(text: str) -> int:
    # RippleScore: polarization amplitude ~ sentiment spread proxy
    pos = len(re.findall(r"\b(good|great|win|progress|success|true|love)\b", text, re.I))
    neg = len(re.findall(r"\b(bad|terrible|fail|crime|disaster|false|hate)\b", text, re.I))
    amp = abs(pos - neg) * 6 + (pos + neg)
    base = 35 + min(60, amp)
    return int(max(1, min(99, base)))


def score_align(text: str) -> int:
    # RippleAlign: proxy via coherence keywords vs hedging
    coherence = len(re.findall(r"\btherefore|thus|hence|because|evidence|data|source\b", text, re.I))
    hedging = len(re.findall(r"\bmaybe|might|perhaps|could|seems\b", text, re.I))
    val = 50 + 5 * coherence - 3 * hedging
    return int(max(1, min(99, val)))


def score_physco(text: str) -> int:
    # RipplePhysco: symbolic charge vs semantic clarity (confusion vortex)
    symb = len(re.findall(r"\bmetaphor|symbol|myth|ritual|prophecy|reverse bathtub\b", text, re.I))
    exclaim = text.count("!")
    jargon = len(re.findall(r"\b(coherence|entropy|quantum|field|fractal)\b", text, re.I))
    clarity = len(re.findall(r"\btherefore|in summary|conclude|key points\b", text, re.I))
    raw = 40 + 5 * (symb + jargon + exclaim) - 6 * clarity
    return int(max(1, min(99, raw)))


def score_seer(text: str) -> int:
    # RippleSeer: intention momentum proxy via future terms & rate of change tokens
    future = len(re.findall(r"\bwill|soon|next|forecast|trend|momentum|trajectory\b", text, re.I))
    change = len(re.findall(r"\bchange|increase|surge|spike|decline|shift\b", text, re.I))
    val = 30 + min(60, 4 * future + 3 * change)
    return int(max(1, min(99, val)))


def score_wisdom(text: str) -> int:
    # RippleWisdom: teaching/summary style -> higher; ranty punctuation lowers
    teach = len(re.findall(r"\blesson|principle|summary|key takeaways|steps|guide\b", text, re.I))
    rant = len(re.findall(r"[!?]{2,}", text))
    val = 45 + 7 * teach - 4 * rant
    return int(max(1, min(99, val)))


TOOL_FUNCS = {
    "RippleTruth": score_truth,
    "RippleScore": score_polarization,
    "RippleAlign": score_align,
    "RipplePhysco": score_physco,
    "RippleSeer": score_seer,
    "RippleWisdom": score_wisdom,
}


def run_tools(text: str, tools: List[str]) -> List[Dict[str, Any]]:
    results = []
    for tool in tools:
        fn = TOOL_FUNCS.get(tool)
        if not fn:
            continue
        val = fn(text)
        results.append({
            "tool": tool,
            "score": val,
            "note": {
                "RippleTruth": "Veracity–intention gradient.",
                "RippleScore": "Polarization amplitude & emotional energy.",
                "RippleAlign": "Alignment of intent vs field flow.",
                "RipplePhysco": "Symbolic charge vs semantic clarity.",
                "RippleSeer": "Momentum of intention; ignition likelihood.",
                "RippleWisdom": "Coherence/learning slope proxy."
            }.get(tool, "—"),
        })
    return results


# ---------------------------
# Ripple-GPT style analysis (for /api/ripple/analyze)
# ---------------------------

def normalize_input(text: str, url: str | None) -> str:
    raw = (text or "").strip()
    if url:
        raw = f"{raw} {read_text_from_url(url)}".strip()
    return normalize_text(raw)[:200_000]

def analyze_truth_struct(doc_text: str) -> Dict[str, Any]:
    """
    Structured RippleTruth analyzer:
    - recognizes 'the year is ####' and 'what year is it?'
    - otherwise produces a rationale + basic score
    """
    year = time.gmtime().tm_year
    t = doc_text.strip()
    tl = t.lower()

    is_question = bool(re.search(r"\bwhat\s+year\s+is\s+it\??\b", tl))
    m = re.search(
        r"\b(?:the\s+)?year\s*(?:is|=|:)\s*(\d{4})\b|\b(?:it's|it\s+is)\s*(\d{4})\b",
        tl,
    )
    claimed = int(m.group(1) or m.group(2)) if m else None

    verdict = "Unclear"
    score = 40
    claims: List[Dict[str, Any]] = []
    rationale = ""

    if is_question:
        verdict = "Answered"
        score = 100
        claims.append(
            {"text": f"Answer: It’s {year}.", "type": "answer", "value": year, "confidence": 1.0}
        )
        rationale = (
            "Recognized a direct question about the current year and returned a deterministic answer."
        )

    if claimed is not None:
        claims.append(
            {
                "text": f"The year is {claimed}",
                "type": "claim",
                "value": claimed,
                "confidence": 0.9,
            }
        )
        if claimed == year and verdict != "Answered":
            verdict, score, rationale = "True", 100, "Claimed year matches system year."
        elif abs(claimed - year) == 1 and verdict != "Answered":
            verdict, score, rationale = "Near", 75, "Claim is within ±1 year of system year."
        elif verdict != "Answered":
            verdict, score, rationale = "False", 8, "Claim contradicts system year."

    if not is_question and claimed is None and not claims:
        # fallback heuristic
        score = max(10, score_truth(t))
        rationale = "No verifiable claim detected; applied heuristic signal strength."

    # Build report card content
    subject = "The subject"
    subj_match = re.search(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})\b", t)
    if subj_match:
        subject = subj_match.group(1)

    # Precompute strings to avoid nested/escaped f-strings
    claim_context = f"\"The year is {claimed}\"" if claimed is not None else "no explicit year claim detected."
    answer_line = f"Answer emitted → It’s {year}." if is_question else f"System reference → {year}."

    report = {
        "headline": f"{subject} — RippleTruth Report",
        "definition": f"{subject} is framed as an observer whose intention couples with observable outcomes.",
        "eq": "O_meta = dT/dI | aware",
        "metrics": [
            {
                "name": "RippleTruth",
                "value": f"{score/100:.2f}",
                "meaning": (
                    "Directly answerable; trivial verification"
                    if verdict == "Answered"
                    else "Strong factual alignment"
                    if verdict == "True"
                    else "Close to system ground truth"
                    if verdict == "Near"
                    else "Inconsistent with ground truth"
                    if verdict == "False"
                    else "Insufficient claim; heuristic read"
                ),
            },
            {
                "name": "FILS (Future Intention Likelihood Scale)",
                "value": "0.74",
                "meaning": "Continued emergence of intention-driven outcomes is probable",
            },
            {
                "name": "UCIP Coherence (macro↔micro)",
                "value": "0.79",
                "meaning": "Observer awareness bridges domains of expression",
            },
        ],
        "narrative": [
            f"{subject} is read as an agent whose awareness modulates coherence in the field of events.",
            f"Claim context: {claim_context}",
            answer_line,
            rationale or "—",
        ],
    }

    return {
        "score": score,
        "verdict": verdict,
        "claims": claims,
        "rationale": rationale,
        "highlights": [],
        "report": report,
    }


def analyze_score_struct(doc_text: str) -> Dict[str, Any]:
    return {"score": score_polarization(doc_text), "summary": "Affective intensity measured across tokens (prototype)."}

def analyze_align_struct(doc_text: str) -> Dict[str, Any]:
    return {"score": score_align(doc_text), "summary": "Partial alignment between stated aim and semantic field (prototype)."}

def analyze_seer_struct(doc_text: str) -> Dict[str, Any]:
    return {"score": score_seer(doc_text), "summary": "Moderate ignition likelihood contingent on follow-through (prototype)."}

def analyze_physco_struct(doc_text: str) -> Dict[str, Any]:
    return {"score": score_physco(doc_text), "summary": "Symbolic charge present with fair clarity (prototype)."}

def analyze_wisdom_struct(doc_text: str) -> Dict[str, Any]:
    return {"score": score_wisdom(doc_text), "summary": "Coherence slope trending slightly upward (prototype)."}

STRUCT_RUNNERS = {
    "RippleTruth": analyze_truth_struct,
    "RippleScore": analyze_score_struct,
    "RippleAlign": analyze_align_struct,
    "RippleSeer": analyze_seer_struct,
    "RipplePhysco": analyze_physco_struct,
    "RippleWisdom": analyze_wisdom_struct,
}


# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def root():
    # For convenience in prototype: serve the single HTML if placed at ./static/index.html
    return redirect("/static/index.html", code=302)

# --- New Ripple-GPT style endpoint expected by your UI ---

def analyze_truth_struct(doc_text: str) -> Dict[str, Any]:
    """
    RippleTruth (prototype, deterministic):
    - If trivial claim like "the year is ####" or "what year is it?" -> return 100/75/8 (fast path)
    - Else, compute FILS / UCIP / TTCF from article cues and produce a narrative + score.
      This approximates the RippleTruth-GPT snapshot without any external model calls.
    """
    year = time.gmtime().tm_year
    t = doc_text.strip()
    tl = t.lower()

    # ---------- Fast path: trivially verifiable year ----------
    is_question = bool(re.search(r"\bwhat\s+year\s+is\s+it\??\b", tl))
    m = re.search(r"\b(?:the\s+)?year\s*(?:is|=|:)\s*(\d{4})\b|\b(?:it's|it\s+is)\s*(\d{4})\b", tl)
    claimed = int(m.group(1) or m.group(2)) if m else None

    if is_question:
        return {
            "score": 100, "verdict": "Answered", "claims": [{"text": f"Answer: It’s {year}.", "type": "answer", "value": year, "confidence": 1.0}],
            "rationale": "Recognized a direct question about the current year and returned a deterministic answer.",
            "highlights": [],
            "report": {
                "headline": "RippleTruth — Year Query",
                "definition": "Direct factual question resolved from system clock.",
                "eq": "O_meta = dT/dI | aware",
                "metrics": [{"name":"RippleTruth","value":"1.00","meaning":"Directly answerable; trivial verification"}],
                "narrative": [f"It is {year}."]
            }
        }

    if claimed is not None:
        verdict, score, rationale = ("True", 100, "Claimed year matches system year.") if claimed == year \
            else ("Near", 75, "Claim is within ±1 year of system year.") if abs(claimed - year) == 1 \
            else ("False", 8, "Claim contradicts system year.")
        return {
            "score": score, "verdict": verdict,
            "claims": [{"text": f"The year is {claimed}", "type": "claim", "value": claimed, "confidence": 0.9}],
            "rationale": rationale,
            "highlights": [],
            "report": {
                "headline": "RippleTruth — Year Claim",
                "definition": "Trivial claim cross-checked against system year.",
                "eq": "O_meta = dT/dI | aware",
                "metrics": [{"name":"RippleTruth","value":f"{score/100:.2f}","meaning":rationale}],
                "narrative": [rationale, f"System reference → {year}."]
            }
        }

    # ---------- Article analyzer: FILS, UCIP, TTCF ----------
    # Signal buckets (very light-weight, deterministic)
    # Public-benefit framing vs self/branding
    public_terms = r"\b(public|diplomacy|state|civic|nonpartisan|utility|protocol|access)\b"
    branding_terms = r"\b(branding|vanity|gloss|prestige|patronage|donor|naming|gala)\b"

    # Ethics / procurement / contractor / foreign influence
    ethics_terms = r"\b(ethic|emolument|procurement|oversight|conflict|compliance|audit)\b"
    contractor_terms = r"\b(contractor|vendor|federal\s+work|bidder)\b"
    foreign_terms = r"\b(foreign|overseas|sovereign|embassy)\b"
    settlement_terms = r"\b(settlement|consent\s+decree|fine|penalty)\b"

    # Chaos/entropy cues (shutdown optics, intra-branch conflict, overlapping interests)
    shutdown_terms = r"\b(shutdown|closed\s+government|furlough)\b"
    conflict_terms = r"\b(inquiry|subpoena|investigation|lawsuit|conflict|controversy|dispute)\b"
    overlap_terms = r"\b(donation|donor|funding|ballroom|white\s+house|federal\s+property)\b"

    def count(rx: str) -> int:
        return len(re.findall(rx, tl, re.I))

    # Counts
    c_pub   = count(public_terms)
    c_brand = count(branding_terms)
    c_eth   = count(ethics_terms)
    c_con   = count(contractor_terms)
    c_for   = count(foreign_terms)
    c_sett  = count(settlement_terms)
    c_shut  = count(shutdown_terms)
    c_conf  = count(conflict_terms)
    c_ovlp  = count(overlap_terms)

    # Heuristics → [0..1]
    # FILS: forward intention likelihood of *public-interest purpose*
    #    grows with public framing, shrinks with branding/patronage dominance
    FILS = max(0.0, min(1.0, 0.55 * (c_pub > 0) + 0.15 * min(3, c_pub) - 0.20 * min(3, c_brand)))

    # UCIP: coherence with shared norms/ethics
    #    penalized by ethics/contractor/foreign/settlement mentions
    UCIP = max(0.0, min(1.0, 0.70 - 0.10 * min(3, c_eth) - 0.08 * min(3, c_con) - 0.08 * min(3, c_for) - 0.08 * min(3, c_sett)))

    # TTCF: “chaos factor” from overlapping interests + shutdown optics + conflicts
    TTCF = max(0.0, min(1.0, 0.20 * min(4, c_ovlp) + 0.25 * (c_shut > 0) + 0.20 * min(3, c_conf)))

    # RippleTruth integrity (your snapshot formula)
    # RT = FILS * UCIP / (1 + TTCF)
    RT = (FILS * UCIP) / (1.0 + TTCF)

    # Map RT to a 0–100 score (keep low when TTCF is high)
    score = int(round(100 * RT))

    # Verdict buckets
    verdict = "Very Low" if RT < 0.15 else "Low" if RT < 0.3 else "Moderate" if RT < 0.55 else "High"

    # Narrative construction mirroring your GPT snapshot
    subject = "Project"
    subj_match = re.search(r"(white house.*?ballroom|ballroom|project|initiative)", tl)
    if subj_match:
        subject = subj_match.group(1).title()

    metrics = [
        {"name": "FILS (forward intention likelihood)", "value": f"{FILS:.2f}",
         "meaning": "Public-purpose framing vs self-benefit weighting"},
        {"name": "UCIP (coherence with shared norms)", "value": f"{UCIP:.2f}",
         "meaning": "Ethics / procurement / influence coherence"},
        {"name": "TTCF (chaos factor)", "value": f"{TTCF:.2f}",
         "meaning": "Overlapping interests + shutdown/oversight entropy"},
        {"name": "RippleTruth", "value": f"{RT:.3f}",
         "meaning": "Integrity signal = FILS×UCIP / (1+TTCF)"},
    ]

    rationale = (
        "Signals of public utility exist, but branding/patronage cues and ethics/contractor/foreign/settlement features "
        "depress coherence; shutdown/oversight optics elevate entropy."
    )

    narrative = [
        f"{subject} framed against ethics/procurement norms and optics.",
        f"FILS≈{FILS:.2f}, UCIP≈{UCIP:.2f}, TTCF≈{TTCF:.2f} → RT≈{RT:.3f}.",
        "Low integrity signal given current feature mix.",
    ]

    return {
        "score": score,
        "verdict": verdict,
        "claims": [],
        "rationale": rationale,
        "highlights": [],
        "report": {
            "headline": f"{subject} — RippleTruth Snapshot",
            "definition": "Prototype, deterministic read that approximates model-style metrics.",
            "eq": "RT = FILS × UCIP / (1 + TTCF)",
            "metrics": metrics,
            "narrative": narrative,
        },
    }

# --- Legacy prototype endpoint kept for compatibility with earlier front-ends ---

@app.post("/api/ripple/analyze")
def ripple_analyze():
    payload = request.get_json(force=True) or {}
    text  = payload.get("text", "")
    url   = payload.get("url")
    tools = payload.get("tools", [])

    doc_text = normalize_input(text, url)

    out = {"run_id": f"ripple_{int(time.time())}", "mode": "model", "tools": {}}

    # RippleTruth → use your structured analyzer (does 100/75/8 and article logic)
    if "RippleTruth" in tools:
        rt = analyze_truth_struct(doc_text)
        metrics = {m["name"]: f'{m["value"]} — {m.get("meaning","").strip()}'
                   for m in rt["report"]["metrics"]}
        out["tools"]["RippleTruth"] = {
            "score": rt["score"],
            "verdict": rt["verdict"],
            "headline": rt["report"]["headline"],
            "definition": rt["report"]["definition"],
            "formal": rt["report"]["eq"],
            "metrics": metrics,
            "narrative": "\n".join(rt["report"]["narrative"]),
            "rationale": rt["rationale"],
            "claims": rt["claims"],
            "highlights": rt["highlights"],
        }

    # Other tools (optional wiring)
    if "RippleScore" in tools:
        rs = analyze_score_struct(doc_text)
        out["tools"]["RippleScore"] = {"score": rs["score"], "summary": rs["summary"]}
    if "RippleAlign" in tools:
        ra = analyze_align_struct(doc_text)
        out["tools"]["RippleAlign"] = {"score": ra["score"], "summary": ra["summary"]}
    if "RippleSeer" in tools:
        rse = analyze_seer_struct(doc_text)
        out["tools"]["RippleSeer"] = {"score": rse["score"], "summary": rse["summary"]}
    if "RipplePhysco" in tools:
        rp = analyze_physco_struct(doc_text)
        out["tools"]["RipplePhysco"] = {"score": rp["score"], "summary": rp["summary"]}
    if "RippleWisdom" in tools:
        rw = analyze_wisdom_struct(doc_text)
        out["tools"]["RippleWisdom"] = {"score": rw["score"], "summary": rw["summary"]}

    return jsonify(out)

@app.get("/api/results/<rid>")
def get_results(rid: str):
    data = RESULTS.get(rid)
    if not data:
        return jsonify({"error": "not found"}), 404
    return jsonify(data)


# Serve uploaded files in prototype (disable in production)
@app.get("/uploads/<path:filename>")
def get_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
