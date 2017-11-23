from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

doc = """
One player decides how to divide a certain amount between himself and the other
player.

See: Kahneman, Daniel, Jack L. Knetsch, and Richard H. Thaler. "Fairness
and the assumptions of economics." Journal of business (1986):
S285-S300.

"""


class Constants(BaseConstants):
    name_in_url = 'dictator'
    players_per_group = 2
    num_rounds = 2
    treatment_seq = ['charity', 'person']
    instructions_template = 'dictator/Instructions.html'
    charity_instructions_template = 'dictator/CharityInstructions.html'

    # Initial amount allocated to the dictator
    endowment = c(100)


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            for g in self.get_groups():
                grouptreatment = random.sample(Constants.treatment_seq, len(Constants.treatment_seq))
                g.person_round=grouptreatment.index('person') +1
                g.paying_round = random.randint(1, Constants.num_rounds)
                for p in g.get_players():
                    p.participant.vars['treatmentseq'] = grouptreatment
                    p.participant.vars['paying_round'] = g.paying_round
        else:
            for g in self.get_groups():
                g.paying_round = g.in_round(1).paying_round
                g.person_round = g.in_round(1).person_round
        for p in self.get_players():
            p.treatment = p.participant.vars.get('treatmentseq')[p.round_number - 1]


class Group(BaseGroup):
    person_round = models.IntegerField()
    paying_round = models.IntegerField()

    kept = models.CurrencyField(
        doc="""Amount dictator decided to keep for himself""",
        min=0, max=Constants.endowment,
        verbose_name='I will keep (from 0 to %i)' % Constants.endowment
    )

    def set_payoffs(self):
        recipient = self.get_player_by_role('recipient')
        dictator = self.get_player_by_role('dictator')
        recipient_p_round = [p.round_number for p in recipient.in_all_rounds() if p.treatment == 'person'][0]
        dictator_p_round = dictator.participant.vars.get('paying_round')

        recipient.payoff = Constants.endowment - self.in_round(recipient_p_round).kept
        dictator.payoff = self.in_round(dictator_p_round).kept


class Player(BasePlayer):
    participantvarsdump = models.CharField(doc='for storing all participantvars data for the simplicity')
    treatment = models.CharField(doc='stores the info about the treatment in this round')

    def role(self):
        return 'dictator' if self.id_in_group == 1 else 'recipient'
