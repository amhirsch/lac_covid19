import os.path
import pickle
from typing import Any, Dict, Iterable, Tuple

import numpy as np
import pandas as pd

import lac_covid19.cache_mgmt as cache_mgmt
import lac_covid19.const as const
import lac_covid19.lacph_prid as lacph_prid
import lac_covid19.lac_regions as lac_regions
import lac_covid19.scrape_daily_stats as scrape_daily_stats

REGION = 'Region'
POPULATION = 'Population'


def query_all_dates(use_cached: bool = True) -> Tuple[Dict[str, Any]]:
    def assert_check(contents: Any) -> bool:
        return ((type(contents) is tuple) and
                all(map(lambda x: type(x) is dict, contents)))

    FILENAME = 'all_dates.pickle'
    all_dates = None

    if use_cached:
        all_dates = cache_mgmt.read_cache(FILENAME, True, assert_check, lambda x: pickle.load(x))

    if not all_dates:
        all_dates = tuple(map(lambda x: scrape_daily_stats.query_single_date(x),
                              lacph_prid.DAILY_STATS))
        cache_mgmt.write_cache(all_dates, FILENAME, True, assert_check,
                               lambda x, y: pickle.dump(x, y))

    return all_dates


def access_generic(*key_name):
    dict_access = None
    if len(key_name) == 1:
        dict_access = lambda x: x[key_name[0]]
    elif len(key_name) == 2:
        dict_access = lambda x: x[key_name[0]][key_name[1]]
    elif len(key_name) == 3:
        dict_access = lambda x: x[key_name[0]][key_name[1]][key_name[2]]

    return dict_access


def tidy_data(df: pd.DataFrame, var_desc: str, value_desc: str) -> pd.DataFrame:
    df = df.melt(id_vars=const.DATE, var_name=var_desc, value_name=value_desc)
    df[var_desc] = df[var_desc].astype('category')
    df.sort_values(by=[const.DATE, var_desc], ignore_index=True, inplace=True)
    return df


def access_date(pr_stats):
    return pd.to_datetime(pr_stats[const.DATE], unit='D')


def date_limits(date_series):
    return (date_series[const.DATE].min(), date_series[const.DATE].max())


def make_df_dates(pr_stats):
    data = {
        const.DATE:
            map(lambda x: pd.to_datetime(x[const.DATE]), pr_stats),
        const.CASES:
            map(lambda x: x[const.CASES], pr_stats),
        const.HOSPITALIZATIONS:
            map(lambda x: x[const.HOSPITALIZATIONS], pr_stats),
        const.DEATHS:
            map(lambda x: x[const.DEATHS], pr_stats)
    }
    return pd.DataFrame(data)


def single_day_race(pr_stats):
    recorded_races = set()
    indiv_race = []

    for race in pr_stats[const.CASES_BY_RACE].keys():
        recorded_races.add(race)
    for race in pr_stats[const.DEATHS_BY_RACE].keys():
        recorded_races.add(race)

    for race in recorded_races:
        data = {
            const.DATE: pd.to_datetime(pr_stats[const.DATE]),
            const.RACE: race,
            const.CASES: pr_stats[const.CASES_BY_RACE].get(race, np.nan),
            const.DEATHS: pr_stats[const.DEATHS_BY_RACE].get(race, np.nan)
        }
        indiv_race.append(pd.DataFrame(data, index=(0,)))

    df = pd.concat(indiv_race, ignore_index=True)
    df[const.CASES] = df[const.CASES].convert_dtypes()
    df[const.DEATHS] = df[const.DEATHS].convert_dtypes()
    return df


def make_by_race(pr_stats):
    pr_stats = tuple(filter(lambda x: (x[const.CASES_BY_RACE] or x[const.DEATHS_BY_RACE]), pr_stats))
    per_day = tuple(map(lambda x: single_day_race(x), pr_stats))
    per_day = tuple(filter(lambda x: x is not None, per_day))
    df = pd.concat(per_day, ignore_index=True)
    df[const.RACE] = df[const.RACE].astype('category')
    return df


def single_day_loc(pr_stats):
    df = pd.DataFrame(pr_stats[const.LOCATIONS], columns=(const.LOC_NAME, const.CASES, const.CASES_NORMALIZED))
    df[const.CASES] = df[const.CASES].convert_dtypes()
    record_date = pd.Series(pd.to_datetime(pr_stats[const.DATE])).repeat(df.shape[0]).reset_index(drop=True)
    df[const.DATE] = record_date
    df[REGION] = df.apply(lambda x: lac_regions.REGION_MAP.get(x[const.LOC_NAME], None), axis='columns').astype('string')
    df = df[[const.DATE, REGION, const.LOC_NAME, const.CASES, const.CASES_NORMALIZED]]
    return df


