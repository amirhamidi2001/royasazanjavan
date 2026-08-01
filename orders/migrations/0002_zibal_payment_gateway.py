# Replace the ZarinPal-specific payment fields with generic, gateway-agnostic
# ones so the project can support Zibal (production) and, optionally,
# ZarinPal (development/sandbox) through the same Order model.
#
# RenameField is used (rather than remove+add) so that any existing
# zarinpal_authority / zarinpal_ref_id data already stored in the database
# is preserved under the new field names instead of being dropped.
from django.db import migrations, models


def backfill_payment_gateway(apps, schema_editor):
    """Any order that already has a payment_track_id at this point was
    necessarily created through the old ZarinPal-only flow, so tag it
    accordingly for historical/reporting purposes."""
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(
        payment_track_id__isnull=False, payment_gateway__isnull=True
    ).exclude(payment_track_id="").update(payment_gateway="zarinpal")


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="zarinpal_authority",
            new_name="payment_track_id",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="zarinpal_ref_id",
            new_name="payment_reference",
        ),
        migrations.RemoveIndex(
            model_name="order",
            name="orders_orde_zarinpa_e2e923_idx",
        ),
        migrations.AlterField(
            model_name="order",
            name="payment_track_id",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=255,
                verbose_name="شناسه پیگیری تراکنش",
                help_text="Track ID (زیبال) یا Authority (زرین‌پال) بازگشتی از درگاه",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="payment_reference",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=255,
                verbose_name="شماره مرجع پرداخت",
                help_text="شماره مرجع نهایی تراکنش پس از تایید موفق پرداخت",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_gateway",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=20,
                choices=[("zibal", "زیبال"), ("zarinpal", "زرین‌پال (تست)")],
                verbose_name="درگاه پرداخت",
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["payment_track_id"], name="orders_orde_payment_590d0c_idx"
            ),
        ),
        migrations.RunPython(
            code=backfill_payment_gateway,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
