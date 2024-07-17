

# NB
# currency example: USD, NGN, etc..
# transaction_reference is a unique string for each transaction, ex. ibved879vbew98gb8qe
# redirect_url is the url to be redirected to after the transaction has been completed or failed
# You can get the transaction id from the redirect_url e.g /tx_ref=ref&transaction_id=30490&status=successful
# tx_ref is transaction_reference... ALways crosscheck transaction_reference to prevent vunerability
from .gateways import Flutterwave, Paystack


def get_payment_url(
    user_id:str,
    email:str,
    name:str,
    phone:str,
    transaction_reference: str, 
    amount: float, 
    currency: str, 
    redirect_url: str,
    description: str,
    gateway:str = "flutterwave"
):
    
    if gateway.lower() == "flutterwave":
        flutterwave = Flutterwave()
        return flutterwave.get_url(
            user_id,
            email,
            name,
            phone,
            transaction_reference,
            amount,
            currency,
            redirect_url,
            description,
        )
    elif gateway.lower() == "paystack":
        paystack = Paystack()
        return paystack.get_url(
            user_id,
            email,
            name,
            phone,
            transaction_reference,
            amount,
            currency,
            redirect_url,
        )
    else:
        return {"status":False,"message":"gateway not implemented", "payment_link":"", "gateway":gateway.lower()}

    
# data = get_payment_url("hdububudbe", "test@gmail.com", "Nkoye Chzie", "09032092438", "abiusbviu97ubiu42we", 200, "USD","https://kwekmarket.com/", "payment for goods and services", "flutterwave")
# print("flwave", data)
# data = get_payment_url("hdububudbe", "test@gmail.com", "Nkoye Chzie", "09032092438", "abiusbviu97ubiu42we", 200, "NGN","https://kwekmarket.com/", "payment for goods and services", "paystack")
# print("paystack", data)



def verify_transaction(transaction_id:str, gateway:str):
    if gateway.lower() == "flutterwave":
        flutterwave = Flutterwave()
        return flutterwave.verify(transaction_id)
    elif gateway.lower() == "paystack":
        paystack = Paystack()
        return paystack.verify(transaction_id)
    else :
        return {"status":False,"message":"gateway not implemented", "transaction_info":""}

# print("verify",verify_transaction("g6kyn3fe97", "paystack"))




    
