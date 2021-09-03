import configparser
import os
from datetime import datetime
from datetime import timedelta

import pandas as pd
from utility import logger

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_RAW = f'{CURRENT_DIR}/data/00_raw/'
ROOT_CLEAN = f'{CURRENT_DIR}/data/01_clean/'
DROPPABLE_INVERTER_COL_LIST = ['in_voltage_0', 'in_current_0', 'out_current',
                               'out_voltage', 'out_frequency', 'operation_hour', 'phase_r_t', 'phase_r_i',
                               'phase_r_v', 'phase_r_f', 'phase_r_p', 'phase_s_t', 'phase_s_i',
                               'phase_s_v', 'phase_s_f', 'phase_s_p', 'phase_t_t', 'phase_t_i',
                               'phase_t_v', 'phase_t_f', 'phase_t_p', 'power_factor_pf', 'power_factor_va',
                               'power_factor_var', 'power_factor_kvar', 'power_factor_kvarh', 'create_time'
                               ]
PRESERVABLE_IRRADIANCE_COL_LIST = ['site_id', 'data_time', 'value_1']
PRESERVABLE_THERMAL_COL_LIST = ['site_id', 'data_time', 'value_1']
INVERTER_CODE_COL_LIST = [
    'errcodee', 'errcodef', 'errcodeg', 'errcodeh', 'wcode1', 'wcode2',
    'wcode3', 'fcode1', 'fcode2', 'fcode3', 'fcode4', 'fcode5']
INVERTER_CURRENT_AND_POWER_LIST = ['in_current_1', 'in_current_2',
                                   'in_current_3', 'in_current_4', 'in_current_5', 'in_current_6',
                                   'in_current_7', 'in_current_8', 'out_power', 'power_lifetime']

START_IDX_OF_TIMEZONE = -6


def parse_datetime(dt_str):
    return datetime.strptime(dt_str[:START_IDX_OF_TIMEZONE],
                             '%Y-%m-%d %H:%M:%S')


def rescale_datetimeindex(objs, startdt, enddt):
    rescaled_index = pd.date_range(start=startdt,
                                   end=enddt,
                                   freq='2min',
                                   name='data_time')

    return objs.reindex(rescaled_index)


def is_first_or_last_datadt_in_margin(dt,
                                      earliest_time,
                                      latest_time,
                                      config):
    margin_mins = \
        config['preprocessing']['missing_margin_data_replace_max_duration_mins']

    margin_mins = int(margin_mins)

    delta_in_start_and_earliest = (dt.index[0] - earliest_time).seconds/60
    delta_in_end_and_latest = (latest_time - dt.index[-1]).seconds/60

    if delta_in_start_and_earliest <= margin_mins and \
            delta_in_end_and_latest <= margin_mins:
        return True

    return False


def is_nan_num_under_threshold(dt_index, config):
    ss = pd.Series(dt_index)

    duration_mins = \
        config['preprocessing']['missing_data_replace_max_duration_mins']
    duration_mins = int(duration_mins)

    return not (ss.diff() >= timedelta(minutes=duration_mins)).any()


def create_earliest_and_latest_dt(year, month, day, config):
    earliest_time = config['preprocessing']['start_time_of_day']
    latest_time = config['preprocessing']['end_time_of_day']
    earliest_dt = datetime.strptime(f'{year}-{month}-{day} {earliest_time}',
                                    '%Y-%m-%d %H:%M')
    latest_dt = datetime.strptime(f'{year}-{month}-{day} {latest_time}',
                                  '%Y-%m-%d %H:%M')
    return earliest_dt, latest_dt


def interpolate_inverter_by_powerlifetime(df):
    power_lifetime = df[['power_lifetime']].dropna()
    power_lifetime = power_lifetime.reset_index()

    power_lifetime['data_time_shift'] = power_lifetime['data_time'].shift()
    power_lifetime['time_diff'] = \
        power_lifetime['data_time'] - power_lifetime['data_time_shift']
    power_lifetime['power_lifetime_diff'] = \
        power_lifetime['power_lifetime'].diff()

    bool_mask = (power_lifetime['time_diff'] != timedelta(minutes=2)) \
        & (power_lifetime['power_lifetime_diff'] == 0)

    power_lifetime = power_lifetime[bool_mask]

    for _, row in power_lifetime.iterrows():
        start_dt = row['data_time_shift'] + timedelta(minutes=2)
        end_dt = row['data_time'] - timedelta(minutes=2)
        df.loc[start_dt:end_dt, INVERTER_CURRENT_AND_POWER_LIST] = 0

    df = df.interpolate(method='linear')

    return df


