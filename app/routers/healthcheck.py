from fastapi import APIRouter

router = APIRouter(tags=["System"])

@router.get("/test-cors")
def test_cors():
    return {"status": "ok"}
