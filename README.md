# Cricket Match Scorer

A terminal-based Python tool for recording cricket matches ball-by-ball, generating detailed scorecards, and producing HTML and Markdown analysis reports for easy sharing and visualization.

Record a live match, output professional scorecards, and get instant stats summaries—all from the command line.

---

## Quick Start

```bash
# Install as a package
pip install -e .

# Run match scorer
python -m scorecard_generator.main

# Manage teams
python -m scorecard_generator.teams_manager
```

---

## What It Does

- **Ball-by-ball match recording** — Enter each run, wicket, and extra interactively
- **Automatic scorecards** — Generates batting and bowling scorecards in professional cricket format
- **Ball-by-ball reports** — CSV exports with complete match data
- **HTML & Markdown reports** — Automatic generation of formatted match summaries and statistics
- **Team management** — Create teams, assign captains/wicketkeepers, select playing XIs

---

## Folder Structure

```
scorecard-generator/
├── scorecard_generator/          # Main package
│   ├── main.py                   # Match scorer entry point
│   ├── game_logic.py             # Ball-by-ball simulation and event processing
│   ├── scorecard.py              # Scorecard formatting and display
│   ├── match_report_html.py      # HTML report generation
│   ├── match_report_md.py        # Markdown report generation
│   ├── match_stats.py            # Stats and analysis
│   ├── scorecard_export.py       # CSV export (Cricsheet format)
│   ├── models.py                 # Data classes (Team, Player, Innings, BallEvent)
│   ├── input_handlers.py         # User input validation
│   ├── team_utils.py             # XI loading utilities
│   ├── teams_manager.py          # Interactive team manager
│   └── exports/                  # Generated match files
├── teams/                        # Team and XI CSV files
├── test/                         # Test suite
└── docs/                         # Documentation
```

## Team CSV Format

Teams are stored as CSV files with columns: `number`, `name`, `role`
- `role` is optional: `c` (captain), `wk` (wicketkeeper), or `c,wk` (both)
- Example: `16,Jos Buttler,c,wk` displays as `Jos Buttler (c)†`

---

## How It Works

1. **Start a match** — Run `main.py`, select teams, choose openers and first bowler
2. **Record ball-by-ball** — Enter runs, wickets, extras, and other events
3. **Generate reports** — Automatic output includes:
   - Console scorecards (batting & bowling)
   - HTML report with match summary and stats
   - Markdown report for documentation
   - CSV export in Cricsheet format for interoperability
4. All outputs saved to `exports/` folder

---

## Example Team CSV

```
number,name,role
16,Jos Buttler,c,wk
18,Virat Kohli,c
7,MS Dhoni,wk
33,Player Name,
```

---

## Legacy

Original monolithic version in `legacy/` folder (not maintained).


