#!/usr/bin/env python3
"""Fixture tests for automation/check_publish_readiness.py.

Dependency-free (stdlib unittest only). Run from the repo root:

    python3 scripts/test_check_publish_readiness.py

Every case drives the pure `assess(nova, social, today)` function with an
inline fixture, so nothing here reads the live state files, touches the
inbox, or needs network. The first case is a faithful copy of the live
state shape on 2026-10-17 that produced three weeks of false "still
queued, posts tonight" nudges about the dropped 2026-09-14 episode.
"""
import contextlib
import datetime
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "automation"))

import check_publish_readiness as cpr  # noqa: E402
import post_to_meta  # noqa: E402

TODAY = datetime.date(2026, 10, 17)
UNPOSTED = {"facebook": False, "instagram": False, "tiktok": False, "threads": False}
POSTED = {"facebook": True, "instagram": True, "tiktok": False, "threads": True}


def post(publish_date, day="Monday", published=UNPOSTED, video="https://files2.heygen.ai/x.mp4", **extra):
    p = {
        "day": day,
        "publish_date": publish_date,
        "topic": f"topic for {publish_date}",
        "video_path": video,
        "platforms_published": dict(published),
    }
    p.update(extra)
    return p


def nova(status, publish_date, **extra):
    state = {"status": status, "publish_date": publish_date, "pr_number": None, "video_id": None}
    state.update(extra)
    return state


LIVE_SOCIAL = {
    "posts": [
        post("2026-10-05", published=POSTED, posted_at="2026-10-05T02:18:31+00:00"),
        post(
            "2026-09-14",
            dropped="2026-09-26: 12 days stale, HeyGen URL expired Sep 24",
        ),
    ]
}
LIVE_NOVA = nova("awaiting_topic_pick", "2026-10-07", last_proposed="2026-10-06")


class DroppedPosts(unittest.TestCase):
    def test_live_state_is_not_overdue(self):
        """Repro of the false alert: before the fix this returned
        ('overdue', 'Monday 2026-09-14 (33d late)') every evening."""
        kind, detail, _ = cpr.assess(LIVE_NOVA, LIVE_SOCIAL, TODAY)
        self.assertNotEqual(kind, "overdue")
        self.assertNotIn("2026-09-14", detail)

    def test_live_state_surfaces_the_parked_topic_list(self):
        kind, detail, log = cpr.assess(LIVE_NOVA, LIVE_SOCIAL, TODAY)
        self.assertEqual(kind, "stale")
        self.assertIn("2026-10-07", detail)
        self.assertIn("never picked", detail)
        self.assertIn("(10d past)", detail)
        self.assertIn("NOVA 1/2/3", detail)
        self.assertTrue(any("parked" in line for line in log))

    def test_dropped_post_due_today_is_not_ready(self):
        social = {"posts": [post(TODAY.isoformat(), dropped="owner said no")]}
        kind, _, _ = cpr.assess(nova("idle", None), social, TODAY)
        self.assertEqual(kind, "none")

    def test_dropped_post_does_not_mask_todays_status(self):
        social = {"posts": [post("2026-09-14", dropped="x")]}
        kind, detail, _ = cpr.assess(nova("pr_open", TODAY.isoformat(), pr_number=91), social, TODAY)
        self.assertEqual((kind, detail), ("needs_approval", "91"))


class OverdueVersusHeld(unittest.TestCase):
    def test_one_day_late_posts_tonight(self):
        social = {"posts": [post("2026-10-16", day="Friday")]}
        kind, detail, _ = cpr.assess(nova("idle", None), social, TODAY)
        self.assertEqual((kind, detail), ("overdue", "Friday 2026-10-16 (1d late)"))

    def test_held_post_is_not_reported_as_posting_tonight(self):
        social = {"posts": [post("2026-10-14", day="Wednesday")]}
        kind, _, log = cpr.assess(nova("idle", None), social, TODAY)
        self.assertEqual(kind, "none")
        self.assertTrue(any("Held as stale" in line and "2026-10-14 (3d late)" in line for line in log))

    def test_held_post_does_not_mask_a_shippable_one(self):
        social = {"posts": [post("2026-10-14", day="Wednesday"), post("2026-10-16", day="Friday")]}
        kind, detail, _ = cpr.assess(nova("idle", None), social, TODAY)
        self.assertEqual((kind, detail), ("overdue", "Friday 2026-10-16 (1d late)"))

    def test_cutoff_matches_post_to_meta(self):
        self.assertEqual(cpr.MAX_DAYS_LATE, post_to_meta.MAX_DAYS_LATE)

    def test_fully_posted_is_not_queued(self):
        social = {"posts": [post(TODAY.isoformat(), published=POSTED)]}
        kind, _, _ = cpr.assess(nova("idle", None), social, TODAY)
        self.assertEqual(kind, "none")

    def test_unrendered_is_not_queued(self):
        social = {"posts": [post(TODAY.isoformat(), video=None)]}
        kind, _, _ = cpr.assess(nova("awaiting_topic_pick", TODAY.isoformat()), social, TODAY)
        self.assertEqual(kind, "needs_pick")


