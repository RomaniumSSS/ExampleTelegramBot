from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "timezone" VARCHAR(50) NOT NULL DEFAULT 'UTC';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "timezone";"""


MODELS_STATE = (
    "eJztmXtv2kgQwL8K8l85KRc5BgKtTpWAkJZrgFNielWrylrsxVixd6m9bkKjfPfbWfxcPw"
    "okaYmuUkTMzKy989vdeZh7xaMWdoOTMaXWJbWV1417hSAP8wtZddxQ0GqVKkDA0NyNbKll"
    "uNQWUjQPmI9MxhUL5AaYiywcmL6zYg4lXEpC1wUhNbmhQ+xUFBLna4gNRm3Mltjnis9fuN"
    "ghFr7DQfx1dWMsHOxauek6FjxbyA22XgnZbDY6vxCW8Li5YVI39EhqvVqzJSWJeRg61gmM"
    "AZ2NCfYRw1bGDZhl5HIs2syYC5gf4mSqViqw8AKFLsBQ/lqExAQGDfEk+Gi9UXbAY1ICaB"
    "3CgMX9w8ar1GchVeBRg3e9q6Pm2R/CSxow2xdKQUR5EAMRQ5uhgmsK8htyuUMFliPCylEm"
    "9hJNPst9OMaCFGS6iWKSMaH9sPEp8X9/aqetTqvbPGt1uYmYSyLp1JAdTXQBMAVGKCvhpe"
    "O7CmCxvcSLT3ELXtGu+om4aljow486zNkLgq8uCCYfeldi6417H8Xe89aR5nI6eRubUx4d"
    "NnFjMric9iWcpo/BfQOxItRzrmGOh8vB5kdKeK1o6El8caCbk/tgTYm7jta6jv5oPLzWe+"
    "N/cktw3tOHoNFy+GPp0SYkpCuQ3KTx70h/14CvjU/TyVAOHImd/kmBOaGQUYPQWwNZmWAX"
    "S2MwuYUNA+wbu4XpzJCnjNW/9ND8IDRDglvclEZmoFGkd0F97NjkPV4LhiM+D0TMsggTZf"
    "RZdJuDpZZK053lo9sk6We3BXePO4WZcHDQux70zoeKgDhH5s0t8i0jRxM0VKOSJLEtqjzN"
    "kyWIIFv4D17AnLNgS0qoGHh1/QQO/a6dXn7txPhWtH3klYa5vmNXFlHSwKcppX6M9UkKqV"
    "ea1mx2NLV51m23Op12V00qqqKqrrTqj95CdZXLT8VyC86KuC4AHiyRX51H4jEvpOziYebO"
    "cDGx2ZJ/1drtGnBx1cWtpPQeF2TaRve70vpfVFo+9oCbHxiYAOCyYESpixEpX97S8dIqz/"
    "kNnmthd01928f2/nR6mVvE/khuSWbj/vDq6FSsHjdyWEUciiEZHvUJn44Rb3WpD6w8RJU3"
    "qDpPW56lfWKVor56rar873lSKuzp3CkpPSFpsOoWki8MgANRvgT4G37cEsg3+BVLoKkvcA"
    "kAyHdKdsrG2TF7ZeO9gooy0wePQJvPx211i3TcVivpgqqk16vuW7JNReZdqxTUo6EX76+w"
    "i4SHRcTF97qHl5urGsGH52zfeth3zKVS0sBFmuO6Fg6lNgfTw1W2G9t2GVEcO4Am45Fva2"
    "ted/MyJzoo28avzJCfF74OvpuAo7EDxMj8ZQI8VbeJ/9yqEqDQSe0YJQyTkl7s7+vppKIP"
    "S4dIIGeEO/jZckx23HCdgH05TKw1FMHr+h8X5N8RpHoFbtDfLcs+fXp5+A/ZGWog"
)
