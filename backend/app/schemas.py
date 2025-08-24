from pydantic import BaseModel

class MatchInput(BaseModel):
    teamA: str
    teamB: str
    venue: str
    toss_winner: str
    toss_decision: str
    competition: str