import requests
from bs4 import BeautifulSoup

class SecEdgar:
    def __init__(self,fileurl):
        self.fileurl = fileurl #assumes we just the company tickers json
        self.name_dict = {}
        self.ticker_dict = {}
        self.headers = {'user-agent': 'MLT Jaime Ojeda jaimeojeda426@gmail.com'}

        r = requests.get(self.fileurl,headers = self.headers)

        self.filejson = r.json() #stores JSON retrived from website, turns into python dict where key is an index for a company
                                #value is dict with the following keys/fields for each company: cik_str, ticker, title.
        self.clk_json_to_dict() #call method here to automate initliazation, don't have to call the method when creating an object since it just calls it already

    def clk_json_to_dict(self):
        #fills our two dictionaries, one where company name is key, other where stock ticker is key from json file

        #iterate through the json's values, which are dictionaries
        for company in self.filejson.values(): 
            cik = str(company['cik_str']).zfill(10)
            ticker = company['ticker']
            name = company['title']

            self.name_dict[name.lower()] = (name,ticker,cik)
            self.ticker_dict[ticker.lower()] = (name,ticker,cik)
       
    def name_to_cik(self, name):
        return self.name_dict[name.lower()]
    
    def ticker_to_cik(self,ticker):
        return self.ticker_dict[ticker.lower()]
    
    def __fetch_submissions(self,cik):
        return requests.get(f'https://data.sec.gov/submissions/CIK{cik}.json',headers = self.headers).json()
                
    def __fetch_facts(self,cik):
        r = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',headers = self.headers)
        file_json = r.json()
        return file_json["facts"]
    
    def __display_filing(self,htm_doc):
        soup = BeautifulSoup(htm_doc, "lxml")
        return soup.get_text()
    
    def annual_filing(self,cik, year):
        facts_json = self.__fetch_facts(cik)
        shares_dicts = facts_json["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"]
        accn = ""
        for dicts in shares_dicts:
            if dicts['fy'] == year and dicts['form'] == '10-K':
                accn = dicts['accn']
                break
        
        submissions = self.__fetch_submissions(cik)['filings']['recent']

        primaryDocument = None
        for index,num in enumerate(submissions['accessionNumber']):
            if num == accn:
                primaryDocument = submissions['primaryDocument'][index]
                break
        
        accn = accn.replace('-',"")

        doc = requests.get(f'https://www.sec.gov/Archives/edgar/data/{cik}/{accn}/{primaryDocument}', headers = self.headers).text
        return self.__display_filing(doc)





    #def quarterly_filing(cik, year, quarter):


se = SecEdgar('https://www.sec.gov/files/company_tickers.json')
#print(se.ticker_to_cik('NOFCF'))
#print(se.name_to_cik('dsg global inc.'))
print(se.annual_filing('0000320193',2021))
