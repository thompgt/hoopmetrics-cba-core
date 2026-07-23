"""Small illustrative dataset backing the Player Evaluator's name/season
autofill so a user only has to pick a name, a season, and a cap-space
figure -- not type in raw box-score/advanced stats by hand.

These are approximate, publicly reported per-game averages for a broader
set of well-known players/seasons, included for demonstration purposes.
This is not a live stats feed -- swap PLAYERS for a real data source (a
stats API client, a CSV export, etc.) to back this with guaranteed-accurate,
continuously updated figures.

games_played is that season's own total, reused across all three trailing
injury-history slots (games_played_last_3) as a simplification, since a
full three-season game log isn't tracked here.
"""

PLAYERS = {
    "Nikola Jokic": {
        "2022-23": dict(team="DEN", age=28, years_of_service=7, all_nba_honors=True,
                         games_played=69, minutes_per_game=33.7,
                         pts=24.5, reb=11.8, ast=9.8, stl=1.3, blk=0.7),
        "2023-24": dict(team="DEN", age=29, years_of_service=8, all_nba_honors=True,
                         games_played=79, minutes_per_game=34.6,
                         pts=26.4, reb=12.4, ast=9.0, stl=1.3, blk=0.9),
        "2024-25": dict(team="DEN", age=30, years_of_service=9, all_nba_honors=True,
                         games_played=70, minutes_per_game=36.7,
                         pts=29.6, reb=12.7, ast=10.2, stl=1.8, blk=0.6),
    },
    "Giannis Antetokounmpo": {
        "2022-23": dict(team="MIL", age=28, years_of_service=9, all_nba_honors=True,
                         games_played=63, minutes_per_game=32.1,
                         pts=31.1, reb=11.8, ast=5.7, stl=0.8, blk=0.8),
        "2023-24": dict(team="MIL", age=29, years_of_service=10, all_nba_honors=True,
                         games_played=73, minutes_per_game=35.2,
                         pts=30.4, reb=11.5, ast=6.5, stl=1.2, blk=1.1),
        "2024-25": dict(team="MIL", age=30, years_of_service=11, all_nba_honors=True,
                         games_played=67, minutes_per_game=34.6,
                         pts=30.4, reb=11.9, ast=6.5, stl=0.9, blk=1.2),
    },
    "Luka Doncic": {
        "2022-23": dict(team="DAL", age=23, years_of_service=4, all_nba_honors=True,
                         games_played=66, minutes_per_game=36.2,
                         pts=32.4, reb=8.6, ast=8.0, stl=1.4, blk=0.5),
        "2023-24": dict(team="DAL", age=24, years_of_service=5, all_nba_honors=True,
                         games_played=70, minutes_per_game=37.5,
                         pts=33.9, reb=9.2, ast=9.8, stl=1.4, blk=0.5),
    },
    "Shai Gilgeous-Alexander": {
        "2022-23": dict(team="OKC", age=24, years_of_service=4, all_nba_honors=True,
                         games_played=68, minutes_per_game=35.5,
                         pts=31.4, reb=4.8, ast=5.5, stl=1.6, blk=0.9),
        "2023-24": dict(team="OKC", age=25, years_of_service=5, all_nba_honors=True,
                         games_played=75, minutes_per_game=34.0,
                         pts=30.1, reb=5.5, ast=6.2, stl=2.0, blk=0.9),
        "2024-25": dict(team="OKC", age=26, years_of_service=6, all_nba_honors=True,
                         games_played=76, minutes_per_game=34.2,
                         pts=32.7, reb=5.0, ast=6.4, stl=1.7, blk=1.0),
    },
    "Jayson Tatum": {
        "2022-23": dict(team="BOS", age=24, years_of_service=5, all_nba_honors=True,
                         games_played=74, minutes_per_game=36.9,
                         pts=30.1, reb=8.8, ast=4.6, stl=1.1, blk=0.7),
        "2023-24": dict(team="BOS", age=25, years_of_service=6, all_nba_honors=True,
                         games_played=74, minutes_per_game=35.7,
                         pts=26.9, reb=8.1, ast=4.9, stl=1.0, blk=0.6),
    },
    "Stephen Curry": {
        "2022-23": dict(team="GSW", age=34, years_of_service=13, all_nba_honors=False,
                         games_played=56, minutes_per_game=34.7,
                         pts=29.4, reb=6.1, ast=6.3, stl=0.9, blk=0.4),
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
        "2022-23": dict(team="PHI", age=28, years_of_service=6, all_nba_honors=True,
                         games_played=66, minutes_per_game=34.6,
                         pts=33.1, reb=10.2, ast=4.2, stl=1.0, blk=1.7),
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
    "LeBron James": {
        "2023-24": dict(team="LAL", age=39, years_of_service=21, all_nba_honors=True,
                         games_played=71, minutes_per_game=35.3,
                         pts=25.7, reb=7.3, ast=8.3, stl=1.3, blk=0.5),
    },
    "Kawhi Leonard": {
        "2023-24": dict(team="LAC", age=32, years_of_service=12, all_nba_honors=True,
                         games_played=68, minutes_per_game=34.3,
                         pts=23.7, reb=6.1, ast=3.6, stl=1.6, blk=0.9),
    },
    "Paul George": {
        "2023-24": dict(team="LAC", age=33, years_of_service=13, all_nba_honors=False,
                         games_played=74, minutes_per_game=33.9,
                         pts=22.6, reb=5.2, ast=3.5, stl=1.5, blk=0.4),
    },
    "Jimmy Butler": {
        "2023-24": dict(team="MIA", age=34, years_of_service=12, all_nba_honors=False,
                         games_played=60, minutes_per_game=33.9,
                         pts=20.8, reb=5.3, ast=5.0, stl=1.3, blk=0.4),
    },
    "Domantas Sabonis": {
        "2023-24": dict(team="SAC", age=27, years_of_service=7, all_nba_honors=True,
                         games_played=82, minutes_per_game=35.7,
                         pts=19.4, reb=13.7, ast=8.2, stl=0.9, blk=0.5),
    },
    "Trae Young": {
        "2023-24": dict(team="ATL", age=25, years_of_service=5, all_nba_honors=False,
                         games_played=54, minutes_per_game=35.5,
                         pts=25.7, reb=2.8, ast=10.8, stl=1.3, blk=0.1),
    },
    "Tyrese Haliburton": {
        "2023-24": dict(team="IND", age=23, years_of_service=3, all_nba_honors=True,
                         games_played=69, minutes_per_game=32.4,
                         pts=20.1, reb=3.9, ast=10.9, stl=1.2, blk=0.7),
    },
    "James Harden": {
        "2023-24": dict(team="LAC", age=34, years_of_service=14, all_nba_honors=False,
                         games_played=72, minutes_per_game=34.2,
                         pts=16.6, reb=4.5, ast=8.5, stl=1.1, blk=0.6),
    },
    "Chris Paul": {
        "2023-24": dict(team="GSW", age=38, years_of_service=18, all_nba_honors=False,
                         games_played=58, minutes_per_game=26.4,
                         pts=9.2, reb=3.9, ast=6.8, stl=1.7, blk=0.2),
    },
    "De'Aaron Fox": {
        "2023-24": dict(team="SAC", age=25, years_of_service=6, all_nba_honors=True,
                         games_played=74, minutes_per_game=34.2,
                         pts=26.6, reb=4.6, ast=5.6, stl=2.0, blk=0.4),
    },
    "Donovan Mitchell": {
        "2023-24": dict(team="CLE", age=27, years_of_service=6, all_nba_honors=True,
                         games_played=55, minutes_per_game=35.3,
                         pts=26.6, reb=5.1, ast=6.1, stl=1.8, blk=0.4),
    },
    "Rudy Gobert": {
        "2023-24": dict(team="MIN", age=31, years_of_service=10, all_nba_honors=True,
                         games_played=76, minutes_per_game=32.6,
                         pts=14.0, reb=12.9, ast=1.3, stl=0.7, blk=2.1),
    },
    "Anthony Davis": {
        "2023-24": dict(team="LAL", age=30, years_of_service=11, all_nba_honors=True,
                         games_played=76, minutes_per_game=35.5,
                         pts=24.7, reb=12.6, ast=3.5, stl=1.2, blk=2.3),
    },
    "Karl-Anthony Towns": {
        "2023-24": dict(team="MIN", age=28, years_of_service=8, all_nba_honors=False,
                         games_played=62, minutes_per_game=32.7,
                         pts=21.8, reb=8.3, ast=3.0, stl=0.7, blk=0.6),
    },
    "Myles Turner": {
        "2023-24": dict(team="IND", age=27, years_of_service=8, all_nba_honors=False,
                         games_played=74, minutes_per_game=28.6,
                         pts=17.1, reb=6.9, ast=1.1, stl=0.7, blk=2.0),
    },
    "Bam Adebayo": {
        "2023-24": dict(team="MIA", age=26, years_of_service=6, all_nba_honors=False,
                         games_played=71, minutes_per_game=34.0,
                         pts=19.3, reb=10.4, ast=3.9, stl=1.1, blk=0.9),
    },
    "Julius Randle": {
        "2023-24": dict(team="NYK", age=29, years_of_service=9, all_nba_honors=False,
                         games_played=46, minutes_per_game=35.0,
                         pts=24.0, reb=9.2, ast=5.0, stl=0.6, blk=0.3),
    },
    "Nikola Vucevic": {
        "2023-24": dict(team="CHI", age=33, years_of_service=12, all_nba_honors=False,
                         games_played=82, minutes_per_game=33.4,
                         pts=18.0, reb=10.5, ast=3.3, stl=0.8, blk=0.6),
    },
    "Jaylen Brown": {
        "2023-24": dict(team="BOS", age=27, years_of_service=7, all_nba_honors=True,
                         games_played=70, minutes_per_game=33.5,
                         pts=23.0, reb=5.5, ast=3.6, stl=1.1, blk=0.5),
    },
    "Mikal Bridges": {
        "2023-24": dict(team="BKN", age=27, years_of_service=5, all_nba_honors=False,
                         games_played=82, minutes_per_game=35.4,
                         pts=19.6, reb=4.5, ast=3.6, stl=1.0, blk=0.4),
    },
    "OG Anunoby": {
        "2023-24": dict(team="NYK", age=26, years_of_service=6, all_nba_honors=False,
                         games_played=66, minutes_per_game=33.5,
                         pts=14.7, reb=4.1, ast=2.1, stl=1.5, blk=0.6),
    },
    "Draymond Green": {
        "2023-24": dict(team="GSW", age=33, years_of_service=11, all_nba_honors=False,
                         games_played=65, minutes_per_game=27.3,
                         pts=8.6, reb=7.2, ast=6.0, stl=1.0, blk=0.7),
    },
    "Pascal Siakam": {
        "2023-24": dict(team="IND", age=29, years_of_service=7, all_nba_honors=False,
                         games_played=77, minutes_per_game=34.2,
                         pts=21.3, reb=7.0, ast=3.7, stl=0.9, blk=0.4),
    },
    "Brandon Ingram": {
        "2023-24": dict(team="NOP", age=26, years_of_service=7, all_nba_honors=False,
                         games_played=64, minutes_per_game=34.0,
                         pts=20.8, reb=5.1, ast=5.7, stl=0.8, blk=0.6),
    },
    "Zion Williamson": {
        "2023-24": dict(team="NOP", age=23, years_of_service=4, all_nba_honors=False,
                         games_played=70, minutes_per_game=31.9,
                         pts=22.9, reb=5.8, ast=5.0, stl=0.9, blk=0.6),
    },
    "Alperen Sengun": {
        "2023-24": dict(team="HOU", age=21, years_of_service=2, all_nba_honors=False,
                         games_played=63, minutes_per_game=30.1,
                         pts=21.1, reb=9.3, ast=5.0, stl=1.2, blk=0.8),
    },
    "Evan Mobley": {
        "2023-24": dict(team="CLE", age=22, years_of_service=2, all_nba_honors=False,
                         games_played=74, minutes_per_game=30.3,
                         pts=15.7, reb=9.4, ast=2.8, stl=0.8, blk=1.4),
    },
    "Paolo Banchero": {
        "2023-24": dict(team="ORL", age=21, years_of_service=1, all_nba_honors=False,
                         games_played=80, minutes_per_game=33.9,
                         pts=22.6, reb=6.9, ast=5.4, stl=0.9, blk=0.5),
    },
    "Franz Wagner": {
        "2023-24": dict(team="ORL", age=22, years_of_service=2, all_nba_honors=False,
                         games_played=78, minutes_per_game=34.7,
                         pts=19.7, reb=4.9, ast=3.7, stl=1.0, blk=0.4),
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
