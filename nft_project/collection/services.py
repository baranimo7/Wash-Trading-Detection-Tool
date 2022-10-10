from array import array
from ast import Eq
import collections
from pickle import TRUE
from re import L, S
import string
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import math
#from web3 import Web3
import json
import requests
from collections import Counter
import numpy
import pymongo
from pymongo import MongoClient
import pprint
import certifi
from django.conf import settings as django_settings
import os
from datetime import date, datetime


class MongoMService:
    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4)
        #put your mongoDB link here
        self.cluster = pymongo.MongoClient("", tlsCAFile=certifi.where())
        self.db = self.cluster['test']
        self.collection = self.db['test']

        self.headers1 = {  # you can use your own Moralis API Key
            'x-api-key': ''
        }
        self.messages = list()

    def SCC(self, collections):
        #this method detects the SCCs of each token and returns all suspicious SCCs in a list
        ListSCC = list()
        ListFinalSCC = list()
        array = []
        dicti = dict()
        set_tokens = set()
        mongo_status = False
        
        
        if self.collection.count_documents({'_id': collections}) > 0:
            #we check if the transaction history of the collection is already stored in MongoDB
            mngo_status = True
            a = self.collection.find({"_id": collections})

            # transactions are stored at the 'token'
            for object in a:
                b = object['token']
                #  for each token we get the SCC's and store at a List
            for x in b:
              Graph_simple=(self.simplfy(b[x]))
              while(nx.is_empty(Graph_simple)==False):
               for e in list(nx.strongly_connected_components(Graph_simple)):
                #we only consider SCCs which contains more than 1 addresses   
                if len(e)>1:
                 ListSCC.append(e)
                Graph_simple=self.decrease( Graph_simple)
     
            for l in ListSCC:
                if ListSCC.count(l)>=5:
                  ListFinalSCC.append(l)      
            return ListFinalSCC
        else:
            #  if the collection is not on the db we should get the transaction history and store it and than get the SCCs
            # this is the endpoint to obtain the list of tokens on the given collection
            url = 'https://deep-index.moralis.io/api/v2/nft/'+collections+'?chain=eth&format=decimal'
            response = requests.request("GET", url, headers=self.headers1)
            resp = response.json()
            length = (int(math.ceil(int(resp['total'])/int(resp['page_size']))))
            i1 = 0
            #  loop for getting all the token_id's
        while i1 < length:
            
           
            for x in resp['result']:
                #this endpoint gets the transaction data of the given token in the collection
                url2 = 'https://deep-index.moralis.io/api/v2/nft/'+collections+'/'+x['token_id']+'/transfers?chain=eth&format=decimal'
                response2 = requests.request("GET", url2, headers=self.headers1)
                resp2 = response2.json()
                if resp2['total'] > 0:
                 array = []
                 length2 = (int(math.ceil(int(resp2['total'])/int(resp2['page_size']))))
                 i = 0
                    #  loop for getting diferent pages of the list of transactions of a single token
                 while i < length2:
                  for y in resp2['result']:
                     #these attributes from the result of endpoint are needded to analyze wash trading 
                     array.append((y['from_address'], y['to_address'], y['value'], y["transaction_hash"],y["block_timestamp"]))
                  if length2-i != 1:
                   url2 = 'https://deep-index.moralis.io/api/v2/nft/'+collections+'/'+x['token_id']+'/transfers?chain=eth&format=decimal&cursor=' + resp2['cursor']
                   response2 = requests.request("GET", url2, headers=self.headers1)
                   resp2 = response2.json()
                  i = i+1
                  dicti[x['token_id']] = array
            if length-i1 != 1:
             url = 'https://deep-index.moralis.io/api/v2/nft/'+collections+'?chain=eth&format=decimal&cursor=' + resp['cursor']
             response = requests.request("GET", url, headers=self.headers1)
             resp = response.json()
            i1 = i1+1
  
        #obtained token list and transaction history are stored on mongodb
        mongodicti = {"_id": collections, "token": dicti}
        self.collection.insert_one(mongodicti)

        #here starts the actual analysis part
        for x in dicti:
         Graph_simple = (self.simplfy(dicti[x]))
         while(nx.is_empty(Graph_simple) == False ):
          for e in list(nx.strongly_connected_components(Graph_simple)):
           if len(e) > 1:
            ListSCC.append(e)
           Graph_simple = self.decrease(Graph_simple)

        for l in ListSCC:
         #SCCs which are repeated more than 5 times are marked as suspicious   
         if ListSCC.count(l) >= 5:
          ListFinalSCC.append(l)         

    
        return ListFinalSCC
    
    

    def Graph_vis2(self, collections, token):
        #this method is used to create trade graph & transaction history graph
        start_time = datetime.now()
        list_dates2 = []
        list_values = []
        #list_wash_dates = []
        list_wash_dates2 = []
        list_wash_values = []
        a = self.collection.find({"_id": collections})
        # transaction historys are obtained from the collection in MongoDB
        
        #PART 1: here starts the creation of the transaction history graph
        for object in a:
            b = object['token']
        
        #here the list of transactions and their dates are obtained for transaction history graph
        for x in b:
            if (x == token):
                for element in b[x]:
                    date1 = element[4]
                    year = (int(date1[0:4]))
                    month = int(date1[5:7])
                    day = int(date1[8:10])
                    list_dates2.append(date(year, month, day))
                    #this step is needded to convert wei in eth
                    list_values.append(float(element[2]) / 1000000000000000000)

    

        library = self.Washtrading_volume2(collections)
         #here the list of suspicious transactions and their dates are obtained transaction history graphs
        if (token in library):
            for element in library[token]:
                date1 = element[4]
                year = (int(date1[0:4]))
                month = int(date1[5:7])
                day = int(date1[8:10])
                #list_wash_dates.append(date(year, month, day))
                list_wash_dates2.append(date(year, month, day))
                list_wash_values.append(float(element[2]) / 1000000000000000000)

        plt.figure(figsize=(9, 9))
        plt.plot(list_dates2, list_values, 'go', label='Transaction')
        plt.plot(list_wash_dates2, list_wash_values, 'b*', label='Suspicious Transaction')
        plt.title('Transaction History')
        plt.xlabel('Time')
        plt.ylabel('Value in eth')
        plt.legend(loc='best')
        plt.xticks(rotation=90)
        filename1="{collections}_{token}_1.png".format(collections=collections,token=token)
        plt.savefig("static/images/"+filename1, dpi=99)
        plt.clf()
        
        #PART 2: here starts the creation of the trade graph
        a = self.collection.find({"_id": collections})
        g = nx.Graph()
        
        #total value of wash traded transactions and number of these transactions between pair of nodes are obtained to create the graph
        wash_value = 0
        number_wash_transactions = 0
        if (token in library):
            for element in library[token]:
                wash_value = wash_value + int(element[2]) / 1000000000000000000
                number_wash_transactions = number_wash_transactions + 1
                i = 0
                number_w_transaction=0
                for element2 in library[token]:
                 if ((element[0]==element2[0] and element[1]== element2[1])or (element[0]==element2[1] and element[1]== element2[0])):
                   i=i+int(element2[2])/1000000000000000000
                   number_w_transaction=number_w_transaction+1
                i="%.2f" %i    
                g.add_edge(element[0][0:6],element[1][0:6], color='r', weight=str(i)+"eth/ "+str(number_w_transaction)+"transaction(s)")
       

        for object in a:
            b = object['token']
        #total value of not suspicious transactions and number of these transactions between pair of nodes are obtained to create the graph
        for x in b:
            if (x == token):
                for c in b[x]:
                    transaction_value = 0
                    number_of_transaction=0
                    for element2 in b[x]:
                        if ((c[0] == element2[0] and c[1] == element2[1]) or (
                                c[0] == element2[1] and c[1] == element2[0])):
                            transaction_value = transaction_value + int(c[2]) / 1000000000000000000
                            number_of_transaction=number_of_transaction+1
                    if(g.has_edge(c[0][0:6],c[1][0:6])==False and g.has_edge(c[1][0:6],c[0][0:6])==False):  
                     transaction_value="%.2f" %transaction_value
                     g.add_edge(c[0][0:6],c[1][0:6], color='b', weight=str(transaction_value)+"eth/ "+str(number_of_transaction)+"transaction(s)")
        pos = nx.circular_layout(g)

        colors = nx.get_edge_attributes(g, 'color').values()
        weights = nx.get_edge_attributes(g, 'weight').values()

        nx.draw(g, pos, edge_color=colors)
        labels = nx.get_edge_attributes(g, 'weight')
        nx.draw_networkx_labels(g, pos, font_size=10, font_family="sans-serif")
        nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)

        filename2="{collections}_{token}_2.png".format(collections=collections,token=token)
        plt.savefig("static/images/"+filename2, dpi=99)
        end_time = datetime.now()
        time_difference22 = end_time - start_time
        
        return filename1, filename2


    def WCC(self, collections):
      #this method detects the WCCs in each tokens transfer graph and returns all suspicious WCCs in a list
        ListWCC = list()
        ListFinalWCC = list()
 
        a = self.collection.find({"_id": collections})
        #transactions are stored at the 'token'
        for object in a:
            b=object['token']
     
        for x in b:
           Graph_simple = (self.simplfy2(b[x]))
           while (nx.is_empty(Graph_simple) == False):
            for e in list(nx.weakly_connected_components(Graph_simple)):
             if len(e) > 1:
              ListWCC.append(e)
             Graph_simple = self.decrease(Graph_simple)
        for l in ListWCC:
         #WCCs that are repeted more than 3 times are marked as a wash trade   
         if ListWCC.count(l) >= 3:

          ListFinalWCC.append(l)
 
        return ListFinalWCC


    def simplfy(self, list):
     #this method is used to change trade graphs(multigraph) into directed graphs
      
     Simplified_graph=nx.DiGraph()
 
     for e in list:
      number_transaction = 0
      for a in list:
        
         if e[0] == a[0] and e[1] == a[1]:
           number_transaction= number_transaction+1
      #the weight of the edges show the number of the number of transactions between the pair of nodes in the given direction
      Simplified_graph.add_edge(e[0], e[1], weight=number_transaction)
     return Simplified_graph

    def simplfy2(self, list):
     #this method is used to change transfer graphs(multigraph) into directed graphs
     Simplified_graph=nx.DiGraph()
 
     for e in list:
      number_transaction = 0
      for a in list:
       #we don't include the minting transactions   
       if int(e[2]) == 0 and e[0] != '0x0000000000000000000000000000000000000000':
        if e[0] == a[0] and e[1] == a[1]:
         number_transaction = number_transaction+1

      if int(e[2]) == 0 and e[0] != '0x0000000000000000000000000000000000000000':
       #the weight of the edges show the number of the number of transactions between the pair of nodes in the given direction   
       Simplified_graph.add_edge(e[0], e[1], weight=number_transaction)
     return Simplified_graph

    def decrease(self, Graph):
     #this method decreases the weight of the edges by one 
     Graph2 = nx.DiGraph()
     for u,v,d in Graph.edges(data=True):
      #if a weight reaches weight 0, it is removed from the graph   
      if d['weight'] > 1:
        d['weight'] -= 1
        Graph2.add_edge(u, v, weight=d['weight'])
     Graph = Graph2
     return Graph

    def MongoM(self, collections):
     #this method is used to analyze the suspicious wash trading activities
     total_start=datetime.now()
     ListWT = self.SCC(collections) + self.WCC(collections)
     
     #with this endpoint name of the collection is obtained  
     url_info = 'https://deep-index.moralis.io/api/v2/nft/'+collections+'/metadata?chain=eth'
     response_info = requests.request("GET", url_info, headers=self.headers1)
     resp_info = response_info.json()
     self.messages.append("Name: " + str(resp_info["name"]))
     self.messages.append("Collection Address: " + str(resp_info["token_address"]))
     set1 = set()
     volume = 0
     newDict = dict()
     TotalAddress = set()
     total_volume = 0
     wash_volume = 0
      
     for xi in ListWT:
      for y in xi:
       #length of this set returns the number of wash traded accounts   
       set1.add(y)
    
     a = self.collection.find({"_id": collections})
       

     for object in a:
      b = object['token']
         #retrieving ALL to and from addresses 
     for x in b:
      for element in b[x]:
       #storing all addresses that were part of a trade   
       TotalAddress.add(element[0])
       TotalAddress.add(element[1])
       #summing up the trade volumes of each transaction 
       total_volume = total_volume+int(element[2])

     #here the suspicious address ratio is calculated     
     adressRatio = (len(set1)/len(TotalAddress))*100
          
     self.messages.append("Number of Total Adresses : " + str(len(TotalAddress)))
     self.messages.append("Number of Washtrading Adresses : " + str(len(set1))+" ("+ str("%.2f" % adressRatio)+"%)")
   
     connectdict=dict()
     set_partners=set()
     d1 = date(1900, 5, 3)
     d11 = date(1900, 5, 3)

     #in the following loop suspicious partners of each suspicious account are obtained and stored in a dictionary 
     for suspicious_address in set1:
      for suspicious_SCCWCC in ListWT:
       if suspicious_address in suspicious_SCCWCC:
        for adres in suspicious_SCCWCC:   
         set_partners.add(adres)
      connectdict[suspicious_address] = set_partners
      set_partners.clear

     #in the following loop suspicious trades are obtained and suspicious tokens,and transactions are stored in dictionary (newDict)
     for x in b:
      array1 = []
      for s in set1:
       for a in b[x]:
        if a[0] == s and a[1] in connectdict[s]:

         array1.append(a)
         date1 = a[4]
         year = (int(date1[0:4]))
         month = int(date1[5:7])
         day = int(date1[8:10])
         d2=date(year, month, day)

         #date of the last wash trading activity is obtained
         if(d2>d1):
          d1=d2
         #here the total wash trading volume is calculated
         wash_volume  =wash_volume+int(a[2])
      if len(array1) != 0:
       newDict[x] = array1
     if(d1!=d11):
      self.messages.append("Date of the Last Wash Trading Activity: " +str(d1))
     else:
      self.messages.append("0 suspicious activity detected")

     #this endpoint gets the usd value of eth
     url_eth= 'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD'
     response_eth=requests.get(url_eth)
     data=response_eth.json()
     volumeRatio = (wash_volume/total_volume)*100
     self.messages.append("Total Volume: " +str("%.2f" %(total_volume/1000000000000000000))+"eth/ " + str("%.2f" %((total_volume/1000000000000000000)*int(data["USD"]))) + "usd")
     self.messages.append("Wash Trading Volume: " +str("%.2f" %(wash_volume/1000000000000000000))+"eth/ (" + str("%.2f" % volumeRatio)+"%)")

     dicti = dict()
     a = self.collection.find({"_id": collections})

     for object in a:
        b=object['token']
     
     for x in b:
            dicti[x] = (b[x])
   
     #dictionary consisting of each token is returned (this is required for token dropdown)
     return  {'dicti': dicti, 'messages': self.messages}


    def Washtrading_volume2(self, collections):
       #this method is used to identify suspicious accounts and trades, without printing anything on the console
        ListWT=self.SCC(collections)+self.WCC(collections)
   
        set1=set()
        set_scc_wcc=set()
        volume=0
        newDict=dict()
        TotalAddress=set()
        total_volume=0
        wash_volume=0
        scc_wcc_total_lenth=0

        for xi in ListWT:
            #obtaining suspicious SCC/WCCs
            set_scc_wcc.add(frozenset(xi))
            for y in xi:
             #obtaining suspicious addresses   
             set1.add(y)
        
        a=self.collection.find({"_id": collections})
        
        for object in a:
            b=object['token']
            
        number_of_tokens=0  
        for x in b:
           number_of_tokens=number_of_tokens+1
           for element in b[x]:
            #getting every addresses that were involved in a trade   
            TotalAddress.add(element[0])
            TotalAddress.add(element[1])
            #finding total trade volume
            total_volume=total_volume+int(element[2])

        connectdict=dict()
        set_partners=set()
        
        for e in set1:
          for l in ListWT:
            if e in l:
                for adres in l:
                 set_partners.add(adres)
          connectdict[e]=set_partners
          set_partners.clear

        for x in b:
            array1=[]
            for s in set1:
             for a in b[x]:
              if a[0]==s and a[1] in connectdict[s]:
                array1.append(a)
            #thw returned dictionary consists of wash traded tokens and their transactions
            if len(array1)!=0:   
            
             newDict[x]=array1  


        return newDict