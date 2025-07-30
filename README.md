# GW2 Trading Post Dashboard

A real-time dashboard for tracking item prices and personal trading profit/loss in Guild Wars 2 using the official API.

## Features

- Add/remove tracked items
- Record purchase history
- Live trading post prices with TP fee adjustment
- Profit/loss calculation and bar chart visualization
- Refreshable item list

## How to Run

1. Clone the repository:
```git clone https://github.com/JosephinePalmhede/gw2-trading-dashboard.git```
```cd gw2-trading-dashboard```

2. Install dependencies:
```pip install -r requirements.txt```

3. Run the app:
```streamlit run app.py```

## Notes

- The app fetches data from the official GW2 API.
- Some data files like `portfolio.json` are created automatically when you make purchases.