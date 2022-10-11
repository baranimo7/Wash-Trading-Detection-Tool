# Wash Trading Detection Tool

### This project is part of the paper:  

"Towards an Online Service to Detect NFT Wash Trading Activities on the Ethereum Blockchain"  
written by Baran Kalkavan.  


## Web application to detect wash trading activities in a given NFT collection

### Requirements to run the project:
1) Get an API key from Moralis and enter it into the `__init__` method inside `collection/services.py`
2) Create a MongoDb collection and cluster as described in `__init__` and enter the link into the method

### Steps to run the project:

```
pip install virtualenv

virtualenv nftprojectenv

source nftprojectenv/bin/activate

cd nft_project

pip install -r requirements.txt

python manage.py runserver
```

