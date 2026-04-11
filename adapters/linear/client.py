from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import base64
import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request


class LinearAdapterError(RuntimeError):
    """Erro base do adapter do Linear."""


class LinearConfigError(LinearAdapterError):
    """Erro de configuração do adapter."""


class LinearAuthenticationError(LinearAdapterError):
    """Erro de autenticação do adapter."""


class LinearApiError(LinearAdapterError):
    """Erro HTTP ou de transporte na API do Linear."""


class LinearGraphQLError(LinearAdapterError):
    """Erro retornado pela GraphQL API do Linear."""

    def __init__(self, errors: list[dict[str, Any]]) -> None:
        self.errors = errors
        message = "; ".join(str(item.get("message", "erro GraphQL desconhecido")) for item in errors)
        super().__init__(message)


@dataclass
class LinearConfig:
    api_url: str = "https://api.linear.app/graphql"
    oauth_token_url: str = "https://api.linear.app/oauth/token"
    timeout_seconds: int = 20
    auth_mode: str = "auto"
    oauth_access_token: str = ""
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_scopes: str = "read,write,comments:create"
    oauth_use_client_credentials: bool = False
    oauth_redirect_uri: str = ""
    personal_api_key: str = ""
    allow_personal_api_key_bootstrap: bool = False
    team_id: str = ""
    team_key: str = ""
    organization_id: str = ""
    workspace_url_key: str = ""

    @classmethod
    def from_env(cls, root: Path | None = None) -> "LinearConfig":
        if root is not None:
            load_dotenv_file(root / ".env")
            load_dotenv_file(root / ".env.local", overwrite=True)

        config = cls(
            api_url=os.getenv("LINEAR_API_URL", cls.api_url),
            oauth_token_url=os.getenv("LINEAR_OAUTH_TOKEN_URL", cls.oauth_token_url),
            timeout_seconds=parse_int(os.getenv("LINEAR_TIMEOUT_SECONDS"), 20),
            auth_mode=os.getenv("LINEAR_AUTH_MODE", "auto").strip() or "auto",
            oauth_access_token=os.getenv("LINEAR_OAUTH_ACCESS_TOKEN", "").strip(),
            oauth_client_id=os.getenv("LINEAR_OAUTH_CLIENT_ID", "").strip(),
            oauth_client_secret=os.getenv("LINEAR_OAUTH_CLIENT_SECRET", "").strip(),
            oauth_scopes=os.getenv("LINEAR_OAUTH_SCOPES", "read,write,comments:create").strip(),
            oauth_use_client_credentials=parse_bool(os.getenv("LINEAR_OAUTH_USE_CLIENT_CREDENTIALS"), False),
            oauth_redirect_uri=os.getenv("LINEAR_OAUTH_REDIRECT_URI", "").strip(),
            personal_api_key=os.getenv("LINEAR_PERSONAL_API_KEY", "").strip(),
            allow_personal_api_key_bootstrap=parse_bool(
                os.getenv("LINEAR_ALLOW_PERSONAL_API_KEY_BOOTSTRAP"), False
            ),
            team_id=os.getenv("LINEAR_TEAM_ID", "").strip(),
            team_key=os.getenv("LINEAR_TEAM_KEY", "").strip(),
            organization_id=os.getenv("LINEAR_ORGANIZATION_ID", "").strip(),
            workspace_url_key=os.getenv("LINEAR_WORKSPACE_URL_KEY", "").strip(),
        )
        config.validate()
        return config

    def validate(self) -> None:
        allowed = {"auto", "oauth_access_token", "oauth_client_credentials", "personal_api_key"}
        if self.auth_mode not in allowed:
            raise LinearConfigError(
                f"LINEAR_AUTH_MODE inválido: {self.auth_mode}. Valores aceitos: {', '.join(sorted(allowed))}"
            )
        if self.timeout_seconds <= 0:
            raise LinearConfigError("LINEAR_TIMEOUT_SECONDS deve ser maior que zero")
        if self.auth_mode == "oauth_access_token" and not self.oauth_access_token:
            raise LinearConfigError(
                "LINEAR_AUTH_MODE=oauth_access_token requer LINEAR_OAUTH_ACCESS_TOKEN configurado"
            )
        if self.auth_mode == "oauth_client_credentials":
            if not self.oauth_client_id or not self.oauth_client_secret:
                raise LinearConfigError(
                    "LINEAR_AUTH_MODE=oauth_client_credentials requer LINEAR_OAUTH_CLIENT_ID e LINEAR_OAUTH_CLIENT_SECRET"
                )
        if self.auth_mode == "personal_api_key" and not self.personal_api_key:
            raise LinearConfigError(
                "LINEAR_AUTH_MODE=personal_api_key requer LINEAR_PERSONAL_API_KEY configurado"
            )

    def default_team_ref(self) -> str:
        if self.team_id:
            return self.team_id
        if self.team_key:
            return self.team_key
        raise LinearConfigError(
            "Nenhum team padrão configurado. Defina LINEAR_TEAM_ID ou LINEAR_TEAM_KEY, ou informe --team na CLI."
        )

    def auth_summary(self) -> dict[str, Any]:
        has_client_credentials = bool(self.oauth_client_id and self.oauth_client_secret)
        return {
            "auth_mode": self.auth_mode,
            "oauth_access_token_configured": bool(self.oauth_access_token),
            "oauth_client_credentials_configured": has_client_credentials,
            "oauth_client_credentials_enabled": self.oauth_use_client_credentials,
            "personal_api_key_configured": bool(self.personal_api_key),
            "personal_api_key_bootstrap_enabled": self.allow_personal_api_key_bootstrap,
            "default_team_id": self.team_id or None,
            "default_team_key": self.team_key or None,
            "organization_id": self.organization_id or None,
            "workspace_url_key": self.workspace_url_key or None,
        }


