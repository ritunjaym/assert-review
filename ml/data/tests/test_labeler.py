import pytest
from ml.data.labeler import compute_importance, _path_score, _security_score
from ml.data.schema import FileRecord, PRRecord


def make_pr(files):
    total_add = sum(f.additions for f in files)
    total_del = sum(f.deletions for f in files)
    return PRRecord(
        pr_id=1, repo="test/repo", title="Test",
        state="merged", author="user", created_at="2024-01-01",
        files=files, total_additions=total_add, total_deletions=total_del,
    )


@pytest.mark.parametrize("filename,expected_range", [
    ("src/core/auth.py", (0.7, 1.0)),
    ("README.md", (0.0, 0.2)),
    ("docs/guide.rst", (0.0, 0.2)),
    ("package.json", (0.2, 0.5)),
])
def test_path_score_ranges(filename, expected_range):
    score = _path_score(filename)
    assert expected_range[0] <= score <= expected_range[1], f"{filename}: {score}"


def test_security_score_positive():
    assert _security_score("src/auth/token.py", None) == 1.0
    assert _security_score("services/crypto.go", None) == 1.0
    assert _security_score("utils/password_hash.py", None) == 1.0


def test_security_score_negative():
    assert _security_score("src/ui/button.tsx", None) == 0.0
    assert _security_score("README.md", None) == 0.0


def test_test_file_penalty():
    f = FileRecord(filename="src/auth/__tests__/login.test.ts", additions=20, deletions=5)
    pr = make_pr([f])
    scores = compute_importance(f, pr)
    # Even a security-named test file should be penalized
    assert scores["importance_score"] < 0.9


def test_config_file_penalty():
    f = FileRecord(filename="config/settings.yaml", additions=5, deletions=2)
    pr = make_pr([f])
    scores = compute_importance(f, pr)
    # Config files should get penalty
    assert scores["importance_score"] < 0.5


def test_large_package_json_not_penalized():
    f = FileRecord(filename="package.json", additions=60, deletions=10)
    pr = make_pr([f])
    scores = compute_importance(f, pr)
    # Large package.json changes should NOT get config penalty
    # (it should be higher than a small config change)
    f_small = FileRecord(filename="config.yaml", additions=5, deletions=2)
    pr_small = make_pr([f_small])
    scores_small = compute_importance(f_small, pr_small)
    assert scores["importance_score"] >= scores_small["importance_score"]


def test_importance_score_bounds():
    for filename, additions, deletions in [
        ("src/main.py", 100, 50),
        ("README.md", 5, 2),
        ("src/auth/jwt.py", 30, 10),
        ("tests/test_foo.py", 20, 5),
    ]:
        f = FileRecord(filename=filename, additions=additions, deletions=deletions)
        pr = make_pr([f])
        scores = compute_importance(f, pr)
        assert 0.0 <= scores["importance_score"] <= 1.0, f"{filename}: {scores['importance_score']}"


def test_security_file_high_importance():
    f = FileRecord(filename="src/auth/oauth.py", additions=50, deletions=10)
    pr = make_pr([f])
    scores = compute_importance(f, pr)
    assert scores["importance_score"] > 0.5  # Security + source path = high importance
