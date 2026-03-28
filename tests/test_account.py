from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from postgrest.exceptions import APIError

from stellar.account.schemas import CreateUserAccount, CreateUserAccountResponse
from stellar.account.service import AccountService
from stellar.enums import AccountStatus, UserRole


@pytest.fixture
def service() -> AccountService:
    return AccountService()


@pytest.fixture
def payload() -> CreateUserAccount:
    return CreateUserAccount(
        email="newuser@example.com",
        password="securepassword123",
        role=UserRole.SUPPORT,
        status=AccountStatus.ACTIVE,
    )


def make_auth_user(role: str, user_id: str | None = None) -> SimpleNamespace:
    """Build a fake Supabase get_user response."""
    return SimpleNamespace(
        user=SimpleNamespace(
            id=user_id or str(uuid4()),
            email="newuser@example.com",
            user_metadata={"role": role},
        )
    )


# --- is_allowed_role ---


def test_is_allowed_role_returns_true_for_developer(service: AccountService) -> None:
    assert service._is_allowed_role("developer") is True


def test_is_allowed_role_returns_true_for_leadership(service: AccountService) -> None:
    assert service._is_allowed_role("leadership") is True


def test_is_allowed_role_returns_true_for_manager(service: AccountService) -> None:
    assert service._is_allowed_role("manager") is True


def test_is_allowed_role_returns_false_for_support(service: AccountService) -> None:
    assert service._is_allowed_role("support") is False


def test_is_allowed_role_returns_false_for_ic(service: AccountService) -> None:
    assert service._is_allowed_role("ic") is False


def test_is_allowed_role_returns_false_for_lead(service: AccountService) -> None:
    assert service._is_allowed_role("lead") is False


def test_is_allowed_role_returns_false_for_none(service: AccountService) -> None:
    assert service._is_allowed_role(None) is False


def test_is_allowed_role_returns_false_for_unknown_role(
    service: AccountService,
) -> None:
    assert service._is_allowed_role("unknown") is False


# --- create_user_account ---
async def test_create_user_account_success(
    service: AccountService, payload: CreateUserAccount
) -> None:
    new_user_id = str(uuid4())

    mock_supabase = AsyncMock()
    mock_supabase.auth.get_user.return_value = make_auth_user("developer")
    mock_supabase.auth.sign_up.return_value = make_auth_user(
        "support", user_id=new_user_id
    )

    result = await service.create_user_account(
        payload, token="valid-token", supabase=mock_supabase
    )

    assert isinstance(result, CreateUserAccountResponse)
    assert str(result.id) == new_user_id
    assert result.email == "newuser@example.com"
    assert result.role == "support"


async def test_create_user_account_raises_404_when_caller_not_found(
    service: AccountService, payload: CreateUserAccount
) -> None:
    mock_supabase = AsyncMock()
    mock_supabase.auth.get_user.return_value = SimpleNamespace(user=None)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_user_account(
            payload, token="bad-token", supabase=mock_supabase
        )

    assert exc_info.value.status_code == 404


async def test_create_user_account_raises_403_for_disallowed_role(
    service: AccountService, payload: CreateUserAccount
) -> None:
    mock_supabase = AsyncMock()
    mock_supabase.auth.get_user.return_value = make_auth_user("support")

    with pytest.raises(HTTPException) as exc_info:
        await service.create_user_account(
            payload, token="valid-token", supabase=mock_supabase
        )

    assert exc_info.value.status_code == 403


async def test_create_user_account_raises_400_when_signup_returns_no_user(
    service: AccountService, payload: CreateUserAccount
) -> None:
    mock_supabase = AsyncMock()
    mock_supabase.auth.get_user.return_value = make_auth_user("developer")
    mock_supabase.auth.sign_up.return_value = SimpleNamespace(user=None)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_user_account(
            payload, token="valid-token", supabase=mock_supabase
        )

    assert exc_info.value.status_code == 400


async def test_create_user_account_raises_400_on_api_error(
    service: AccountService, payload: CreateUserAccount
) -> None:
    mock_supabase = AsyncMock()
    mock_supabase.auth.get_user.return_value = make_auth_user("developer")
    mock_supabase.auth.sign_up.side_effect = APIError(
        {"message": "duplicate email", "code": "23505", "details": "", "hint": ""}
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_user_account(
            payload, token="valid-token", supabase=mock_supabase
        )

    assert exc_info.value.status_code == 400


async def test_create_user_account_raises_500_on_unexpected_error(
    service: AccountService, payload: CreateUserAccount
) -> None:
    mock_supabase = AsyncMock()
    mock_supabase.auth.get_user.side_effect = RuntimeError("unexpected crash")

    with pytest.raises(HTTPException) as exc_info:
        await service.create_user_account(
            payload, token="valid-token", supabase=mock_supabase
        )

    assert exc_info.value.status_code == 500
