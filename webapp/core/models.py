#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : OKF - Spending Stories
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : proprietary journalism++
# -----------------------------------------------------------------------------
# Creation : 05-Aug-2013
# Last mod : 05-Aug-2013
# -----------------------------------------------------------------------------

from django.utils.translation import ugettext as _
from model_utils.managers     import PassThroughManager
from webapp.currency.models import Currency
# from economics                import CPI
from django.db                import models
import fields
import datetime

# from webapp.libs.economics import Inflation # changed version of Inflation                       

# CPI_DATA_URL = 'http://localhost:8000/static/data/datapackage.json'

YEAR_CHOICES = []
for r in range(1999, (datetime.datetime.now().year)):
    YEAR_CHOICES.append((r,r))

# -----------------------------------------------------------------------------
#
#    THEMES
#
# -----------------------------------------------------------------------------
class Theme(models.Model):
    title       = models.CharField(max_length=80)
    slug        = models.SlugField(primary_key=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    def __unicode__(self):
        return self.title

# class CurrencyQuerySet(models.query.QuerySet):
#     def find(self, currency=None):
#         return self.filter(iso_code=currency)


# class Currency(models.Model):
#     # The ISO code for currencies, possible values are based on what 
#     iso_code = models.CharField(primary_key=True, max_length=3)
#     name     = models.CharField(max_length=120)
#     # The exchange rate took from OpenExchangeRate
#     rate     = models.FloatField()
#     objects  = PassThroughManager.for_queryset_class(CurrencyQuerySet)()

#     def get_exchange_rate(self):
#         return self.rate

#     def __unicode__(self):
#         return "%s - %s" % (self.name, self.iso_code)

# class InflationWrapper(object):
#     instance = None
#     # Simple Singleton wrapper 
#     def __new__(klass, *args, **kargs):
#         if klass.instance is None:
#             klass.instance = object.__new__(klass, *args, **kargs)
#             klass.instance.cpi = CPI(datapackage=CPI_DATA_URL)
#             klass.instance.inflation = Inflation(source=klass.instance.cpi)
#         return klass.instance

#     def closest_ajustment_year(self, country=None):
#         cpi_closest = self.cpi.closest(
#             country=country, 
#             date=datetime.date.today(),
#             limit=datetime.timedelta(366*3))
#         return cpi_closest.date


#     def inflate(self, reference=None, country=None, amount=None):
#         '''
#         Inflate the given `amount` to the last available inflation year (see 
#         closest_ajustment_year)
#         '''
#         # the target date, i.e the date for which we gonna compute the inflation level 
#         # is found by getting the closest date to today having CPI data. 
#         target_date = self.closest_ajustment_year(country)
#         try: 
#             closest_ref_date = self.cpi.closest(country=country, date=reference).date # get the closest date for reference date
#         except:
#             closest_ref_date = target_date
#         # We inflate the given amount to the targeted year (the closent year available)
#         return self.inflation.inflate(
#             amount=amount, 
#             target=target_date, 
#             reference=closest_ref_date, 
#             country=country
#         ) 



class StoryQuerySet(models.query.QuerySet):
    relevance_query = "SELECT * FROM core_stories ORDER BY amount_usd_current / %s %s"

    def published(self):
        return self.filter(published=True)

    def relevance(self, amount):
        return self.all() 


class Story(models.Model):
    '''
    The model representing a spending
    '''
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    value      = models.IntegerField(_('The spending value')) # The spending amount 
    title      = models.CharField(_('Story title'), max_length=140)
    country    = fields.CountryField() # ISO code of the country 
    source     = models.URLField(_('Story\'s source URL'), max_length=140)
    currency   = models.ForeignKey(Currency)
    continuous = models.BooleanField(_('Is a countinuous spending'), default=False)
    published  = models.BooleanField(_('Publish this story'),        default=False)
    sticky     = models.BooleanField(_('Is a top story'),            default=False)
    year       = models.IntegerField(_('The spending year'),         choices=YEAR_CHOICES)
    objects    = PassThroughManager.for_queryset_class(StoryQuerySet)()
    
    def _inflate_value(self):
        '''
        Used to ajust the value of the story value
        ''' 
        raise Exception("TO BE IMPLEMENTED")
        # reference = datetime.date(self.year, 1, 1)
        # return round(InflationWrapper().inflate(
        #     amount=self.value,
        #     country=self.country,
        #     reference=reference))
    
    def _convert_to_usd(self):
        '''
        Return the current value converted into USD 
        ''' 
        exchange_rate = self.currency.get_exchange_rate()
        return round(self.value_current * exchange_rate)

    def _get_ajustement_year(self):
        '''
        Return the closest available year for inflation ajustement, ideally it 
        should return the current year - 1
        ''' 
        raise Exception("TO BE IMPLEMENTED")
        # return InflationWrapper().closest_ajustment_year(country=self.country).year

    # all calculated fields
    value_current            = property(_inflate_value)
    value_current_usd        = property(_convert_to_usd)
    inflation_ajustment_year = property(_get_ajustement_year)
