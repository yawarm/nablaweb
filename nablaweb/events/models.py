# -*- coding: utf-8 -*-


from django.db import models
from django.contrib.auth.models import User
from news.models import News
import datetime
from urlparse import urlparse

class AbstractEvent(News):
    short_name = models.CharField("kort navn", max_length=20, blank=True, null=True, help_text="Brukes på steder hvor det ikke er plass til å skrive hele overskriften, for eksempel kalenderen.")

    # Indikerer hvem som står bak arrangementet.
    # Dette feltet er valgfritt.
    organizer = models.CharField(verbose_name="organisert av", max_length=100, blank=True, help_text="Den som står bak arrangementet")

    # Hvor arrangementet foregår.
    location = models.CharField(u"sted", max_length=100, blank=False)

    # Når arrangementet starter.
    event_start = models.DateTimeField(verbose_name="start", null=True, blank=False)

    # Når arrangementet slutter.
    # Dette feltet er valgfritt.
    # Datoen er ikke tidligere enn event_start.
    event_end = models.DateTimeField(verbose_name="slutt", null=True, blank=True)

    # Om arrangementet krever påmelding.
    # Dette feltet er påkrevd.
    registration_required = models.BooleanField(verbose_name="påmelding", null=False, blank=False)

    # Frist for å melde seg på arrangementet.
    # Dette feltet er satt hvis registration_required er sann.
    # Datoen er ikke senere enn event_start.
    registration_deadline = models.DateTimeField(verbose_name="påmeldingsfrist", null=True, blank=True)

    # Når påmeldingen starter.
    # Dette feltet er valgfritt.
    # Dette feltet er bare satt hvis registration_required er sann.
    # Datoen er ikke senere enn registration_deadline.
    registration_start = models.DateTimeField(verbose_name="påmelding åpner", null=True, blank=True)

    # Frist for å melde seg av arrangementet.
    # Dette feltet er valgfritt.
    # Dette feltet er bare satt hvis registration_required er sann.
    # Datoen er ikke tidligere enn registration_start, hvis dette er satt.
    # Datoen er ikke senere enn event_start.
    deregistration_deadline = models.DateTimeField(verbose_name="avmelding stenger", null=True, blank=True)

    # Hvor mange plasser arrangementet har.
    # Dette feltet er satt hvis og bare hvis registration_required er sann.
    # Antall plasser er et heltall ikke mindre enn null.
    places = models.PositiveIntegerField(verbose_name="antall plasser", null=True, blank=True)

    # Om arrangementet har venteliste.
    # Dette feltet er valgfritt.
    # Dette feltet er bare satt hvis registration_required er sann.
    has_queue = models.NullBooleanField(verbose_name="har venteliste", null=True, blank=True, help_text="Om ventelisten er på, vil det være mulig å melde seg på selv om arrangementet er fullt. De som er i ventelisten vil automatisk bli påmeldt etter hvert som plasser blir ledige.")
    
    # URL til Facebook-siden til arrangementet
    # Dette feltet er valgfritt.
    facebook_url = models.CharField(verbose_name="facebook-url", blank=True, max_length=100, help_text="URL-en til det tilsvarende arrangementet på Facebook")

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s, %s' % (self.headline, self.event_start.strftime('%d.%m.%y'))

    def free_places(self):
        raise NotImplemented

    def is_full(self):
        raise NotImplemented

    def users_attending(self):
        raise NotImplemented

    def users_waiting(self):
        raise NotImplemented

    def percent_full(self):
        raise NotImplemented

    def users_registered(self):
        raise NotImplemented

    def is_registered(self, user):
        raise NotImplemented

    def has_waiting_list(self):
        raise NotImplemented

    def register_user(self, user):
        raise NotImplemented

    def deregister_user(self, user):
        raise NotImplementedError

    def move_user_to_place(self, user, place):
        raise NotImplementedError
        
    def get_short_name(self):
        raise NotImplementedError

