# import from standard library packages
from datetime import date, datetime, timedelta
import random
from typing import List, Optional

# import from third-party packages
from faker import Faker
from numpy.random import Generator

# define heart failure ICD-10 codes
hf_icd10_codes = {
    'I50.0': 'Congestive heart failure',
    'I50.1': 'Left ventricular failure',
    'I50.2': 'Systolic (congestive) heart failure',
    'I50.20': 'Unspecified systolic (congestive) heart failure',
    'I50.21': 'Acute systolic (congestive) heart failure',
    'I50.22': 'Chronic systolic (congestive) heart failure',
    'I50.23': 'Acute on chronic systolic (congestive) heart failure',
    'I50.3': 'Diastolic (congestive) heart failure',
    'I50.30': 'Unspecified diastolic (congestive) heart failure',
    'I50.31': 'Acute diastolic (congestive) heart failure',
    'I50.32': 'Chronic diastolic (congestive) heart failure',
    'I50.33': 'Acute on chronic diastolic (congestive) heart failure',
    'I50.4': 'Combined systolic (congestive) and diastolic (congestive) heart failure',
    'I50.40': 'Unspecified combined systolic (congestive) and diastolic (congestive) heart failure',
    'I50.41': 'Acute combined systolic (congestive) and diastolic (congestive) heart failure',
    'I50.42': 'Chronic combined systolic (congestive) and diastolic (congestive) heart failure',
    'I50.43': 'Acute on chronic combined systolic (congestive) and diastolic (congestive) heart failure',
    'I50.9': 'Heart failure, unspecified',
    'I11.0': 'Hypertensive heart disease with (congestive) heart failure',
    'I13.0': 'Hypertensive heart and chronic kidney disease with heart failure and stage 1 through stage 4 chronic kidney disease, or unspecified chronic kidney disease',
    'I13.2': 'Hypertensive heart and chronic kidney disease with heart failure and with stage 5 chronic kidney disease, or end stage renal disease',
    'I97.13': 'Postprocedural heart failure',
    'I97.130': 'Postprocedural heart failure following cardiac surgery',
    'I97.131': 'Postprocedural heart failure following other surgery',
    'I09.81': 'Heart failure rheumatic (chronic) (inactive) (with chorea)',
}


# define a function to recursively build dispenses
def build_dispenses(
    study_id: str,
    dates_lb: date,
    dates_ub: date,
    fakes_generator: Faker,
    rng: Generator,
    current_dispenses: Optional[List] = None,
) -> List:

    # determine whether to use hyphenated drug name as an infrequent data issue
    create_hyphenated_name_flag = 1 if random.uniform(0,1) < 0.1 else 0

    # if needed, create an initial dispense and kick off recursively building
    # additional dispenses for the provided study_id
    if current_dispenses is None:
        dispense_date = fakes_generator.date_between_dates(
            dates_lb,
            dates_ub,
        ).strftime('%Y-%m-%d')
        drug_id = (
            random.choice(['Drug-A', 'Drug-B'])
            if create_hyphenated_name_flag
            else random.choice(['Drug A', 'Drug B'])
        )
        days_supply = random.choice([30, 60, 90])
        current_dispenses = [
            [
                study_id,
                dispense_date,
                drug_id,
                days_supply,
            ],
        ]
        return build_dispenses(
            study_id=study_id,
            dates_lb=dates_lb,
            dates_ub=dates_ub,
            fakes_generator=fakes_generator,
            rng=rng,
            current_dispenses=current_dispenses,
        )

    # otherwise, randomly decide whether to create a new dispense
    most_recent_dispense_date = datetime.strptime(
        current_dispenses[-1][1],
        '%Y-%m-%d'
    ).date()
    most_recent_days_supply = current_dispenses[-1][3]
    days_until_next_dispense = round(
        rng.lognormal() * 7 + (most_recent_days_supply - 7)
    )
    next_dispense_date = (
        most_recent_dispense_date +
        timedelta(days=days_until_next_dispense)
    )
    if (
        random.uniform(a=0, b=1) <= .85-(len(current_dispenses)-1)/10
        and
        next_dispense_date <= dates_ub
    ):
        drug_id = current_dispenses[-1][2]
        next_days_supply = random.choice([30, 60, 90])
        current_dispenses.append(
            [
                study_id,
                next_dispense_date.strftime('%Y-%m-%d'),
                drug_id,
                next_days_supply,
            ],
        )
        return build_dispenses(
            study_id=study_id,
            dates_lb=dates_lb,
            dates_ub=dates_ub,
            fakes_generator=fakes_generator,
            rng=rng,
            current_dispenses=current_dispenses,
        )
    else:
        return current_dispenses


# define a function to recursively build diagnoses
def build_diagnoses(
    study_id: str,
    dates_lb: date,
    dates_ub: date,
    fakes_generator: Faker,
    current_diagnoses: Optional[List] = None,
) -> List:

    # if needed, create an initial empty diagnoses list
    if current_diagnoses is None:
        current_diagnoses = []

    # if needed, create an initial diagnosis and kick off recursively building
    # additional diagnoses for the provided study_id
    if not current_diagnoses and random.uniform(a=0, b=1) <= .20:
        dx_date = fakes_generator.date_between_dates(
            dates_lb,
            dates_ub,
        ).strftime('%Y-%m-%d')
        dx_code = random.choice(list(hf_icd10_codes.keys()))
        dx_name = hf_icd10_codes[dx_code]
        current_diagnoses = [
            [
                study_id,
                dx_date,
                dx_code,
                dx_name,
            ],
        ]
        return build_diagnoses(
            study_id=study_id,
            dates_lb=dates_lb,
            dates_ub=dates_ub,
            fakes_generator=fakes_generator,
            current_diagnoses=current_diagnoses,
        )
    elif not current_diagnoses:
        return current_diagnoses

    # otherwise, randomly decide whether to create a new diagnosis
    if random.uniform(a=0, b=1) <= .50:
        most_recent_dx_date = datetime.strptime(
            current_diagnoses[-1][1],
            '%Y-%m-%d'
        ).date()
        next_dx_date = fakes_generator.date_between_dates(
            most_recent_dx_date,
            dates_ub,
        )
        next_dx_code = random.choice(list(hf_icd10_codes.keys()))
        next_dx_name = hf_icd10_codes[next_dx_code]
        current_diagnoses.append(
            [
                study_id,
                next_dx_date.strftime('%Y-%m-%d'),
                next_dx_code,
                next_dx_name,
            ],
        )
        return build_diagnoses(
            study_id=study_id,
            dates_lb=dates_lb,
            dates_ub=dates_ub,
            fakes_generator=fakes_generator,
            current_diagnoses=current_diagnoses,
        )
    else:
        return current_diagnoses
