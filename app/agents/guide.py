"""guide_node — case_type 기준 YAML 룩업."""
from pathlib import Path
import yaml
from functools import lru_cache
from app.config import settings
from app.state import AgentState


@lru_cache(maxsize=1)
def _load_guides() -> dict:
    path = Path(settings.guides_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


async def guide_node(state: AgentState) -> dict:
    domain = state.get("domain")
    case_type = state.get("case_type")
    if not domain or not case_type:
        return {"guide_steps": []}

    guides = _load_guides()
    key = f"{domain}.{case_type}"
    steps = guides.get(key, [])
    return {"guide_steps": steps}
