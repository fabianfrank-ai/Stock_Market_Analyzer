# I create the dataframes manually for an animation and quicker User experience


from datetime import date
import pandas as pd
from calendar import monthrange
from pathlib import Path
import plotly as pt
import sqlite3


from core.market_screener import correlations, heatmap
from core.network_graphing import plot_network


def get_month_end(year, month):
    day = monthrange(year, month)[1]
    return date(year, month, day)


def dataframe_to_parquet_network():
    '''Converts pandas dataframes into csv and parquet data'''
    year = 2020
    quarter = 1
    while year < 2026:
        # calculation for start quartal
        month_start = 1 + (quarter - 1) * 3

        # calculate the start and end date of a quartal
        start_date = date(year, month_start, 1)
        end_date = get_month_end(year, month_start + 2)

        # calculate correlations
        correlation_dataframe = correlations(start_date, end_date)

        correlation_dataframe.fillna(0)
        correlation_dataframe.clip(-1, 1)

        # save data as parquet(fast for code) and readable csv(if desired)
        correlation_dataframe.to_parquet(
            f"stock_crypto/data_saved/correlation_parquet/Correlations_{year}_Q{quarter}.parquet")
        print(
            f'Parquet file for {quarter}, {year} has been saved successfully')
        # increase quartal
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1


def dataframe_to_parquet_heatmap():
    '''Converts pandas dataframes into csv and parquet data'''
    year = 2020
    quarter = 1
    while year < 2026:
        # calculation for start quartal
        month_start = 1 + (quarter - 1) * 3

        # calculate the start and end date of a quartal
        start_date = date(year, month_start, 1)
        end_date = get_month_end(year, month_start + 2)

        # calculate heatmaps
        heatmap_dataframe = heatmap(start_date, end_date)

        # save data as parquet(fast for code) and readable csv(if desired)
        heatmap_dataframe.to_parquet(
            f"stock_crypto/data_saved/heatmap_parquet/Heatmap_{year}_Q{quarter}.parquet")
        print(
            f'Parquet file for {quarter}, {year} has been saved successfully')

        # increase quartal
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1


# lots of debugging because it is(was) very unstable


choice = input(
    "What do you want to convert?\n -1 correlations \n -2 heatmaps \n -3 parquet \n - DO NOT USE, WORK IN PROGRESS: 4 to sql \n Enter number: ")

if choice == '1':
    dataframe_to_parquet_network()
elif choice == '2':
    dataframe_to_parquet_heatmap()
else:
    print("Invalid input, try again")
