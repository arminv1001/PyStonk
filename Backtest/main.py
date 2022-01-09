from data_prep.CSVDataPreparer import *
from RSI import *


if __name__ == "__main__":
    csv_dir = '/Users/mr.kjn/Projects/Studienarbeit/backtest_data'

    symbols = ["AAPL", "IBM"]
    csvDP = CSVDataPreparer(csv_dir=csv_dir, csv_symbols=symbols)

    closes = csvDP.get_assets_historic_data('2021-01-01', '2021-12-31', symbols)
    print(closes.index[1])
    
    RSI(closes['IBM'])

