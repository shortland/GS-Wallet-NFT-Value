#!/usr/bin/python3

import requests
import json
import time
import os


if __name__ == '__main__':
    # Save all data from run of the script to this object, then write it to a file for future comparison
    data_run = dict()

    # TODO: Maybe do something with this one day
    # Total requests to each endpoint
    data_run["metrics"] = dict()
    data_run["metrics"]["endpoint_requests"] = dict()
    data_run["metrics"]["endpoint_requests"]["api.nft.gamestop.com"] = 0
    data_run["metrics"]["endpoint_requests"]["api3.loopring.io"] = 0

    # Get the current time. This will be the file save name as-well for better indexing
    data_run["time"] = int(time.time())

    # Equivalent to 1 eth
    data_run["eth_dust_factor"] = 1000000000000000000.0

    # This is private, read from .key file
    loopring_l2_api_key = ""
    with open(".key", "r") as f:
        loopring_l2_api_key = f.read().rstrip()

    # GS one
    data_run["loopring_l2_account_id"] = 150002

    # Get an L2 accountId's NFT holdings
    data_run["my_nfts"] = requests.get(
        "https://api3.loopring.io/api/v3/user/nft/balances?accountId={}&limit=100".format(
            data_run["loopring_l2_account_id"]
        ),
        headers={
            "X-API-KEY": loopring_l2_api_key
        }
    ).json()
    data_run["metrics"]["endpoint_requests"]["api3.loopring.io"] += 1

    print("account nfts:")
    print(data_run["my_nfts"])

    data_run["usd_to_eth"] = float(requests.get(
        "https://api.nft.gamestop.com/nft-svc-marketplace/ratesAndFees"
    ).json()["rates"][0]["quotes"][0]["rate"])
    data_run["metrics"]["endpoint_requests"]["api.nft.gamestop.com"] += 1

    # keep track of total worth
    total_worth_eth = 0.0
    total_worth_usd = 0.0

    data_run["nft_order_book"] = dict()
    data_run["game_stop_nft_data"] = dict()
    data_run["collection_stats"] = dict()
    for i in range(0, len(data_run["my_nfts"]["data"]), 1):
        print("")

        token_id = data_run["my_nfts"]["data"][i]["nftId"]
        contract_address = data_run["my_nfts"]["data"][i]["tokenAddress"]

        # Get GameStop Metadata of an NFT
        data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)] = requests.get(
            "https://api.nft.gamestop.com/nft-svc-marketplace/getNft?tokenIdAndContractAddress={}_{}".format(
                token_id,
                contract_address
            )
        ).json()
        data_run["metrics"]["endpoint_requests"]["api.nft.gamestop.com"] += 1
        # https://api.nft.gamestop.com/nft-svc-marketplace/getNft?tokenIdAndContractAddress=0x6f02466fc4d4820ed1e737c6c87682ffddc427a10927f982b56744d70a2433c7_0x8c8201d8ff0dcab054d392113666e870757e9fdf

        print("Name: {}".format(data_run["game_stop_nft_data"]["{}_{}".format(
            token_id, contract_address)]["name"]))
        print("Token ID: {}".format(token_id))
        print("Contract Address: {}".format(contract_address))

        is_gamestop_nft = False
        if "nftId" in data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]:
            is_gamestop_nft = True

        if is_gamestop_nft:
            print("NFT ID (GS): {}".format(
                data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["nftId"]))

        print("Amount: {}".format(data_run["my_nfts"]["data"][i]["total"]))

        if is_gamestop_nft:
            print(
                "GS Link: https://nft.gamestop.com/token/{}/{}".format(contract_address, token_id))

            # Get orderbook of the NFT
            data_run["nft_order_book"][data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["nftId"]] = requests.get(
                "https://api.nft.gamestop.com/nft-svc-marketplace/getNftOrders?nftId={}".format(
                    data_run["game_stop_nft_data"]["{}_{}".format(
                        token_id, contract_address)]["nftId"]
                )
            ).json()
            data_run["metrics"]["endpoint_requests"]["api.nft.gamestop.com"] += 1

            # Get the cheapest available one for sale
            # We could store more metadata (like how many for sale, or who is selling), but this will suffice.
            cheapest = -1
            for j in range(0, len(data_run["nft_order_book"][data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["nftId"]]), 1):
                if int(data_run["nft_order_book"][data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["nftId"]][j]["pricePerNft"]) < cheapest or cheapest == -1:
                    cheapest = int(
                        data_run["nft_order_book"][data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["nftId"]][j]["pricePerNft"])

            data_run["collection_stats"][data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["collectionId"]] = requests.get(
                "https://api.nft.gamestop.com/nft-svc-marketplace/getCollectionStats?collectionId={}".format(
                    data_run["game_stop_nft_data"]["{}_{}".format(
                        token_id, contract_address)]["collectionId"]
                )
            ).json()
            data_run["metrics"]["endpoint_requests"]["api.nft.gamestop.com"] += 1

            if (cheapest == -1):
                # print(
                #     "TODO: Can't infer price. Thus we print out price last paid & cheapest price in collection"
                # )
                # TODO: in what scenario does this not work, and should i just show the last trade value of the specific NFT?
                # Collection Floor Price
                print("Collection Floor Price: {} ETH; ${} USD".format(
                    float(data_run["collection_stats"][data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["collectionId"]]["floorPrice"]) /
                    data_run["eth_dust_factor"],
                    round(
                        float(data_run["collection_stats"][data_run["game_stop_nft_data"]["{}_{}".format(token_id, contract_address)]["collectionId"]]["floorPrice"]) /
                        data_run["eth_dust_factor"] * data_run["usd_to_eth"], 2
                    )
                ))

                total_worth_eth += (
                    (
                        float(
                            data_run["collection_stats"][data_run["game_stop_nft_data"]["{}_{}".format(
                                token_id, contract_address)]["collectionId"]]["floorPrice"]
                        ) / data_run["eth_dust_factor"]
                    ) * int(data_run["my_nfts"]["data"][i]["total"])
                )
                total_worth_usd += (
                    (
                        (
                            float(
                                data_run["collection_stats"][data_run["game_stop_nft_data"]["{}_{}".format(
                                    token_id, contract_address)]["collectionId"]]["floorPrice"]
                            ) / data_run["eth_dust_factor"]
                        ) * data_run["usd_to_eth"]
                    ) * int(data_run["my_nfts"]["data"][i]["total"])
                )

            else:
                print("Lowest Listed Price: {} ETH; ${} USD".format(
                    float(cheapest/data_run["eth_dust_factor"]),
                    round(
                        float(cheapest/data_run["eth_dust_factor"]) * data_run["usd_to_eth"], 2)
                ))

                total_worth_eth += (
                    (
                        float(cheapest / data_run["eth_dust_factor"])
                    ) * int(data_run["my_nfts"]["data"][i]["total"])
                )
                total_worth_usd += (
                    (
                        float(
                            cheapest / data_run["eth_dust_factor"]
                        ) * data_run["usd_to_eth"]
                    ) * int(data_run["my_nfts"]["data"][i]["total"])
                )

    print("\n\ntotal worth:\n\teth: {};\n\tusd: ${}".format(
        total_worth_eth, total_worth_usd))

    # TODO: Maybe do something here one day, store the data for a future project.
    os.makedirs("saves", exist_ok=True)
    os.makedirs(
        "saves/{}".format(data_run["loopring_l2_account_id"]), exist_ok=True)

    with open("saves/{}/{}.json".format(data_run["loopring_l2_account_id"], data_run["time"]), "w") as f:
        print(json.dumps(data_run), file=f)
