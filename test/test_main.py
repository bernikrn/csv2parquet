import pytest
from httpx import AsyncClient
from fastapi import status

# To run the tests: pytest test_main.py

@pytest.mark.asyncio
async def test_register_and_upload():
    async with AsyncClient(base_url="http://localhost:8000") as ac:

        # Try to get user id
        response = await ac.get("/get_user_id/", params={"username": "coco"})
        assert response.status_code == status.HTTP_200_OK
        user_id = response.json().get("user_id")
        assert isinstance(user_id, int)

        # Try to get user id
        response = await ac.get("/get_user_id/", params={"username": "iusbgfiweubv"})
        assert response.status_code == status.HTTP_404_NOT_FOUND
