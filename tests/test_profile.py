from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from postgrest.exceptions import APIError

from stellar.enums import AccountStatus, Gender, JobTitle
from stellar.profile.schemas import CreateProfile, Profile, PublicProfile, UpdateProfile
from stellar.profile.service import ProfileService


@pytest.fixture
def service() -> ProfileService:
    return ProfileService()


@pytest.fixture
def user_id() -> str:
    return str(uuid4())


@pytest.fixture
def profile_data(user_id: str) -> dict:
    return {
        "id": str(uuid4()),
        "user_id": user_id,
        "first_name": "John",
        "last_name": "Doe",
        "gender": Gender.MALE,
        "bio": None,
        "birth_date": None,
        "phone_number": None,
        "avatar_url": None,
        "job_title": JobTitle.CL13,
        "team_id": None,
        "project_id": None,
        "account_status": AccountStatus.ACTIVE,
        "onboarded": False,
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }


@pytest.fixture
def create_payload() -> CreateProfile:
    return CreateProfile(
        first_name="John",
        last_name="Doe",
        gender=Gender.MALE,
        account_status=AccountStatus.ACTIVE,
        onboarded=False,
    )


def make_mock_supabase(query_data: list | None = None) -> MagicMock:
    """Build a mock Supabase client with a chainable table query."""
    mock = MagicMock()
    mock_chain = MagicMock()
    mock_chain.select.return_value = mock_chain
    mock_chain.insert.return_value = mock_chain
    mock_chain.update.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute = AsyncMock(return_value=SimpleNamespace(data=query_data or []))
    mock.table.return_value = mock_chain
    return mock


# --- get_profile ---


async def test_get_profile_success(
    service: ProfileService, user_id: str, profile_data: dict
) -> None:
    mock_supabase = make_mock_supabase([profile_data])

    result = await service.get_profile(user_id, mock_supabase)

    assert isinstance(result, Profile)
    assert result.user_id == user_id
    assert result.first_name == "John"


