# Contribution Bot

A tiny GitHub Actions bot that gets **12 opportunities per UTC day** to make
at most one commit per two-hour slot.

For each UTC date, the bot deterministically chooses a daily target from
**0 through 12 inclusive**, then selects exactly that many of the day's
12 two-hour slots. When a selected slot runs, it appends one meaningless
line to `data/activity.log` and commits the change.

## Behavior

- Runs every 2 hours via GitHub Actions.
- Maximum: 12 commits/day.
- Minimum: 0 commits/day.
- Daily target is uniformly selected from 0..12.
- Each selected two-hour slot creates at most one commit.
- Re-running the same slot will not create a duplicate entry.
- No external server or cloud service is required.

## Files

```text
.
├── .github/
│   └── workflows/
│       └── contribute.yml
├── bot/
│   └── contribute.py
├── data/
│   └── activity.log
├── .gitignore
└── README.md
```

## Setup

1. Copy these files into the default branch of your repository.
2. Push them to GitHub.
3. Open **Settings → Actions → General**.
4. Under **Workflow permissions**, make sure the workflow can write repository
   contents. The workflow itself requests `contents: write`.
5. Open the **Actions** tab and manually run **Contribution Bot** once to test it.

Scheduled workflows run from the repository's default branch.

## Schedule

The workflow currently uses:

```yaml
- cron: "17 */2 * * *"
```

GitHub cron schedules use UTC. This runs at minute 17 of every even UTC hour.

The unusual minute is intentional: scheduled Actions can be delayed during
heavily loaded times, especially around the top of the hour.

## Important GitHub contribution-chart details

For commits to appear on a GitHub profile's contribution graph, GitHub's
contribution-counting rules still apply. In particular, the commit email,
repository visibility/settings, branch, and account association can matter.

If commits made as `github-actions[bot]` do not appear on the profile you want,
replace the two `git config` lines in the workflow with your own GitHub-linked
commit name and noreply email.

Example:

```bash
git config user.name "YOUR_GITHUB_NAME"
git config user.email "YOUR_GITHUB_NOREPLY_EMAIL"
```

Do not put a private email address in the workflow unless you are comfortable
exposing it in Git commit metadata.
