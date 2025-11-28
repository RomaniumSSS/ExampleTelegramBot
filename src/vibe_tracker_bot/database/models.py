from tortoise import fields, models
import datetime


class User(models.Model):
    id = fields.UUIDField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    # Reminders
    reminders_enabled = fields.BooleanField(default=False)
    reminder_morning_time = fields.TimeField(null=True, default=datetime.time(9, 0))
    reminder_evening_time = fields.TimeField(null=True, default=datetime.time(20, 0))
    timezone = fields.CharField(max_length=50, default="UTC")

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
