from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView

from .forms import AlternativeFormset
from .models import Alternative, UserAlreadyVoted, Voting, VotingDeactive, VotingEvent

####################
### Admin views ####
####################


class VotingEventList(PermissionRequiredMixin, ListView):
    permission_required = "vote.vote_admin"
    model = VotingEvent
    template_name = "vote/voting_event_list.html"


class VotingList(PermissionRequiredMixin, DetailView):
    """List of all votings in a voting event"""

    permission_required = "vote.vote_admin"
    model = VotingEvent
    template_name = "vote/voting_list.html"


class CreateVoting(PermissionRequiredMixin, CreateView):
    """View for creating new votings"""

    permission_required = "vote.vote_admin"
    template_name = "vote/voting_form.html"
    model = Voting
    fields = ["event", "title", "description"]

    def get_initial(self):
        event_id = self.kwargs["pk"]
        event = get_object_or_404(VotingEvent, pk=event_id)
        return {
            "event": event,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs["pk"]
        context["event_id"] = event_id
        if self.request.POST:
            context["alternatives"] = AlternativeFormset(self.request.POST)
        else:
            context["alternatives"] = AlternativeFormset()
        return context

    def form_valid(self, form, **kwargs):
        """Called if all forms are valid. Creates voting and associated alternatives"""
        context = self.get_context_data()
        alternatives = context["alternatives"]
        event_id = self.kwargs["pk"]
        with transaction.atomic():
            self.object = form.save()
            if alternatives.is_valid():
                alternatives.instance = self.object
                event_id = alternatives.instance.event.pk
                alternatives.save()
        return redirect("voting-list", pk=event_id)
        return super().form_valid(form)


class VotingDetail(PermissionRequiredMixin, DetailView):
    """Display details such as alternatives and results"""

    permission_required = "vote.vote_admin"
    model = Voting
    template_name = "vote/voting_detail.html"


@login_required
@permission_required("vote.vote_admin", raise_exception=True)
def activate_voting(request, pk, redirect_to):
    """Open voting"""
    voting = Voting.objects.get(pk=pk)
    voting.is_active = True
    voting.save()
    return redirect(redirect_to)


@login_required
@permission_required("vote.vote_admin", raise_exception=True)
def deactivate_voting(request, pk, redirect_to):
    """Close voting"""
    voting = Voting.objects.get(pk=pk)
    voting.is_active = False
    voting.save()
    return redirect(redirect_to)


###########################################
### Non admin vies, only login required ###
###########################################


class ActiveVotingList(LoginRequiredMixin, ListView):
    """Display list of active votings"""

    model = Voting
    template_name = "vote/active_voting_list.html"

    def get_queryset(self):
        return self.model.objects.exclude(is_active=False)


class Vote(LoginRequiredMixin, DetailView):
    """Display alternatives and lets users vote"""

    model = Voting
    template_name = "vote/voting_vote.html"

    def post(self, request, **kwargs):
        """Submit a vote from chosen alternative"""
        voting_id = kwargs["pk"]
        voting = get_object_or_404(Voting, pk=voting_id)
        try:
            alternative = voting.alternatives.get(pk=request.POST["alternative"])
            alternative.add_vote(request.user)
        except (KeyError, Alternative.DoesNotExist):
            messages.warning(request, "Du har ikke valgt et alternativ.")
            return redirect("voting-vote", pk=voting_id)
        except UserAlreadyVoted:
            messages.error(request, "Du har allerede stemt i denne avstemningen!")
        except VotingDeactive:
            messages.error(
                request, "Denne avstemningen er ikke lenger åpen for stemming!"
            )
        else:
            messages.success(
                request, f"Suksess! Du har stemt i avstemningen {voting.title}"
            )
        return redirect("active-voting-list")
