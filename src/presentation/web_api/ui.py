from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(include_in_schema=False)


# ----------------------------
# In-memory demo storage (replace with DB/interactors)
# ----------------------------
@dataclass
class ChatSummary:
    id: str
    title: str

@dataclass
class ChoiceVM:
    id: str
    label: str

@dataclass
class MessageVM:
    role: str           # "assistant" | "user"
    kind: str           # "question" | "feedback" | "info" | "user_choice"
    text: str


_SESSIONS: dict[str, dict[str, Any]] = {}
_CHATS: dict[str, dict[str, Any]] = {}


def _get_session_key(request: Request) -> str | None:
    return request.cookies.get("session_key")


def _require_session_key(request: Request) -> str:
    sk = _get_session_key(request)
    if not sk or sk not in _SESSIONS:
        # No session cookie => redirect to login
        raise RuntimeError("NO_SESSION")
    return sk


def _render_login(request: Request, error: str | None = None) -> HTMLResponse:
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error},
        status_code=200,
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # If already logged in => go to app
    sk = _get_session_key(request)
    if sk and sk in _SESSIONS:
        return RedirectResponse("/app", status_code=303)
    return _render_login(request)


@router.post("/login")
def login_submit(
    request: Request,
    name: str = Form(...),
    grade: int = Form(...),
):
    name = name.strip()
    if not name:
        return _render_login(request, error="Name is required.")

    # Create session + cookie
    sk = str(uuid4())
    _SESSIONS[sk] = {"name": name, "grade": grade, "chat_ids": []}

    resp = RedirectResponse("/app", status_code=303)
    resp.set_cookie(
        "session_key",
        sk,
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS
        max_age=60 * 60 * 24 * 30,  # 30 days
    )
    return resp


@router.get("/logout")
def logout(request: Request):
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("session_key")
    return resp


@router.get("/app", response_class=HTMLResponse)
def app_shell(request: Request, chat_id: str | None = None):
    try:
        sk = _require_session_key(request)
    except RuntimeError:
        return RedirectResponse("/login", status_code=303)

    # pick current chat
    chat_ids = _SESSIONS[sk]["chat_ids"]
    current_chat_id = chat_id or (chat_ids[0] if chat_ids else None)

    return templates.TemplateResponse(
        "app.html",
        {
            "request": request,
            "student_name": _SESSIONS[sk]["name"],
            "grade": _SESSIONS[sk]["grade"],
            "current_chat_id": current_chat_id,
        },
    )


# ----------------------------
# Partials (HTMX)
# ----------------------------
@router.get("/partials/chats", response_class=HTMLResponse)
def partial_chats_list(request: Request, current_chat_id: str | None = None):
    try:
        sk = _require_session_key(request)
    except RuntimeError:
        return RedirectResponse("/login", status_code=303)

    chats = []
    for cid in _SESSIONS[sk]["chat_ids"]:
        chat = _CHATS[cid]
        chats.append(ChatSummary(id=cid, title=chat["title"]))

    return templates.TemplateResponse(
        "partials/chats_list.html",
        {
            "request": request,
            "chats": chats,
            "current_chat_id": current_chat_id,
        },
    )


@router.post("/chat/new", response_class=HTMLResponse)
def create_chat(request: Request):
    sk = _require_session_key(request)

    cid = str(uuid4())
    title = f"Chat #{len(_SESSIONS[sk]['chat_ids']) + 1}"

    _CHATS[cid] = {
        "title": title,
        "messages": [
            MessageVM(role="assistant", kind="question", text="Choose a topic:"),
        ],
        "choices": [
            ChoiceVM(id="topic_fractions", label="Fractions"),
            ChoiceVM(id="topic_equations", label="Equations"),
            ChoiceVM(id="topic_geometry", label="Geometry"),
        ],
    }
    _SESSIONS[sk]["chat_ids"].insert(0, cid)

    # Build chats list data
    chats = [
        ChatSummary(id=xid, title=_CHATS[xid]["title"])
        for xid in _SESSIONS[sk]["chat_ids"]
    ]

    # Render partials to strings
    chats_html = templates.get_template("partials/chats_list.html").render(
        request=request,
        chats=chats,
        current_chat_id=cid,
    )
    chat_html = templates.get_template("partials/chat_view.html").render(
        request=request,
        chat_id=cid,
        messages=_CHATS[cid]["messages"],
        choices=_CHATS[cid]["choices"],
    )

    # OOB swaps: update sidebar + main chat pane without reload
    body = f"""
    <div id="chats-list" hx-swap-oob="innerHTML">
      {chats_html}
    </div>

    <div id="chat-pane-wrapper" hx-swap-oob="innerHTML">
      {chat_html}
    </div>
    """

    return HTMLResponse(
        body,
        headers={
            "HX-Push-Url": f"/app?chat_id={cid}",
        },
    )


