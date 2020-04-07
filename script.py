# -*- coding: utf-8 -*-
import bs4 as bs
import csv
import sys
import os

from urllib import urlopen

#Methods
def get_ticker_info(ticker, csvString):
	
	url = 'https://www.marketwatch.com/investing/stock/{}/financials'.format(ticker)

	soup = bs.BeautifulSoup(urlopen(url).read(), "lxml")
	tickerName = soup.find(id = "instrumentname").text
	print "Analizing: {} - {}".format(ticker.upper(), tickerName)

	#EPS
	if soup.find(text = ' EPS (Basic)'):
		espTitle = soup.find(text = ' EPS (Basic)').parent
		espValues = espTitle.findNextSiblings(attrs = {'class': 'valueCell'})

		averageEps = 0
		for esp in espValues:
			text = cleanString(esp.text)
			if text == "NaN":
				averageEps = "N/A"
				break
			averageEps = averageEps + float(text)

		if averageEps != "N/A":
			averageEps = "$ {:.2f}".format(averageEps / len(espValues))
	
	else:
		averageEps = "N/A"
	
	#Gross income
	if soup.find(text = ' Gross Income'):
		grossIncomeTitle = soup.find(text = ' Gross Income').parent
		grossIncomeValues = grossIncomeTitle.findNextSiblings(attrs = {'class': 'valueCell'})
		averageGrossIncomesFormatted = ""
		averageGrossIncomes = 0
		for grossIncome in grossIncomeValues:
			text = cleanString(grossIncome.text)
			if text == "NaN":
				averageGrossIncomesFormatted = "N/A"
				break
			value = float(text[:-1])
			value = checkForMillion(text, value)

			averageGrossIncomes = averageGrossIncomes + value
		
		if averageGrossIncomesFormatted != "N/A":
			averageGrossIncomes = averageGrossIncomes / len(grossIncomeValues)
			averageGrossIncomesFormatted = "{:.2f} B".format(averageGrossIncomes)
		
		#Net income
		netIncomeTitle = soup.find(text = ' Net Income').parent
		netIncomeValues = netIncomeTitle.findNextSiblings(attrs = {'class': 'valueCell'})
		averageNetIncomesFormatted = ""
		averageNetIncomes = 0
		for netIncome in netIncomeValues:
			text = cleanString(netIncome.text)
			if text == "NaN":
				averageNetIncomesFormatted = "N/A"
				break
			value = float(text[:-1])
			value = checkForMillion(text, value)

			averageNetIncomes = averageNetIncomes + value
		if averageNetIncomesFormatted != "N/A":
			averageNetIncomes = averageNetIncomes / len(netIncomeValues)
			averageNetIncomesFormatted = "{:.2f} B".format(averageNetIncomes)

		#Annual Expenses
		annualExpenses = "{:.2f} B".format(averageGrossIncomes - averageNetIncomes)

		url = "https://www.marketwatch.com/investing/stock/{}/financials/balance-sheet".format(ticker)
		soup = bs.BeautifulSoup(urlopen(url).read(), "lxml")
		
		#Available Cash 
		cashTitle = soup.find(text = ' Cash & Short Term Investments').parent
		cashValues = cashTitle.findNextSiblings(attrs = {'class': 'valueCell'})

		currentCashValueText = cashValues[-1].text

		currentCashValue = float(currentCashValueText[:-1])
		currentCashValue = checkForMillion(currentCashValueText, currentCashValue)
		currentCashValueFormatted = "{:.2f} B".format(currentCashValue)
		if (averageGrossIncomes - averageNetIncomes) != 0:
			noIncomeOperationCapacity = "{:.2f} years".format(currentCashValue / (averageGrossIncomes - averageNetIncomes))
		else:
			noIncomeOperationCapacity = "N/A"

	else:
		noIncomeOperationCapacity = "N/A"
		currentCashValueFormatted = "N/A"
		annualExpenses = "N/A"
		averageNetIncomesFormatted = "N/A"
		averageGrossIncomesFormatted = "N/A"

	url = 'https://www.marketwatch.com/investing/stock/{}/financials/cash-flow'.format(ticker)	
	soup = bs.BeautifulSoup(urlopen(url).read(), "lxml")	
	netInvestingText = "N/A"
	netFinancialText = "N/A"
	
	if soup.find(text = ' Net Investing Cash Flow'):
		netInvestingTitle = soup.find(text = ' Net Investing Cash Flow').parent
		netInvestingValues = netInvestingTitle.findNextSiblings(attrs = {'class': 'valueCell'})
		
		netInvestingText = ""
		for value in netInvestingValues:
			netInvestingText = netInvestingText + (value.text + " | ")

	if soup.find(text = ' Net Financing Cash Flow'):
		netFinancialTitle = soup.find(text = ' Net Financing Cash Flow').parent
		netFinancialValues = netFinancialTitle.findNextSiblings(attrs = {'class': 'valueCell'})
	
		netFinancialText = ""
		for value in netFinancialValues:
			netFinancialText = netFinancialText + (value.text + " | ")

	line = "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(
		ticker, 
		tickerName, 
		averageEps, 
		averageGrossIncomesFormatted, 
		averageNetIncomesFormatted, 
		annualExpenses, 
		currentCashValueFormatted, 
		noIncomeOperationCapacity,
		netInvestingText,
		netFinancialText
	)
	
	csvString += line

	f = open('./output.csv','w')
	f.write("{}\n".format(csvString))
	f.close()

	return csvString

def read_csv():
	with open('./input.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		tickers = []
		for row in csv_reader:
			tickers.append(row[0])
		return tickers

def cleanString(string):
	if string == "-":
		return "NaN"
	string = string.replace(")", "")
	string = string.replace("(", "")
    
	return string

def checkForMillion(text, value):
	if text[-1:] == "M":
		value = value / 1000

	return value



#Execution
os.system('clear')

csvString = "Ticker, Company Name, EPS, Gross Income, Net Income, Annual Expenses, Available Cash, No Income Operation Capacity, Net Investing Cash Flow, Net Financing Cash Flow\n"

tickers = read_csv()
for ticker in tickers:
	csvString = get_ticker_info(ticker, csvString)

