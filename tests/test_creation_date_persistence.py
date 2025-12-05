import os
import time
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytest
from slate.main import handle_page_build, _rebuild_page
from slate.site import Page, Site


# Mock datetime to control time
class MockDatetime(datetime):
    _now = datetime(2024, 1, 1, 10, 0, 0)

    @classmethod
    def now(cls):
        return cls._now

    @classmethod
    def advance(cls, minutes=10):
        cls._now += timedelta(minutes=minutes)


def test_creation_date_persistence(tmp_path):
    # Setup
    source_file = tmp_path / "test.md"
    template_file = tmp_path / "template.html"
    template_file.write_text(
        "<html>{{content}}<!-- {{creation_time}} --></html>", encoding="utf-8"
    )

    source_file.write_text(
        f"---\ntitle: Test Page\ntemplate: {template_file}\n---\nContent",
        encoding="utf-8",
    )

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    output_file = output_dir / "test.html"

    # Mock args
    args = MagicMock()
    args.template = str(template_file)
    args.description = "Desc"
    args.output = str(output_file)

    # Mock Site and Page
    page = Page(source_file, output_file, {}, None, False)
    site = MagicMock(spec=Site)
    site.index_page = page
    site.categories = {}

    # 1. First Build at 10:00
    with patch("slate.main.datetime", MockDatetime):
        MockDatetime._now = datetime(2024, 1, 1, 10, 0, 0)
        _rebuild_page(
            page=page,
            site=site,
            category_name=None,
            version="v1.0",
            main_parser=MagicMock(),
            fmt="html",
            output_root=None,  # Use page.output_path
        )

    assert output_file.exists()
    content1 = output_file.read_text()

    # Extract metadata
    # We look for the comment we added in the template for easy checking,
    # but the logic relies on the slate metadata comment at the end.
    assert "<!-- 10:00 -->" in content1

    # Verify slate metadata exists
    assert "<!-- slate: {" in content1

    # 2. Second Build at 10:10 (No Clean)
    # Should preserve 10:00 creation time
    with patch("slate.main.datetime", MockDatetime):
        MockDatetime._now = datetime(2024, 1, 1, 10, 10, 0)
        _rebuild_page(
            page=page,
            site=site,
            category_name=None,
            version="v1.0",
            main_parser=MagicMock(),
            fmt="html",
            output_root=None,
        )

    content2 = output_file.read_text()
    # Expectation: Creation time should still be 10:00
    # Current behavior (bug): It will be 10:10

    # We assert the DESIRED behavior (persistence)
    # If this fails, we have reproduced the bug (or rather, confirmed the feature is missing)
    if "<!-- 10:00 -->" not in content2:
        pytest.fail(
            f"Creation time was updated to {MockDatetime._now.strftime('%H:%M')}, expected 10:00"
        )

    # 3. Third Build at 10:20 (With Clean - simulated by deleting file)
    output_file.unlink()

    with patch("slate.main.datetime", MockDatetime):
        MockDatetime._now = datetime(2024, 1, 1, 10, 20, 0)
        _rebuild_page(
            page=page,
            site=site,
            category_name=None,
            version="v1.0",
            main_parser=MagicMock(),
            fmt="html",
            output_root=None,
        )

    content3 = output_file.read_text()
    assert "<!-- 10:20 -->" in content3
