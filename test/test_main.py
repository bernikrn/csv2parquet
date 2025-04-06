import pytest
from httpx import AsyncClient
#from app.main import app  # Or from your FastAPI entrypoint

@pytest.mark.asyncio
async def test_register_and_upload():
    #async with AsyncClient(app=main, base_url="http://test") as ac:
    async with AsyncClient(base_url="http://localhost:8000") as ac:

        # Try to get user id
        response = await ac.get("/get_user_id/", params={"username": "coco"})
        assert response.status_code == 200
        user_id = response.json().get("user_id")
        assert isinstance(user_id, int)

        # Try to get user id
        response = await ac.get("/get_user_id/", params={"username": "iusbgfiweubv"})
        assert response.status_code == 404
