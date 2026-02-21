"""Export FastAPI OpenAPI spec to docs/openapi.json."""
import json
import sys
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from main import app

output = Path(__file__).parent.parent.parent / "docs" / "openapi.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(app.openapi(), indent=2))
print(f"OpenAPI spec written to {output} ({len(app.openapi()['paths'])} endpoints)")
