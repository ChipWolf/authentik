"""invitation stage logic"""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from authentik.flows.stage import StageView
from authentik.stages.invitation.models import Invitation, InvitationStage
from authentik.stages.invitation.signals import invitation_used
from authentik.stages.prompt.stage import PLAN_CONTEXT_PROMPT

INVITATION_TOKEN_KEY = "token"  # nosec
INVITATION_IN_EFFECT = "invitation_in_effect"


class InvitationStageView(StageView):
    """Finalise Authentication flow by logging the user in"""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Apply data to the current flow based on a URL"""
        stage: InvitationStage = self.executor.current_stage
        if INVITATION_TOKEN_KEY not in request.GET:
            # No Invitation was given, raise error or continue
            if stage.continue_flow_without_invitation:
                return self.executor.stage_ok()
            return self.executor.stage_invalid()

        token = request.GET[INVITATION_TOKEN_KEY]
        invite: Invitation = get_object_or_404(Invitation, pk=token)
        self.executor.plan.context[PLAN_CONTEXT_PROMPT] = invite.fixed_data
        self.executor.plan.context[INVITATION_IN_EFFECT] = True
        invitation_used.send(sender=self, request=request, invitation=invite)
        return self.executor.stage_ok()
