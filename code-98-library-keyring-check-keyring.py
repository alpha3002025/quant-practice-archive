import keyring

service_name = "tiingo"
username = "noriskfullpush"

# 키링에서 토큰 조회
api_token = keyring.get_password(service_name, username)

print(api_token)