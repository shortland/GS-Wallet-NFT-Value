# L2 NFT Balance

Estimate the value of your NFT holdings using the GameStop NFT Marketplace.

**Only works with NFT's purchased from the GameStop NFT marketplace, as they use the Loopring protocol, wallets, etc...**

## Howto

Get your Loopring L2 apiKey via the steps mentioned on [Loopring's Docs](https://docs.loopring.io/en/basics/key_mgmt.html).

Paste your apiKey into the file `example.key`, then rename the file to `.key`.

That's it! Run the file `my_nfts.py`

## Misc

This script was pretty hacked together and uses several of GameStop's NFT api endpoints. One day these endpoints may change or might no longer be accessible to the public (this is likely).

In any case, some parts of this script can/should be rewritten to query Loopring's Subgraph instead of hackily using GameStop's API.

Some parts, e.g. the order book can only be accessed via GameStop & not the blockchain.
