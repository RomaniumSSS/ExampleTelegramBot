from tortoise import fields, models


class User(models.Model):
    id = fields.UUIDField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    mood_logs: fields.ReverseRelation["MoodLog"]

    class Meta:
        table = "users"


class MoodLog(models.Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField(
        "models.User", related_name="mood_logs", on_delete=fields.CASCADE
    )
    value = fields.IntField()
    note = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "mood_logs"
