from pathlib import Path

root = Path('.')

# 1) Explicit providers must quarantine after a qualifying provider failure so
# they are not called again for later URLs in the same audit. No cross-provider
# fallback is introduced for SINGLE_PROVIDER mode.
p = root / 'src/searchgeo/m18_ai.py'
s = p.read_text(encoding='utf-8')

old = '''        self._history: list[ProviderAttempt] = []\n        self.policy = _policy(self.name, self.model)\n'''
new = '''        self._history: list[ProviderAttempt] = []\n        self.policy = _policy(self.name, self.model)\n        self._runtime_state = RuntimeProviderState.ACTIVE\n        self._successful_urls: set[str] = set()\n'''
if old in s and 'self._runtime_state = RuntimeProviderState.ACTIVE' not in s:
    s = s.replace(old, new, 1)

old = '''    def analyze(self, semantic_input: SemanticInput) -> SemanticProviderResult:\n        self._last_attempt = None\n        if not self.api_key:\n'''
new = '''    def analyze(self, semantic_input: SemanticInput) -> SemanticProviderResult:\n        self._last_attempt = None\n        if self._runtime_state is RuntimeProviderState.QUARANTINED_FOR_AUDIT:\n            return SemanticProviderResult(\n                ProviderState.UNAVAILABLE,\n                reason="AI_PROVIDER_UNAVAILABLE:PROVIDER_QUARANTINED",\n                provider=self.name,\n                model=self.model,\n                reasoning_profile=self.reasoning_profile,\n                diagnostic=ProviderDiagnostic(ProviderErrorClass.UNKNOWN_PROVIDER_ERROR, error_code="PROVIDER_QUARANTINED"),\n            )\n        if not self.api_key:\n'''
if old in s and 'AI_PROVIDER_UNAVAILABLE:PROVIDER_QUARANTINED' not in s:
    s = s.replace(old, new, 1)

old = '''        self._history.append(self._last_attempt)\n        return SemanticProviderResult(\n            ProviderState.AVAILABLE,\n'''
new = '''        self._runtime_state = RuntimeProviderState.ACTIVE\n        self._successful_urls.add(semantic_input.page_url)\n        self._history.append(self._last_attempt)\n        return SemanticProviderResult(\n            ProviderState.AVAILABLE,\n'''
if old in s and 'self._successful_urls.add(semantic_input.page_url)' not in s:
    s = s.replace(old, new, 1)

old = '''        self._history.append(self._last_attempt)\n        return SemanticProviderResult(\n            ProviderState.UNAVAILABLE,\n'''
new = '''        self._runtime_state = RuntimeProviderState.QUARANTINED_FOR_AUDIT\n        self._history.append(self._last_attempt)\n        return SemanticProviderResult(\n            ProviderState.UNAVAILABLE,\n'''
if old in s and 'self._runtime_state = RuntimeProviderState.QUARANTINED_FOR_AUDIT\n        self._history.append(self._last_attempt)' not in s:
    s = s.replace(old, new, 1)

old = '''    def attempt_history(self) -> tuple[ProviderAttempt, ...]:\n        return tuple(self._history)\n\n\nclass OpenAIProvider(ResponsesSemanticProvider):\n'''
new = '''    def attempt_history(self) -> tuple[ProviderAttempt, ...]:\n        return tuple(self._history)\n\n    def session_snapshot(self) -> dict[str, Any]:\n        successful = bool(self._successful_urls)\n        return {\n            "strategy": "SINGLE_PROVIDER",\n            "enabled": True,\n            "initial_provider": self.name,\n            "initial_model": self.model,\n            "initial_reasoning_profile": self.reasoning_profile,\n            "effective_provider": self.name if successful else None,\n            "effective_model": self.model if successful else None,\n            "effective_reasoning_profile": self.reasoning_profile if successful else None,\n            "configured_chain": [{\n                "provider": self.name,\n                "model": self.model,\n                "reasoning_profile": self.reasoning_profile,\n                "rank": self.policy.rank,\n                "qualification": self.policy.qualification,\n            }],\n            "provider_states": {self.name: self._runtime_state.value},\n            "successful_urls": {self.name: len(self._successful_urls)},\n            "excluded_configurations": [],\n        }\n\n\nclass OpenAIProvider(ResponsesSemanticProvider):\n'''
if old in s and 'def session_snapshot(self) -> dict[str, Any]:' not in s.split('class OpenAIProvider', 1)[0]:
    s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')

# 2) Add directed explicit-quarantine and end-to-end persistence/report tests.
p = root / 'tests/test_m18_multi_ai_provider.py'
s = p.read_text(encoding='utf-8')
if 'import sqlite3\n' not in s:
    s = s.replace('import json\n', 'import json\nimport sqlite3\n', 1)
if 'from pathlib import Path\n' not in s:
    s = s.replace('from email.message import Message\n', 'from email.message import Message\nfrom pathlib import Path\n', 1)
if 'from tempfile import TemporaryDirectory\n' not in s:
    s = s.replace('import unittest\n', 'from tempfile import TemporaryDirectory\nimport unittest\n', 1)