@router.get("/partials/chat/{chat_id}", response_class=HTMLResponse)
def partial_chat_view(request: Request, chat_id: str):
    try:
        sk = _require_session_key(request)
    except RuntimeError:
        return RedirectResponse("/login", status_code=303)

    if chat_id not in _SESSIONS[sk]["chat_ids"]:
        return HTMLResponse("Not found", status_code=404)

    # Chat view
    chat = _CHATS[chat_id]
    chat_html = templates.get_template("partials/chat_view.html").render(
        request=request,
        chat_id=chat_id,
        messages=chat["messages"],
        choices=chat["choices"],
    )

    # Sidebar (re-render with selected chat)
    chats = [
        ChatSummary(id=cid, title=_CHATS[cid]["title"])
        for cid in _SESSIONS[sk]["chat_ids"]
    ]
    chats_html = templates.get_template("partials/chats_list.html").render(
        request=request,
        chats=chats,
        current_chat_id=chat_id,
    )

    # Return chat html + OOB update for sidebar
    body = f"""
    {chat_html}

    <div id="chats-list" hx-swap-oob="innerHTML">
      {chats_html}
    </div>
    """

    return HTMLResponse(body)


@router.post("/chat/{chat_id}/choose", response_class=HTMLResponse)
def choose(request: Request, chat_id: str, choice_id: str = Form(...)):
    try:
        sk = _require_session_key(request)
    except RuntimeError:
        return RedirectResponse("/login", status_code=303)

    if chat_id not in _SESSIONS[sk]["chat_ids"]:
        return HTMLResponse("Not found", status_code=404)

    chat = _CHATS[chat_id]

    allowed = {c.id: c for c in chat["choices"]}
    if choice_id not in allowed:
        return HTMLResponse("Invalid choice", status_code=400)

    picked = allowed[choice_id]
    chat["messages"].append(MessageVM(role="user", kind="user_choice", text=picked.label))

    # demo next step (replace with your application interactor)
    if choice_id.startswith("topic_"):
        chat["messages"].append(MessageVM(
            role="assistant",
            kind="question",
            text=f"Great. Start the test for “{picked.label}”?"
        ))
        chat["choices"] = [
            ChoiceVM(id="start_test_yes", label="Yes"),
            ChoiceVM(id="start_test_no", label="No"),
        ]
    elif choice_id == "start_test_yes":
        chat["messages"].append(MessageVM(
            role="assistant",
            kind="question",
            text="Q1) 1/2 + 1/4 = ?"
        ))
        chat["choices"] = [
            ChoiceVM(id="a", label="3/4"),
            ChoiceVM(id="b", label="2/6"),
            ChoiceVM(id="c", label="1/6"),
        ]
    elif choice_id in {"a", "b", "c"}:
        is_correct = (choice_id == "a")
        chat["messages"].append(MessageVM(
            role="assistant",
            kind="feedback",
            text=("✅ Correct!" if is_correct else "❌ Incorrect. The answer is 3/4.")
        ))
        chat["messages"].append(MessageVM(
            role="assistant",
            kind="info",
            text="(Demo) Test finished. Chat deactivated."
        ))
        chat["choices"] = []  # no more buttons

    return templates.TemplateResponse(
        "partials/chat_view.html",
        {
            "request": request,
            "chat_id": chat_id,
            "messages": chat["messages"],
            "choices": chat["choices"],
        },
        headers={"HX-Trigger": "refresh-chats"},  # refresh sidebar if you want
    )
