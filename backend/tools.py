from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
import yfinance as yf
import pandas as pd

@tool
def get_complete_financial_data(company_query):
    """this function is to find the detail data about the company"""
    try:
        search = yf.Search(company_query, max_results=1)
        
        if not search.quotes:
            return f"No ticker found for '{company_query}'"
        
        ticker_symbol = search.quotes[0]['symbol']
        ticker = yf.Ticker(ticker_symbol)
    
        history = ticker.history(period="1d")

        current_price = None
        if not history.empty:
            current_price = history['Close'].iloc[-1]
        else:
            current_price = ticker.fast_info.get('last_price')
            
        if current_price is None:
            current_price = ticker.info.get('regularMarketPrice')

        return {
            "symbol": ticker_symbol,
            "name": search.quotes[0].get('shortname', 'N/A'),
            "current_price": current_price,
            "history": history,
            "fundamentals": ticker.info, 
            "balance_sheet": ticker.balance_sheet
        }

    except Exception as e:
        return f"An error occurred: {e}"


@tool
def search_web(query:str):
  """this is the tool used to do the web-serch"""
  try:
    tool = TavilySearch(max_result = 2 ,topic="finance")
    responce = tool.invoke({"query":query})
    return responce
  except Exception as e:
    ValueError(e)
    


Tools = [get_complete_financial_data, search_web]

