# I create the dataframes manually for an animation and quicker User experience


from datetime import date
import pandas as pd 
from calendar import monthrange
from pathlib import Path


from core.market_screener import correlations
from core.network_graphing import plot_network



def get_month_end(year, month):
    day = monthrange(year, month)[1]
    return date(year, month, day)


def dataframe_to_csv_parquet():
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
        correlation_dataframe.clip(-1,1)

        # save data as parquet(fast for code) and readable csv(if desired)
        correlation_dataframe.to_parquet(f"personal_projects/stock_crypto/data_saved/correlation_parquet/Q{quarter}_{year}_correlations.parquet")
        print(f'Parquet file for {quarter}, {year} has been saved successfully')
        correlation_dataframe.to_csv(f"personal_projects/stock_crypto/data_saved/correlation_csv/Q{quarter}_{year}_correlations.csv")
        print(f'CSV file for {quarter}, {year} has been crteated successfully')

        # increase quartal
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1
#dataframe_to_csv_parquet()

def parquet_to_html():
    for file in Path("personal_projects/stock_crypto/data_saved/correlation_parquet").glob("*.parquet"):
        print(f"Starting with {file.stem}")
        df = pd.read_parquet(file)
        
        df.fillna(0)
        df.clip(-1,1)

        try: 
            fig = plot_network(df, 0.7)

                
            
            output_path = Path("personal_projects/stock_crypto/data_saved/correlation_html") / f"{file.stem}.html"
            fig.write_html(output_path)
            print(f"{file.stem} has been added successfully")
            del df, fig
        except Exception as e:
            print(f'{file.stem} could not be added, please check')
            print(df.isna().sum().sum())
            print(df.min().min(), df.max().max())
            del df
        
parquet_to_html()