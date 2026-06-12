from __future__ import annotations

import os
import sys
from datetime import date
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from bwa_backend import app as blog_app

app = FastAPI(title="Blog Writing Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Blog topic")
    as_of: str = Field(default="", description="ISO date (defaults to today)")


class TaskInfo(BaseModel):
    id: int
    title: str
    goal: str
    target_words: int
    requires_research: bool
    requires_citations: bool
    requires_code: bool
    tags: list[str]


class GenerateResponse(BaseModel):
    blog_title: str
    mode: str
    needs_research: bool
    queries: list[str]
    evidence: list[dict]
    tasks: list[TaskInfo]
    markdown: str


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    as_of = req.as_of or date.today().isoformat()

    inputs: Dict[str, Any] = {
        "topic": req.topic,
        "mode": "",
        "needs_research": False,
        "queries": [],
        "evidence": [],
        "plan": None,
        "as_of": as_of,
        "recency_days": 7,
        "sections": [],
        "merged_md": "",
        "md_with_placeholders": "",
        "image_specs": [],
        "final": "",
    }

    out = blog_app.invoke(inputs)

    plan = out.get("plan")
    evidence_raw = out.get("evidence") or []
    evidence = []
    for e in evidence_raw:
        if hasattr(e, "model_dump"):
            evidence.append(e.model_dump())
        elif isinstance(e, dict):
            evidence.append(e)

    tasks = []
    if plan and hasattr(plan, "tasks"):
        for t in plan.tasks:
            tasks.append(
                TaskInfo(
                    id=t.id,
                    title=t.title,
                    goal=t.goal,
                    target_words=t.target_words,
                    requires_research=t.requires_research,
                    requires_citations=t.requires_citations,
                    requires_code=t.requires_code,
                    tags=list(t.tags) if hasattr(t, "tags") else [],
                )
            )
    elif plan and isinstance(plan, dict):
        for t in plan.get("tasks", []):
            tasks.append(TaskInfo(**t))

    return GenerateResponse(
        blog_title=plan.blog_title if hasattr(plan, "blog_title") else plan.get("blog_title", ""),
        mode=out.get("mode", ""),
        needs_research=out.get("needs_research", False),
        queries=out.get("queries", []),
        evidence=evidence,
        tasks=tasks,
        markdown=out.get("final", ""),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
