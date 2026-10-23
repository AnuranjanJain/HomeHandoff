from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.domain.models import AskRequest, ConfirmRequest
from app.service import HomeHandoffService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="HomeHandoff", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
service = HomeHandoffService()


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html", context={"app_name": "HomeHandoff"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "simulated"}


@app.get("/api/state")
def get_state() -> dict:
    return service.state.model_dump(mode="json")


@app.post("/api/ask")
def ask(request: AskRequest) -> dict:
    return service.handle_request(request.message).model_dump(mode="json")


@app.post("/api/confirm")
def confirm(request: ConfirmRequest) -> dict:
    try:
        return service.confirm(request.action_id).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/reset")
def reset() -> dict:
    return service.reset().model_dump(mode="json")