class TodaysPipeline(unittest.TestCase):
    def test_ready(self):
        social = {"posts": [post(TODAY.isoformat())]}
        kind, _, _ = cpr.assess(nova("idle", None), social, TODAY)
        self.assertEqual(kind, "ready")

    def test_needs_approval(self):
        kind, detail, _ = cpr.assess(nova("pr_open", TODAY.isoformat(), pr_number=90), {}, TODAY)
        self.assertEqual((kind, detail), ("needs_approval", "90"))

    def test_rendering(self):
        kind, detail, _ = cpr.assess(nova("rendering", TODAY.isoformat(), video_id="vid1"), {}, TODAY)
        self.assertEqual((kind, detail), ("rendering", "vid1"))

    def test_needs_pick(self):
        kind, detail, _ = cpr.assess(nova("awaiting_topic_pick", TODAY.isoformat()), {}, TODAY)
        self.assertEqual((kind, detail), ("needs_pick", TODAY.isoformat()))

    def test_unexpected_status_today_flags_as_needs_pick(self):
        kind, detail, log = cpr.assess(nova("bogus", TODAY.isoformat()), {}, TODAY)
        self.assertEqual((kind, detail), ("needs_pick", TODAY.isoformat()))
        self.assertTrue(any("unexpected status" in line for line in log))

    def test_future_slot_is_none(self):
        kind, _, _ = cpr.assess(nova("awaiting_topic_pick", "2026-10-19"), {}, TODAY)
        self.assertEqual(kind, "none")

    def test_empty_state_is_none(self):
        kind, _, _ = cpr.assess({}, {}, TODAY)
        self.assertEqual(kind, "none")


class ParkedPipeline(unittest.TestCase):
    def test_unapproved_pr_past_its_slot(self):
        kind, detail, _ = cpr.assess(nova("pr_open", "2026-10-16", pr_number=90), {}, TODAY)
        self.assertEqual(kind, "stale")
        self.assertIn("PR #90", detail)
        self.assertIn("(1d past)", detail)
        self.assertIn("APPROVE 90", detail)

    def test_failed_render_past_its_slot(self):
        kind, detail, _ = cpr.assess(nova("failed", "2026-10-14"), {}, TODAY)
        self.assertEqual(kind, "stale")
        self.assertIn("render failed", detail)
        self.assertIn("render-retry-nova.yml", detail)

    def test_idle_with_old_publish_date_is_not_parked(self):
        # check_nova_render leaves publish_date None on reset, but a hand
        # edit might not; idle is never a parked state.
        kind, _, _ = cpr.assess(nova("idle", "2026-10-07"), {}, TODAY)
        self.assertEqual(kind, "none")

    def test_rendering_past_its_slot_is_left_to_render_check(self):
        kind, _, _ = cpr.assess(nova("rendering", "2026-10-16", video_id="v"), {}, TODAY)
        self.assertEqual(kind, "none")

    def test_queued_post_wins_over_parked_pipeline(self):
        # Something will actually post tonight; that is the more useful fact.
        social = {"posts": [post(TODAY.isoformat())]}
        kind, _, _ = cpr.assess(LIVE_NOVA, social, TODAY)
        self.assertEqual(kind, "ready")


class ResultLineContract(unittest.TestCase):
    """publish-nudge-nova.yml does `grep '^RESULT:' | tail -n1` then
    `cut -d: -f2` for kind and `-f3-` for detail -- so every RESULT line
    must be exactly one line and the kind must never contain a colon."""

    CASES = [
        (LIVE_NOVA, LIVE_SOCIAL),
        (nova("pr_open", "2026-10-16", pr_number=90), {}),
        (nova("failed", "2026-10-14"), {}),
        (nova("idle", None), {"posts": [post("2026-10-16", day="Friday")]}),
        (nova("pr_open", TODAY.isoformat(), pr_number=90), {}),
        ({}, {}),
    ]

    def test_single_line_and_colon_free_kind(self):
        for nova_state, social in self.CASES:
            kind, detail, log = cpr.assess(nova_state, social, TODAY)
            self.assertNotIn(":", kind)
            self.assertNotIn("\n", detail)
            for line in log:
                self.assertNotIn("\n", line)
                self.assertFalse(line.startswith("RESULT:"))

    def test_main_reads_files_and_emits_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "automation"))
            with open(os.path.join(tmp, cpr.NOVA_STATE_PATH), "w", encoding="utf-8") as f:
                json.dump(LIVE_NOVA, f)
            with open(os.path.join(tmp, cpr.SOCIAL_STATE_PATH), "w", encoding="utf-8") as f:
                json.dump(LIVE_SOCIAL, f)
            cwd = os.getcwd()
            out = io.StringIO()
            try:
                os.chdir(tmp)
                with contextlib.redirect_stdout(out):
                    cpr.main(today=TODAY)
            finally:
                os.chdir(cwd)
        lines = out.getvalue().splitlines()
        result = [l for l in lines if l.startswith("RESULT:")]
        self.assertEqual(len(result), 1)
        kind, detail = result[0].split(":", 2)[1:]
        self.assertEqual(kind, "stale")
        self.assertIn("2026-10-07", detail)

    def test_main_tolerates_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = os.getcwd()
            out = io.StringIO()
            try:
                os.chdir(tmp)
                with contextlib.redirect_stdout(out):
                    cpr.main(today=TODAY)
            finally:
                os.chdir(cwd)
        self.assertIn("RESULT:none:", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
