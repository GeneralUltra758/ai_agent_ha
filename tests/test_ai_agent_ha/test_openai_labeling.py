"""Tests for OpenAI Platform API Key branding in config flow and translations."""

import json
import os

import pytest

COMPONENT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "custom_components", "ai_agent_ha"
    )
)

OPENAI_LABEL = "OpenAI Platform API Key"


def _load_json(path):
    with open(path) as f:
        return json.load(f)


class TestOpenAILabeling:
    """Verify unambiguous OpenAI credential naming and billing help text."""

    def test_config_flow_token_label(self):
        """TOKEN_LABELS must use the unambiguous OpenAI Platform API Key label."""
        config_flow_path = os.path.join(COMPONENT_DIR, "config_flow.py")
        with open(config_flow_path) as f:
            source = f.read()
        assert f'"openai": "{OPENAI_LABEL}"' in source

    def test_config_flow_keeps_openai_token_key(self):
        """The config entry key must remain openai_token for compatibility."""
        config_flow_path = os.path.join(COMPONENT_DIR, "config_flow.py")
        with open(config_flow_path) as f:
            source = f.read()
        assert '"openai": "openai_token"' in source

    def test_strings_and_en_label(self):
        """strings.json and en.json expose the new label in config and options."""
        for rel in ("strings.json", os.path.join("translations", "en.json")):
            data = _load_json(os.path.join(COMPONENT_DIR, rel))
            for section in ("config", "options"):
                for step in data[section]["step"].values():
                    labels = step.get("data", {})
                    if "openai_token" in labels:
                        assert labels["openai_token"] == OPENAI_LABEL

    def test_english_help_text_mentions_billing_separation(self):
        """English help text must explain API billing vs ChatGPT subscriptions."""
        for rel in ("strings.json", os.path.join("translations", "en.json")):
            data = _load_json(os.path.join(COMPONENT_DIR, rel))
            found = False
            for section in ("config", "options"):
                for step in data[section]["step"].values():
                    desc = step.get("data_description", {}).get("openai_token")
                    if desc:
                        found = True
                        assert "OpenAI Platform" in desc
                        assert "ChatGPT" in desc
                        assert "separate" in desc
            assert found, f"openai_token data_description missing in {rel}"

    @pytest.mark.parametrize("lang", ["en", "de", "es", "ca"])
    def test_translation_schema_matches_strings(self, lang):
        """Every translation must expose the same openai_token keys as strings.json."""
        strings = _load_json(os.path.join(COMPONENT_DIR, "strings.json"))
        translation = _load_json(
            os.path.join(COMPONENT_DIR, "translations", f"{lang}.json")
        )
        for section in ("config", "options"):
            for step_id, step in strings[section]["step"].items():
                for group in ("data", "data_description"):
                    keys = set(step.get(group, {}))
                    if "openai_token" not in keys:
                        continue
                    t_step = translation[section]["step"][step_id]
                    t_keys = set(t_step.get(group, {}))
                    assert "openai_token" in t_keys, (
                        f"{lang}.json missing openai_token in "
                        f"{section}.{step_id}.{group}"
                    )
                    label = t_step["data"]["openai_token"]
                    assert label, "openai_token label must not be empty"
                    assert "OpenAI" in label

    def test_no_oauth_or_device_auth_claims(self):
        """Translations must not advertise OAuth/device/subscription auth."""
        for fname in os.listdir(os.path.join(COMPONENT_DIR, "translations")):
            if not fname.endswith(".json"):
                continue
            data = _load_json(
                os.path.join(COMPONENT_DIR, "translations", fname)
            )
            blob = json.dumps(data).lower()
            assert "device code" not in blob
            assert "oauth" not in blob
            assert "sign in with" not in blob
