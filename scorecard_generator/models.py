from collections import defaultdict

BALLS_PER_OVER = 6
MAX_OVERS = 2  # Update later for 20
MAX_BOWLER_OVERS = 1 # update Later for 4 overs in T20

# Pre-defined cricket formats
CRICKET_FORMATS = {
    'T20': {'name': 'T20', 'max_overs': 20, 'max_bowler_overs': 4, 'balls_per_over': 6},
    'ODI': {'name': 'One Day', 'max_overs': 50, 'max_bowler_overs': 10, 'balls_per_over': 6},
    'TEST': {'name': 'First Class', 'max_overs': None, 'max_bowler_overs': None, 'balls_per_over': 6},
}

class Player:
    def __init__(self, number, name):
        self.number = number
        self.name = name
        self.batting = {
            'runs': 0, 'balls': 0, '4s': 0, '6s': 0,
            'SR': 0.0, 'dismissal': 'not out',
            'scoring_distribution': defaultdict(int)  # Track 0s, 1s, 2s, 3s, 4s, 6s
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

class Partnership:
    """Tracks partnership between two batters."""
    def __init__(self, batter1, batter2, wicket_number, start_score):
        self.batter1 = batter1  # Player object
        self.batter2 = batter2  # Player object
        self.wicket_number = wicket_number  # 1st, 2nd, 3rd wicket, etc.
        self.start_score = start_score
        self.end_score = None
        self.runs = 0
        self.balls = 0
        self.batter1_runs = 0
        self.batter1_balls = 0
        self.batter2_runs = 0
        self.batter2_balls = 0

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
        
        # Match stats tracking
        self.phase_stats = {
            'powerplay': {'runs': 0, 'wickets': 0, 'balls': 0},
            'middle': {'runs': 0, 'wickets': 0, 'balls': 0},
            'final': {'runs': 0, 'wickets': 0, 'balls': 0}
        }
        self.partnerships = []  # List of Partnership objects
        self.current_partnership = None  # Active partnership
        self.over_totals = []  # Runs scored in each over [over_0_runs, over_1_runs, ...]
        self.cumulative_runs = []  # Total score after each over

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
        
        # Calculate overs using bowler_overs data (more reliable)
        # bowler_overs is dict like {bowler_num: [over_0, over_1, ...]}
        if self.bowler_overs:
            # Get all distinct over numbers that were bowled
            all_overs_bowled = set()
            for overs_list in self.bowler_overs.values():
                all_overs_bowled.update(overs_list)
            
            if all_overs_bowled:
                # Maximum over number tells us how many complete overs exist
                max_over = max(all_overs_bowled)
                
                # Count balls in the last (potentially incomplete) over
                # Exclude all wide and no-ball variants (they don't count as legal deliveries)
                balls_in_last_over = sum(
                    1 for be in self.balls 
                    if be.over == max_over and not (
                        be.event.startswith('wide') or 
                        be.event.startswith('no ball')
                    )
                )
                
                # Calculate overs: complete overs + fractional part from last over
                complete_overs, remainder = divmod(balls_in_last_over, BALLS_PER_OVER)
                overs = max_over + complete_overs + remainder / 10
            else:
                overs = 0
        else:
            # Fallback: count from balls if no bowler_overs available
            # Count all deliveries except wides and no-balls (which don't count as legal)
            balls = sum(1 for be in self.balls if not (
                be.event.startswith('wide') or 
                be.event.startswith('no ball')
            ))
            overs = balls // BALLS_PER_OVER + (balls % BALLS_PER_OVER) / 10
        
        rr = total_runs / (overs * BALLS_PER_OVER / BALLS_PER_OVER) if overs > 0 else 0
        return total_runs, wickets, overs, rr


def get_current_phase(over, format_config):
    """Determine current phase (powerplay/middle/final) based on format and over number.
    
    Args:
        over: 0-indexed over number
        format_config: Dict with 'name' and 'max_overs'
    
    Returns:
        'powerplay', 'middle', 'final', or None (for unlimited formats)
    """
    if format_config['name'] == 'T20':
        if over < 6:
            return 'powerplay'
        elif over < 16:
            return 'middle'
        else:
            return 'final'
    elif format_config['name'] == 'One Day':
        if over < 10:
            return 'powerplay'
        elif over < 40:
            return 'middle'
        else:
            return 'final'
    # First Class or unlimited formats don't have phases
    return None
