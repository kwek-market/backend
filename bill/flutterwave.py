import requests
import json
from decouple import config

# NB
# currency example: USD, NGN, etc..
# transaction_reference is a unique string for each transaction, ex. ibved879vbew98gb8qe
# redirect_url is the url to be redirected to after the transaction has been completed or failed
# You can get the transaction id from the redirect_url e.g /tx_ref=ref&transaction_id=30490&status=successful
# tx_ref is transaction_reference... ALways crosscheck transaction_reference to prevent vunerability
def get_payment_url(
    user_id:str,
    email:str,
    name:str,
    phone:str,
    transaction_reference: str, 
    amount: int, 
    currency: str, 
    redirect_url: str,
    description: str
):
    Url = "https://api.flutterwave.com/v3/payments"
    headers = {
        "Authorization": "Bearer " + config("FLUTTERWAVE_SEC_KEY"),
        "Content-Type": "application/json",
    }
    payload = json.dumps(
        {
            "tx_ref": transaction_reference,
            "amount": amount,
            "currency": currency,
            "redirect_url": redirect_url,
            "payment_options": "",
            "meta": {"consumer_id": user_id},
            "customer": {
                "email": email,
                "phonenumber": phone,
                "name": name,
            },
            "customizations": {
                "title": "Kwek Market",
                "description": description,
                "logo": "https://kwekmarket.com/_next/image?url=%2Fsvg%2Fkweklogo.svg&w=256&q=75",
            },
        }
    )

    try:
        response = requests.request("POST", Url, headers=headers, data=payload)
        if response.json()["status"] == "success":
            return {"status":True,"message":response.json()['message'], "payment_link":response.json()['data']['link']}
        else:
            return {"status":False,"message":response.json()['message'], "payment_link":""}
    except Exception as e:
        return {"status":False,"message":e, "payment_link":""}

# get_payment_url("hdububudbe", "test@gmail.com", "Nkoye Chzie", "09032092438", "abiusbviu97ubiu42we", 200, "USD","https://kwekmarket.com/", "payment for goods and services")


def verify_transaction(transaction_id:int):
    url = "https://api.flutterwave.com/v3/transactions/{}/verify".format(transaction_id)
    payload={}
    headers = {
    'Content-Type': 'application/json',
    'Authorization': "Bearer " + config("FLUTTERWAVE_SEC_KEY")
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.json()["status"] == "success":
            return {"status":True,"message":response.json()['message'], "transaction_info":response.json()['data']}
        else:
            return {"status":False,"message":response.json()['message'], "transaction_info":""}
    except Exception as e:
        return {"status":False,"message":e, "transaction_info":""}


# SAMPLE TRANSACTION INFO 
# {
#         "id": 27870909,
#         "tx_ref": "abiusbviu97ubiu42we",
#         "flw_ref": "FLW-MOCK-ca39dabda2ccfaf61f5e03e3ab9",
#         "device_fingerprint": "e2b61db5b200c6ef69ab23134fd2",
#         "amount": 200,
#         "currency": "USD",
#         "charged_amount": 207.6,
#         "app_fee": 7.6,
#         "merchant_fee": 0,
#         "processor_response": "Approved. Successful",
#         "auth_model": "VBVSECURECODE",
#         "ip": "52.209.154.143",
#         "narration": "CARD Transaction ",
#         "status": "successful",
#         "payment_type": "card",
#         "created_at": "2021-12-31T07:57:11.000Z",
#         "account_id": 66137,
#         "card": {
#             "first_6digits": "553188",
#             "last_4digits": "2950",
#             "issuer": " CREDIT",
#             "country": "NIGERIA NG",
#             "type": "MASTERCARD",
#             "token": "flw-t1nf-a7cd8ef25c8e89baf0f80df881d9fccc-m03k",
#             "expiry": "09/32"
#         },
#         "meta": {
#             "__CheckoutInitAddress": "https://ravemodal-dev.herokuapp.com/v3/hosted/pay/dd85dafd60138ca58811",
#             "consumer_id": "hdububudbe"
#         },
#         "amount_settled": 200,
#         "customer": {
#             "id": 1479642,
#             "name": "Nwye Chzie",
#             "phone_number": "N/A",
#             "email": "gregofl@gmail.com",
#             "created_at": "2021-12-31T07:57:10.000Z"
#         }
#     }
    