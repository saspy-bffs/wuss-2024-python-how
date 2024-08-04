# import from standard library packages
import random
from datetime import date, datetime
import pathlib

# import from third-party packages
from faker import Faker
import numpy
import pandas

# import from local packages
import helper_fcns

# setup global object for generating fake data
fake = Faker()

# setup global pseudo-random number generator
global_prng = numpy.random.default_rng()

# setup path for output files
output_path = pathlib.Path.cwd() / 'fakes'
output_path.mkdir(parents=True, exist_ok=True)

# setup datetime stamp for output files
datetime_stamp = datetime.strftime(datetime.now(), '%Y_%m_%dT%H_%M_%S')

# set parameters for patients_df DataFrame
number_of_rows_for_patients_df = 2**12
date_lower_bound_for_patients_df = date(year=1940, month=1, day=1)
date_upper_bound_for_patients_df = date(year=1949, month=12, day=31)


# iteratively build contents for patients DataFrame with infrequent data issues
patients_list = []
for n in range(number_of_rows_for_patients_df):

    # determine whether to output a test user as an infrequent data issue
    create_test_user_flag = 1 if random.uniform(0,1) < 0.001 else 0

    # determine whether to output incorrect units as an infrequent data issue
    create_height_in_meters_flag = 1 if random.uniform(0,1) < 0.005 else 0

    # determine whether to output incorrect encoding as an infrequent data issue
    create_member_as_text_flag = 1 if random.uniform(0,1) < 0.005 else 0

    # create a random centimeter height value
    height_in_cm = round(global_prng.normal(loc=175, scale=7.5), 1)

    # use the flags above when creating a new patient record
    new_patient = [
        # build a value for column 'study_id'
        f'S-{n:04}',

        # build a value for column 'first_name'
        "TEST" if create_test_user_flag else fake.first_name(),

        # build a value for column 'middle_name'
        "" if create_test_user_flag else fake.first_name(),

        # build a value for column 'last_name'
        "PATIENT" if create_test_user_flag else fake.last_name(),

        # build a value for column 'suffix'
        "" if create_test_user_flag else fake.suffix(),

        # build a value for column 'height'
        (
            height_in_cm/100
            if create_height_in_meters_flag
            else height_in_cm
        ),

        # build a value for column 'member'
        (
            random.choice(['N', 'Y'])
            if create_member_as_text_flag
            else fake.pyint(min_value=0, max_value=1)
        ),

        # build a value for column 'birth_date'
        '1840-12-31' if create_test_user_flag else fake.date_between_dates(
            date_lower_bound_for_patients_df,
            date_upper_bound_for_patients_df,
        ).strftime('%Y-%m-%d'),
    ]
    patients_list.append(new_patient)

# assemble final patients DataFrame
patients_df = pandas.DataFrame(
    patients_list,
    columns=[
        'study_id',
        'first_name',
        'middle_name',
        'last_name',
        'suffix',
        'height',
        'member',
        'birth_date',
    ],
)

# check for data errors
print(f'Test patients:\n{patients_df[patients_df["first_name"] == "TEST"]}')
print(f'Heights in meters:\n{patients_df[patients_df["height"] < 10]}')
print(f'Member = "Y":\n{patients_df[patients_df["member"] == "Y"]}')
print(f'Member = "N":\n {patients_df[patients_df["member"] == "N"]}')

# output patients DataFrame into designated directory
patients_df_output_file = output_path / f'patients-{datetime_stamp}.csv'
print(f'DataFrame now being written to disk as {patients_df_output_file}')
patients_df.to_csv(patients_df_output_file, index=False)


# iteratively build contents for dispenses DataFrame using a helper function
date_lower_bound_for_dispenses_df = date(year=1990, month=1, day=1)
date_upper_bound_for_dispenses_df = date(year=2009, month=12, day=31)
dispenses_list = []
for study_id in patients_df['study_id']:
    new_dispenses = helper_fcns.build_dispenses(
        study_id=study_id,
        dates_lb=date_lower_bound_for_dispenses_df,
        dates_ub=date_upper_bound_for_dispenses_df,
        fakes_generator=fake,
        rng=global_prng,
    )
    dispenses_list.extend(new_dispenses)

# assemble final dispenses DataFrame
dispenses_df = pandas.DataFrame(
    dispenses_list,
    columns=[
        'study_id',
        'dispense_date',
        'drug_id',
        'days_supply',
    ],
)

# output dispenses DataFrame to designated directory
dispenses_df_output_file = output_path / f'dispenses-{datetime_stamp}.csv'
print(f'DataFrame now being written to disk as {dispenses_df_output_file}')
dispenses_df.to_csv(dispenses_df_output_file, index=False)


# iteratively build contents for diagnoses DataFrame using a helper function
date_lower_bound_for_diagnoses_df = date(year=2010, month=1, day=1)
date_upper_bound_for_diagnoses_df = date(year=2019, month=12, day=31)
diagnoses_list = []
for study_id in patients_df['study_id']:
    new_diagnoses = helper_fcns.build_diagnoses(
        study_id=study_id,
        dates_lb=date_lower_bound_for_diagnoses_df,
        dates_ub=date_upper_bound_for_diagnoses_df,
        fakes_generator=fake,
    )
    diagnoses_list.extend(new_diagnoses)

# assemble final diagnoses DataFrame
diagnoses_df = pandas.DataFrame(
    diagnoses_list,
    columns=[
        'study_id',
        'dx_date',
        'dx_code',
        'dx_name',
    ],
)

# output diagnoses DataFrame to into designated directory
diagnoses_df_output_file = output_path / f'diagnoses-{datetime_stamp}.csv'
print(f'DataFrame now being written to disk as {diagnoses_df_output_file}')
diagnoses_df.to_csv(diagnoses_df_output_file, index=False)