def parse_bool(raw: str | None, default: bool) -> bool:
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def parse_int(raw: str | None, default: int) -> int:
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise LinearConfigError(f"Valor inteiro inválido: {raw}") from exc


def load_dotenv_file(path: Path, overwrite: bool = False) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or (key in os.environ and not overwrite):
            continue
        os.environ[key] = strip_env_value(value.strip())


def strip_env_value(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"\"", "'"}:
        return raw[1:-1]
    return raw


class LinearClient:
    def __init__(self, config: LinearConfig) -> None:
        self.config = config
        self._cached_oauth_token: str | None = None
        self._cached_oauth_expiry: float = 0.0
        self._ssl_context = build_ssl_context()

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            **self._build_auth_headers(),
        }
        request = urllib.request.Request(self.config.api_url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.config.timeout_seconds,
                context=self._ssl_context,
            ) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise LinearApiError(self._format_http_error(exc.code, raw)) from exc
        except urllib.error.URLError as exc:
            raise LinearApiError(f"Falha de rede ao chamar o Linear: {exc.reason}") from exc

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LinearApiError("Resposta inválida do Linear: JSON malformado") from exc

        if parsed.get("errors"):
            raise LinearGraphQLError(parsed["errors"])
        data = parsed.get("data")
        if not isinstance(data, dict):
            raise LinearApiError("Resposta inválida do Linear: campo 'data' ausente")
        return data

    def _build_auth_headers(self) -> dict[str, str]:
        mode, value = self._resolve_authentication()
        if mode.startswith("oauth"):
            return {"Authorization": f"Bearer {value}"}
        if mode == "personal_api_key":
            return {"Authorization": value}
        raise LinearAuthenticationError(f"Modo de autenticação não suportado: {mode}")

    def _resolve_authentication(self) -> tuple[str, str]:
        mode = self.config.auth_mode
        if mode == "oauth_access_token":
            return (mode, self.config.oauth_access_token)
        if mode == "oauth_client_credentials":
            return (mode, self._get_client_credentials_token())
        if mode == "personal_api_key":
            return (mode, self.config.personal_api_key)

        if self.config.oauth_access_token:
            return ("oauth_access_token", self.config.oauth_access_token)
        if self.config.oauth_use_client_credentials and self.config.oauth_client_id and self.config.oauth_client_secret:
            return ("oauth_client_credentials", self._get_client_credentials_token())
        if self.config.allow_personal_api_key_bootstrap and self.config.personal_api_key:
            return ("personal_api_key", self.config.personal_api_key)
        raise LinearAuthenticationError(
            "Nenhuma credencial ativa do Linear encontrada. Configure LINEAR_OAUTH_ACCESS_TOKEN, ou habilite client credentials, ou permita bootstrap com personal API key."
        )

    def _get_client_credentials_token(self) -> str:
        now = time.time()
        if self._cached_oauth_token and now < self._cached_oauth_expiry:
            return self._cached_oauth_token

        if not self.config.oauth_client_id or not self.config.oauth_client_secret:
            raise LinearAuthenticationError(
                "Client credentials não configuradas. Defina LINEAR_OAUTH_CLIENT_ID e LINEAR_OAUTH_CLIENT_SECRET."
            )

        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "scope": self.config.oauth_scopes,
                "client_id": self.config.oauth_client_id,
                "client_secret": self.config.oauth_client_secret,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.config.oauth_token_url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        basic_token = base64.b64encode(
            f"{self.config.oauth_client_id}:{self.config.oauth_client_secret}".encode("utf-8")
        ).decode("ascii")
        request.add_header("Authorization", f"Basic {basic_token}")

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.config.timeout_seconds,
                context=self._ssl_context,
            ) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise LinearAuthenticationError(
                f"Falha ao obter token OAuth client_credentials: {self._format_http_error(exc.code, raw)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise LinearAuthenticationError(
                f"Falha de rede ao obter token OAuth client_credentials: {exc.reason}"
            ) from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LinearAuthenticationError("Resposta inválida do endpoint OAuth do Linear") from exc

        access_token = str(payload.get("access_token", "")).strip()
        expires_in = int(payload.get("expires_in", 0) or 0)
        if not access_token:
            raise LinearAuthenticationError(
                f"Endpoint OAuth do Linear não retornou access_token. Payload: {json.dumps(payload, ensure_ascii=False)}"
            )

        self._cached_oauth_token = access_token
        self._cached_oauth_expiry = time.time() + max(expires_in - 30, 30)
        return access_token

    @staticmethod
    def _format_http_error(status_code: int, raw_body: str) -> str:
        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError:
            return f"HTTP {status_code}: {raw_body.strip() or 'sem corpo'}"

        if isinstance(parsed, dict):
            if parsed.get("errors"):
                messages = "; ".join(
                    str(item.get("message", "erro desconhecido")) for item in parsed.get("errors", [])
                )
                return f"HTTP {status_code}: {messages}"
            if parsed.get("error_description"):
                return f"HTTP {status_code}: {parsed.get('error_description')}"
            if parsed.get("message"):
                return f"HTTP {status_code}: {parsed.get('message')}"
        return f"HTTP {status_code}: {raw_body.strip() or 'sem corpo'}"


