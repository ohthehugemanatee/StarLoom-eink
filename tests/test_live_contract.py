import os
from datetime import datetime

import pytest

from starloom_eink.starloom import fetch_children

URL = os.environ.get("STARLOOM_URL")
KEY = os.environ.get("STARLOOM_API_KEY")


@pytest.mark.skipif(not (URL and KEY), reason="STARLOOM_URL and STARLOOM_API_KEY not set")
def test_live_instance_shape():
    children = fetch_children(URL, KEY)
    assert children
    for child in children:
        assert child.name
        assert isinstance(child.balance, int)
        for stamp in (child.last_award, child.last_spend):
            assert stamp is None or (isinstance(stamp, datetime) and stamp.tzinfo is not None)
