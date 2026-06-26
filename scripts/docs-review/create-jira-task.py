#!/usr/bin/env python3
"""Read a JSON batch from stdin and create one Jira task per doc, assigned round-robin."""

import argparse
import json
import os
import sys

from jira import JIRA


JIRA_URL = os.environ.get("JIRA_URL", "https://jira-jppol.atlassian.net")
JIRA_PROJECT = os.environ.get("JIRA_PROJECT", "IDP")


def build_description(doc: dict) -> str:
    return "\n".join([
        f"[{doc['title']}|{doc['url']}] is overdue for review.",
        "",
        f"* Last reviewed: {doc['last_reviewed_on']}",
        f"* Overdue by: {doc['days_overdue']} days",
        "",
        "_To close this: update last_reviewed_on in the page frontmatter._",
    ])


def resolve_account_ids(client: JIRA, emails: list) -> list:
    ids = []
    for email in emails:
        users = client.search_users(query=email)
        if not users:
            sys.exit(f"Error: no Jira user found for '{email}'")
        ids.append(users[0].accountId)
    return ids


def assignees_with_open_task(client: JIRA, account_ids: list) -> set:
    ids_csv = ", ".join(f'"{aid}"' for aid in account_ids)
    jql = (
        f'project = "{JIRA_PROJECT}" AND labels = "Docs" '
        f'AND assignee in ({ids_csv}) AND status = "To Do"'
    )
    resp = client._session.post(
        f"{JIRA_URL}/rest/api/3/search/jql",
        json={"jql": jql, "maxResults": 50, "fields": ["assignee", "summary"]},
    )
    resp.raise_for_status()
    return {
        issue["fields"]["assignee"]["accountId"]
        for issue in resp.json().get("issues", [])
        if issue["fields"]["summary"].startswith("Review docs:")
    }


def find_active_sprint_id(client: JIRA) -> "int | None":
    boards = client.boards(projectKeyOrID=JIRA_PROJECT)
    if not boards:
        print(f"Warning: no board found for project '{JIRA_PROJECT}', skipping sprint assignment", file=sys.stderr)
        return None
    sprints = client.sprints(boards[0].id, state="active")
    if not sprints:
        print("Warning: no active sprint found, skipping sprint assignment", file=sys.stderr)
        return None
    return sprints[0].id


def _write_results(path: "str | None", dry_run: bool, results: list) -> None:
    if not path:
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"dry_run": dry_run, "results": results}, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Create one Jira task per doc from a JSON batch, assigned round-robin."
    )
    parser.add_argument("batch_file", help="Path to the JSON batch file produced by check-review-dates.py")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print tasks without creating them")
    parser.add_argument("--results-file", metavar="FILE",
                        help="Write a JSON summary of actions taken to this file")
    args = parser.parse_args()

    with open(args.batch_file, encoding="utf-8") as f:
        data = json.load(f)
    batch = data.get("batch", [])

    if not batch:
        print("Batch is empty — nothing to create.")
        return

    raw_assignees = os.environ.get("JIRA_ASSIGNEES", "")
    assignee_emails = [e.strip() for e in raw_assignees.split(",") if e.strip()]
    if not assignee_emails:
        sys.exit("Error: JIRA_ASSIGNEES must be set (comma-separated list of emails)")

    results = []

    if args.dry_run:
        print("\n### Tasks (dry run)")
        for i, doc in enumerate(batch):
            assignee = assignee_emails[i % len(assignee_emails)]
            print(f"- [{doc['title']}]({doc['url']}) would be assigned to {assignee}")
            results.append({"title": doc["title"], "url": doc["url"], "assignee": assignee, "status": "would_create"})
        _write_results(args.results_file, args.dry_run, results)
        return

    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_TOKEN")
    if not email or not token:
        sys.exit("Error: JIRA_EMAIL and JIRA_TOKEN environment variables must be set.")

    client = JIRA(server=JIRA_URL, basic_auth=(email, token))
    assignee_ids = resolve_account_ids(client, assignee_emails)
    sprint_id = find_active_sprint_id(client)
    busy_ids = assignees_with_open_task(client, assignee_ids)

    print("\n### Tasks")
    for i, doc in enumerate(batch):
        assignee_id = assignee_ids[i % len(assignee_ids)]
        assignee_email = assignee_emails[i % len(assignee_emails)]

        if assignee_id in busy_ids:
            print(f"- Skipped [{doc['title']}]({doc['url']}) — {assignee_email} already has an open review task")
            results.append({"title": doc["title"], "url": doc["url"], "assignee": assignee_email, "status": "skipped_busy"})
            continue

        summary = f"Review docs: {doc['title']}"
        jql = f'project = "{JIRA_PROJECT}" AND summary = "{summary}" AND statusCategory != Done'
        resp = client._session.post(
            f"{JIRA_URL}/rest/api/3/search/jql",
            json={"jql": jql, "maxResults": 1, "fields": ["summary"]},
        )
        resp.raise_for_status()
        existing = resp.json().get("issues", [])
        if existing:
            print(f"- Skipped [{doc['title']}]({doc['url']}) — {existing[0]['key']} already open")
            results.append({"title": doc["title"], "url": doc["url"], "assignee": assignee_email, "status": "skipped_duplicate", "existing_key": existing[0]["key"]})
            continue

        issue = client.create_issue(fields={
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "issuetype": {"name": "Task"},
            "description": build_description(doc),
            "assignee": {"accountId": assignee_id},
            "labels": ["Docs"],
        })
        if sprint_id:
            client.add_issues_to_sprint(sprint_id, [issue.key])
        print(f"- Created [{issue.key}]({JIRA_URL}/browse/{issue.key}) [{doc['title']}]({doc['url']}) assigned to {assignee_email}")
        results.append({"title": doc["title"], "url": doc["url"], "assignee": assignee_email, "status": "created", "jira_key": issue.key})

    _write_results(args.results_file, args.dry_run, results)


if __name__ == "__main__":
    main()
