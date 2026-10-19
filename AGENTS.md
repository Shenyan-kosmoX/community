# Community maintenance

This repository hosts public community collaboration, not private company strategy.

- Keep claims grounded. Do not invent projects, members, research outcomes, grants, or independent reviews.
- `community.json` is the identity and routing configuration; `content/` contains homepage sources. Run `python tools/build.py --profile ../Shenyan-kosmoX-profile` after changing them.
- Keep project scientific work in its own repository. A discussion becomes an issue only when there is concrete work; link instead of duplicating status.
- Resource applications are closed until actual allocation and private delivery arrangements are configured and announced. Never put credentials or private research in an issue.
- Passing CI is limited to the checks executed. It does not certify scientific correctness.
- Run `python tools/check.py --profile ../Shenyan-kosmoX-profile` and `python -m unittest discover -s tests -v` before handing off changes.
- Respect the user's authorization for remote publishing and settings; do not publish internal planning files from neighboring directories. Never expand access or send messages outside the authorized task.
- Respect the separate terms for code, original prose and artwork in `LICENSING.md`.
