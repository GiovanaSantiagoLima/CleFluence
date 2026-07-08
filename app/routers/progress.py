from fastapi import APIRouter

from app.db.neo4j_db import run_query
from app.schemas.progress import ErrorRecord, VocabularyUpdate

router = APIRouter(prefix="/progress", tags=["progress"])


@router.put("/{user_id}/vocabulary")
async def update_vocabulary(user_id: str, payload: VocabularyUpdate):
    query = """
    MERGE (u:User {id: $user_id})
    MERGE (v:Vocabulary {word: $word})
    MERGE (u)-[r:PROGRESS_ON]->(v)
    SET r.status = $status, r.updated_at = datetime()
    """
    await run_query(query, {"user_id": user_id, "word": payload.word, "status": payload.status})
    return {"ok": True}


@router.post("/{user_id}/errors")
async def record_error(user_id: str, payload: ErrorRecord):
    query = """
    MERGE (u:User {id: $user_id})
    MERGE (e:ErrorPattern {type: $error_type})
    MERGE (u)-[r:MAKES_ERROR]->(e)
    ON CREATE SET r.count = 1
    ON MATCH SET r.count = r.count + 1
    SET r.last_example = $example, r.skill = $skill
    """
    await run_query(
        query,
        {"user_id": user_id, "error_type": payload.error_type, "example": payload.example, "skill": payload.skill},
    )
    return {"ok": True}


@router.get("/{user_id}/graph")
async def get_graph(user_id: str):
    query = """
    MATCH (u:User {id: $user_id})-[r]->(n)
    RETURN elementId(n) AS id, labels(n)[0] AS type,
        coalesce(n.word, n.type) AS label, r.status AS status, type(r) AS relationship
    """
    return await run_query(query, {"user_id": user_id})
