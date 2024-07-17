import requests
import json
from decouple import config

class Flutterwave():
    base_url = "https://api.flutterwave.com"
    sec_key = config("FLUTTERWAVE_SEC_KEY")

    def get_url(
        self,
        user_id:str,
        email:str,
        name:str,
        phone:str,
        transaction_reference: str, 
        amount: float, 
        currency: str, 
        redirect_url: str,
        description: str
        ):
        Url = f"{self.base_url}/v3/payments"
        headers = {
            "Authorization": "Bearer " + self.sec_key,
            "Content-Type": "application/json",
        }
        payload = json.dumps(
            {
                "tx_ref": transaction_reference,
                "amount": amount,
                "currency": currency,
                "redirect_url": redirect_url,
                "payment_options": "",
                "meta": {"consumer_id": str(user_id)},
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
                return {"status":True,"message":response.json()['message'], "payment_link":response.json()['data']['link'],"reference":transaction_reference, "gateway":"flutterwave"}
            else:
                return {"status":False,"message":response.json()['message'], "payment_link":"", "gateway":"flutterwave"}
        except Exception as e:
            return {"status":False,"message":e, "payment_link":"", "gateway":"flutterwave"}
        
    def verify(self, transaction_id:str):
        url = f"{self.base_url}/v3/transactions/{transaction_id}/verify"
        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + self.sec_key
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.json()["status"] == "success":
                return {"status":True,"message":response.json()['message'], "transaction_info":response.json()['data']}
            else:
                return {"status":False,"message":response.json()['message'], "transaction_info":""}
        except Exception as e:
            return {"status":False,"message":e, "transaction_info":""}



class Paystack():
    base_url = "https://api.paystack.co"
    sec_key = config("PAYSTACK_SEC_KEY")

    def get_url(
            self,
            user_id:str,
            email:str,
            name:str,
            phone:str,
            transaction_reference: str, 
            amount: float, 
            currency: str, 
            redirect_url: str,
        ):
        headers = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + self.sec_key,
        "Cache-Control": "no-cache",
        } 
        url = f"{self.base_url}/transaction/initialize"
        payload = json.dumps({
        "email": email,
        "amount": amount * 100,
        "currency": currency,
        "ref": transaction_reference,
        "callback_url": redirect_url,
        "metadata": {
            "consumer_id": str(user_id),
            "email": email,
            "phonenumber": phone,
            "name": name
        }
        })

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.json()["status"] == True:
                print("paystack response", response.json())
                return {"status":True,"message":response.json()['message'], "payment_link":response.json()['data']['authorization_url'],"reference":response.json()['data']["reference"], "gateway":"paystack"}
            else:
                return {"status":False,"message":response.json()['message'], "payment_link":"", "gateway":"paystack"}
        except Exception as e:
            return {"status":False,"message":e, "payment_link":"", "gateway":"paystack"}
        

    def verify(self, transaction_ref: str):
        url = f"{self.base_url}/transaction/verify/{transaction_ref}"
        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + self.sec_key
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.json()["status"] == True:
                data = response.json()['data']
                amount = data["amount"]/100
                data["amount"] = amount
                return {"status":True,"message":response.json()['message'], "transaction_info":response.json()['data']}
            else:
                return {"status":False,"message":response.json()['message'], "transaction_info":""}
        except Exception as e:
            return {"status":False,"message":e, "transaction_info":""}


    

# SAMPLE Flutterwave TRANSACTION INFO 
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

# SAMPLE Paystack TRANSACTION INFO 
# {
#         "id": 3963143943,
#         "domain": "test",
#         "status": "success",
#         "reference": "ishpjcfvwh",
#         "receipt_number": null,
#         "amount": 500,
#         "message": null,
#         "gateway_response": "Successful",
#         "paid_at": "2024-07-09T11:35:00.000Z",
#         "created_at": "2024-07-09T11:26:05.000Z",
#         "channel": "card",
#         "currency": "NGN",
#         "ip_address": "102.90.47.25",
#         "metadata": {
#             "consumer_id": "26fv83v",
#             "email": "email",
#             "phonenumber": "phone",
#             "name": "name"
#         },
#         "log": {
#             "start_time": 1720524878,
#             "time_spent": 22,
#             "attempts": 1,
#             "errors": 0,
#             "success": true,
#             "mobile": false,
#             "input": [],
#             "history": [
#                 {
#                     "type": "action",
#                     "message": "Attempted to pay with card",
#                     "time": 21
#                 },
#                 {
#                     "type": "success",
#                     "message": "Successfully paid with card",
#                     "time": 22
#                 }
#             ]
#         },
#         "fees": 8,
#         "fees_split": null,
#         "authorization": {
#             "authorization_code": "AUTH_n39jb4tbie",
#             "bin": "408408",
#             "last4": "4081",
#             "exp_month": "12",
#             "exp_year": "2030",
#             "channel": "card",
#             "card_type": "visa ",
#             "bank": "TEST BANK",
#             "country_code": "NG",
#             "brand": "visa",
#             "reusable": true,
#             "signature": "SIG_kCQ4ejFHXKT4AU3v1Q0V",
#             "account_name": null,
#             "receiver_bank_account_number": null,
#             "receiver_bank": null
#         },
#         "customer": {
#             "id": 174098847,
#             "first_name": null,
#             "last_name": null,
#             "email": "customer@gmail.com",
#             "customer_code": "CUS_hs0hw67wqw6zkng",
#             "phone": null,
#             "metadata": null,
#             "risk_action": "default",
#             "international_format_phone": null
#         },
#         "plan": null,
#         "split": {},
#         "order_id": null,
#         "paidAt": "2024-07-09T11:35:00.000Z",
#         "createdAt": "2024-07-09T11:26:05.000Z",
#         "requested_amount": 500,
#         "pos_transaction_data": null,
#         "source": null,
#         "fees_breakdown": null,
#         "connect": null,
#         "transaction_date": "2024-07-09T11:26:05.000Z",
#         "plan_object": {},
#         "subaccount": {}
#     }