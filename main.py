import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

licenses_data: dict = {}


def _find_licenses_file() -> Path:
    secret_path = Path("/etc/secrets/licenses.json")
    if secret_path.exists():
        return secret_path
    return Path(__file__).parent / "licenses.json"


def load_licenses():
    global licenses_data
    licenses_file = _find_licenses_file()
    if not licenses_file.exists():
        raise FileNotFoundError(
            f"licenses.json not found in /etc/secrets/ or {licenses_file.parent}"
        )
    licenses_data = json.load(open(licenses_file))["licenses"]


load_licenses()


class ValidateRequest(BaseModel):
    key: str
    app: str


@app.post("/validate")
def validate(req: ValidateRequest):
    if not req.key or not req.app:
        return {"valid": False, "reason": "bad_request"}

    if req.key not in licenses_data:
        return {"valid": False, "reason": "not_found"}

    lic = licenses_data[req.key]

    if lic["app"] != req.app:
        return {"valid": False, "reason": "invalid_app"}

    if lic["expires"]:
        exp_date = datetime.fromisoformat(lic["expires"])
        if exp_date < datetime.now():
            return {"valid": False, "reason": "expired"}

    response = {"valid": True, "expires": lic["expires"]}

    standard_fields = {"app", "expires"}
    for field, value in lic.items():
        if field not in standard_fields and value:
            response[field] = value

    return response
