#!/usr/bin/python

import paypalrestsdk,random,string

sender_batch_id = ''.join(
    random.choice(string.ascii_uppercase) for i in range(12))

paypalrestsdk.configure({
  "mode": "live", # sandbox or live
  "client_id": "",
  "client_secret": "" })

payout = paypalrestsdk.Payout({
    "sender_batch_header": {
        "sender_batch_id": sender_batch_id,
        "email_subject": "You have a payment"
    },
    "items": [
        {
            "recipient_type": "EMAIL",
            "amount": {
                "value": 0.50,
                "currency": "EUR"
            },
            "receiver": "a@protonmail.com",
            "note": "Thank you.",
            "sender_item_id": "item_1"
        }
    ]
})


if payout.create():
    print("payout[%s] created successfully" %
          (payout.batch_header.payout_batch_id))
else:
    print(payout.error)
