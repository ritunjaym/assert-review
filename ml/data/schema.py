from pydantic import BaseModel, Field
from typing import Optional


class Hunk(BaseModel):
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    context: list[str] = Field(default_factory=list)
    added_lines: list[str] = Field(default_factory=list)
    removed_lines: list[str] = Field(default_factory=list)
    raw: str = ""


class FileRecord(BaseModel):
    filename: str
    status: str = "modified"  # added, removed, modified, renamed
    additions: int = 0
    deletions: int = 0
    patch: Optional[str] = None
    hunks: list[Hunk] = Field(default_factory=list)


class PRRecord(BaseModel):
    pr_id: int
    repo: str
    title: str
    state: str
    author: str
    created_at: str
    merged_at: Optional[str] = None
    files: list[FileRecord] = Field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0


class LabeledFile(BaseModel):
    pr_id: int
    repo: str
    pr_title: str
    filename: str
    status: str
    additions: int
    deletions: int
    patch: Optional[str] = None
    importance_score: float
    path_score: float
    size_score: float
    security_score: float
    hunk_count: int


class LabeledHunk(BaseModel):
    pr_id: int
    repo: str
    filename: str
    hunk_index: int
    old_start: int
    new_start: int
    added_lines: list[str]
    removed_lines: list[str]
    raw: str
    importance_score: float
