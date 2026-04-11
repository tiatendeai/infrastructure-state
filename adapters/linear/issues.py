from __future__ import annotations

from typing import Any

from adapters.linear.client import LinearClient, LinearConfigError


ISSUE_QUERY = """
query Issue($id: String!) {
  issue(id: $id) {
    id
    identifier
    title
    description
    url
    createdAt
    updatedAt
    team {
      id
      key
      name
    }
    state {
      id
      name
      type
    }
    project {
      id
      name
    }
  }
}
"""

ISSUE_UPDATE_STATE_MUTATION = """
mutation IssueUpdateState($id: String!, $stateId: String!) {
  issueUpdate(
    id: $id
    input: {
      stateId: $stateId
    }
  ) {
    success
    issue {
      id
      identifier
      title
      url
      updatedAt
      state {
        id
        name
        type
      }
    }
  }
}
"""

COMMENT_CREATE_MUTATION = """
mutation CommentCreate($issueId: String!, $body: String!) {
  commentCreate(
    input: {
      issueId: $issueId
      body: $body
    }
  ) {
    success
    comment {
      id
      body
      url
      createdAt
    }
  }
}
"""


def get_issue(client: LinearClient, identifier: str) -> dict[str, Any]:
    ref = identifier.strip()
    if not ref:
        raise LinearConfigError("Identifier da issue é obrigatório")
    issue = client.graphql(ISSUE_QUERY, {"id": ref}).get("issue")
    if not issue:
        raise LinearConfigError(f"Issue não encontrada: {ref}")
    return issue


def update_issue_status(client: LinearClient, identifier: str, state_id: str) -> dict[str, Any]:
    payload = client.graphql(ISSUE_UPDATE_STATE_MUTATION, {"id": identifier.strip(), "stateId": state_id.strip()})
    mutation = payload.get("issueUpdate", {})
    if not mutation.get("success"):
        raise LinearConfigError(f"Linear não confirmou a atualização de status para {identifier}")
    return mutation.get("issue", {})


def add_comment(client: LinearClient, identifier: str, body: str) -> dict[str, Any]:
    text = body.strip()
    if not text:
        raise LinearConfigError("O comentário não pode ser vazio")
    issue = get_issue(client, identifier)
    issue_id = str(issue.get("id", "")).strip()
    if not issue_id:
        raise LinearConfigError(f"Issue {identifier} não retornou UUID")
    payload = client.graphql(COMMENT_CREATE_MUTATION, {"issueId": issue_id, "body": text})
    mutation = payload.get("commentCreate", {})
    if not mutation.get("success"):
        raise LinearConfigError(f"Linear não confirmou a criação do comentário em {identifier}")
    return {
        "issue": {
            "id": issue.get("id"),
            "identifier": issue.get("identifier"),
            "title": issue.get("title"),
            "url": issue.get("url"),
        },
        "comment": mutation.get("comment", {}),
    }
