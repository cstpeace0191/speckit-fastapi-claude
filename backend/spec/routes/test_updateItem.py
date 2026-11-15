import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models import ItemUpdate
from src.routes.items import update_item

ITEM = {"id": "1234", "name": "New title", "completed": False}


@pytest.mark.asyncio
async def test_it_updates_items_correctly():
    item_id = "1234"
    update_payload = {"name": "New title", "completed": False}

    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value=ITEM) as mock_get:
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            result = await update_item(item_id, ItemUpdate(**update_payload))

            assert mock_update.call_count == 1
            assert mock_update.call_args[0][0] == item_id
            assert mock_update.call_args[0][1] == update_payload
            assert result == ITEM


@pytest.mark.asyncio
async def test_update_items_api_endpoint():
    item_id = "1234"
    update_payload = {"name": "New title", "completed": False}

    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value=ITEM) as mock_get:
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put(f"/api/items/{item_id}", json=update_payload)

            assert response.status_code == 200
            assert response.json() == ITEM
            assert mock_update.call_count == 1


@pytest.mark.asyncio
async def test_toggling_completed_true_then_false_restores_the_original_state():
    existing = {"id": "1234", "name": "Milk", "completed": False}

    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value=existing):
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                await ac.put("/api/items/1234", json={"completed": True})
                assert mock_update.call_args[0][1]["completed"] is True

            existing["completed"] = True
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                await ac.put("/api/items/1234", json={"completed": False})
                assert mock_update.call_args[0][1]["completed"] is False


@pytest.mark.asyncio
async def test_completed_only_update_leaves_the_name_unchanged():
    existing = {"id": "1234", "name": "Milk", "completed": False}

    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value=existing):
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                await ac.put("/api/items/1234", json={"completed": True})

            assert mock_update.call_args[0][1]["name"] == "Milk"


@pytest.mark.asyncio
async def test_updating_an_unknown_item_returns_404():
    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value=None):
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put("/api/items/unknown-id", json={"completed": True})

            assert response.status_code == 404
            assert response.json() == {"detail": "Item not found"}
            assert mock_update.call_count == 0


@pytest.mark.asyncio
async def test_rename_is_trimmed_before_it_is_saved():
    existing = {"id": "1234", "name": "Milk", "completed": False}

    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value=existing):
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                await ac.put("/api/items/1234", json={"name": "  Oat milk  "})

            assert mock_update.call_args[0][1]["name"] == "Oat milk"


@pytest.mark.asyncio
async def test_space_only_rename_is_rejected():
    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value={"id": "1234", "name": "Milk", "completed": False}):
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put("/api/items/1234", json={"name": "   "})

            assert response.status_code == 422
            assert mock_update.call_count == 0


@pytest.mark.asyncio
async def test_rename_longer_than_255_characters_is_rejected():
    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value={"id": "1234", "name": "Milk", "completed": False}):
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.put("/api/items/1234", json={"name": "a" * 256})

            assert response.status_code == 422
            assert mock_update.call_count == 0


@pytest.mark.asyncio
async def test_rename_keeps_completed_state():
    existing = {"id": "1234", "name": "Milk", "completed": True}

    with patch("src.persistence.get_item", new_callable=AsyncMock, return_value=existing):
        with patch("src.persistence.update_item", new_callable=AsyncMock) as mock_update:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                await ac.put("/api/items/1234", json={"name": "Oat milk"})

            assert mock_update.call_args[0][1] == {"name": "Oat milk", "completed": True}
