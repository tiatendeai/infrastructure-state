from __future__ import annotations

from typing import Any

from adapters.linear.client import LinearClient, LinearConfigError, resolve_team


TEAM_STATES_QUERY = """
query TeamStates($teamId: String!) {
  team(id: $teamId) {
    id
    key
    name
    states {
      nodes {
        id
        name
        type
        position
      }
    }
  }
}
"""


def list_statuses(client: LinearClient, team_ref: str) -> dict[str, Any]:
    team = resolve_team(client, team_ref)
    payload = client.graphql(TEAM_STATES_QUERY, {"teamId": team["id"]})
    team_payload = payload.get("team") or {}
    states = team_payload.get("states", {}).get("nodes", [])
    states = sorted(states, key=lambda item: (int(item.get("position") or 0), str(item.get("name") or "")))
    return {
        "team": {
            "id": team_payload.get("id", team.get("id")),
            "key": team_payload.get("key", team.get("key")),
            "name": team_payload.get("name", team.get("name")),
        },
        "states": states,
    }


def find_status_by_name(client: LinearClient, team_ref: str, status_name: str) -> dict[str, Any]:
    normalized = status_name.strip().lower()
    if not normalized:
        raise LinearConfigError("Nome do status é obrigatório")

    payload = list_statuses(client, team_ref)
    matches = [item for item in payload["states"] if str(item.get("name", "")).strip().lower() == normalized]
    if not matches:
        raise LinearConfigError(
            f"Status '{status_name}' não encontrado no team {payload['team'].get('key') or payload['team'].get('id')}"
        )
    if len(matches) > 1:
        raise LinearConfigError(f"Status ambíguo no Linear: {status_name}")
    return matches[0]
