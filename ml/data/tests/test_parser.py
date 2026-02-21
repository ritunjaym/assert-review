import pytest
from ml.data.parser import parse_patch, parse_pr
from ml.data.schema import Hunk


SIMPLE_PATCH = """\
@@ -1,5 +1,6 @@
 line1
 line2
-old_line3
+new_line3
+new_line4
 line4
 line5
"""

MULTI_HUNK_PATCH = """\
@@ -1,4 +1,4 @@
 line1
-old2
+new2
 line3
 line4
@@ -10,4 +10,5 @@
 line10
 line11
+extra_line
 line12
 line13
"""

NO_CHANGE_PATCH = """\
@@ -1,3 +1,3 @@
 line1
 line2
 line3
"""


def test_parse_patch_single_hunk():
    hunks = parse_patch(SIMPLE_PATCH)
    assert len(hunks) == 1
    h = hunks[0]
    assert h.old_start == 1
    assert h.new_start == 1
    assert "old_line3" in h.removed_lines
    assert "new_line3" in h.added_lines
    assert "new_line4" in h.added_lines
    assert len(h.added_lines) == 2
    assert len(h.removed_lines) == 1


def test_parse_patch_multi_hunk():
    hunks = parse_patch(MULTI_HUNK_PATCH)
    assert len(hunks) == 2
    assert hunks[0].old_start == 1
    assert hunks[1].old_start == 10
    assert "old2" in hunks[0].removed_lines
    assert "new2" in hunks[0].added_lines
    assert "extra_line" in hunks[1].added_lines


def test_parse_patch_empty():
    assert parse_patch("") == []
    assert parse_patch(None) == []


def test_parse_pr_builds_record():
    pr_json = {
        "number": 42,
        "repo": "test/repo",
        "title": "Test PR",
        "state": "closed",
        "user": {"login": "testuser"},
        "created_at": "2024-01-01T00:00:00Z",
        "merged_at": "2024-01-02T00:00:00Z",
        "files": [
            {
                "filename": "src/auth/login.py",
                "status": "modified",
                "additions": 10,
                "deletions": 5,
                "patch": SIMPLE_PATCH,
            }
        ],
    }
    pr = parse_pr(pr_json)
    assert pr.pr_id == 42
    assert pr.repo == "test/repo"
    assert len(pr.files) == 1
    assert pr.files[0].filename == "src/auth/login.py"
    assert len(pr.files[0].hunks) == 1
    assert pr.total_additions == 10
    assert pr.total_deletions == 5
