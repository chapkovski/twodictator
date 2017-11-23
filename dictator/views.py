from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class Introduction(Page):
    def is_displayed(self):
        return self.player.treatment == 'person'


class CharityIntro(Page):
    def is_displayed(self):
        return self.player.role() == 'dictator' and self.player.treatment == 'charity'


class Offer(Page):
    def is_displayed(self):
        return self.player.role() == 'dictator'

    form_model = models.Group
    form_fields = ['kept']


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        if self.round_number == Constants.num_rounds:
            self.group.set_payoffs()

    def vars_for_template(self):
        if self.player.id_in_group == 2:
            body_text = "You are participant 2. Waiting for participant 1 to decide."
        else:
            body_text = 'Please wait'
        return {'body_text': body_text}


class Results(Page):
    def is_displayed(self):
        self.player.participantvarsdump = self.participant.vars
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        person_kept=self.group.in_round(self.group.person_round).kept
        paying_round_kept=self.group.in_round(self.group.paying_round).kept
        return {
            'paying_round_kept':paying_round_kept,
            'person_kept': person_kept,
            'offer': Constants.endowment - person_kept,
        }


page_sequence = [
    Introduction,
    CharityIntro,
    Offer,
    ResultsWaitPage,
    Results,
]