def do_clean_inverter(src_df, site_id, config):
    src_df.drop(columns=DROPPABLE_INVERTER_COL_LIST, inplace=True)

    earliest_dt, latest_dt = \
        create_earliest_and_latest_dt(src_df['data_time'].iloc[0].year,
                                      src_df['data_time'].iloc[0].month,
                                      src_df['data_time'].iloc[0].day,
                                      config)

    rtn_df = pd.DataFrame()

    for device_id, data in src_df.groupby(by='device_id'):
        tmp_df = data.set_index(keys='data_time').sort_index(ascending=True)

        if is_first_or_last_datadt_in_margin(tmp_df,
                                             earliest_dt,
                                             latest_dt,
                                             config) and \
                is_nan_num_under_threshold(tmp_df.index, config):

            tmp_df = rescale_datetimeindex(tmp_df,
                                           tmp_df.index[0],
                                           tmp_df.index[-1])
            tmp_df.loc[:, INVERTER_CODE_COL_LIST] = \
                tmp_df.loc[:, INVERTER_CODE_COL_LIST].fillna(method='ffill')

            tmp_df.loc[:, INVERTER_CURRENT_AND_POWER_LIST] = \
                interpolate_inverter_by_powerlifetime(
                    tmp_df.loc[:, INVERTER_CURRENT_AND_POWER_LIST])

            col = tmp_df.columns.symmetric_difference(
                INVERTER_CODE_COL_LIST + INVERTER_CURRENT_AND_POWER_LIST
                + ['device_id', 'site_id'])

            tmp_df.loc[:, col] = tmp_df.loc[:,
                                            col].interpolate(method='linear')

            tmp_df = rescale_datetimeindex(tmp_df, earliest_dt, latest_dt)

            tmp_df['is_correction_inverter'] = tmp_df['site_id'].isna()
            tmp_df['site_id'].fillna(value=site_id, inplace=True)
            tmp_df['device_id'].fillna(value=device_id, inplace=True)

            tmp_df = tmp_df.fillna(method='bfill')
            tmp_df = tmp_df.fillna(method='ffill')
            tmp_df = tmp_df.fillna(value=0)

        else:
            tmp_df = rescale_datetimeindex(tmp_df, earliest_dt, latest_dt)
            tmp_df['is_correction_inverter'] = None
            tmp_df['site_id'].fillna(value=site_id, inplace=True)
            tmp_df['device_id'].fillna(value=device_id, inplace=True)

        tmp_df = tmp_df.drop(columns='power_lifetime')
        rtn_df = rtn_df.append(tmp_df)

    rtn_df.reset_index(inplace=True)

    return rtn_df


def clean_thermal_irradiance(table_name, src_df, site_id, config):
    earliest_dt, latest_dt = \
        create_earliest_and_latest_dt(src_df['data_time'].iloc[0].year,
                                      src_df['data_time'].iloc[0].month,
                                      src_df['data_time'].iloc[0].day,
                                      config)

    if table_name == 'irradiance':
        rtn_df = src_df[PRESERVABLE_IRRADIANCE_COL_LIST]
    elif table_name == 'thermal':
        rtn_df = src_df[PRESERVABLE_THERMAL_COL_LIST]

    is_correction_col_name = f'is_correction_{table_name}'
    rtn_df = rtn_df.set_index(keys='data_time').sort_index(ascending=True)
    rtn_df = rtn_df.rename(columns={'value_1': table_name})

    if is_first_or_last_datadt_in_margin(rtn_df,
                                         earliest_dt,
                                         latest_dt,
                                         config) and \
            is_nan_num_under_threshold(rtn_df.index, config):

        rtn_df = rescale_datetimeindex(rtn_df,
                                       rtn_df.index[0],
                                       rtn_df.index[-1])

        rtn_df[table_name].interpolate(method='linear', inplace=True)

        rtn_df = rescale_datetimeindex(rtn_df, earliest_dt, latest_dt)

        rtn_df[is_correction_col_name] = rtn_df['site_id'].isna()
        rtn_df['site_id'].fillna(value=site_id, inplace=True)
        rtn_df[table_name].fillna(method='bfill', inplace=True)
        rtn_df[table_name].fillna(method='ffill', inplace=True)

    else:
        rtn_df = rescale_datetimeindex(rtn_df, earliest_dt, latest_dt)
        rtn_df[is_correction_col_name] = None
        rtn_df['site_id'].fillna(value=site_id, inplace=True)

    rtn_df.reset_index(inplace=True)

    return rtn_df


def do_clean_irradiance(src_df, site_id, config):
    return clean_thermal_irradiance('irradiance', src_df, site_id, config)


def do_clean_thermal(src_df, site_id, config):
    return clean_thermal_irradiance('thermal', src_df, site_id, config)


def main():
    try:
        config = configparser.ConfigParser()
        config.read(f'{CURRENT_DIR}/config.ini')

        for site_id in os.listdir(ROOT_RAW):
            for table_name in os.listdir(os.path.join(ROOT_RAW, site_id)):

                if table_name == 'inverter':
                    do_clean = do_clean_inverter
                elif table_name == 'irradiance':
                    do_clean = do_clean_irradiance
                elif table_name == 'thermal':
                    do_clean = do_clean_thermal
                else:
                    logger.warn(f'Unsupported table:{table_name}')
                    continue

                src_path = os.path.join(ROOT_RAW, site_id, table_name)
                dst_path = os.path.join(ROOT_CLEAN, site_id, table_name)

                if not os.path.exists(dst_path):
                    os.makedirs(dst_path)

                file_list = os.listdir(src_path)
                for idx, file in enumerate(file_list):
                    src_df = pd.read_csv(os.path.join(src_path, file),
                                         parse_dates=['data_time'],
                                         date_parser=parse_datetime)

                    if len(src_df) == 0:
                        logger.info(
                            f'Empty data, skip it, site_id[{site_id}], '
                            + f'table_name[{table_name}], file[{file}]')
                        continue

                    df = do_clean(src_df, site_id, config)

                    df.to_csv(os.path.join(dst_path, file),
                              index=False,
                              mode='w')
                    logger.info(
                        f'clean completed, site_id[{site_id}], '
                        + f'table_name[{table_name}], '
                        + f'file[{file},({idx+1}/{len(file_list)})]')

    except Exception:
        logger.exception(f'Failed to clean data, site_id[{site_id}], '
                         + f'table_name[{table_name}], file[{file}]')


if __name__ == '__main__':
    logger = logger.init_logger('clean.log')
    main()
