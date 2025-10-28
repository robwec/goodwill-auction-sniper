**Goodwill Auction Sniper**

A simple requests-based sniper script in Python.

I haven't used this script in months (June 2024) as of posting this, but it worked swimmingly while I did use it.

1. Place username and password in nobackup/userpass.json

2. Observe a manual login with F12 and copy the headers and json_data into goodwill-refresh-bearer.py

3. Run goodwill-refresh-bearer.py to refresh the active login bearer token. This may need to be done periodically, like every few days or so.

4. Place fields "Title","ID","End Time","Item Value","Shipping" in snipelist.csv, one row per item you want to snipe. Old auctions won't affect the sniper but should be manually cleaned.  
Item Value is your full estimate of the item's value. The script uses a custom formula for calculating snipe price given the shipping and some other variables (in the goodwill-sniper.py script). These can be modified and tested by loading a DF of the CSV with auctions ending in the future, and modifying the bid valuation function as desired.

5. Once all that is done, run python3 goodwill-sniper.py

6. Each time you add new items to the .csv, close and restart the goodwill-sniper.py script again.

Currently set up to snipe 7 seconds before auction end, although that's easy to change in the scripts if desired.


(If you're trying to use this for a business, please please contact me. I have experience with eBay's and Amazon's APIs too.)
