"""
FastAPI web demo for the fine-tuned FLAN-T5 construction rule extractor.

Run locally from the src/ directory:
    uvicorn app:app --reload --port 8000

Then open http://127.0.0.1:8000 in a browser.

Set the MODEL_PATH environment variable to point at a different model
directory; otherwise it defaults to models/flan_t5_construction/flan_t5_construction.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from run_inference import generate_json, load_model

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "flan_t5_construction" / "flan_t5_construction"
MODEL_PATH = Path(os.environ.get("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
STATIC_DIR = Path(__file__).parent / "static"

model_state: dict = {}

# Only the numeric performance fields are surfaced to the chatbot - the model's
# categorical fields (surface_type, construction_type, building_category, ...)
# have not been validated for accuracy and are left out to avoid showing
# unreliable information.
NUMERIC_FIELDS = ["max_u_value", "max_f_factor", "max_c_factor", "max_shgc", "min_vt", "min_vt_shgc"]
NUMERIC_FIELD_UNIT_KEYS = {
    "max_u_value": "u_value",
    "max_f_factor": "f_factor",
    "max_c_factor": "c_factor",
    "max_shgc": "shgc",
    "min_vt": "vt",
    "min_vt_shgc": "vt",
}


def extract_numeric_requirements(parsed: dict) -> dict:
    """Pull out just the numeric outputs (+ units) from a parsed rule JSON."""
    outputs = parsed.get("outputs") or {}
    units = parsed.get("units") or {}
    requirements = {}
    for field in NUMERIC_FIELDS:
        value = outputs.get(field)
        if value is not None:
            requirements[field] = {"value": value, "unit": units.get(NUMERIC_FIELD_UNIT_KEYS[field])}
    return requirements


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model path does not exist: {MODEL_PATH}\n"
            "Set the MODEL_PATH environment variable to your fine-tuned model directory."
        )
    tokenizer, model, device = load_model(str(MODEL_PATH))
    model_state["tokenizer"] = tokenizer
    model_state["model"] = model
    model_state["device"] = device
    yield
    model_state.clear()


app = FastAPI(title="Construction Code Requirement Checker", lifespan=lifespan)


class CheckRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_path": str(MODEL_PATH),
        "device": model_state.get("device"),
    }


@app.post("/check")
def check(request: CheckRequest) -> dict:
    """Runs synchronously (not async def) so FastAPI offloads this CPU-bound
    model call to a worker thread instead of blocking the event loop."""
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")

    result = generate_json(
        text,
        model_state["tokenizer"],
        model_state["model"],
        model_state["device"],
    )

    if "error" in result:
        return result

    return {
        "climate_zone": (result.get("inputs") or {}).get("climate_zone"),
        "rule_category": result.get("rule_category"),
        "numeric_requirements": extract_numeric_requirements(result),
    }
