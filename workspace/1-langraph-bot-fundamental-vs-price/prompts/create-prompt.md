
현재 tiingo 에서 받아오는 news 데이터는 다음과 같습니다.
```json
[
  {
    "id": 91332925,
    "publishedDate": "2026-01-04T03:30:19Z",
    "title": "Perplexity CEO Says On-Device AI Threatens Data Centers As Industry Faces '$10 Trillion Question' \u2014 Apple, Qualcomm Positioned To Benefit",
    "url": "https://finance.yahoo.com/news/perplexity-ceo-says-device-ai-033019227.html",
    "description": "Aravind Srinivas, CEO of Perplexity AI, which is backed by Jeff Bezos and Nvidia Corp. (NASDAQ:NVDA), issued a contrarian warning about the future of artificial intelligence, saying on-device intelligence running on personal devices could disrupt the centralized data center model driving massive infrastructure investments. Localized AI Could Upend Data Center Industry \u201cThe biggest threat to a data center is if the intelligence can be packed locally on a chip that\u2019s running on the device and then",
    "source": "finance.yahoo.com",
    "tags": [
      "Aravind Srinivas",
      "Artificial Intelligence",
      "Data Center",
      "Intelligence",
      "Personal Devices",
      "Stock",
      "Technology",
      "Unknown Sector"
    ],
    "crawlDate": "2026-01-04T03:47:27.079802Z",
    "tickers": [
      "aapl",
      "goog",
      "googl",
      "hpq",
      "lnvgf",
      "lnvgy",
      "nvda",
      "qcom",
      "ssnlf"
    ]
  },
  {
    "id": 91332712,
    "publishedDate": "2026-01-04T02:31:17Z",
    "title": "TSMC Secures One-Year US Export License To Keep China Chip Operations Running: Report",
    "url": "https://finance.yahoo.com/news/tsmc-secures-one-us-export-023117235.html",
    "description": "Taiwan Semiconductor Manufacturing Co. (NYSE:TSM) has secured a one-year U.S. export license allowing it to import the U.S. chipmaking equipment into its China operations. US Grants Annual License For TSMC's China Operations On Thursday, TSMC said the U.S. Department of Commerce has approved an annual export license covering its Nanjing fabrication plant, reported Reuters. This allows U.S.-controlled equipment to be supplied without requiring separate approvals from individual vendors. The compa",
    "source": "finance.yahoo.com",
    "tags": [
      "China",
      "Export License",
      "Manufacturing Operations",
      "Nanjing",
      "Stock",
      "Taiwan",
      "Taiwan Semiconductor Manufacturing Co.",
      "Technology",
      "Tsmc",
      "U.S. Department Of Commerce",
      "Unknown Sector"
    ],
    "crawlDate": "2026-01-04T02:54:26.934262Z",
    "tickers": [
      "aapl",
      "nvda",
      "ssnlf",
      "tsm"
    ]
  },
  {
    "id": 91332472,
    "publishedDate": "2026-01-04T01:30:19Z",
    "title": "Elon Musk's 2025: From Trump Power Broker To Tesla Turmoil",
    "url": "https://finance.yahoo.com/news/elon-musks-2025-trump-power-013019232.html",
    "description": "Whether it\u2019s bold predictions or political commentary, billionaire Elon Musk, CEO of Tesla Inc. (NASDAQ:TSLA) and SpaceX, as well as the world\u2019s richest person, has been in the headlines this year for a multitude of reasons. With Tesla's Robotics push and SpaceX's looming IPO, 2025 has proven to be a pivotal year for the 54-year-old businessman. Let's take a look at Musk's 2025. Elon Musk Was Instrumental For Trump's Reelection The billionaire was instrumental in securing President Donald Trump'",
    "source": "finance.yahoo.com",
    "tags": [
      "Consumer Cyclical",
      "Elon Musk",
      "Real Estate",
      "Stock",
      "Technology",
      "Tesla Inc",
      "Tesla Robotaxis",
      "Trump",
      "Unknown Sector",
      "Utilities"
    ],
    "crawlDate": "2026-01-04T01:47:35.365858Z",
    "tickers": [
      "aapl",
      "four",
      "meta",
      "msft",
      "plug",
      "pw",
      "terp",
      "tsla"
    ]
  },
  {
    "id": 91331668,
    "publishedDate": "2026-01-03T22:47:21Z",
    "title": "'s Biggest Stories of 2026 To Watch For: WBD, Bad Bunny, Disney CEO",
    "url": "https://deadline.com/2026/01/biggest-stories-2026-predictions-1236659377/",
    "description": "Bad Bunny at the Super Bowl, Disney's next CEO, Keith Richards' health, America 250, Trump & the midterms, Nick Reiner's trial & WBD - 2026's big stories",
    "source": "deadline.com",
    "tags": [
      "Amptp",
      "Bad Bunny",
      "Basic Materials",
      "Caa",
      "Consumer Cyclical",
      "Dana Walden",
      "Disney",
      "Donald Trump",
      "Keith Richards",
      "Labor",
      "Look Ahead 2026",
      "Netflix",
      "Netflix Wb",
      "Nfl",
      "Nick Reiner",
      "Paramount",
      "Range Media Partners",
      "Real Estate",
      "Rob Reiner",
      "Rolling Stones",
      "Stephen Colbert",
      "Stock",
      "Super Bowl",
      "Technology",
      "Wbd"
    ],
    "crawlDate": "2026-01-03T23:05:34.706275Z",
    "tickers": [
      "aapl",
      "dis",
      "nflx",
      "pgre",
      "pzg"
    ]
  },
  {
    "id": 91331523,
    "publishedDate": "2026-01-03T22:30:00Z",
    "title": "Berkshire is selling Apple stock and buying this other magnificent artificial intelligence (AI) stock instead",
    "url": "https://www.fool.com.au/2026/01/04/berkshire-is-selling-apple-stock-and-buying-this-other-magnificent-artificial-intelligence-ai-stock-instead-usfeed/",
    "description": "Berkshire Hathaway has been selling Apple stock throughout the artificial intelligence (AI) revolution.",
    "source": "fool.com.au",
    "tags": [
      "Financial Services",
      "Stock",
      "Technology",
      "Unknown Sector"
    ],
    "crawlDate": "2026-01-03T22:34:24.827765Z",
    "tickers": [
      "aapl",
      "brk-a",
      "brk-b",
      "goog",
      "googl",
      "msft",
      "nvda",
      "pltr"
    ]
  }
]
```



위 형식의 데이터에서 각각의 기사 데이터에 대해 다음과 같은 형식의 결과물을 도출해내려고 합니다.

```
기사 1. {{title}} 을 한글로 번역한 한글 제목
- 원문 제목 : {{title}} 
- URL : {{url}}
- 출처 : {{source}}
- 발행일 : {{publishedDate}}

[요약]
{{url}} 의 내용을 직접 조회 후 해당 기사의 내용을 한글로 번역하고 전문적인 추세추종, 퀀트투자자 입장에서 한글로 요약, 5 ~ 10 줄 내외로 요약
---
기사 2. {{title}} 을 한글로 번역한 한글 제목
- 원문 제목 : {{title}} 
- URL : {{url}}
- 출처 : {{source}}
- 발행일 : {{publishedDate}}

[요약]
{{url}} 의 내용을 직접 조회 후 해당 기사의 내용을 한글로 번역하고 전문적인 추세추종, 퀀트투자자 입장에서 한글로 요약, 5 ~ 10 줄 내외로 요약
---
기사 3
...
```


이 작업에 대한 프롬프트를 작성하세요.
