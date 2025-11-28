from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "reminder_morning_time" TIME DEFAULT '09:00:00';
        ALTER TABLE "users" ADD "reminder_evening_time" TIME DEFAULT '20:00:00';
        ALTER TABLE "users" ADD "reminders_enabled" INT NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "reminder_morning_time";
        ALTER TABLE "users" DROP COLUMN "reminder_evening_time";
        ALTER TABLE "users" DROP COLUMN "reminders_enabled";"""


MODELS_STATE = (
    "eJztmP9v2joQwP8VlJ/6pL6KBlrYND0JKN14KzC18N60aYpMYkLUxGaOsxZV/d/nM3FCnC"
    "+Drl2pNqmiyd058X3Ovjvnzgiog/3waEipc0Fd43XtziAowOJCVx3WDLRcpgoQcDTzY1vq"
    "WD51pRTNQs6QzYVijvwQC5GDQ5t5S+5RIqQk8n0QUlsYesRNRRHxvkbY4tTFfIGZUHz+Is"
    "QecfAtDtXt8tqae9h3MtP1HHi3lFt8tZSy6XRwdi4t4XUzy6Z+FJDUerniC0oS8yjynCMY"
    "AzoXE8wQx86GGzDL2GUlWs9YCDiLcDJVJxU4eI4iH2AYb+YRsYFBTb4Jfpr/GDvgsSkBtB"
    "7hwOLufu1V6rOUGvCq3rvO5UHj9C/pJQ25y6RSEjHu5UDE0Xqo5JqC/IZ84VCO5YDwYpSJ"
    "vUZTzPIhHJUgBZkuIkVSEXoYNjEl8e9v87jZarYbp822MJFzSSStCrKD0UQCTIERygt4Tf"
    "BtCTBlr/ESU9yCV7yqfiGuChaT/scJzDkIw68+CEb/dS7l0ht2Psq1F6xizcV49FaZU5Ed"
    "1nlj1LsYdzWcNsPgvoV4HuqZ0HAvwMVgsyM1vE489Ehd7OniFD44Y+Kv4lhX0R8M+1eTzv"
    "BDJgRnnUkfNGYGv5IerFNCGoHkIbX/B5N3NbitfRqP+nriSOwmnwyYE4o4tQi9sZCzkeyU"
    "VIHJBDYKMbN2S9MbQx4zVz/rpvlBaoYCN78uzMxAI0/vnDLsueQ9XkmGAzEPROyiDBNX9G"
    "n8mL2llkrTlcXQTVL0N5eFcE84hbl0sNe56nXO+oaEOEP29Q1ijpWhCRpqUk2S2OZVgRno"
    "EkSQK/0HL2DOm2ALWigFvLx/Aof+9E4vv3fiYim6DAWFaa7ruaVNlDbwcVqpH2N9lEbqlW"
    "k2Gi2z3jhtnzRbrZN2Pemo8qqq1qo7eAvdVaY+5dst2CvyOge4t0CsvI6oMS+k7RJp5tby"
    "MXH5QtyaJycV4FTXJay08q4aMnOt+9Np/RadFsMBcGOhhQkALkpGlPoYkeLwFo7XojwTD3"
    "iqwO5a+rbP7d3x+CITxO5AP5JMh93+5cGxjJ4w8nhJHlKQrIAyIqZjqaWunQNLN1HpA8r2"
    "05Z76SG5yqi/el2vi7+nKamwpjO7pHCHpMmqnSu+MAA2RHEI8Df8cyHQH/AcITDrLyQEuS"
    "NKebu92QtvfCLUclE89Pz9JfaR9DkfgvznyP0rKWXnl/unPHV0MPPshVFw7og1h1UnD5Ta"
    "7M3Ro7RL3rY5jrffHvTGP/mRseIrrajO8UbZtgneGPKgHvg5erSnb4Jha+wAMTZ/mQCP6/"
    "UtAAqrUoBSp50iKOGYFBwh/r0aj0qOD+kQDeSUCAc/O57ND2u+F/Iv+4m1giJ4Xf1NXP/8"
    "rZVZeEB3tyr7+OXl/jupzgG8"
)
