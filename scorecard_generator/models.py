from collections import defaultdict

BALLS_PER_OVER = 6
MAX_OVERS = 2  # Update later for 20
MAX_BOWLER_OVERS = 1 # update Later for 4 overs in T20

class Player:
    def __init__(self, number, name):
        self.number = number
        self.name = name
        self.batting = {
            'runs': 0, 'balls': 0, '4s': 0, '6s': 0,
            'SR': 0.0, 'dismissal': 'not out'
        }
        self.bowling = {
            'balls': 0, 'runs': 0, 'wickets': 0, 'maidens': 0,
            'dots': 0, '4s': 0, '6s': 0, 'wides': 0, 'noballs': 0
        }
        self.batted = False
        self.bowled = False

    def __str__(self):
        return f"{self.number} {self.name}"

class Team:
    def __init__(self, name):
        self.name = name
        self.players = {}
        self.order = []
        self.bowler_order = []
        self.wicketkeeper_number = None
        self.captain_number = None

    def add_player(self, player):
        self.players[player.number] = player

    def get_player(self, number):
        return self.players[number]

    def all_players(self):
        return [self.players[num] for num in sorted(self.players)]

    def get_batters(self):
        return [self.players[num] for num in self.order]

    def get_bowlers(self):
        return [self.players[num] for num in self.bowler_order]

class BallEvent:
    def __init__(self, over, ball, bowler, batter, runs, event, fielders=None):
        self.over = over
        self.ball = ball
        self.bowler = bowler
        self.batter = batter
        self.runs = runs
        self.event = event
        self.fielders = fielders or []

class Innings:
    def __init__(self, batting_team, bowling_team):
        self.batting_team = batting_team
        self.bowling_team = bowling_team
        self.balls = []
        self.current_batters = []
        self.dismissed = []
        self.did_not_bat = []
        self.fall_of_wickets = []
        self.extras = defaultdict(int)
        self.bowler_overs = defaultdict(list)

    def add_ball(self, ball_event):
        self.balls.append(ball_event)

    def get_score(self):
        total_runs = 0
        
        # Get all extras from the extras dictionary
        # This includes wides, no balls (penalty), byes, leg byes
        total_runs = sum(self.extras.values())
        
        # Add runs scored by batters (off normal deliveries and wickets)
        for player in self.batting_team.players.values():
            total_runs += player.batting['runs']
        
        wickets = len(self.fall_of_wickets)
        # Only count balls for legal deliveries
        balls = sum(1 for be in self.balls if be.event in ['normal', 'bye', 'leg bye', 'wicket', 'run out''bye_run_out', 'leg_bye_run_out'])
        overs = balls // BALLS_PER_OVER + (balls % BALLS_PER_OVER) / 10
        rr = total_runs / (balls / 6) if balls else 0
        return total_runs, wickets, overs, rr
