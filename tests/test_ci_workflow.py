from pathlib import Path

import yaml

CI = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
IMAGE = "ghcr.io/ohthehugemanatee/starloom-eink"


def _publish():
    jobs = yaml.safe_load(CI.read_text())["jobs"]
    assert "publish" in jobs
    return jobs["publish"]


def _step(job, uses):
    steps = [s for s in job["steps"] if s.get("uses", "").startswith(uses)]
    assert len(steps) == 1, uses
    return steps[0]


def test_publish_waits_for_tests():
    assert {"test", "e2e"} <= set(_publish()["needs"])


def test_publish_runs_only_on_main_push():
    cond = _publish()["if"]
    assert "github.event_name == 'push'" in cond
    assert "refs/heads/main" in cond


def test_publish_permissions_are_minimal():
    assert _publish()["permissions"] == {"contents": "read", "packages": "write"}


def test_publish_logs_in_with_the_workflow_token():
    login = _step(_publish(), "docker/login-action")["with"]
    assert login["registry"] == "ghcr.io"
    assert login["password"] == "${{ secrets.GITHUB_TOKEN }}"


def test_publish_pushes_tagged_amd64_image():
    job = _publish()
    meta = _step(job, "docker/metadata-action")["with"]
    assert meta["images"] == IMAGE
    assert "type=sha" in meta["tags"]
    assert "latest" in meta["tags"]
    build = _step(job, "docker/build-push-action")["with"]
    assert build["push"] is True
    assert build["platforms"] == "linux/amd64"
    assert "steps.meta.outputs.tags" in build["tags"]
