import keyring
import pandas as pd
import requests
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


api_key_finnhub = keyring.get_password("finnhub", "noriskfullpush")
api_key_gemini = keyring.get_password("gemini_quant_automation", "noriskfullpush")




# # google_api_key = os.environ.get("GOOGLE_API_KEY")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-3-pro",
#     google_api_key=api_key_gemini,
#     temperature=0.1,
#     convert_system_message_to_human=True
# )

# translate_prompt = ChatPromptTemplate.from_messages([
#     ("system", "당신은 전문 금융 분석가이자 번역가입니다. 제공된 금융 뉴스를 분석하여 다음 형식에 맞춰 한국어로 작성하세요:\n\n1. **제목**: 한국어로 번역된 제목\n2. **핵심 요약**: 뉴스 내용을 바탕으로 투자자에게 중요한 핵심 내용을 3줄 이내로 요약\n3. **원문 정보**: 원문 제목과 링크(제공된 경우)를 표기"),
#     ("user", "뉴스 데이터:\n제목: {title}\n내용: {description}\n링크: {url}")
# ])

# translate_chain = translate_prompt | llm | StrOutputParser()

# for article in news_data[:3]:
#     try:
#         # Finnhub 데이터 필드 매핑: headline -> title, summary -> description
#         result = translate_chain.invoke({
#             "title": article.get('headline', ''),
#             "description": article.get('summary', ''),
#             "url": article.get('url', '')
#         })
#         print("\n" + result)
#         print("-" * 50)
#     except Exception as e:
#         print(f"Error processing article: {e}")