class Event(AbstractEvent):

    class Meta:
        verbose_name = "arrangement"
        verbose_name_plural = "arrangement"

    # Overlagre for å automatisk vedlikeholde ventelisten.
    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        #self.test_event_fields()
        self._prune_queue()

    # Overlagre for å slette registreringer sammen med arrangementet.
    def delete(self, *args, **kwargs):
        self.eventregistration_set.all().delete()
        super(Event, self).delete(*args, **kwargs)

    # Verifiserer formen på facebook-urlen, og endrer den hvis den er feil.
    def clean(self):
        parsed = urlparse(self.facebook_url)
        noscheme = parsed.netloc + parsed.path
        self.facebook_url = 'http' + '://' + noscheme.replace("http://", "").replace("https://", "")
        
        if (self.facebook_url == "http://"):
            self.facebook_url = ""
    
    # Henter short_name hvis den finnes, og kutter av enden av headline hvis ikke.
    def get_short_name(self):
        if self.short_name:
            return self.short_name
        else:
            return self.headline[0:18].capitalize() + '...'
    
    # Returnerer antall ledige plasser, dvs antall plasser som
    # umiddelbart gir brukeren en garantert plass, og ikke bare
    # ventelisteplass.
    def free_places(self):
        try: return max(self.places - self.eventregistration_set.count(), 0)
        # Dersom arrangementet ikke krever påmelding er self.places None.
        except TypeError: return 0

    # Returnerer False (True) dersom arrangementet (ikke) har ledige plasser.
    def is_full(self):
        return self.free_places() == 0

    # Returnerer antall brukere som er påmeldt.
    def users_attending(self):
        try: return min(self.eventregistration_set.count(), self.places)
        # Dersom arrangementet ikke krever påmelding er self.places None.
        except TypeError: return 0

    # Returnerer antall brukere som står på venteliste.
    def users_waiting(self):
        try: return max(self.eventregistration_set.count() - self.places, 0)
        # Dersom arrangementet ikke krever påmelding er self.places None.
        except TypeError: return 0
    
    # Returnerer hvor mange prosent av plassene som er tatt
    def percent_full(self):
        return self.users_attending() * 100 / self.places

    # Returnerer antall brukere som er registrerte, og som dermed
    # enten er påmeldte eller står på venteliste.
    def users_registered(self):
        # Alternativt: self.users_attending() + self.users_waiting()
        return self.eventregistration_set.count()

    # Returnerer True dersom brukeren er registrert, False ellers.
    def is_registered(self, user):
        try:
            self.eventregistration_set.get(user=user)
            return True
        except EventRegistration.DoesNotExist:
            return False

    # Returnerer True dersom arrangementet har venteliste, False ellers.
    def has_waiting_list(self):
        return bool(self.has_queue)

    # Forsøker å melde brukeren på arrangementet.  Returnerer en
    # tekststreng som indikerer hvor vellykket operasjonen var.
    def register_user(self, user):
        if self.registration_deadline is None:
            msg = 'noreg'
        elif datetime.datetime.now() > self.registration_deadline:
            msg = 'closed'
        else:
            # TODO: Bruk select_for_update(), når den blir tilgjengelig.
            # https://docs.djangoproject.com/en/dev/ref/models/querysets/#select-for-update
            regs = self.eventregistration_set # .select_for_update()
            places = self.places
            try:
                reg = regs.get(user=user)
                msg = 'reg_exists'
            except EventRegistration.DoesNotExist:
                number = regs.count() + 1
                if number > places and not self.has_waiting_list():
                    msg = 'full'
                else:
                    reg = regs.create(event=self, user=user, number=number)
                    if reg.number <= places:
                        msg = 'attend'
                    else:
                        msg = 'queue'
        return msg

    # Melder brukeren av arrangementet. I praksis sørger metoden bare
    # for at brukeren ikke er påmeldt lengre, uavhengig av status før.
    def deregister_user(self, user):
        regs = self.eventregistration_set
        try:
            reg = regs.get(user=user)
            
            if self.deregistration_deadline is None:
                msg = 'not_allowed'
            elif self.deregistration_deadline < datetime.datetime.now():
                msg = 'dereg_closed'
            else:
                self.move_user_to_place(user, 1e12)
                self.eventregistration_set.get(user=user).delete()
                msg = 'dereg'

        # Brukeren er ikke påmeldt
        except EventRegistration.DoesNotExist:
            msg = 'not_reg'

        return msg

    # Flytter brukeren til den oppgitte plassen, eller først/sist
    # dersom plassnummeret er for lavt/høyt. Returnerer det nye
    # plassnummeret, eller None dersom brukeren ikke er påmeldt.
    def move_user_to_place(self, user, place):
        # TODO: Bruk select_for_update(), når den blir tilgjengelig.
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#select-for-update
        reg_set = self.eventregistration_set # .select_for_update()

        # Antall registreringer.
        regs = reg_set.count()

        # Dersom "ønsket" plass er ikke-positiv, endre til 1.
        new = max(1, place)

        # Dersom "ønsket" plass er høyere enn antall påmeldte, endre til siste plass.
        new = min(regs, new)

        # Forsøk å hente ut registreringen til brukeren som skal flyttes.
        try: u_reg = reg_set.get(user=user)
        # Returner dersom brukeren ikke er påmeldt.
        except EventRegistration.DoesNotExist: return None

        # Hent ut nåværende kønummer.
        current = u_reg.number

        # Brukeren er allerede på riktig plass.
        if current == new: return new

        # Brukeren skal oppover på ventelisten, dvs. lavere kønummer.
        elif new < current:
            # Flytt brukere mellom ny og gammel plass nedover.
            reg_set.filter(number__range=(new, current-1)).update(number=models.F('number')+1)

        # Brukeren skal nedover på ventelisten, dvs. høyere kønummer.
        else:
            # Flytt brukere mellom ny og gammel plass oppover.
            reg_set.filter(number__range=(current+1, new)).update(number=models.F('number')-1)

        # Lagre det nye kønummeret.
        u_reg.number = new
        u_reg.save()

        return new

    # Sletter overflødige registreringer.
    def _prune_queue(self):
        # Dersom registrering ikke trengs lengre.
        if not self.registration_required:
            self.eventregistration_set.all().delete()

        # Dersom arrangementet ikke har venteliste lengre,
        # eller antall plasser reduseres.
        elif not self.has_waiting_list():
            self.eventregistration_set.filter(number__gt=self.places).delete()

    # Tester at feltene har verdier som lovet i kommentarene ovenfor.
    def test_event_fields(self):
        assert isinstance(self.location, str) or isinstance(self.location, unicode)
        assert self.location != '' and self.location != u''

        assert self.event_start is not None
        assert isinstance(self.event_start, datetime.datetime)

        if self.event_end is not None:
            assert isinstance(self.event_end, datetime.datetime)
            assert self.event_end >= self.event_start

        if self.registration_deadline is not None:
            assert isinstance(self.registration_deadline, datetime.datetime)
            assert self.registration_deadline <= self.event_start 
            assert isinstance(self.places, int) or isinstance(self.places, long)
            assert self.places >= 0
            assert isinstance(self.has_queue, bool)
        else:
            assert self.places is None
            assert self.deregistration_deadline is None
            assert self.registration_start is None
            assert self.has_queue is None

        if self.registration_start is not None:
            assert isinstance(self.registration_start, datetime.datetime)
            assert self.registration_start <= self.registration_deadline

        if self.deregistration_deadline is not None:
            assert isinstance(self.deregistration_deadline, datetime.datetime)
            assert self.deregistration_deadline <= self.event_start
            if self.registration_start is not None:
                assert self.deregistration_deadline >= self.registration_start
            
        if self.has_queue is not None:
            assert isinstance(self.has_queue, bool)

        if self.places is not None:
            assert isinstance(self.places, int)
            assert self.places >= 0


