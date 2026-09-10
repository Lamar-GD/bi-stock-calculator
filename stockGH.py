
from pathlib import Path
import pandas as pd

PATH_SOURCE = Path(__file__).parent
PATH_TRANS = PATH_SOURCE / 'invent_trans'
PATH_STOCK = PATH_SOURCE / 'stock'

class StockCalculator:
# _______________________________________________________________________
    def __init__(self, trans_path, stock_path):
        self.trans_path = trans_path
        self.stock_path = stock_path
        self.initial_stock = None
        self.transactions = None
        self.transactions_grouped = None
        self.final_result = None
#_______________________________________________________________________
    def load_initial_stock(self):
        file_path = self.stock_path / 'stock_2025_04_30.csv'
        self.initial_stock = pd.read_csv(file_path, sep = ";", dtype = str)
        print(self.initial_stock.head())
# _______________________________________________________________________
    def load_transactions(self):
        all_files = []
        for file_path in self.trans_path.glob('*.csv'):
            file_path = pd.read_csv(file_path, sep = ";", dtype = str)
            all_files.append(file_path)
        self.transactions = pd.concat(all_files, ignore_index = True)
        print(self.transactions.head())
# _______________________________________________________________________
    def aggregate_transactions(self):
        self.transactions['qty'] = self.transactions['qty'].astype(float)
        self.transactions['cost_amount'] = self.transactions['cost_amount'].astype(float)
        self.transactions_grouped = self.transactions.groupby(['item_id','location_id','trans_date'], as_index = False)[['qty','cost_amount']].sum()
        print(self.transactions_grouped.head())
#_______________________________________________________________________
    def calculate_daily_stock(self):
        self.initial_stock['qty'] = self.initial_stock['qty'].astype(float)
        self.initial_stock['cost_amount'] = self.initial_stock['cost_amount'].astype(float)
        self.initial_stock['trans_date'] = '2025-04-30'
        combined = pd.concat([self.initial_stock, self.transactions_grouped], ignore_index = True)
        combined = combined.sort_values(by = 'trans_date')
        combined[['qty', 'cost_amount']] = combined.groupby(['item_id', 'location_id'])[['qty', 'cost_amount']].cumsum()
        self.final_result = combined
        print("stocks")
        print(self.final_result.head())
#_______________________________________________________________________
    def save_target_stock(self, terget_date):
        target_stock = self.final_result[(self.final_result['trans_date'] == terget_date)]
        target_stock = target_stock.round({'qty':2, 'cost_amount':2})
        output_file = self.stock_path / f'stock_{terget_date.replace('-','_')}.csv'
        target_stock.to_csv(output_file, sep = ";", index = False)
        print(f"File saved: {output_file}")
#_______________________________________________________________________

def main() -> None:
    calc = StockCalculator(PATH_TRANS, PATH_STOCK)
    calc.load_initial_stock()
    calc.load_transactions()
    calc.aggregate_transactions()
    calc.calculate_daily_stock()
    calc.save_target_stock('2025-07-31')
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'Oops... Something wrong! Error: {e}')
