import os.path
import pickle
from typing import Any, Dict, Iterable, Optional, Tuple, Union

import numpy as np
import pandas as pd

import lac_covid19.const as const
import lac_covid19.lac_regions as lac_regions
import lac_covid19.scrape_daily_stats as scrape_daily_stats

DATE = const.DATE
CASES = const.CASES
DEATHS = const.DEATHS

RATE_SCALE = const.RATE_SCALE
CASES_NORMALIZED = RATE_SCALE
CASE_RATE = const.CASE_RATE
DEATH_RATE = const.DEATH_RATE
RATE_SCALE = const.RATE_SCALE

AREA = const.AREA
REGION = const.REGION
POPULATION = const.POPULATION


def demographic_table(table_dir: str, desc: str) -> str:
    """Returns the file path of the passed demographic description."""
    return os.path.join(table_dir, 'demographic_table_{}.csv'.format(desc))

TABLE_DIR = os.path.join(os.path.dirname(__file__), 'lacph_import')


def read_lacph_table(table_path: str,
                     indep_var: str, pop_var: str) -> pd.Series:
    """Produces a mapping between groups and population size"""

    df = pd.read_csv(table_path)
    df = df[df[pop_var].notna()]
    df[pop_var] = df[pop_var].convert_dtypes()

    return pd.Series(df[pop_var].to_numpy('int'),
                     index=df[indep_var].to_numpy('str'))


def read_csa_population() -> pd.Series:
    table_path = os.path.join(TABLE_DIR, 'city_community_table.csv')
    indep_var = 'geo_merge'
    pop_var = 'population'
    lac_raw = read_lacph_table(table_path, indep_var, pop_var)

    lb_pas = pd.Series((const.POPULATION_LONG_BEACH, const.POPULATION_PASADENA),
                       index=(const.CITY_OF_LB, const.CITY_OF_PAS))

    return lac_raw.append(lb_pas)


def read_demographic_population(demographic: str) -> pd.Series:
    """Helper function to reading in a demographic table for its population
        entries.
    """

    table_path = demographic_table(TABLE_DIR, demographic)
    characteristic = 'characteristic'
    population = 'POP'

    return read_lacph_table(table_path, characteristic, population)


def read_age_population() -> pd.Series:
    raw_values = read_demographic_population('age')
    new_names = (
        const.AGE_0_17,
        const.AGE_18_40,
        const.AGE_41_65,
        const.AGE_OVER_65,
    )
    return pd.Series(raw_values.to_numpy('int'), index=new_names)


def read_gender_population() -> pd.Series:
    return read_demographic_population('gender')


def read_race_population() -> pd.Series:
    raw_values = read_demographic_population('race')
    new_names = (
        const.RACE_AI_AN,
        const.RACE_ASIAN,
        const.RACE_BLACK,
        const.RACE_HL,
        const.RACE_NH_PI,
        const.RACE_WHITE,
    )
    return pd.Series(raw_values.to_numpy('int'), index=new_names)


def calculate_rate(date_group_entry: pd.Series, population_map: pd.Series,
                   group_col: str, count_col: str) -> float:
    """Calculates the case or death rate of a given entry and population
        mapping.
    """

    group = date_group_entry[group_col]
    count = date_group_entry[count_col]

    if group not in population_map or count is pd.NA:
        return np.nan

    return round((count / population_map[group] * RATE_SCALE), 2)


def query_all_dates() -> Tuple[Dict[str, Any]]:
    """Loads in previously scraped press releases. See query_all_dates() in
        module scrape_daily_stats for more information.
    """

    if not os.path.isfile(const.FILE_ALL_DATA_RAW):
        return scrape_daily_stats.query_all_dates()

    with open(const.FILE_ALL_DATA_RAW, 'rb') as f:
        return pickle.load(f)


