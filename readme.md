<!-- An Online Web Service to Detect Wash Trading  -->
## An Online Web Service to Detect Wash Trading 

This project is part of the paper: `Towards an Online Service to Detect NFT Wash Trading Activities on the Ethereum Blockchain`, and in this project a web application to the detect wash trading activities in the given NFT collection is presented. 

**Requirements:**
1. You should get an API key from Moralis and put in the `__init__` method in the services.py
2. You should create a mongoDb collection and cruster as described in `__init__` method in the services.py and put the link in the method

**Running the project:**
```
pip install virtualenv

virtualenv nftprojectenv

source nftprojectenv/bin/activate

cd nft_project

pip install -r requirements.txt

python manage.py runserver
```

**After you run the project:**

-You can enter the NFT contract_address of any collection on the Ethereum blockchain and get the analysis results (this process can take more than an hour depending on the size of the collection).

-Alternatively, you can choose from the existing collections in our database from the dropdown and get the results immediately.

-When the results are ready, you can choose from the tokens to get.



