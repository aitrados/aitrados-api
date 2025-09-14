---
title: "Broker Setup Overview"
description: ""
date: "2023-05-22T00:44:31+01:00"
lastmod: "2023-05-22T00:44:31+01:00"
draft: false
toc: true
weight: 510
slug: "broker-setup-overview"
---


Welcome to the broker configuration guide. Below are the key points and frequently asked questions.

---

## Location of the Trading Gateway Configuration File

The configuration file is located in()
````plaintext
~/.aitrados/aitrados_trade_gateway.json
````
#### Note:'~' is computer username directory



---
## Local Broker transaction log file location

The database file is located in()
````plaintext
~/.aitrados/aitrados_database.db
````
#### Note:'~' is computer username directory



## File Format

The configuration file uses JSON format. Example:
````json
{
  "BROKER_1": {

  },
  "BROKER_2": {

  }
}
````

---

## How to Disable a Broker

To disable a specific broker, set the `enable` property to `false`:
````json
"BROKER_1": {
  "enable": false
}
````



---

## Set the maximum capital position percentage

To set the maximum capital position percentage for a broker, use the `maximum_fund_percentage` property. This value should be between 0 and 1, representing the percentage of total capital that can be allocated to this broker.
````json
"BROKER_1": {
  "maximum_fund_percentage": 0.3
}
````



---
## How to Set Up Staging Order to locally
To set up staging orders locally, you can use the following configuration. This allows you to stage open, close, and conditional orders locally for a specific broker.
````json
"BROKER_1": {
    "enable_open_order_staging_orders_locally": true,
    "enable_close_order_staging_orders_locally":true,
    "enable_conditional_order_staging_orders_locally":true,
}
````
If you set up a Staging Order, when the price reaches your specified level, it will ensure full execution and be submitted to the broker at the market price.
Unfilled orders will wait until all are completed, unless you cancel the order.
all order staging will be recorded in the local database, and you can view the order status in the local database.
````plaintext
~/.aitrados/aitrados_database.db
````




---



## Can Paper Account Be Used Together with Other Accounts?

**No**. Since the Paper account has the highest trading privileges and supports the widest variety of instruments, it cannot be used simultaneously with other accounts.

---

## Does the system support trading with multiple brokers at the same time?

**Yes**, multiple brokers can be traded concurrently.

---

## How to Set Up Cross-Broker Arbitrage?

Configure the trading gateways for two brokers to enable arbitrage between them.

---

Feel free to modify the configuration to suit your trading needs.
