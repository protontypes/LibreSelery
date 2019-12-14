#!/usr/bin/python

import paypalrestsdk,random,string

sender_batch_id = ''.join(
    random.choice(string.ascii_uppercase) for i in range(12))

paypalrestsdk.configure({
  "mode": "live", # sandbox or live
  "client_id": "AcvKXoiEwfYirNs8VU-CdmBDWn7ScnKSMoVvjhTw24WEyjounYAw1fQWebeQC18kHfJ1bGQgMUOIgaom",
  "client_secret": "EL6Vp212Gvhv6o31IM7jzz10rccM7Xdfp5ET1fNuaA-QIMk-XZWa3JFoHtX9yRwypKzOgdSeNU4emz1t" })

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
            "receiver": "ly0@protonmail.com",
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
