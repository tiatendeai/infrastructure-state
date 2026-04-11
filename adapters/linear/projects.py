from __future__ import annotations

from typing import Any

from adapters.linear.client import LinearClient, LinearGraphQLError, resolve_team


TEAM_PROJECTS_QUERY = """
query TeamProjects($teamId: String!) {
  team(id: $teamId) {
    id
    key
    name
    projects {
      nodes {
        id
        name
        url
        createdAt
        updatedAt
      }
    }
  }
}
"""

ALL_PROJECTS_QUERY = """
query Projects {
  projects {
    nodes {
      id
      name
      url
      createdAt
      updatedAt
      teams {
        nodes {
          id
          key
          name
        }
      }
    }
  }
}
"""


def list_projects(client: LinearClient, team_ref: str) -> dict[str, Any]:
    team = resolve_team(client, team_ref)
    try:
        payload = client.graphql(TEAM_PROJECTS_QUERY, {"teamId": team["id"]})
        team_payload = payload.get("team") or {}
        projects = team_payload.get("projects", {}).get("nodes", [])
        return {
            "team": {
                "id": team_payload.get("id", team.get("id")),
                "key": team_payload.get("key", team.get("key")),
                "name": team_payload.get("name", team.get("name")),
            },
            "projects": projects,
            "source": "team.projects",
        }
    except LinearGraphQLError:
        payload = client.graphql(ALL_PROJECTS_QUERY)
        projects = payload.get("projects", {}).get("nodes", [])
        filtered = []
        for project in projects:
            teams = project.get("teams", {}).get("nodes", [])
            if any(str(item.get("id", "")) == str(team["id"]) for item in teams):
                filtered.append(project)
        return {
            "team": team,
            "projects": filtered,
            "source": "projects.filtered_by_teams",
        }