if 'from searchgeo.acquisition import HttpClient\n' not in s:
    s = s.replace('from searchgeo.m18_ai import (\n', 'from searchgeo.acquisition import HttpClient\nfrom searchgeo.audit_runner import run_audit\nfrom searchgeo.discovery import DiscoveryEngine\nfrom searchgeo.m18_ai import (\n', 1)
if 'from tests.test_m12_stable_baseline import _FixtureRenderer, _server\n' not in s:
    s = s.replace('from searchgeo.semantic import SemanticEvidenceInput, SemanticInput\n', 'from searchgeo.semantic import SemanticEvidenceInput, SemanticInput\nfrom tests.test_m12_stable_baseline import _FixtureRenderer, _server\n', 1)

marker = '''\n\nif __name__ == "__main__":\n    unittest.main()\n'''
methods = r'''

    def test_explicit_provider_quarantine_blocks_retries_across_urls(self) -> None:
        calls = 0

        def fail(*_):
            nonlocal calls
            calls += 1
            raise TimeoutError()

        provider = OpenAIProvider(api_key="x", transport=fail)
        first = provider.analyze(_input("https://example.com/a", "SNP-A"))
        second = provider.analyze(_input("https://example.com/b", "SNP-B"))

        self.assertEqual(first.state, ProviderState.UNAVAILABLE)
        self.assertEqual(second.state, ProviderState.UNAVAILABLE)
        self.assertEqual(second.reason, "AI_PROVIDER_UNAVAILABLE:PROVIDER_QUARANTINED")
        self.assertEqual(calls, 1)
        snapshot = provider.session_snapshot()
        self.assertEqual(snapshot["strategy"], "SINGLE_PROVIDER")
        self.assertEqual(snapshot["provider_states"]["OPENAI"], "QUARANTINED_FOR_AUDIT")
        self.assertEqual(len(provider.attempt_history()), 1)

    def test_run_audit_persists_attempts_and_enriches_both_reports(self) -> None:
        with _server() as origin, TemporaryDirectory() as directory:
            html = f"""<!doctype html><html lang='pt-BR'><head><title>Guia M18</title>
<meta name='description' content='Guia técnico.'><link rel='canonical' href='{origin}/'>
<script type='application/ld+json'>{{"@context":"https://schema.org","@type":"Article","headline":"Guia M18"}}</script>
</head><body><main><h1>Guia M18</h1><h2>Visão geral</h2><p>Conteúdo técnico verificável para integração M18.</p></main></body></html>"""
            secret = "M18-INTEGRATION-SECRET"
            provider = OpenAIProvider(api_key=secret, transport=_success_transport())
            result = run_audit(
                f"{origin}/",
                audits_root=Path(directory),
                project_name="Integração M18",
                max_pages=1,
                semantic_provider=provider,
                discovery_engine=DiscoveryEngine(HttpClient(timeout=1)),
                renderer=_FixtureRenderer(html),
                lazy_probe=lambda url, device: None,
            )

            connection = sqlite3.connect(result.audit_root / "audit.db")
            connection.row_factory = sqlite3.Row
            try:
                attempts = connection.execute(
                    "SELECT provider,model,status,input_tokens,output_tokens,estimated_cost FROM ai_provider_attempts WHERE audit_id=? ORDER BY started_at",
                    (result.audit_id,),
                ).fetchall()
                self.assertEqual(len(attempts), 2)
                self.assertTrue(all(row["provider"] == "OPENAI" for row in attempts))
                self.assertTrue(all(row["model"] == "gpt-5.6-terra" for row in attempts))
                self.assertTrue(all(row["status"] == "SUCCESS" for row in attempts))
                self.assertTrue(all(row["input_tokens"] == 100 for row in attempts))
                self.assertTrue(all(row["output_tokens"] == 50 for row in attempts))
                self.assertTrue(all(row["estimated_cost"] is not None for row in attempts))
                session = connection.execute(
                    "SELECT strategy,effective_provider,effective_model,status FROM ai_audit_sessions WHERE audit_id=?",
                    (result.audit_id,),
                ).fetchone()
                self.assertIsNotNone(session)
                self.assertEqual(session["strategy"], "SINGLE_PROVIDER")
                self.assertEqual(session["effective_provider"], "OPENAI")
                self.assertEqual(session["effective_model"], "gpt-5.6-terra")
            finally:
                connection.close()

            report = result.report_path.read_text(encoding="utf-8")
            remediation = (result.audit_root / "remediation.html").read_text(encoding="utf-8")
            self.assertIn("Uso de IA — execução e telemetria", report)
            self.assertIn("ESTIMATED_COST", report)
            self.assertIn("OPENAI", report)
            self.assertIn("gpt-5.6-terra", report)
            self.assertIn("Contexto da análise semântica", remediation)
            self.assertIn("Este bloco é informativo", remediation)
            self.assertNotIn(secret, report)
            self.assertNotIn(secret, remediation)
'''
if 'test_explicit_provider_quarantine_blocks_retries_across_urls' not in s:
    s = s.replace(marker, methods + marker, 1)

p.write_text(s, encoding='utf-8')
