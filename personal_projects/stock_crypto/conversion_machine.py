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


def dataframe_to_csv_parquet_network():
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
#dataframe_to_csv_parquet_network()



def dataframe_to_csv_parquet_heatmap():
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
        heatmap_dataframe = correlations(start_date, end_date)
        
        heatmap_dataframe.fillna(0)
        heatmap_dataframe.clip(-1,1)

        # save data as parquet(fast for code) and readable csv(if desired)
        heatmap_dataframe.to_parquet(f"personal_projects/stock_crypto/data_saved/heatmap_parquet/Heatmap_{quarter}_{year}.parquet")
        

        # increase quartal
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1






# lots of debugging because it is very unstable
def parquet_to_html():
    '''Convert dataframes, saved as parquet into html plots'''
    for file in Path("personal_projects/stock_crypto/data_saved/correlation_parquet").glob("*.parquet"):
        print(f"Starting with {file.stem}")
        df = pd.read_parquet(file).copy()
        
        df.clip(-1,1)
        fig = {}
        

        try: 
            fig = plot_network(df, 0.7)
         
        

            print(f"Figure has {len(fig.data)} traces and {len(fig.layout.shapes)} shapes BEFORE write_html")   

            output_path = Path("personal_projects/stock_crypto/data_saved/correlation_html") / f"{file.stem}.html"
            fig.write_html(output_path, full_html = True, include_plotlyjs = True)
            
            print(f"Plot has {len(fig.data)} traces and {len(fig.layout.shapes)} shapes AFTER write_html")
            print([trace.name for trace in fig.data])
            print(fig.layout.shapes)
            fig.layout.shapes = ()
            
            
            print(f"{file.stem} has been added successfully")
         
        except Exception as e:
            print(f'{file.stem} could not be added, please check : {e}')
            print(df.isna().sum().sum())
            print(df.min().min(), df.max().max())
      
        
#parquet_to_html()


choice = input("What do you want to convert?\n -1 correlations \n -2 heatmaps \n -3 parquet")

if choice == '1':
    dataframe_to_csv_parquet_network()
elif choice == '2':
    dataframe_to_csv_parquet_heatmap()
elif choice == '3':
    parquet_to_html()
else:
    print ("Invalid input, try again")