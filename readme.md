# Wash Trading Detection Tool

### This project is part of the paper:  

"Towards an Online Service to Detect NFT Wash Trading Activities on the Ethereum Blockchain"  
written by Baran Kalkavan.  


## Web application to detect wash trading activities in a given NFT collection

### Requirements to run the project:
1) Get an API key from Moralis
2) Create a MongoDb collection and cluster

### Steps to run the project:

1) Enter your key and cluster into `nft_project/config.py`

```py
# API-Key
cnf_api = "your-api-key"

# MongoDB Cluster
cnf_cls = "your-cluster"
```

2) Run the following command inside the main directory

```
bash start.sh
```

3) Enter the link in the terminal into your browser

```
...
Starting development server at http://127.0.0.1:8000/
```
