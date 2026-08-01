# ZarinPal has been fully removed from the project - Zibal is now the only
# supported payment gateway in both development and production. This only
# updates the `choices` metadata on payment_gateway (CharField is not
# DB-constrained by choices), so any historical orders that already have
# payment_gateway="zarinpal" keep that value untouched as an accurate
# historical record; only new orders can no longer be created with it.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_zibal_payment_gateway"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_gateway",
            field=models.CharField(
                blank=True,
                choices=[("zibal", "زیبال")],
                max_length=20,
                null=True,
                verbose_name="درگاه پرداخت",
            ),
        ),
    ]
