"""Shards by position, for CI (#187).

A shard keeps the collected tests whose position, modulo TEST_SHARD_COUNT,
equals TEST_SHARD_INDEX. The shards of one count together hold every test
exactly once: a partition by position cannot leave a test out. With neither
variable set, every test runs (a local run and Ubuntu are unchanged). One set
without the other, or a value out of range, is a usage error, never a
silent run of fewer tests.

Each shard prints the count it kept and a digest of the whole ordered list
it collected. Equal digests in every shard, with kept counts that add up to
the total, show that each test ran exactly once.
"""
import hashlib
import os

import pytest

COUNT = "TEST_SHARD_COUNT"
INDEX = "TEST_SHARD_INDEX"


def _shard():
    count, index = os.environ.get(COUNT), os.environ.get(INDEX)
    if count is None and index is None:
        return None
    if count is None or index is None:
        raise pytest.UsageError(f"{COUNT} and {INDEX} are set together or not at all")
    try:
        n, i = int(count), int(index)
    except ValueError:
        raise pytest.UsageError(f"{COUNT} and {INDEX} must be whole numbers") from None
    if n < 1 or not 0 <= i < n:
        raise pytest.UsageError(f"need {COUNT} >= 1 and 0 <= {INDEX} < {COUNT}")
    return n, i


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    shard = _shard()
    if shard is None:
        return
    n, i = shard
    keep = [item for pos, item in enumerate(items) if pos % n == i]
    drop = [item for pos, item in enumerate(items) if pos % n != i]
    digest = hashlib.sha256("\n".join(item.nodeid for item in items).encode("utf-8")).hexdigest()[:12]
    config._shard_line = (
        f"shard {i} of {n}: kept {len(keep)} of {len(items)} collected, order digest {digest}"
    )
    if drop:
        config.hook.pytest_deselected(items=drop)
    items[:] = keep


def pytest_terminal_summary(terminalreporter, config):
    line = getattr(config, "_shard_line", None)
    if line:
        terminalreporter.write_line(line)
