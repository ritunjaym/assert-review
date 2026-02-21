import re
from .schema import Hunk, FileRecord, PRRecord


def parse_patch(patch: str) -> list[Hunk]:
    """Split unified diff into hunks."""
    if not patch:
        return []
    
    hunks = []
    hunk_pattern = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', re.MULTILINE)
    
    matches = list(hunk_pattern.finditer(patch))
    for i, match in enumerate(matches):
        old_start = int(match.group(1))
        old_lines = int(match.group(2)) if match.group(2) is not None else 1
        new_start = int(match.group(3))
        new_lines = int(match.group(4)) if match.group(4) is not None else 1
        
        # Extract hunk body
        start_pos = match.end()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(patch)
        body = patch[start_pos:end_pos]
        
        context = []
        added = []
        removed = []
        
        for line in body.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added.append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                removed.append(line[1:])
            elif line.startswith(' '):
                context.append(line[1:])
        
        raw = patch[match.start():end_pos]
        hunks.append(Hunk(
            old_start=old_start,
            old_lines=old_lines,
            new_start=new_start,
            new_lines=new_lines,
            context=context,
            added_lines=added,
            removed_lines=removed,
            raw=raw,
        ))
    
    return hunks


def parse_pr(pr_json: dict) -> PRRecord:
    """Parse GitHub PR JSON into PRRecord."""
    files = []
    total_add = 0
    total_del = 0
    
    for f in pr_json.get("files", []):
        patch = f.get("patch", "")
        hunks = parse_patch(patch) if patch else []
        file_rec = FileRecord(
            filename=f.get("filename", ""),
            status=f.get("status", "modified"),
            additions=f.get("additions", 0),
            deletions=f.get("deletions", 0),
            patch=patch,
            hunks=hunks,
        )
        files.append(file_rec)
        total_add += f.get("additions", 0)
        total_del += f.get("deletions", 0)
    
    return PRRecord(
        pr_id=pr_json.get("number", 0),
        repo=pr_json.get("repo", ""),
        title=pr_json.get("title", ""),
        state=pr_json.get("state", "merged"),
        author=pr_json.get("user", {}).get("login", ""),
        created_at=pr_json.get("created_at", ""),
        merged_at=pr_json.get("merged_at"),
        files=files,
        total_additions=total_add,
        total_deletions=total_del,
    )
