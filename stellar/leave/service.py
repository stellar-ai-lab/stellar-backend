import logging
from typing import List

from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from stellar.auth_context import AuthContext
from stellar.enums import AccountStatus, JobTitle, LeaveRequestStatus
from stellar.leave.schemas import (
    ApproverResponse,
    LeaveRequestCreation,
    LeaveRequestResponse,
)

log = logging.getLogger(__name__)


class LeaveService:
    """Leave service."""

    LEAVE_REQUESTS_TABLE = "leave_requests"
    PROFILES_TABLE = "profiles"

    async def create_leave_request(
        self, auth: AuthContext, payload: LeaveRequestCreation
    ) -> LeaveRequestResponse:
        """Create a new leave request.

        Args:
            auth: Authentication context.
            payload: Payload to create a new leave request.

        Returns:
            Created leave request.
        """
        supabase = auth.client
        current_user_id = auth.current_user_id
        try:
            start_date = payload.start_date
            end_date = payload.end_date
            approver = payload.approver

            if str(approver) == current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot approve your own leave request",
                )

            if start_date > end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start date must be before or equal to end date",
                )

            approver_profile = (
                await supabase.table(self.PROFILES_TABLE)
                .select("user_id, account_status")
                .eq("user_id", str(approver))
                .execute()
            )
            if not approver_profile.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Approver profile not found",
                )
            if approver_profile.data[0]["account_status"] != AccountStatus.ACTIVE.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Approver is not active",
                )

            total_days = (end_date - start_date).days + 1

            overlapping = (
                await supabase.table(self.LEAVE_REQUESTS_TABLE)
                .select("id")
                .eq("user_id", current_user_id)
                .in_(
                    "status",
                    [
                        LeaveRequestStatus.PENDING.value,
                        LeaveRequestStatus.APPROVED.value,
                    ],
                )
                .lte("start_date", end_date.isoformat())
                .gte("end_date", start_date.isoformat())
                .execute()
            )
            if overlapping.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You have existing leave that overlaps with the new leave request",
                )

            data = {
                "user_id": current_user_id,
                "leave_type": payload.leave_type.value,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": total_days,
                "reason": payload.reason,
                "status": LeaveRequestStatus.PENDING.value,
                "approver": str(approver),
            }

            response = (
                await supabase.table(self.LEAVE_REQUESTS_TABLE).insert(data).execute()
            )
            if not response.data or not response.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create leave request",
                )

            return LeaveRequestResponse(**response.data[0])
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to create leave request: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create leave request",
            )
        except Exception as e:
            log.exception(f"Failed to create leave request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_list_of_approvers(self, auth: AuthContext) -> List[ApproverResponse]:
        """Get the list of approvers.

        Args:
            auth: Authentication context.

        Returns:
            List of approvers.
        """
        supabase = auth.client
        try:
            response = (
                await supabase.table(self.PROFILES_TABLE)
                .select("id, user_id, first_name, last_name, avatar_url, job_title")
                .in_(
                    "job_title",
                    [
                        JobTitle.CL9.value,
                        JobTitle.CL8.value,
                        JobTitle.CL7.value,
                        JobTitle.CL6.value,
                        JobTitle.CL5.value,
                    ],
                )
                .eq("account_status", AccountStatus.ACTIVE.value)
                .execute()
            )
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No approvers found",
                )

            approvers: List[ApproverResponse] = []
            for user in response.data:
                approvers.append(ApproverResponse(**user))

            return approvers
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to get list of approvers: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get list of approvers",
            )
        except Exception as e:
            log.exception(f"Failed to get list of approvers: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


leave_service = LeaveService()