class EventRegistration(models.Model):
    # Hvilket arrangement registreringen gjelder.
    event = models.ForeignKey(Event, blank=False, null=True)

    # Brukeren som er registrert.
    user = models.ForeignKey(User, blank=False, null=True)

    # Datoen brukeren ble registrert.
    date = models.DateTimeField(auto_now_add=True, null=True)

    # Kønummer som tilsvarer plass i køen.
    number = models.PositiveIntegerField(blank=False, null=True)

    def __unicode__(self):
        return u'EventRegistration: %s, %d: %s' % (self.event, self.number, self.user)

    # Returnerer True dersom registreringen er en plass på venteliste.
    def is_waiting_place(self):
        return self.number > self.event.places

    # Returnerer True dersom registreringen er en garantert plass.
    def is_attending_place(self):
        return self.number <= self.event.places
    is_attending_place.boolean = True
    is_attending_place.short_description = "har plass"

    class Meta:
        verbose_name = 'påmelding'
        verbose_name_plural = 'påmeldte'


class EventPenalty(models.Model):
    # Hvilket arrangement straffen gjelder.
    event = models.ForeignKey(Event)

    # Brukeren straffen gjelder.
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u'EventPenalty: %s, %s' % (self.event, self.user)

    def get_display_name(self):
        return u'%s' % (self.event)
