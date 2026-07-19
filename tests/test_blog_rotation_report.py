from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin" / "report-blog-rotation"


def page(ids: tuple[int, int, int]) -> str:
    articles = []
    for index, item_id in enumerate(ids):
        featured = index == 0
        category = "Transformation Strategy" if featured else f"Category {item_id}"
        category_attr = "" if featured else f' data-post-category="{category}"'
        featured_label = "<span>Featured</span>" if featured else ""
        articles.append(
            f'''<article data-collection-item data-collection-item-id="{item_id}" data-collection-slot="{index + 1}"{category_attr}>
<div class="thread-post-meta">{featured_label}<span>{category}</span><span>Draft</span></div>
<h3>Title {item_id}</h3><p>Summary {item_id}</p></article>'''
        )
    return textwrap.dedent(
        f"""
        <!-- PM:COLLECTION-TRANSFORMATION-THREAD -->
        <section id="blog">{''.join(articles)}</section>
        <!-- /PM:COLLECTION-TRANSFORMATION-THREAD -->
        """
    )


class BlogRotationReportTests(unittest.TestCase):
    def test_reporter_parses_collection_system_markup(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("COLLECTION-TRANSFORMATION-THREAD", script)
        self.assertIn("data-collection-item-id", script)
        self.assertIn("data-collection-slot", script)
        self.assertNotIn("data-thread-post-id", script)

    def test_reporter_identifies_removed_and_added_collection_items(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            target = repo / "deploy/prd/www/index.html"
            target.parent.mkdir(parents=True)
            target.write_text(page((1, 2, 3)), encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Tests"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "old"], cwd=repo, check=True)
            target.write_text(page((4, 5, 6)), encoding="utf-8")

            result = subprocess.run(
                [str(SCRIPT)],
                cwd=repo / "deploy/prd",
                env={**os.environ, "EXPECTED_ROTATION_COUNT": "3"},
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertIn("removed_count=3 added_count=3", result.stdout)
            self.assertIn("BLOG_REMOVED id=1 tt_id=TT-001", result.stdout)
            self.assertIn("BLOG_ADDED id=4 tt_id=TT-004", result.stdout)
            self.assertIn('category="Transformation Strategy"', result.stdout)


if __name__ == "__main__":
    unittest.main()
