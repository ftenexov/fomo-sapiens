# fomo.family API reference (extracted from HAR capture, 2026-09-01)

All `prod-api.fomo.family` endpoints require `Authorization: Bearer <privy access token>` plus browser-like headers (see SKILL.md). Responses wrap payloads as `{success, message, responseObject, statusCode}`.

## GET https://fomo-api.mobula.io/api/2/token/ohlcv-history
Query example: `address=0x39dbed3a2bd333467115de45665cc57f813c4571&chainId=evm%3A4663&period=1m&usd=true&from=1000&to=1788270349000&amount=1500`
Response shape:
```json
{
 "data": [
  {
   "v": 3488.4258344052955,
   "o": 0.35996899179773295,
   "h": 0.36042179935332735,
   "l": 0.35996899179773295,
   "c": 0.36042179935332735,
   "t": 1788180120000
  },
  {
   "v": 11007.830336293246,
   "o": 0.36042179935332735,
   "h": 0.36042179935332735,
   "l": 0.3590036627736999,
   "c": 0.3590036627736999,
   "t": 1788180180000
  },
  "... 1500 items total"
 ]
}
```

## GET https://prod-api.fomo.family/feed/token
Query example: `tokenAddress=0x39dbed3a2bd333467115de45665cc57f813c4571&networkId=4663&excludeThesis=true&threshold=1000`
Response shape:
```json
{
 "success": true,
 "message": "Token feed retrieved successfully",
 "responseObject": {
  "items": [
   {
    "type": "swap_sell",
    "id": "<redacted>",
    "tradeId": "<redacted>",
    "createdAt": "2026-09-01T13:44:49.895Z",
    "userId": "<redacted>",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": null,
    "verified": false,
    "twitter": null,
    "usdAmount": 5273.673567999999,
    "marketCap": 297483899.5803643,
    "fdv": 420812020.6475797,
    "price": 0.4208120206475797,
    "isDev": false
   },
   {
    "type": "swap_buy",
    "id": "<redacted>",
    "tradeId": "<redacted>",
    "createdAt": "2026-09-01T13:43:03.024Z",
    "userId": "<redacted>",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": null,
    "verified": false,
    "twitter": null,
    "usdAmount": 1187.67311,
    "marketCap": 302778215.15017587,
    "fdv": 428301204.55306536,
    "price": 0.42830120455306536,
    "isDev": false
   },
   "... 100 items total"
  ],
  "hasNextPage": true
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/feed/token/sortedThesis
Query example: `tokenAddress=0x39dbed3a2bd333467115de45665cc57f813c4571&networkId=4663&afterTime=1788238800000&limit=80&beforeTime=1788292800000&threshold=1000`
Response shape:
```json
{
 "success": true,
 "message": "Token thesis feed retrieved successfully",
 "responseObject": {
  "items": [
   {
    "type": "thesis",
    "id": "<uuid>",
    "tradeId": "<uuid>",
    "createdAt": "2026-09-01T05:01:51.336Z",
    "userId": "<uuid>",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>",
    "verified": false,
    "twitter": null,
    "comment": {
     "id": "<uuid>",
     "userId": "<uuid>",
     "tradeId": "<uuid>",
     "comment": "pons has another ~$1m aside just today for buyback and burn - and adding tens of thousands of dollars to that number eve...",
     "createdAt": "2026-09-01T05:01:51.336Z",
     "parentId": null,
     "numLikes": 50,
     "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
     "networkId": 4663,
     "shortCommentSegments": [
      {
       "text": "pons has another ~$1m aside just today for buyback and burn - and adding tens of thousands of dollars to that number eve...",
       "link": null,
       "provider": null
      }
     ],
     "reactions": {
      "counts": {
       "likeCount": 50
      },
      "reactions": {
       "like": false
      }
     },
     "olderThesis": 10,
     "newerThesis": 1
    },
    "numReplies": 0,
    "authorTrade": {
     "humanTokenAmount": 10957903.012617486,
     "usdValue": 4631842.392495936,
     "unrealizedPnlUsd": 2915637.2030700855,
     "realizedPnlUsd": -1936778.0646503444,
     "percentageUnrealizedPnl": 169.88861361300863,
     "percentageRealizedPnl": -96.76331881174214,
     "closedAt": null
    },
    "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
    "networkId": 4663,
    "ticker": "PONS",
    "tokenImageUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_small_bd2a5c52259a.png",
    "equity": 0,
    "threshold": 6568620.45714628,
    "isDev": false
   },
   {
    "type": "thesis",
    "id": "<uuid>",
    "tradeId": "<uuid>",
    "createdAt": "2026-09-01T07:34:29.138Z",
    "userId": "<uuid>",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>"success": true,
 "message": "Token thesis feed retrieved successfully",
 "responseObject": {
  "items": [
   {
    "type": "thesis",
    "id": "<uuid>",
    "tradeId": "<uuid>",
    "createdAt": "2026-09-01T13:34:05.643Z",
    "userId": "<uuid>",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>",
    "verified": false,
    "twitter": null,
    "comment": {
     "id": "<uuid>",
     "userId": "<uuid>",
     "tradeId": "<uuid>",
     "comment": "higher 1B is fud\uff01",
     "createdAt": "2026-09-01T13:34:05.643Z",
     "parentId": null,
     "numLikes": 2,
     "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
     "networkId": 4663,
     "shortCommentSegments": [
      {
       "text": "higher 1B is fud\uff01",
       "link": null,
       "provider": null
      }
     ],
     "reactions": {
      "counts": {
       "likeCount": 2
      },
      "reactions": {
       "like": false
      }
     },
     "olderThesis": 0,
     "newerThesis": 0
    },
    "numReplies": 0,
    "authorTrade": {
     "humanTokenAmount": 3384.0326835707087,
     "usdValue": 1430.4110944682027,
     "unrealizedPnlUsd": 1281.6028094682026,
     "realizedPnlUsd": 0,
     "percentageUnrealizedPnl": 861.2442576488281,
     "percentageRealizedPnl": 0,
     "closedAt": null
    },
    "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
    "networkId": 4663,
    "ticker": "PONS",
    "tokenImageUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_small_bd2a5c52259a.png",
    "equity": 0,
    "threshold": 1430.4110944682027,
    "isDev": false
   },
   {
    "type": "thesis",
    "id": "<uuid>",
    "tradeId": "<uuid>",
    "createdAt": "2026-09-01T13:28:42.710Z",
    "userId": "<uuid>",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>",
    "verified": false,
    "twitter": null,
    "comment": {
     "id": "<uuid>",
     "userId":
...truncated
```

## GET https://prod-api.fomo.family/hodlers/devs
Query example: `tokenAddress=0x39dbed3a2bd333467115de45665cc57f813c4571&networkId=4663`
Response shape:
```json
{
 "success": true,
 "message": "Dev holdings found",
 "responseObject": {
  "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
  "networkId": 4663,
  "devHoldings": [
   {
    "user": {
     "id": "<uuid>",
     "address": "GRFL1ZMedQj7gUvpimztaCM2HzXHf1RnG7d4AnBRhZPW",
     "evmAddress": "0x47fb428bb217fe6b39bd30ee33367fd73fa6ddf4",
     "createdAt": "2025-11-04T14:44:25.261Z",
     "displayName": "<redacted>",
     "userHandle": "<redacted>",
     "profilePictureLink": "<redacted>",
     "description": "<redacted>",
     "following": 23,
     "followers": 21239,
     "activated": false,
     "verified": false,
     "isReferred": false,
     "isRestricted": false,
     "swapCount": 266,
     "numTrades": 1637,
     "totalVolume": 39145.081699,
     "private": false,
     "thumbhash": "<redacted>",
     "coverPhotoLink": null,
     "coverPhotoThumbhash": null,
     "twitter": null,
     "clan": {
      "id": "<uuid>",
      "name": "Nobi Ventures",
      "iconLink": "<profile-pic-url>",
      "iconThumbhash": "LvgVBwC4uId5h3h/dWaId4iIhmQIuIkP"
     }
    },
    "tradeId": "<uuid>",
    "humanAmount": 77068.01,
    "sumSwapOpen": 44763.77,
    "price": 0.422694231475,
    "value": 32576.2,
    "pnl": 23972.48,
    "unrealizedPnl": 23972.48,
    "realizedPnl": 0,
    "costBasis": 8603.07,
    "averageEntryPrice": 0.111638,
    "comment": {
     "id": "<uuid>",
     "userId": "<uuid>",
     "tradeId": "<uuid>",
     "comment": "You can now see which tokens distribute creator rewards to holders.\n\nSee here: https://x.com/meadgod/status/209382995406...",
     "createdAt": "2026-08-29T22:44:28.379Z",
     "parentId": null,
     "numLikes": 197,
     "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
     "networkId": 4663,
     "shortCommentSegments": [
      {
       "text": "You can now see which tokens distribute creator rewards to holders.\n\nSee here: https://x.com/meadgod/status/209382995406...",
       "link": null,
       "provider": null
      }
     ],
     "reactions": {
      "counts": {
       "likeCount": 194
      },
      "rea
...truncated
```

## POST https://prod-api.fomo.family/hodlers/friends
Body example: `{"tokens": [{"address": "HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump", "networkId": 1399811149}, {"address": "BKXtSJWJk8s6DGEv71a3HohqHMhzn1iXLAzxMm6ZXjmy", "networkId": 1399811149}, "... 75 items total"], "limit": 2}`
Response shape:
```json
{
 "success": true,
 "message": "Top friend holders found",
 "responseObject": {
  "tokens": [
   {
    "tokenAddress": "HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump",
    "networkId": 1399811149,
    "topHolders": [],
    "totalHolders": 0
   },
   {
    "tokenAddress": "BKXtSJWJk8s6DGEv71a3HohqHMhzn1iXLAzxMm6ZXjmy",
    "networkId": 1399811149,
    "topHolders": [],
    "totalHolders": 0
   },
   "... 75 items total"
  ]
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/hodlers/top
Query example: `tokens=%5B%7B%22address%22%3A%220x39dbed3a2bd333467115de45665cc57f813c4571%22%2C%22networkId%22%3A4663%7D%5D`
Response shape:
```json
{
 "success": true,
 "message": "Top holders found",
 "responseObject": [
  {
   "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
   "networkId": 4663,
   "topHolders": [
    {
     "user": {
      "id": "<uuid>",
      "address": "HvdahwUMiFStRDFkNi2VQVjkY6tvsi5FZ3bnBH5LSK7d",
      "evmAddress": "0x3a6962e0a77a66a14c558bee1fe3880bfe51ebe9",
      "createdAt": "2026-07-06T19:16:25.904Z",
      "displayName": "<redacted>",
      "userHandle": "<redacted>",
      "profilePictureLink": "<redacted>",
      "description": "<redacted>",
      "following": 3,
      "followers": 9932,
      "activated": false,
      "verified": false,
      "isReferred": true,
      "isRestricted": false,
      "swapCount": 178,
      "numTrades": 121,
      "totalVolume": 258428.212268,
      "private": false,
      "thumbhash": "<redacted>",
      "coverPhotoLink": null,
      "coverPhotoThumbhash": null,
      "twitter": null,
      "clan": null
     },
     "tradeId": "<uuid>",
     "humanAmount": 10957903.01,
     "sumSwapOpen": 12907012.58,
     "price": 0.422694231475,
     "value": 4631842.39,
     "pnl": 978859.14,
     "unrealizedPnl": 2915637.2,
     "realizedPnl": -1936778.06,
     "costBasis": 3717767.27,
     "averageEntryPrice": 0.156618,
     "comment": {
      "id": "<uuid>",
      "userId": "<uuid>",
      "tradeId": "<uuid>",
      "comment": "fyi, it's even more bullish now that I think about it: because of the burns, the market cap shown here on fomo actually ...",
      "createdAt": "2026-09-01T13:12:03.211Z",
      "parentId": null,
      "numLikes": 7,
      "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
      "networkId": 4663,
      "shortCommentSegments": [
       {
        "text": "fyi, it's even more bullish now that I think about it: because of the burns, the market cap shown here on fomo actually ...",
        "link": null,
        "provider": null
       }
      ],
      "reactions": {
       "counts": {
        "likeCount": 8
       },
       "reactions": {
        "like": false
       }
      },
      "olderThesis": 11,
      "newerThesis": 0
     },
     "numReplies": 0,
     "show
...truncated
```

## POST https://prod-api.fomo.family/proxy/cryptoTokens
Response shape:
```json
{
 "success": true,
 "message": "Successfully fetched 73 crypto tokens (from 73 total)",
 "responseObject": [
  {
   "change24": "-0.003978321597618646",
   "createdAt": 1699892062,
   "holders": 62222,
   "liquidity": "823056.3602351254",
   "marketCap": "1542849148292.8472",
   "priceUSD": "77766.3770577769",
   "volume24": "1657465.1675403854",
   "token": {
    "address": "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",
    "decimals": 8,
    "networkId": 1399811149,
    "name": "Bitcoin",
    "symbol": "BTC",
    "info": {
     "circulatingSupply": 19839540,
     "id": "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh:1399811149",
     "imageLargeUrl": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
     "imageSmallUrl": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
     "imageThumbUrl": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
     "name": "Bitcoin",
     "symbol": "BTC",
     "totalSupply": 19839540
    },
    "socialLinks": {
     "discord": null,
     "telegram": null,
     "twitter": "<redacted>",
     "website": "https://wbtc.network"
    },
    "launchpad": null
   }
  },
  {
   "change24": "-0.002702710867339253",
   "createdAt": 1666839853,
   "holders": 82996,
   "liquidity": "2647759.5005299007",
   "marketCap": "294636024884.1803",
   "priceUSD": "2442.4935015456276",
   "volume24": "8603962.151543148",
   "token": {
    "address": "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
    "decimals": 8,
    "networkId": 1399811149,
    "name": "Ethereum",
    "symbol": "ETH",
    "info": {
     "circulatingSupply": 120629195,
     "id": "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs:1399811149",
     "imageLargeUrl": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
     "imageSmallUrl": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
     "imageThumbUrl": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
     "name": "Ethereum",
     "symbol": "ETH",
     "totalSupply": 120629195
    },
    "socialLinks": {
     "discord": null,
     "telegram": null,
     "twitter": "<redacted>",
     "website": "https://weth.io/"
    },
    "launchpad": null
   }
  },
  "... 73 items total"
 ],
 "statusCode": 200
}
```

## POST https://prod-api.fomo.family/proxy/filterTokens
Body example: `["cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij:1399811149", "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs:1399811149", "... 4 items total"]`
Response shape:
```json
{
 "success": true,
 "message": "Successfully fetched 4 cached, 0 fresh",
 "responseObject": [
  {
   "buyCount1": null,
   "buyCount4": null,
   "buyCount12": null,
   "buyCount24": null,
   "change5m": "0.003639459925647536",
   "change1": "-0.0005428074488384588",
   "change4": "-0.0016504160394295378",
   "change12": "-0.009147551525819333",
   "change24": "-0.0009613713586095207",
   "createdAt": 1731000424,
   "exchanges": [
    {
     "name": "Orca"
    }
   ],
   "holders": 72459,
   "liquidity": "7450796.034990855",
   "marketCap": "1544708356132.0735",
   "pair": {
    "protocol": "Orca"
   },
   "priceUSD": "77860.0893030823",
   "sellCount1": null,
   "sellCount4": null,
   "sellCount12": null,
   "sellCount24": null,
   "token": {
    "address": "cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij",
    "decimals": 8,
    "networkId": 1399811149,
    "createdAt": 1731000424,
    "name": "Bitcoin",
    "symbol": "BTC",
    "freezable": null,
    "mintable": null,
    "isScam": null,
    "i18n": null,
    "info": {
     "address": "cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij",
     "circulatingSupply": 19839540,
     "cmcId": null,
     "description": null,
     "id": "cbbtcf3aa214zXHbiAZQwf4122FBYbraNdFqgw4iMij:1399811149",
     "imageBannerUrl": null,
     "imageLargeUrl": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
     "imageSmallUrl": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
     "imageThumbUrl": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
     "name": "Bitcoin",
     "networkId": 1399811149,
     "symbol": "BTC",
     "totalSupply": 19839540
    },
    "socialLinks": {
     "discord": null,
     "telegram": null,
     "twitter": "<redacted>",
     "website": "https://www.coinbase.com/"
    },
    "launchpad": null
   },
   "txnCount1": 3185,
   "txnCount4": 7678,
   "txnCount12": 20438,
   "txnCount24": 46425,
   "uniqueBuys1": null,
   "uniqueBuys4": null,
   "uniqueBuys12": null,
   "uniqueBuys24": null,
   "uniqueSells1": null,
   "uniqueSells4": null,
   "uniqueSells12": null,
   "uniqueSells24": null,
   "volume1": "3538182.9494444653",
   "volume5m": "1018424.4366287966",
   "volume4": "7320866.457773146",
   "volume12": "15342301.232691396",
   "volume24": "36951782.20749962"
  },
  {
   "buyCount1": null,
   "buyCount4": null,
   "buyCount12": null,
   "buyCount24": null,
   "change5m": "0.001976614741556614",
   "change1": "-0.0014299054973814166",
   "cha
...truncated
```

## POST https://prod-api.fomo.family/proxy/mostHeld
Response shape:
```json
{
 "success": true,
 "message": "Successfully fetched most held tokens",
 "responseObject": [
  {
   "change24": "0.97496121595809",
   "createdAt": 1784738253,
   "liquidity": "997109",
   "marketCap": "179653642",
   "priceUSD": "0.181177077783",
   "volume24": "22107569",
   "token": {
    "address": "0x2e8c31162b855a2ffa90f6f8634643ad6f111e18",
    "decimals": 18,
    "networkId": 4663,
    "name": "Artificial Inu",
    "symbol": "AI",
    "info": {
     "circulatingSupply": "989544742.952718984396199383",
     "id": "0x2e8c31162b855a2ffa90f6f8634643ad6f111e18:4663",
     "imageLargeUrl": "https://token-media.defined.fi/4663_0x2e8c31162b855a2ffa90f6f8634643ad6f111e18_large_ff88da525656.png",
     "imageSmallUrl": "https://token-media.defined.fi/4663_0x2e8c31162b855a2ffa90f6f8634643ad6f111e18_small_5262a498e0da.png",
     "imageThumbUrl": "https://token-media.defined.fi/4663_0x2e8c31162b855a2ffa90f6f8634643ad6f111e18_thumb_390d89c531f0.png",
     "imageThumbHash": "mQcKFwIHOImEeoaAedpXOKeFiKEHl50P",
     "name": "Artificial Inu",
     "symbol": "AI",
     "totalSupply": "991591453.151661299074185643"
    },
    "socialLinks": {
     "discord": null,
     "telegram": "https://t.me/artificially_inu",
     "twitter": "<redacted>",
     "website": "https://artificialinu.com/"
    },
    "launchpad": {
     "launchpadName": "LONG",
     "launchpadIconUrl": "https://crypto-exchange-logos-production.s3.us-west-2.amazonaws.com/launchpad/long.png",
     "graduationPercent": null
    }
   }
  },
  {
   "change24": "0.1336246942541174",
   "createdAt": 1784338933,
   "liquidity": "1558969",
   "marketCap": "422694231",
   "priceUSD": "0.422694231475",
   "volume24": "33022832",
   "token": {
    "address": "0x39dbed3a2bd333467115de45665cc57f813c4571",
    "decimals": 18,
    "networkId": 4663,
    "name": "Pons",
    "symbol": "PONS",
    "info": {
     "circulatingSupply": "706928236.324076210799163674",
     "id": "0x39dbed3a2bd333467115de45665cc57f813c4571:4663",
     "imageLargeUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_large_4d07826ce769.png",
     "imageSmallUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_small_bd2a5c52259a.png",
     "imageThumbUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_thumb_af38c5d84ec2.png",
     "imageThumbHash": "LuiFBQA2h3mfU3pFZoZglPepCWV6lnRpaA==",
     "name": "Pons",
     "symbol": "PONS",

...truncated
```

## POST https://prod-api.fomo.family/proxy/tokenDetails
Body example: `{"tokenId": "0x39dbed3a2bd333467115de45665cc57f813c4571:4663"}`
Response shape:
```json
{
 "success": true,
 "message": "Successfully fetched token details",
 "responseObject": {
  "buyCount5m": 18,
  "buyCount1": 382,
  "buyCount4": 2053,
  "buyCount24": 19182,
  "buyVolume5m": "14290",
  "buyVolume1": "611349",
  "buyVolume4": "2299428",
  "buyVolume24": "16666045",
  "sellCount5m": 24,
  "sellCount1": 550,
  "sellCount4": 1834,
  "sellCount24": 15849,
  "sellVolume5m": "35266",
  "sellVolume1": "554568",
  "sellVolume4": "2469255",
  "sellVolume24": "16356693",
  "uniqueBuys5m": 10,
  "uniqueBuys1": 166,
  "uniqueBuys4": 645,
  "uniqueBuys24": 4984,
  "uniqueSells5m": 12,
  "uniqueSells1": 283,
  "uniqueSells4": 666,
  "uniqueSells24": 5552,
  "holders": 60780,
  "top10HoldersPercent": 37.42843830126869,
  "isLowFees": false
 },
 "statusCode": 200
}
```

## POST https://prod-api.fomo.family/proxy/tokenWarnings
Body example: `{"address": "0x39dbed3a2bd333467115de45665cc57f813c4571", "networkId": 4663}`
Response shape:
```json
{
 "success": true,
 "message": "Token is on allowlist",
 "responseObject": {
  "disableBuying": false,
  "disableSelling": false,
  "warnings": []
 },
 "statusCode": 200
}
```

## POST https://prod-api.fomo.family/proxy/trendingTokens
Response shape:
```json
{
 "success": true,
 "message": "Successfully fetched 50 trending tokens",
 "responseObject": [
  {
   "change24": "0.13224245364038986",
   "createdAt": 1783975341,
   "holders": 60783,
   "liquidity": "4485370.308079437",
   "marketCap": "298803584.8059357",
   "priceUSD": "0.4226787994985304",
   "volume24": "83989676.07052135",
   "token": {
    "address": "0x39dbed3a2bd333467115de45665cc57f813c4571",
    "decimals": 18,
    "networkId": 4663,
    "name": "Pons",
    "symbol": "PONS",
    "info": {
     "circulatingSupply": "706928251.8083204",
     "id": "0x39dbed3a2bd333467115de45665cc57f813c4571:4663",
     "imageLargeUrl": "https://metadata.mobula.io/assets/logos/evm_4663_0x39dbed3a2bd333467115de45665cc57f813c4571.webp",
     "imageSmallUrl": "https://metadata.mobula.io/assets/logos/evm_4663_0x39dbed3a2bd333467115de45665cc57f813c4571.webp",
     "imageThumbUrl": "https://metadata.mobula.io/assets/logos/evm_4663_0x39dbed3a2bd333467115de45665cc57f813c4571.webp",
     "name": "Pons",
     "symbol": "PONS",
     "totalSupply": "1000000000"
    },
    "socialLinks": {
     "discord": null,
     "telegram": null,
     "twitter": "<redacted>",
     "website": "https://ponsfamily.com/launchpad"
    },
    "launchpad": {
     "launchpadName": "Pons",
     "launchpadIconUrl": "https://metadata.mobula.io/assets/logos/factory_pons.webp",
     "graduationPercent": 0
    }
   }
  },
  {
   "change24": "0.05041391280518935",
   "createdAt": 1782947894,
   "holders": 101666,
   "liquidity": "4321823.130390615",
   "marketCap": "204514879.03582537",
   "priceUSD": "0.20695917387720808",
   "volume24": "48398107.3137027",
   "token": {
    "address": "0x020bfc650a365f8bb26819deaabf3e21291018b4",
    "decimals": 18,
    "networkId": 4663,
    "name": "Cash Cat",
    "symbol": "CASHCAT",
    "info": {
     "circulatingSupply": "988189483",
     "id": "0x020bfc650a365f8bb26819deaabf3e21291018b4:4663",
     "imageLargeUrl": "https://metadata.mobula.io/assets/logos/168f971b6f871d1054629930d0ba96451d4664d6b6630e774af0935f22537884.png",
     "imageSmallUrl": "https://metadata.mobula.io/assets/logos/168f971b6f871d1054629930d0ba96451d4664d6b6630e774af0935f22537884.png",
     "imageThumbUrl": "https://metadata.mobula.io/assets/logos/168f971b6f871d1054629930d0ba96451d4664d6b6630e774af0935f22537884.png",
     "name": "Cash Cat",
     "symbol": "CASHCAT",
     "totalSupply": "1000000000"
    },
    "socialLinks": {
     "discord": null,
     "telegram": "https:/
...truncated
```

## GET https://prod-api.fomo.family/proxy/verifiedTokens
Response shape:
```json
{
 "success": true,
 "message": "Successfully fetched 417 verified tokens (filtered from 417 total)",
 "responseObject": [
  {
   "change24": "-0.047396392119941816",
   "createdAt": 1703382717,
   "holders": 69044,
   "liquidity": "715966.0949601543",
   "marketCap": "11487596.657143643",
   "priceUSD": "0.020679623798411713",
   "volume24": "51931.474258570146",
   "token": {
    "address": "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC",
    "decimals": 9,
    "networkId": 1399811149,
    "name": "PONKE",
    "symbol": "PONKE",
    "info": {
     "circulatingSupply": "555503174",
     "id": "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC:1399811149",
     "imageLargeUrl": "https://metadata.mobula.io/assets/logos/e24eafc5a9ea137634da4e91a092ee9784374600da965df74765a61e47d54e1b.png",
     "imageSmallUrl": "https://metadata.mobula.io/assets/logos/e24eafc5a9ea137634da4e91a092ee9784374600da965df74765a61e47d54e1b.png",
     "imageThumbUrl": "https://metadata.mobula.io/assets/logos/e24eafc5a9ea137634da4e91a092ee9784374600da965df74765a61e47d54e1b.png",
     "name": "PONKE",
     "symbol": "PONKE",
     "totalSupply": "563842826"
    },
    "socialLinks": {
     "discord": null,
     "telegram": "https://t.me/PonkeHQ",
     "twitter": "<redacted>",
     "website": "https://www.ponke.xyz/"
    },
    "launchpad": null
   }
  },
  {
   "change24": "0.9532725580439637",
   "createdAt": 1786828046,
   "holders": 54770,
   "liquidity": "303820.4429623141",
   "marketCap": "2308243.2368085496",
   "priceUSD": "0.003162217314395103",
   "volume24": "3096640.6491176803",
   "token": {
    "address": "ApZuxdpzMrbEYTGEzeY9afh5pj9d6qPRJCTgQYiipbKg",
    "decimals": 9,
    "networkId": 1399811149,
    "name": "CyberLeek",
    "symbol": "CYBERLEEK",
    "info": {
     "circulatingSupply": "729944531.7375637",
     "id": "ApZuxdpzMrbEYTGEzeY9afh5pj9d6qPRJCTgQYiipbKg:1399811149",
     "imageLargeUrl": "https://metadata.mobula.io/assets/logos/solana_solana_ApZuxdpzMrbEYTGEzeY9afh5pj9d6qPRJCTgQYiipbKg.webp",
     "imageSmallUrl": "https://metadata.mobula.io/assets/logos/solana_solana_ApZuxdpzMrbEYTGEzeY9afh5pj9d6qPRJCTgQYiipbKg.webp",
     "imageThumbUrl": "https://metadata.mobula.io/assets/logos/solana_solana_ApZuxdpzMrbEYTGEzeY9afh5pj9d6qPRJCTgQYiipbKg.webp",
     "name": "CyberLeek",
     "symbol": "CYBERLEEK",
     "totalSupply": "729944531.7375637"
    },
    "socialLinks": {
     "discord": null,
     "telegram": null,
     "twitter": "<redacted>"inTokenId": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149", "outTokenId": "HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump:1399811149", "amount": "3000000", "retry": 0}`
Response shape:
```json
{
 "success": true,
 "message": "Successful v2 swap",
 "responseObject": {
  "v1Swap": {
   "swapTransaction": "<redacted>",
   "feePayerSignature": "<redacted>",
   "feePayerAddress": "<redacted>",
   "feeTierBps": 0,
   "flatFee": 0.1,
   "feeTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
   "dynamicSlippageBps": 4500,
   "lastValidBlockHeight": 421485792,
   "priceImpactPct": 0.03390665683112226,
   "swapUsdValue": 2.8746683631879444,
   "expectedOutHumanAmount": 2601.730147,
   "swapSize": 1120,
   "priorityFeeLamports": 260142,
   "priorityFeePct": 75,
   "platform": "dflow",
   "priceImpactWarningInfo": {
    "warningLevel": "NONE",
    "displayPriceImpactInline": false,
    "name": "",
    "description": "<redacted>"
   }
  }
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/swaps/v2/status
Query example: `relaySwapId=0x1788270406b2d8af46e1b0b50817bdacf728b320dfc618ebdf438b291d29bf06`
Response shape:
```json
{
 "success": true,
 "message": "Got v2 swap status",
 "responseObject": {
  "status": "PENDING"
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/trades
Query example: `userId=<USER_ID>&orderBy=closedAt&tokenAddress=HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump`
Response shape:
```json
{
 "success": true,
 "message": "Trades with details found",
 "responseObject": {
  "activeTrades": [],
  "closedTrades": [],
  "hasNextPage": false,
  "closedCount": 0
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/trades/{id}
Response shape:
```json
{
 "success": true,
 "message": "Trade details found",
 "responseObject": {
  "trade": {
   "userAddress": "<SOLANA_ADDRESS>",
   "tokenAddress": "HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump",
   "createdAt": "2026-09-01T13:46:30.989Z",
   "updatedAt": "2026-09-01T13:46:30.989Z",
   "closedAt": null,
   "humanTokenAmount": 3598.876783,
   "avgEntryPrice": 0.0010836714439411803,
   "avgExitPrice": null,
   "sumSwapOpen": 3598.876783,
   "sumSwapClosed": 0,
   "sumTransferIn": 0,
   "sumTransferOut": 0,
   "avgTransferInPrice": null,
   "avgTransferOutPrice": null,
   "realizedPnlUsd": 0,
   "networkId": 1399811149,
   "commentId": null,
   "id": "<uuid>",
   "tokenMetadata": {
    "symbol": "SOLCAT",
    "networkId": 1399811149,
    "imageLargeUrl": "https://token-media.defined.fi/1399811149_HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump_large_0ec63a69aa8d.png",
    "liquidity": 48220,
    "currentPrice": 0.00100633482734,
    "thumbhash": "<redacted>"
   },
   "unrealizedPnlUsd": -0.2783249539617605,
   "totalCostBasis": 3.9
  },
  "swaps": [
   {
    "id": "<uuid>",
    "signature": "287bcHBnDhtVEVh4R1J3eK76V262SvviPVhY6QxeGdbc7so4LwnpJgxR8bsVD1EZNt3M1T84dA51Wpm32o6Q542w",
    "address": "<SOLANA_ADDRESS>",
    "networkId": 1399811149,
    "inTokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "inAmount": 3900000,
    "inHumanAmount": 3.9,
    "outTokenAddress": "HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump",
    "outAmount": 3598876783,
    "outHumanAmount": 3598.876783,
    "humanUsdAmountIn": 3.9,
    "humanUsdAmountOut": 3.9,
    "createdAt": "2026-09-01T13:46:30.989Z",
    "platformFeeAmount": 100000,
    "platformFeeHumanAmount": 0.1,
    "platformFeeToken": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "inTradeId": null,
    "outTradeId": "<uuid>",
    "referralFeeTokenAmount": null,
    "referralFeeHumanAmount": null,
    "referralFeeToken": null,
    "referralFeeAddress": null,
    "isOffPlatform": false,
    "isCrossmint": false,
    "provider": "DFLOW",
    "inNetworkId": 1399811149,
    "outNetworkId": 1399811149,
    "recipient": null
   }
  ],
  "transfers": [],
  "displayName": "<redacted>",
  "userHandle": "<redacted>",
  "profilePictureLink": null,
  "userId": "<USER_ID>",
  "verified": false,
  "isDev": false,
  "comment": n
...truncated
```

## GET https://prod-api.fomo.family/trades/{id}/comments
Response shape:
```json
{
 "success": true,
 "message": "No comments found",
 "responseObject": {
  "comments": [],
  "hasNextPage": false
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/v2/leaderboard
Response shape:
```json
{
 "success": true,
 "message": "Leaderboard found",
 "responseObject": {
  "leaderboard": [
   {
    "id": "<uuid>",
    "address": "FJDy9FDRy6bwGEUKuAC98bUtN8MkpE2pT7Dj7HE3Z7Q1",
    "evmAddress": "0x2ac082e252143c89c6e3bcb972e49855f9f6711c",
    "createdAt": "2026-05-18T12:45:58.832Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>",
    "description": "<redacted>"If the Lord will, we shall live, and do this, or that.\" - James 4:15",
    "following": 30,
    "followers": 403454,
    "activated": false,
    "verified": false,
    "isReferred": true,
    "isRestricted": false,
    "swapCount": 343,
    "numTrades": 2114,
    "totalVolume": 1948730.735273,
    "private": false,
    "thumbhash": "<redacted>",
    "coverPhotoLink": null,
    "coverPhotoThumbhash": null,
    "twitter": null,
    "totalPnL": 7665832.745316569,
    "clan": {
     "id": "<uuid>",
     "name": "Fantom Troupe",
     "iconLink": "<profile-pic-url>",
     "iconThumbhash": "phgWJwJoh4iPd4Z0hmhneIh4l/xoB3sC"
    },
    "totalHoldings": 87,
    "topHoldings": [
     {
      "imageUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_thumb_af38c5d84ec2.png",
      "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
      "networkId": 4663,
      "humanAmount": 10957901.416319031,
      "price": 0.422694231475,
      "value": 4631841.7177497875,
      "pnl": 4564131.000592202
     },
     {
      "imageUrl": "https://token-media.defined.fi/1399811149_Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk_thumb_c8981520d740.png",
      "tokenAddress": "Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk",
      "networkId": 1399811149,
      "humanAmount": 15904993.286531,
      "price": 0.105525257333,
      "value": 1678378.5094408211,
      "pnl": 840703.3179072486
     },
     "... 3 items total"
    ]
   },
   {
    "id": "<uuid>",
    "address": "43nktK56Bfk3yJK9iqr3Kzyt9npgEB6sPYKAeoYMxeug",
    "evmAddress": "0xb48ae67b008443eaa5b5f20b7e9da4fb39f8e167",
    "createdAt": "2025-11-10T00:15:45.484Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": null,
    "
...truncated
```

## GET https://prod-api.fomo.family/v2/leaderboard/24h
Response shape:
```json
{
 "success": true,
 "message": "24H Leaderboard found",
 "responseObject": {
  "leaderboard": [
   {
    "id": "<uuid>",
    "address": "43nktK56Bfk3yJK9iqr3Kzyt9npgEB6sPYKAeoYMxeug",
    "evmAddress": "0xb48ae67b008443eaa5b5f20b7e9da4fb39f8e167",
    "createdAt": "2025-11-10T00:15:45.484Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": null,
    "description": "<redacted>",
    "following": 38,
    "followers": 387035,
    "activated": false,
    "verified": false,
    "isReferred": false,
    "isRestricted": false,
    "swapCount": 962,
    "numTrades": 1916,
    "totalVolume": 956201.962186,
    "private": false,
    "thumbhash": null,
    "coverPhotoLink": null,
    "coverPhotoThumbhash": null,
    "twitter": null,
    "pnl24h": 2471798.2331310026,
    "clan": null,
    "totalHoldings": 71,
    "topHoldings": [
     {
      "imageUrl": "https://token-media.defined.fi/4663_0x2e8c31162b855a2ffa90f6f8634643ad6f111e18_thumb_390d89c531f0.png",
      "tokenAddress": "0x2e8c31162b855a2ffa90f6f8634643ad6f111e18",
      "networkId": 4663,
      "humanAmount": 29322551.565300036,
      "price": 0.18105377793,
      "value": 5308958.739444806,
      "pnl": 5287752.4060958065
     },
     {
      "imageUrl": "https://token-media.defined.fi/1399811149_9cRCn9rGT8V2imeM2BaKs13yhMEais3ruM3rPvTGpump_thumb_1489ea350df9.png",
      "tokenAddress": "9cRCn9rGT8V2imeM2BaKs13yhMEais3ruM3rPvTGpump",
      "networkId": 1399811149,
      "humanAmount": 10000.198225,
      "price": 0.289190885146,
      "value": 2891.966176323208,
      "pnl": 843743.1688891529
     },
     "... 3 items total"
    ]
   },
   {
    "id": "<uuid>",
    "address": "CDY1JBoi2fKPPsHabyANmp6RP9Lkz8TcrkACsX3rHkka",
    "evmAddress": "0xa14b38a3dfd05c089bae5d60e9d42af3924e5da0",
    "createdAt": "2026-03-18T08:14:07.169Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>",
    "description": "<redacted>",
    "following": 132,
    "followers": 123029,
    "activated": false,
    "verified": false,
    "isReferred": false,
    "isRestricted": false,
    "swapCount": 665,
    "numTrades": 884,
    "totalVolum
...truncated
```

## GET https://prod-api.fomo.family/v2/leaderboard/30d
Response shape:
```json
{
 "success": true,
 "message": "30D Leaderboard found",
 "responseObject": {
  "leaderboard": [
   {
    "id": "<uuid>",
    "address": "FJDy9FDRy6bwGEUKuAC98bUtN8MkpE2pT7Dj7HE3Z7Q1",
    "evmAddress": "0x2ac082e252143c89c6e3bcb972e49855f9f6711c",
    "createdAt": "2026-05-18T12:45:58.832Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>",
    "description": "<redacted>"If the Lord will, we shall live, and do this, or that.\" - James 4:15",
    "following": 30,
    "followers": 403454,
    "activated": false,
    "verified": false,
    "isReferred": true,
    "isRestricted": false,
    "swapCount": 343,
    "numTrades": 2114,
    "totalVolume": 1948730.735273,
    "private": false,
    "thumbhash": "<redacted>",
    "coverPhotoLink": null,
    "coverPhotoThumbhash": null,
    "twitter": null,
    "pnl30d": 7634989.020867732,
    "clan": {
     "id": "<uuid>",
     "name": "Fantom Troupe",
     "iconLink": "<profile-pic-url>",
     "iconThumbhash": "phgWJwJoh4iPd4Z0hmhneIh4l/xoB3sC"
    },
    "totalHoldings": 87,
    "topHoldings": [
     {
      "imageUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_thumb_af38c5d84ec2.png",
      "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
      "networkId": 4663,
      "humanAmount": 10957901.416319031,
      "price": 0.422694231475,
      "value": 4631841.7177497875,
      "pnl": 4564131.000592202
     },
     {
      "imageUrl": "https://token-media.defined.fi/1399811149_Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk_thumb_c8981520d740.png",
      "tokenAddress": "Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk",
      "networkId": 1399811149,
      "humanAmount": 15904993.286531,
      "price": 0.10527346181,
      "value": 1674373.7033379276,
      "pnl": 836698.511804355
     },
     "... 3 items total"
    ]
   },
   {
    "id": "<uuid>",
    "address": "43nktK56Bfk3yJK9iqr3Kzyt9npgEB6sPYKAeoYMxeug",
    "evmAddress": "0xb48ae67b008443eaa5b5f20b7e9da4fb39f8e167",
    "createdAt": "2025-11-10T00:15:45.484Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": null,
    "
...truncated
```

## GET https://prod-api.fomo.family/v2/leaderboard/7d
Response shape:
```json
{
 "success": true,
 "message": "7D Leaderboard found",
 "responseObject": {
  "leaderboard": [
   {
    "id": "<uuid>",
    "address": "FJDy9FDRy6bwGEUKuAC98bUtN8MkpE2pT7Dj7HE3Z7Q1",
    "evmAddress": "0x2ac082e252143c89c6e3bcb972e49855f9f6711c",
    "createdAt": "2026-05-18T12:45:58.832Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": "<redacted>",
    "description": "<redacted>"If the Lord will, we shall live, and do this, or that.\" - James 4:15",
    "following": 30,
    "followers": 403454,
    "activated": false,
    "verified": false,
    "isReferred": true,
    "isRestricted": false,
    "swapCount": 343,
    "numTrades": 2114,
    "totalVolume": 1948730.735273,
    "private": false,
    "thumbhash": "<redacted>",
    "coverPhotoLink": null,
    "coverPhotoThumbhash": null,
    "twitter": null,
    "pnl7d": 6233013.448695778,
    "clan": {
     "id": "<uuid>",
     "name": "Fantom Troupe",
     "iconLink": "<profile-pic-url>",
     "iconThumbhash": "phgWJwJoh4iPd4Z0hmhneIh4l/xoB3sC"
    },
    "totalHoldings": 87,
    "topHoldings": [
     {
      "imageUrl": "https://token-media.defined.fi/4663_0x39dbed3a2bd333467115de45665cc57f813c4571_thumb_af38c5d84ec2.png",
      "tokenAddress": "0x39dbed3a2bd333467115de45665cc57f813c4571",
      "networkId": 4663,
      "humanAmount": 10957901.416319031,
      "price": 0.422694231475,
      "value": 4631841.7177497875,
      "pnl": 4564131.000592202
     },
     {
      "imageUrl": "https://token-media.defined.fi/1399811149_Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk_thumb_c8981520d740.png",
      "tokenAddress": "Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk",
      "networkId": 1399811149,
      "humanAmount": 15904993.286531,
      "price": 0.10527346181,
      "value": 1674373.7033379276,
      "pnl": 836698.511804355
     },
     "... 3 items total"
    ]
   },
   {
    "id": "<uuid>",
    "address": "43nktK56Bfk3yJK9iqr3Kzyt9npgEB6sPYKAeoYMxeug",
    "evmAddress": "0xb48ae67b008443eaa5b5f20b7e9da4fb39f8e167",
    "createdAt": "2025-11-10T00:15:45.484Z",
    "displayName": "<redacted>",
    "userHandle": "<redacted>",
    "profilePictureLink": null,
    "de
...truncated
```

## POST https://prod-api.fomo.family/v2/users
Body example: `{"address": "<SOLANA_ADDRESS>", "evmAddress": "<EVM_ADDRESS>"}`
Response shape:
```json
{
 "success": true,
 "message": "User already exists",
 "responseObject": {
  "id": "<redacted>",
  "address": "<address>",
  "evmAddress": "<redacted>",
  "createdAt": "2026-09-01T13:24:54.111Z",
  "displayName": "<redacted>",
  "userHandle": "<redacted>",
  "profilePictureLink": null,
  "description": null,
  "following": 0,
  "followers": 0,
  "activated": false,
  "verified": false,
  "isReferred": false,
  "isRestricted": false,
  "swapCount": 3,
  "numTrades": 1,
  "totalVolume": 7.42983,
  "private": false,
  "thumbhash": null,
  "coverPhotoLink": null,
  "coverPhotoThumbhash": null,
  "twitter": null,
  "signupReferralCode": null,
  "signupReferrerUserHandle": null
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/v2/users/{id}/balances
Response shape:
```json
{
 "success": true,
 "message": "User balances found",
 "responseObject": {
  "balances": [
   {
    "balance": {
     "address": "<SOLANA_ADDRESS>",
     "tokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
     "walletId": "<SOLANA_ADDRESS>:1399811149",
     "balance": "7442296",
     "tokenId": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149",
     "shiftedBalance": 7.442296
    },
    "tokenFilterResult": {
     "change24": "0.000012631580589679186",
     "createdAt": 1710952381,
     "marketCap": "7751705147",
     "priceUSD": "0.9998875",
     "volume1": "9743964",
     "volume24": "127245924",
     "token": {
      "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "decimals": 6,
      "networkId": 1399811149,
      "name": "USDC",
      "symbol": "USDC",
      "info": {
       "circulatingSupply": "74050527331.15753",
       "id": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v:1399811149",
       "imageLargeUrl": "https://token-media.defined.fi/1399811149_EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v_large_c8d2766f-09f9-48b6-ae77-54a...",
       "imageSmallUrl": "https://token-media.defined.fi/1399811149_EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v_small_c8d2766f-09f9-48b6-ae77-54a...",
       "imageThumbUrl": "https://token-media.defined.fi/1399811149_EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v_thumb_c8d2766f-09f9-48b6-ae77-54a...",
       "imageThumbHash": "JYWFDQIsSFeHeHCNR0iHgHQICFh3iHB0Vw==",
       "name": "USDC",
       "symbol": "USDC",
       "totalSupply": "74050527331.15753"
      },
      "launchpad": {
       "launchpadIconUrl": "https://metadata.mobula.io/assets/logos/factory_orca.webp",
       "graduationPercent": 0
      }
     }
    },
    "userToken": {
     "id": "<uuid>",
     "userAddress": "<SOLANA_ADDRESS>",
     "tokenAddress": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
     "networkId": 1399811149,
     "humanAmountRemaining": 7.442296,
     "tokenAmountRemaining": 7442296,
     "averageEntryPriceUsd": 1,
     "currentRealizedPnlUsd": 0,
     "totalRealizedPnlUsd": 0,
     "currentCostBasisUsd": 12.45370831587,
     "totalCostBasisUsd": 12.45370831587,
     "updatedAt": "2026-09-01T13:45:14.172Z",
     "holdingSince": "2026-09-01T13:44:14.000Z",
     "wasSwapped": true
    },
    "valuation": {
     "useLivePrice": true,
     "includeInEquity": true,
     "includeUnrealizedP
...truncated
```

## GET https://prod-api.fomo.family/v2/users/{id}/swaps
Query example: `tokenAddress=HmJDgky11u77hpBss6D8sjNpYPD5B6fWgSVDj58jpump`
Response shape:
```json
{
 "success": true,
 "message": "Swaps found",
 "responseObject": {
  "swaps": [],
  "hasNextPage": false
 },
 "statusCode": 200
}
```
## GET https://prod-api.fomo.family/config
Response shape:
```json
{
 "success": true,
 "message": "Config retrieved successfully",
 "responseObject": {
  "crossmint": {
   "minimumAmount": 5,
   "minimumAmountByChain": {
    "1": 10
   },
   "dailyMaximum": 2500,
   "maximumAmount": 2500,
   "defaultBuyAmount": 100
  },
  "simulateBeforeSend": false,
  "transferMessageMaxLength": 200,
  "sendPromo": {
   "id": "lunar-ny-2026",
   "animationType": "packets",
   "notePlaceholder": "Send new year greetings",
   "confirmAnimationImageUrl": "https://imagedelivery.net/VWS-JqlWPUIfni0YSL62hg/<uuid>/public",
   "images": [
    {
     "url": "https://imagedelivery.net/VWS-JqlWPUIfni0YSL62hg/<uuid>/public"
    },
    {
     "url": "https://imagedelivery.net/VWS-JqlWPUIfni0YSL62hg/<uuid>/public"
    },
    "... 5 items total"
   ]
  },
  "primarySolanaRpc": "helius",
  "helpCenter": {
   "items": [
    {
     "question": "Failed or pending deposits",
     "answer": [
      {
       "type": "text",
       "text": "A failed or pending deposit/withdrawal request is returned to your bank account within 3 business days.\n\nTo make it clea..."
      }
     ]
    },
    {
     "question": "USD deposit is not available",
     "answer": [
      {
       "type": "text",
       "text": "USD deposit is only available for the following countries at this time: Andorra, Australia, Austria, Belgium, Brazil, Bu..."
      }
     ]
    },
    "... 6 items total"
   ]
  },
  "awaitRelayConfirmationOnSells": false,
  "isUk": true,
  "archaxApprovalDate": "Mar 23, 2026",
  "datadog": {
   "enabled": true,
   "sessionSampleRate": 100,
   "resourceTraceSampleRate": 100
  },
  "performanceTelemetry": {
   "startupEnabled": false,
   "resourceUsageEnabled": false,
   "hermesMemoryEnabled": false,
   "frameRateEnabled": false,
   "networkEnabled": false,
   "screenTimeEnabled": false,
   "navigationEnabled": false
  },
  "socialLinks": {
   "instagram": "https://www.instagram.com/tryfomo",
   "discord": "http://fomo.family/discord",
   "youtube": "https://www.youtube.com/@fomo",
   "tiktok": "https://www.tiktok.com/@fomo"
  },
  "minPurchaseAmountByChain": {
   "1": {
    "buy": 25,
    "sell": 5
   },
   "default": {
    "buy": 2,
    "sell": 2
   }
  },
  "minUsdcTransferByChain": {
   "1": {
    "in": 5,
    "out": 15
   },
   "1337": {
    "in": 5,
    "out": 2
   },
   "default": {
    "in": 0.5,
    "out": 0.5
   }
  },
  "evmGasLimitBufferMultiplier": 15,
  "evmG
```

## GET https://prod-api.fomo.family/tokenAllowList/detailed
Response shape:
```json
{
 "success": true,
 "message": "Token allowlist found",
 "responseObject": {
  "tokens": [
   {
    "name": null,
    "ticker": "PONKE",
    "tokenAddress": "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC",
    "createdAt": "2025-02-12T18:05:33.474Z",
    "iconLink": null,
    "networkId": 1399811149,
    "isLowFees": false,
    "categories": [
     "Memes"
    ],
    "notes": ""
   },
   {
    "name": null,
    "ticker": "BUTTCOIN",
    "tokenAddress": "FasH397CeZLNYWkd3wWK9vrmjd1z93n3b59DssRXpump",
    "createdAt": "2025-02-12T18:05:34.020Z",
    "iconLink": null,
    "networkId": 1399811149,
    "isLowFees": false,
    "categories": [
     "Memes"
    ],
    "notes": ""
   },
   "... 680 items total"
  ],
  "categories": [
   "Memes",
   "Large Caps",
   "... 5 items total"
  ]
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/v2/userTokens/aggregatedSnapshotById
Query example: `userId=<USER_ID>&snapshotId=1788181200`
Response shape:
```json
{
 "success": true,
 "message": "User token snapshot stats found",
 "responseObject": {
  "snapshotId": 1788181200,
  "pnl": 0,
  "equity": 0
 },
 "statusCode": 200
}
```

## GET https://prod-api.fomo.family/watchlist
Response shape:
```json
{
 "success": true,
 "message": "Watchlist found",
 "responseObject": {
  "watchlist": []
 },
 "statusCode": 200
}
```

## POST https://prod-api.fomo.family/swaps/v2/fast-fill
Body example: `{"relaySwapId":"0x1788270406b2d8af46e1b0b50817bdacf728b320dfc618ebdf438b291d29bf06"}`
Response shape:
```json
{
 "success": false,
 "message": "Relay fast fill is not enabled",
 "responseObject": {
  "relaySwapId": "<redacted>",
  "message": "Relay fast fill is not enabled"
 },
 "statusCode": 400
}
```

## WSS wss://prod-api.fomo.family/ws
Live event stream (prices, fills, feed). Not needed for the skill; poll REST instead.

## POST https://prod-api.fomo.family/trades/comment
Creates a thesis (top-level comment on your own trade) or a comment. Route confirmed via Datadog RUM (`"http.route":"/trades/comment","http.method":"POST"`).
Body example: `{"tradeId":"<uuid>","comment":"<text>","visibility":"public"}`
Get `<uuid>` from `GET /trades?userId={me}&tokenAddress={addr}` → `responseObject.activeTrades[0].trade.id` (or closedTrades). The `trade.commentId` field is non-null once a thesis exists.
VERIFIED: returns `200 {"success":true,"message":"Trade comment created successfully","responseObject":{"id","userId","tradeId","comment",...}}`. Intermittently 500s ("Failed to create trade comment") — transient; retry once.
