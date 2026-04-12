import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

licenses_data: dict = {}
versions_data: dict = {}


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


def _find_versions_file() -> Path:
    secret_path = Path("/etc/secrets/versions.json")
    if secret_path.exists():
        return secret_path
    return Path(__file__).parent / "versions.json"


def load_versions():
    global versions_data
    versions_file = _find_versions_file()
    if versions_file.exists():
        versions_data = json.load(open(versions_file))["versions"]


load_versions()


class ValidateRequest(BaseModel):
    key: str
    app: str


class VersionCheckRequest(BaseModel):
    app: str
    version: str


@app.post("/validate")
def validate(req: ValidateRequest):
    if not req.key or not req.app:
        return {"valid": False, "reason": "bad_request"}

    if req.key not in licenses_data:
        return {"valid": False, "reason": "not_found"}

    lic = licenses_data[req.key]

    if lic["app"] != req.app:
        return {"valid": False, "reason": "invalid_app"}

    if lic["expires"] and lic["expires"] != "null":
        exp_date = datetime.fromisoformat(lic["expires"])
        if exp_date < datetime.now():
            return {"valid": False, "reason": "expired"}

    response = {"valid": True, "expires": lic["expires"]}

    standard_fields = {"app", "expires"}
    for field, value in lic.items():
        if field not in standard_fields and value:
            response[field] = value

    return response


@app.post("/check-version")
def check_version(req: VersionCheckRequest):
    if not req.app or not req.version:
        raise HTTPException(status_code=400, detail="bad_request")

    if req.app not in versions_data:
        raise HTTPException(status_code=404, detail="app_not_found")

    latest_version = versions_data[req.app]
    update_available = latest_version != req.version

    return {"update_available": update_available, "latest_version": latest_version}
