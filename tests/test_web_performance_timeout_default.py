from __future__ import annotations

import unittest

from searchgeo import cli
from searchgeo.m21_web_performance import WebPerformanceConfig
from searchgeo.provider_runtime_policy import DEFAULT_WEB_PERFORMANCE_TIMEOUT_SECONDS


class WebPerformanceTimeoutDefaultTests(unittest.TestCase):
    def test_all_runtime_defaults_are_120_seconds(self) -> None:
        self.assertEqual(DEFAULT_WEB_PERFORMANCE_TIMEOUT_SECONDS, 120.0)
        self.assertEqual(cli._DEFAULT_WEB_PERFORMANCE_TIMEOUT_SECONDS, 120.0)
        self.assertEqual(WebPerformanceConfig().timeout_seconds, 120.0)


if __name__ == "__main__":
    unittest.main()