async def test_get_profile_raises_404_when_not_found(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = make_mock_supabase([])

    with pytest.raises(HTTPException) as exc_info:
        await service.get_profile(user_id, mock_supabase)

    assert exc_info.value.status_code == 404


async def test_get_profile_raises_400_on_api_error(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = make_mock_supabase()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = (
        AsyncMock(
            side_effect=APIError(
                {"message": "db error", "code": "500", "details": "", "hint": ""}
            )
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.get_profile(user_id, mock_supabase)

    assert exc_info.value.status_code == 400


async def test_get_profile_raises_500_on_unexpected_error(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = MagicMock()
    mock_supabase.table.side_effect = RuntimeError("unexpected crash")

    with pytest.raises(HTTPException) as exc_info:
        await service.get_profile(user_id, mock_supabase)

    assert exc_info.value.status_code == 500


# --- get_profile_by_user_id ---


async def test_get_profile_by_user_id_success(
    service: ProfileService, user_id: str, profile_data: dict
) -> None:
    mock_supabase = make_mock_supabase([profile_data])

    result = await service.get_profile_by_user_id(user_id, mock_supabase)

    assert isinstance(result, PublicProfile)
    assert result.user_id == user_id
    assert result.first_name == "John"


async def test_get_profile_by_user_id_raises_404_when_not_found(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = make_mock_supabase([])

    with pytest.raises(HTTPException) as exc_info:
        await service.get_profile_by_user_id(user_id, mock_supabase)

    assert exc_info.value.status_code == 404


async def test_get_profile_by_user_id_raises_400_on_api_error(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = make_mock_supabase()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute = (
        AsyncMock(
            side_effect=APIError(
                {"message": "db error", "code": "500", "details": "", "hint": ""}
            )
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.get_profile_by_user_id(user_id, mock_supabase)

    assert exc_info.value.status_code == 400


async def test_get_profile_by_user_id_raises_500_on_unexpected_error(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = MagicMock()
    mock_supabase.table.side_effect = RuntimeError("unexpected crash")

    with pytest.raises(HTTPException) as exc_info:
        await service.get_profile_by_user_id(user_id, mock_supabase)

    assert exc_info.value.status_code == 500


# --- create_profile ---


async def test_create_profile_success(
    service: ProfileService,
    user_id: str,
    create_payload: CreateProfile,
    profile_data: dict,
) -> None:
    mock_supabase = MagicMock()
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain

    # first call: existence check returns empty
    # second call: insert returns the created profile
    mock_chain.select.return_value = mock_chain
    mock_chain.insert.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(data=[]),
            SimpleNamespace(data=[profile_data]),
        ]
    )

    result = await service.create_profile(create_payload, user_id, mock_supabase)

    assert isinstance(result, Profile)
    assert result.user_id == user_id


async def test_create_profile_raises_400_when_profile_already_exists(
    service: ProfileService,
    user_id: str,
    create_payload: CreateProfile,
    profile_data: dict,
) -> None:
    mock_supabase = make_mock_supabase([profile_data])

    with pytest.raises(HTTPException) as exc_info:
        await service.create_profile(create_payload, user_id, mock_supabase)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Profile already exists"


async def test_create_profile_raises_400_when_insert_returns_no_data(
    service: ProfileService,
    user_id: str,
    create_payload: CreateProfile,
) -> None:
    mock_supabase = MagicMock()
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.insert.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(data=[]),
            SimpleNamespace(data=[]),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_profile(create_payload, user_id, mock_supabase)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Failed to create profile"


async def test_create_profile_raises_400_on_api_error(
    service: ProfileService,
    user_id: str,
    create_payload: CreateProfile,
) -> None:
    mock_supabase = MagicMock()
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.insert.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(data=[]),
            APIError(
                {"message": "constraint violation", "code": "23503", "details": "", "hint": ""}
            ),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_profile(create_payload, user_id, mock_supabase)

    assert exc_info.value.status_code == 400


async def test_create_profile_raises_500_on_unexpected_error(
    service: ProfileService,
    user_id: str,
    create_payload: CreateProfile,
) -> None:
    mock_supabase = MagicMock()
    mock_supabase.table.side_effect = RuntimeError("unexpected crash")

    with pytest.raises(HTTPException) as exc_info:
        await service.create_profile(create_payload, user_id, mock_supabase)

    assert exc_info.value.status_code == 500


# --- update_profile ---


async def test_update_profile_success(
    service: ProfileService,
    user_id: str,
    profile_data: dict,
) -> None:
    updated_data = {**profile_data, "first_name": "Jane"}
    mock_supabase = MagicMock()
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.update.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(data=[profile_data]),
            SimpleNamespace(data=[updated_data]),
        ]
    )

    result = await service.update_profile(
        UpdateProfile(first_name="Jane"), user_id, mock_supabase
    )

    assert isinstance(result, Profile)
    assert result.first_name == "Jane"


async def test_update_profile_raises_404_when_profile_not_found(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = make_mock_supabase([])

    with pytest.raises(HTTPException) as exc_info:
        await service.update_profile(
            UpdateProfile(first_name="Jane"), user_id, mock_supabase
        )

    assert exc_info.value.status_code == 404


async def test_update_profile_raises_400_when_payload_is_empty(
    service: ProfileService, user_id: str, profile_data: dict
) -> None:
    mock_supabase = make_mock_supabase([profile_data])

    with pytest.raises(HTTPException) as exc_info:
        await service.update_profile(UpdateProfile(), user_id, mock_supabase)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "No data to update"


async def test_update_profile_raises_400_when_update_returns_no_data(
    service: ProfileService, user_id: str, profile_data: dict
) -> None:
    mock_supabase = MagicMock()
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.update.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(data=[profile_data]),
            SimpleNamespace(data=[]),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.update_profile(
            UpdateProfile(first_name="Jane"), user_id, mock_supabase
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Failed to update profile"


async def test_update_profile_raises_400_on_api_error(
    service: ProfileService, user_id: str, profile_data: dict
) -> None:
    mock_supabase = MagicMock()
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.update.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(data=[profile_data]),
            APIError(
                {"message": "db error", "code": "500", "details": "", "hint": ""}
            ),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.update_profile(
            UpdateProfile(first_name="Jane"), user_id, mock_supabase
        )

    assert exc_info.value.status_code == 400


async def test_update_profile_raises_500_on_unexpected_error(
    service: ProfileService, user_id: str
) -> None:
    mock_supabase = MagicMock()
    mock_supabase.table.side_effect = RuntimeError("unexpected crash")

    with pytest.raises(HTTPException) as exc_info:
        await service.update_profile(
            UpdateProfile(first_name="Jane"), user_id, mock_supabase
        )

    assert exc_info.value.status_code == 500
