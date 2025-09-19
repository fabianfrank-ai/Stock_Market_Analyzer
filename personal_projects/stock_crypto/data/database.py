import sqlite3

# plan was to initially use it, it kind of lost its purpose but might come in handy someday

# create a new database (or connect to existing) and create a table###
conn = sqlite3.connect('stock_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS stocks
             (date TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS buys
             (date TEXT, ticker TEXT)''')
conn.commit()
conn.close()


# function to insert data into a database for all the data
def insert_stock_data(data):
    """insert data into the database"""
    
    conn = sqlite3.connect('stock_data.db')
    c = conn.cursor()
    for index, row in data.iterrows():
        c.execute("INSERT INTO stocks (date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)",
                  (index.strftime('%Y-%m-%d'), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
    conn.commit()
    conn.close()