def make_by_loc(pr_stats, use_cached=True):
    FILENAME = os.path.join(cache_mgmt.CACHE_DIR, 'location-cases.pickle')
    df = None
    if use_cached and os.path.isfile(FILENAME):
        df = pd.read_pickle(FILENAME)
    else:
        all_dates = map(lambda x: single_day_loc(x), pr_stats)
        df = pd.concat(all_dates, ignore_index=True)
        df[REGION] = df[REGION].astype('category')
        df[const.LOC_NAME] = df[const.LOC_NAME].astype('string')
        df.to_pickle(FILENAME)

    return df


def infer_pop(df_loc: pd.DataFrame, loc_type: str, loc_name: str):
    if loc_type == const.CITY:
        if loc_name == 'Long Beach':
            return const.POPULATION_LONG_BEACH
        elif loc_name == 'Pasadena':
            return const.POPULATION_PASADENA
    df_loc = df_loc[(df_loc[const.LOC_CAT] == loc_type) & (df_loc[const.LOC_NAME] == loc_name)]
    pop_estimation = df_loc[const.CASES] / df_loc[const.CASES_NORMALIZED] * const.CASE_RATE_SCALE
    pop_estimation = pop_estimation.round(0)
    return pop_estimation.median()


def is_select_location(location_entry: pd.Series, locations: Iterable[Tuple[str, str]]) -> bool:
    return (location_entry[const.LOC_CAT], location_entry[const.LOC_NAME]) in locations


def aggregate_locations(df_all_loc: pd.DataFrame) -> pd.DataFrame:
    # Filter, keeping only the areas in a region
    df_all_loc = df_all_loc[df_all_loc[REGION].notna()]
    # Estimate the populations using the relationship between cases and case rate
    daily_pop_estimate = df_all_loc[const.CASES] / df_all_loc[const.CASES_NORMALIZED] * const.CASE_RATE_SCALE
    daily_pop_estimate.name = POPULATION
    daily_pop_estimate = daily_pop_estimate.round().convert_dtypes()
    df_all_loc = df_all_loc.join(daily_pop_estimate, how='inner')
    df_all_loc.drop(const.CASES_NORMALIZED, axis='columns', inplace=True)
    # Use each daily estimate to come up with single reasonable guess
    filtered_pop_estimate = df_all_loc[[const.LOC_NAME, POPULATION]]
    filtered_pop_estimate = filtered_pop_estimate[filtered_pop_estimate[POPULATION].notna()]
    area_estimate = filtered_pop_estimate.groupby(const.LOC_NAME).median().reset_index().round().convert_dtypes()
    area_estimate[REGION] = area_estimate.apply(
        lambda x: lac_regions.REGION_MAP[x[const.LOC_NAME]], axis='columns').astype('category')
    # Sum the populations to get per region
    region_estimate = area_estimate.loc[:, [REGION, POPULATION]].groupby(REGION).sum().loc[:, POPULATION]

    # Aggregate the cases and population into regions
    df_region = (df_all_loc[[const.DATE, REGION, const.CASES]]
                 .groupby([const.DATE, REGION]).sum().reset_index())
    df_region[const.CASES_NORMALIZED] = (
        df_region.apply((lambda x:
        x[const.CASES] / region_estimate[x[REGION]] * const.CASE_RATE_SCALE),
        axis='columns').round(2)
    )
    return df_region


def location_cases_comparison(df_all_loc: pd.DataFrame, region_def: Dict[str, Tuple[str, str]]) -> pd.DataFrame:
    REGION = 'Region'
    region_time_series = {}
    for region in region_def:
        df_indiv_region = aggregate_locations(df_all_loc, region_def[region])
        region_name = pd.Series(region, name=REGION, dtype='string').repeat(df_indiv_region.shape[0]).reset_index(drop=True)
        df_indiv_region = pd.concat((df_indiv_region, region_name), axis=1)
        df_indiv_region = df_indiv_region[[const.DATE, REGION, const.CASES_NORMALIZED]]
        region_time_series[region] = df_indiv_region
    df_all_regions = pd.concat(region_time_series.values())
    df_all_regions[REGION] = df_all_regions[REGION].astype('category')
    df_all_regions.sort_values(by=const.DATE, ignore_index=True, inplace=True)
    return df_all_regions


