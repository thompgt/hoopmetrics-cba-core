"""Small illustrative dataset backing the Player Evaluator's name/season
autofill so a user only has to pick a name, a season, and a cap-space
figure -- not type in raw box-score/advanced stats by hand.

These are approximate, publicly reported per-game averages for a handful
of well-known players/seasons, included for demonstration purposes. This
is not a live stats feed -- swap PLAYERS for a real data source (a stats
API client, a CSV export, etc.) to back this with guaranteed-accurate,
continuously updated figures.

games_played is that season's own total, reused across all three trailing
injury-history slots (games_played_last_3) as a simplification, since a
full three-season game log isn't tracked here.
"""

PLAYERS = {
    "Nikola Jokic": {
        "2023-24": dict(team="DEN", age=29, years_of_service=8, all_nba_honors=True,
                         games_played=79, minutes_per_game=34.6,
                         pts=26.4, reb=12.4, ast=9.0, stl=1.3, blk=0.9),
    },
    "Giannis Antetokounmpo": {
        "2023-24": dict(team="MIL", age=29, years_of_service=10, all_nba_honors=True,
                         games_played=73, minutes_per_game=35.2,
                         pts=30.4, reb=11.5, ast=6.5, stl=1.2, blk=1.1),
    },
    "Luka Doncic": {
        "2023-24": dict(team="DAL", age=24, years_of_service=5, all_nba_honors=True,
                         games_played=70, minutes_per_game=37.5,
                         pts=33.9, reb=9.2, ast=9.8, stl=1.4, blk=0.5),
    },
    "Shai Gilgeous-Alexander": {
        "2023-24": dict(team="OKC", age=25, years_of_service=5, all_nba_honors=True,
                         games_played=75, minutes_per_game=34.0,
                         pts=30.1, reb=5.5, ast=6.2, stl=2.0, blk=0.9),
    },
    "Jayson Tatum": {
        "2023-24": dict(team="BOS", age=25, years_of_service=6, all_nba_honors=True,
                         games_played=74, minutes_per_game=35.7,
                         pts=26.9, reb=8.1, ast=4.9, stl=1.0, blk=0.6),
    },
    "Stephen Curry": {
        "2023-24": dict(team="GSW", age=35, years_of_service=14, all_nba_honors=True,
                         games_played=74, minutes_per_game=32.7,
                         pts=26.4, reb=4.5, ast=5.1, stl=0.7, blk=0.4),
    },
    "Kevin Durant": {
        "2023-24": dict(team="PHX", age=35, years_of_service=16, all_nba_honors=True,
                         games_played=75, minutes_per_game=37.2,
                         pts=27.1, reb=6.6, ast=5.0, stl=0.9, blk=1.2),
    },
    "Joel Embiid": {
        "2023-24": dict(team="PHI", age=29, years_of_service=7, all_nba_honors=True,
                         games_played=39, minutes_per_game=33.6,
                         pts=34.7, reb=11.0, ast=5.6, stl=1.2, blk=1.5),
    },
    "Anthony Edwards": {
        "2023-24": dict(team="MIN", age=22, years_of_service=3, all_nba_honors=True,
                         games_played=79, minutes_per_game=35.1,
                         pts=25.9, reb=5.4, ast=5.1, stl=1.3, blk=0.5),
    },
    "Devin Booker": {
        "2023-24": dict(team="PHX", age=27, years_of_service=8, all_nba_honors=False,
                         games_played=68, minutes_per_game=35.7,
                         pts=27.1, reb=4.5, ast=6.9, stl=0.9, blk=0.4),
    },
    "Damian Lillard": {
        "2023-24": dict(team="MIL", age=33, years_of_service=11, all_nba_honors=False,
                         games_played=73, minutes_per_game=35.3,
                         pts=24.3, reb=4.4, ast=7.0, stl=1.0, blk=0.3),
    },
    "Victor Wembanyama": {
        "2023-24": dict(team="SAS", age=20, years_of_service=0, all_nba_honors=False,
                         games_played=71, minutes_per_game=29.7,
                         pts=21.4, reb=10.6, ast=3.9, stl=1.2, blk=3.6),
    },
}

# Publicly reported league salary cap for each season, used to compute a
# player's max-salary bracket via cba.salary_caps.calculate_max_salary
# instead of asking the user to type a raw cap_hit dollar amount.
CAP_FIGURES = {
    "2022-23": 123_655_000,
    "2023-24": 136_021_000,
    "2024-25": 140_588_000,
}
