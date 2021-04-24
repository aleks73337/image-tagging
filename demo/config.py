servers  = [
    "rocket-01.srvs.cloudkafka.com:9094",
    "rocket-02.srvs.cloudkafka.com:9094",
    "rocket-03.srvs.cloudkafka.com:9094",
]
username    = "mtvvpozh"
password    = "xWPcH1LuVZGZHNlxP-vU81qUe2NPbrPD"
topic       = "mtvvpozh-wtf"
api_version = (0, 10, 0, 0)

security_protocol = "SASL_SSL"
sasl_mechanism    = "SCRAM-SHA-256"

value_serializer   = str.encode
value_deserializer = bytes.decode

bot_token = '1363973027:AAHwN8Eqgq8ie_NLNlwA8JH2abn8s957jS4'
openroute_api_key = '5b3ce3597851110001cf624801a052953f394cedaded52428123f8ee'
