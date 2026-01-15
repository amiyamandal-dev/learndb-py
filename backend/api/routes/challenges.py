"""Challenge system API routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.core.session_manager import SessionManager, get_session_manager
from backend.core.challenge_engine import ChallengeEngine, get_challenge_engine
from backend.content.challenges.registry import ChallengeRegistry, get_challenge_registry


router = APIRouter(prefix="/challenges", tags=["challenges"])


# Pydantic models for API
class ChallengeListItem(BaseModel):
    id: str
    title: str
    difficulty: str
    xp_reward: int
    completed: bool = False


class CategoryResponse(BaseModel):
    name: str
    display_name: str
    challenges: List[ChallengeListItem]


class ChallengesListResponse(BaseModel):
    categories: List[CategoryResponse]
    total_count: int


class ChallengeDetail(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    xp_reward: int
    category: str
    estimated_time_minutes: int
    hints_count: int
    prerequisites: List[str]


class SubmitRequest(BaseModel):
    sql: str
    hints_used: int = 0


class SubmitResponse(BaseModel):
    success: bool
    passed: bool
    feedback: str
    xp_earned: int
    execution_time_ms: float
    actual_output: Optional[List[dict]] = None


class HintResponse(BaseModel):
    hint_index: int
    hint: str
    hints_remaining: int


def get_registry() -> ChallengeRegistry:
    return get_challenge_registry()


def get_engine() -> ChallengeEngine:
    return get_challenge_engine()


def get_manager() -> SessionManager:
    return get_session_manager()


@router.get("", response_model=ChallengesListResponse)
async def list_challenges(
    registry: ChallengeRegistry = Depends(get_registry)
):
    """List all challenges grouped by category."""
    categories = registry.get_categories()

    return ChallengesListResponse(
        categories=[
            CategoryResponse(
                name=cat["name"],
                display_name=cat["display_name"],
                challenges=[
                    ChallengeListItem(
                        id=c["id"],
                        title=c["title"],
                        difficulty=c["difficulty"],
                        xp_reward=c["xp_reward"]
                    )
                    for c in cat["challenges"]
                ]
            )
            for cat in categories
        ],
        total_count=len(registry.list_all())
    )


@router.get("/{challenge_id}", response_model=ChallengeDetail)
async def get_challenge(
    challenge_id: str,
    registry: ChallengeRegistry = Depends(get_registry)
):
    """Get challenge details."""
    challenge = registry.get(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")

    return ChallengeDetail(
        id=challenge.id,
        title=challenge.title,
        description=challenge.description,
        difficulty=challenge.difficulty.value,
        xp_reward=challenge.xp_reward,
        category=challenge.category.value,
        estimated_time_minutes=challenge.estimated_time_minutes,
        hints_count=len(challenge.hints),
        prerequisites=challenge.prerequisites
    )


@router.post("/{challenge_id}/setup")
async def setup_challenge(
    challenge_id: str,
    session_id: str,
    registry: ChallengeRegistry = Depends(get_registry),
    engine: ChallengeEngine = Depends(get_engine)
):
    """Set up a challenge for a session."""
    challenge = registry.get(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")

    success, message = engine.setup_challenge(session_id, challenge)

    if not success:
        raise HTTPException(status_code=500, detail=message)

    return {"status": "ready", "message": message}


@router.post("/{challenge_id}/submit", response_model=SubmitResponse)
async def submit_challenge(
    challenge_id: str,
    session_id: str,
    request: SubmitRequest,
    registry: ChallengeRegistry = Depends(get_registry),
    engine: ChallengeEngine = Depends(get_engine)
):
    """Submit a solution for a challenge."""
    challenge = registry.get(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")

    submission = engine.validate_submission(
        session_id=session_id,
        challenge=challenge,
        submitted_sql=request.sql,
        hints_used=request.hints_used
    )

    return SubmitResponse(
        success=submission.passed,
        passed=submission.passed,
        feedback=submission.feedback,
        xp_earned=submission.xp_earned,
        execution_time_ms=submission.execution_time_ms,
        actual_output=submission.actual_output if not submission.passed else None
    )


@router.get("/{challenge_id}/hints/{hint_index}", response_model=HintResponse)
async def get_hint(
    challenge_id: str,
    hint_index: int,
    registry: ChallengeRegistry = Depends(get_registry)
):
    """Get a hint for a challenge."""
    challenge = registry.get(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")

    if hint_index < 0 or hint_index >= len(challenge.hints):
        raise HTTPException(status_code=400, detail="Invalid hint index")

    return HintResponse(
        hint_index=hint_index,
        hint=challenge.hints[hint_index],
        hints_remaining=len(challenge.hints) - hint_index - 1
    )