def build_ssl_context() -> ssl.SSLContext:
    bundle_candidates = [
        os.getenv("LINEAR_CA_BUNDLE", "").strip(),
        os.getenv("SSL_CERT_FILE", "").strip(),
        "/etc/ssl/cert.pem",
    ]
    for candidate in bundle_candidates:
        if candidate and Path(candidate).exists():
            return ssl.create_default_context(cafile=candidate)
    return ssl.create_default_context()


LIST_TEAMS_QUERY = """
query Teams {
  teams {
    nodes {
      id
      key
      name
    }
  }
}
"""


def resolve_team(client: LinearClient, team_ref: str) -> dict[str, Any]:
    ref = team_ref.strip()
    if not ref:
        raise LinearConfigError("Referência de team vazia")

    teams = client.graphql(LIST_TEAMS_QUERY).get("teams", {}).get("nodes", [])
    exact_matches: list[dict[str, Any]] = []
    normalized_matches: list[dict[str, Any]] = []
    ref_lower = ref.lower()

    for team in teams:
        team_id = str(team.get("id", ""))
        team_key = str(team.get("key", ""))
        team_name = str(team.get("name", ""))
        if ref in {team_id, team_key, team_name}:
            exact_matches.append(team)
            continue
        if ref_lower in {team_id.lower(), team_key.lower(), team_name.lower()}:
            normalized_matches.append(team)

    if len(exact_matches) == 1:
        return exact_matches[0]
    if len(normalized_matches) == 1:
        return normalized_matches[0]
    if exact_matches or normalized_matches:
        raise LinearConfigError(f"Referência de team ambígua: {ref}")
    raise LinearConfigError(f"Team não encontrado no Linear: {ref}")
