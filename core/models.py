from django.db import models


class CauseOfDeath(models.Model):
    """One named cause, e.g. "Ischaemic heart diseases".

    Table name follows the team ERD (Cause_of_Death) so the existing
    health_data_gateway lookups find it.
    """

    cause_name = models.CharField(max_length=255, unique=True)
    cause_category = models.CharField(max_length=120, blank=True)
    cause_code = models.CharField(max_length=32, blank=True)

    class Meta:
        db_table = 'cause_of_death'
        ordering = ['cause_name']

    def __str__(self):
        return self.cause_name


class MortalityRecord(models.Model):
    """Deaths for one cause within one age band and sex.

    Loaded from the DOSM "Statistics on Causes of Death" workbook by
    `manage.py import_cod`. One row per (year, location, age_band, sex, cause).
    """

    AGE_BANDS = [
        ('0-14', '0-14'),
        ('15-40', '15-40'),
        ('41-59', '41-59'),
        ('60+', '60 and over'),
    ]
    SEXES = [('male', 'Male'), ('female', 'Female'), ('both', 'Both')]

    # The workbook lists medically and non-medically certified deaths
    # separately. Only the medically certified list is published in English
    # and it is the more reliable basis, so that is what we load.
    CERTIFICATIONS = [
        ('medical', 'Medically certified'),
        ('non_medical', 'Non-medically certified'),
    ]

    cause = models.ForeignKey(
        CauseOfDeath, on_delete=models.CASCADE, related_name='mortality_records'
    )
    year = models.PositiveIntegerField()
    location = models.CharField(max_length=120, default='Malaysia')
    age_band = models.CharField(max_length=16, choices=AGE_BANDS)
    sex = models.CharField(max_length=8, choices=SEXES)
    certification = models.CharField(
        max_length=16, choices=CERTIFICATIONS, default='medical'
    )
    rank = models.PositiveSmallIntegerField()
    death_count = models.PositiveIntegerField()
    # Percentage of all deaths in this age band and sex, as published.
    share_pct = models.FloatField()
    # Deaths from every cause in this group, so shares can be recomputed.
    group_total = models.PositiveIntegerField()

    class Meta:
        db_table = 'mortality_record'
        ordering = ['age_band', 'sex', 'rank']
        constraints = [
            models.UniqueConstraint(
                fields=['year', 'location', 'age_band', 'sex',
                        'certification', 'cause'],
                name='unique_mortality_row',
            )
        ]

    def __str__(self):
        return f'{self.cause} / {self.age_band} / {self.sex} ({self.year})'