def location_some_decrease(df_location, days_back):
    start_date = df_location[const.DATE].max() - pd.Timedelta(days=days_back)
    df_location = df_location[df_location[const.DATE] >= start_date]
    all_locations = df_location[const.LOC_NAME].unique()
    some_decreases = tuple(filter(
        lambda x: not (
            df_location[df_location[const.LOC_NAME] == x]
            .loc[:, const.CASES].is_monotonic_increasing),
        all_locations
    ))
    return some_decreases


def area_slowed_increase(df_area_ts: pd.DataFrame, location: str, days_back: int, threshold: float) -> Tuple[str]:
    MIN_CASES = 'Minimum Cases'
    MAX_CASES = 'Maximum Cases'
    CURR_CASES = 'Current Cases'
    PROP_INC = 'Proportion Increase'
    # Filter to provided time frame
    start_date = df_area_ts[const.DATE].max() - pd.Timedelta(days=days_back)
    df_area_ts = (
        df_area_ts[df_area_ts[const.DATE] >= start_date]
        .loc[:, [location, const.CASES]])
    # Compute summary stats for each area
    area_group = df_area_ts.groupby(location)
    df_min_cases = area_group.min().rename(columns={const.CASES: MIN_CASES})
    df_max_cases = area_group.max().rename(columns={const.CASES: MAX_CASES})
    df_curr_cases = area_group.last().rename(columns={const.CASES: CURR_CASES})
    # Construct the dataframe to use for analysis
    area_cases = (
        pd.concat((df_min_cases, df_max_cases, df_curr_cases), axis='columns')
        .reset_index())
    # Compute relative case increase over duration
    area_cases[PROP_INC] = (area_cases[MAX_CASES] - area_cases[MIN_CASES]) / area_cases[CURR_CASES]
    # Keep only area under threshold
    area_cases = area_cases[area_cases[PROP_INC] < threshold]
    return area_cases[location].astype('string')


def make_by_age(pr_stats):
    data = {
        const.DATE: pd.to_datetime(tuple(map(lambda x: x[const.DATE], pr_stats))),
        const.AGE_0_17: map(lambda x: x[const.CASES_BY_AGE][const.AGE_0_17], pr_stats),
        const.AGE_18_40: map(lambda x: x[const.CASES_BY_AGE][const.AGE_18_40], pr_stats),
        const.AGE_41_65: map(lambda x: x[const.CASES_BY_AGE][const.AGE_41_65], pr_stats),
        const.AGE_OVER_65: map(lambda x: x[const.CASES_BY_AGE][const.AGE_OVER_65], pr_stats)
    }
    return tidy_data(pd.DataFrame(data), const.AGE_GROUP, const.CASES)


def make_by_gender(pr_stats):
    pr_stats = tuple(filter(lambda x: x[const.CASES_BY_GENDER], pr_stats))
    data = {
        const.DATE: pd.to_datetime(tuple(map(lambda x: x[const.DATE], pr_stats))),
        const.MALE: map(lambda x: x[const.CASES_BY_GENDER][const.MALE], pr_stats),
        const.FEMALE: map(lambda x: x[const.CASES_BY_GENDER][const.FEMALE], pr_stats)
    }
    return tidy_data(pd.DataFrame(data), const.GENDER, const.CASES)


if __name__ == "__main__":
    all_dates = query_all_dates()

    last_week = all_dates[-7:]
    june_2 = all_dates[64]
    today = all_dates[-1]

    one_day_loc = single_day_loc(today)

    df_location = make_by_loc(all_dates)
    # df_aggregate = make_df_dates(all_dates)
    df_aggregate = aggregate_locations(df_location)

    # test = aggregate_locations(df_location, const.REGION['San Gabriel Valley'])

    test = area_slowed_increase(df_location, const.LOC_NAME, 14, 0.01)

    # SFV = 'San Fernando Valley'
    # WS = 'Westside'
    # sample_regions = {SFV: const.REGION[SFV], WS: const.REGION[WS]}
    # region_ts = location_cases_comparison(df_location, sample_regions)
    # df_sfv = region_ts[SFV]
    # sfv_series = pd.Series(SFV, name='Region', dtype='string').repeat(df_sfv.shape[0]).reset_index(drop=True)