def tidy_data(df: pd.DataFrame, var_desc: str, value_desc: str,
              make_categorical: bool = True) -> pd.DataFrame:
    """Reshapes data to a tidy format.

    Args:
        df: The DataFrame to be reshaped.
        var_desc: The name given to the newly created variable column.
            (Example: Gender, Race)
        value_desc: The name given to the newly created value column.
            (Example: Cases, Deaths)
        make_categorical: Convert the variable column data type to a category
            instead of a string.
    Returns:
        Input DataFrame in a tidy format.
    """

    df = df.melt(id_vars=DATE, var_name=var_desc, value_name=value_desc)

    variable_type = 'category' if make_categorical else 'string'
    df[var_desc] = df[var_desc].astype(variable_type)

    return df.sort_values(by=[DATE, var_desc], ignore_index=True)


def access_date(
        daily_pr: Dict[str, Any]) -> Dict[str, Union[int, pd.Timestamp]]:
    return pd.to_datetime(daily_pr[DATE])


def make_section_ts(daily_pr: Dict, section: str) -> Dict[str, Any]:
    """Extracts a section and appends the corersponding date."""
    data = daily_pr[section]
    data[DATE] = access_date(daily_pr)
    return data


def create_main_stats(
        many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of total cases, deaths, and hospitalizaitons."""

    TEST_RESULTS = const.TEST_RESULTS
    PERCENT_POSITIVE = const.PERCENT_POSITIVE_TESTS

    data = {
        DATE: map(access_date, many_daily_pr),
        CASES: map(lambda x: x[CASES], many_daily_pr),
        const.HOSPITALIZATIONS:
            map(lambda x: x[const.HOSPITALIZATIONS], many_daily_pr),
        DEATHS: map(lambda x: x[DEATHS], many_daily_pr),
        TEST_RESULTS: map(lambda x: x[TEST_RESULTS], many_daily_pr),
        PERCENT_POSITIVE: map(lambda x: x[PERCENT_POSITIVE], many_daily_pr)
    }

    df = pd.DataFrame(data)
    df[TEST_RESULTS] = df[TEST_RESULTS].convert_dtypes()
    df[PERCENT_POSITIVE] = df[PERCENT_POSITIVE].convert_dtypes()

    return df


def create_by_age(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by age group"""

    AGE_GROUP = const.AGE_GROUP

    data = map(lambda x: make_section_ts(x, const.CASES_BY_AGE), many_daily_pr)
    df = tidy_data(pd.DataFrame(data), const.AGE_GROUP, CASES)

    age_pop = read_age_population()
    df[CASE_RATE] = df.apply(
        lambda x: calculate_rate(x, age_pop, AGE_GROUP, CASES), axis='columns')

    return df


def create_by_gender(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by gender."""

    GENDER = const.GENDER
    CASES_BY_GENDER = const.CASES_BY_GENDER

    data = map(lambda x: make_section_ts(x, CASES_BY_GENDER), many_daily_pr)

    df = tidy_data(pd.DataFrame(data), GENDER, CASES, False)
    df = df[df[GENDER] != const.OTHER]
    df[GENDER] = df[GENDER].astype('category')
    df[CASES] = df[CASES].convert_dtypes()

    gender_pop = read_gender_population()
    df[CASE_RATE] = df.apply(
        lambda x: calculate_rate(x, gender_pop, GENDER, CASES), axis='columns')

    return df


def create_by_race(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases and deaths by race."""

    RACE = const.RACE

    def calculate_rate(date_race_entry: pd.Series, variable_name: str,
                       race_pop: pd.Series) -> float:
        count = date_race_entry[variable_name]
        race = date_race_entry[RACE]
        if race == 'Other' or count is pd.NA:
            return np.nan

        return round((count / race_pop.get(race) * RATE_SCALE), 2)

    cases_raw = map(lambda x: make_section_ts(x, const.CASES_BY_RACE),
                    many_daily_pr)
    deaths_raw = map(lambda x: make_section_ts(x, const.DEATHS_BY_RACE),
                     many_daily_pr)

    # Create cases and deaths tables seperately
    df_cases = (pd.DataFrame(cases_raw)
                .melt(id_vars=DATE, var_name=RACE, value_name=CASES))
    df_deaths = (pd.DataFrame(deaths_raw)
                 .melt(id_vars=DATE, var_name=RACE, value_name=DEATHS))

    # Merge cases and deaths
    df_all = df_cases.merge(df_deaths, on=[DATE, RACE], how='left')
    df_all[RACE] = df_all[RACE].astype('category')
    df_all[CASES] = df_all[CASES].convert_dtypes()
    df_all[DEATHS] = df_all[DEATHS].convert_dtypes()

    df_all = df_all.sort_values(by=[DATE, RACE]).reset_index(drop=True)

    race_pop = read_race_population()

    df_all[CASE_RATE] = df_all.apply(
        lambda x: calculate_rate(x, CASES, race_pop), axis='columns')

    df_all[DEATH_RATE] = df_all.apply(
        lambda x: calculate_rate(x, DEATHS, race_pop), axis='columns')

    return df_all[[DATE, RACE, CASES, CASE_RATE, DEATHS, DEATH_RATE]]


def single_day_area(daily_pr: Dict[str, Any]) -> pd.DataFrame:
    """Converts the area case count to a DataFrame and assigns a
        Los Angeles County region.
    """

    # Leverage the provided grouping of area, cases, and case rate.
    df = pd.DataFrame(daily_pr[AREA], columns=(AREA, CASES, CASE_RATE))
    df[CASES] = df[CASES].convert_dtypes()

    # Attach a date to each entry
    record_date = (pd.Series(pd.to_datetime(daily_pr[DATE])).repeat(df.shape[0])
                   .reset_index(drop=True))
    df[DATE] = record_date

    # Assings region category to every area
    df[REGION] = df.apply(
        lambda x: lac_regions.REGION_MAP.get(x[AREA], pd.NA),
        axis='columns').astype('string')

    return df[[DATE, REGION, AREA, CASES, CASE_RATE]]


def create_by_area(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by area."""

    all_dates = map(single_day_area, many_daily_pr)
    df = pd.concat(all_dates, ignore_index=True)

    df[REGION] = df[REGION].astype('category')
    df[AREA] = df[AREA].astype('string')

    return df


def aggregate_locations(
        df_all_loc: pd.DataFrame,
        exclude_date_area: Optional[Iterable[Tuple[str, str]]] = None
        ) -> pd.DataFrame:
    """Aggregates the individual areas to larger regions and computes the case
        rate. exclude_date_area is of form (date, area) """

    def filter_mask(
        date_area_entry: pd.Series, exclusions: Tuple[str, str]) -> bool:
        date_ = str(date_area_entry[const.DATE])[:10]
        area = date_area_entry[const.AREA]
        return not (date_, area) in exclusions

    area_population = read_csa_population()
    df_all_loc = df_all_loc.drop(columns=CASE_RATE)

    # Drop areas with correctional facility outbreaks from average
    # Identify just the areas, using asterisk suffix
    corr_facility_filter = df_all_loc[AREA].apply(lambda x: x[-1] == '*')
    # Make these areas - with and without asterisk - into list 
    corr_facility_areas = list(
        df_all_loc.loc[corr_facility_filter, [AREA]]
        .groupby(AREA).groups.keys())
    corr_facility_areas += [x.rstrip('*') for x in corr_facility_areas]
    corr_facility_areas = np.array(corr_facility_areas, dtype='str')            
    # Filter these areas, both before and after outbreaks
    df_all_loc = df_all_loc[~df_all_loc[AREA].isin(corr_facility_areas)]

    # Drop erroneous dates and forward fill previous records
    if exclude_date_area:
        drop_entry = df_all_loc.apply(
            lambda x: (x[DATE].isoformat()[:10], x[AREA]) in exclude_date_area,
            axis='columns') 
        df_all_loc.loc[drop_entry, CASES] = pd.NA
        
        # Forward fill using previous area locations
        for area in [x[1] for x in exclude_date_area]:
            area_cases = df_all_loc.loc[df_all_loc[AREA] == area, CASES]
            area_cases = area_cases.fillna(method='pad')
            # Put area cases back into wider area time series
            df_all_loc.loc[area_cases.index, CASES] = area_cases

    # Keep only areas in a region
    df_all_loc = df_all_loc[df_all_loc[REGION].notna()]
    population_col = (df_all_loc[AREA].apply(area_population.get)
                      .convert_dtypes())
    population_col.name = POPULATION

    df_all_loc = df_all_loc.join(population_col, how='left')
    # Use case count and population count to normalize cases
    df_region = df_all_loc.groupby([DATE, REGION]).sum().reset_index()
    # Compute case rate using the estimated area populations.
    df_region[CASE_RATE] = (
        (df_region[CASES] / df_region[POPULATION] * RATE_SCALE)
        .round(2))

    return df_region.drop(columns=POPULATION)


def create_custom_region(df_all_loc: pd.DataFrame,
                         areas: Iterable) -> pd.DataFrame:
    """Tallies the cases and case rate of a custom defined region."""

    area_population = read_csa_population()
    region_pop = 0
    for area in areas:
        region_pop += area_population[area]

    # Takes out the notation of a correctional facility outbreak
    df_all_loc[AREA] = df_all_loc[AREA].apply(lambda x: x.rstrip('*'))

    # Keep only areas from parameter
    df_custom_region = df_all_loc[df_all_loc[AREA].isin(areas)]
    df_custom_region = df_custom_region.groupby(DATE).sum()

    case_multiplier = RATE_SCALE / region_pop
    df_custom_region[CASE_RATE] = (df_custom_region[CASES]
                                   * case_multiplier).round(2)

    return df_custom_region.reset_index()


def area_slowed_increase(
        df_area_ts: pd.DataFrame, days_back: int, threshold: float,
        by_region: bool = True) -> pd.Series:
    """Determines which locations have slowed the rate of cases recently.

    Args:
        df_area_ts: The area cases time series to use for the calculation.
        days_back: The number of recent days to use in determining rate.
        threshold: Maximum ratio of cases jump over median cases to allow to
            qualify as slowed cases.
    """

    min_cases = 'Minimum Cases'
    max_cases = 'Maximum Cases'
    curr_cases = 'Current Cases'
    prop_inc = 'Proportion Increase'

    location = REGION if by_region else AREA

    # Filter to provided time frame
    start_date = df_area_ts[DATE].max() - pd.Timedelta(days=days_back)
    df_area_ts = (
        df_area_ts[df_area_ts[DATE] >= start_date]
        .loc[:, [location, CASES]])

    # Compute summary stats for each area
    area_group = df_area_ts.groupby(location)
    df_min_cases = area_group.min().rename(columns={CASES: min_cases})
    df_max_cases = area_group.max().rename(columns={CASES: max_cases})
    df_curr_cases = area_group.last().rename(columns={CASES: curr_cases})

    # Construct the dataframe to use for analysis
    area_cases = (
        pd.concat((df_min_cases, df_max_cases, df_curr_cases), axis='columns')
        .reset_index())

    # Compute relative case increase over duration
    area_cases[prop_inc] = ((area_cases[max_cases] - area_cases[min_cases])
                            / area_cases[curr_cases])

    # Keep only area under threshold
    area_cases = area_cases[area_cases[prop_inc] < threshold]
    return area_cases[location].astype('string')


if __name__ == "__main__":
    every_day = query_all_dates()
    last_week = every_day[-7:]
    today = every_day[-1]

    # df_summary = create_main_stats(every_day)
    # df_age = create_by_age(every_day)
    # df_gender = create_by_gender(every_day)
    # df_race = create_by_race(last_week)
    df_area = create_by_area(last_week)
    # df_region = aggregate_locations(df_area)

    # csa_pop = read_csa_population()
    # df_custom_region = create_custom_region(
    #     df_area, ('City of Burbank', 'City of Glendale'))
