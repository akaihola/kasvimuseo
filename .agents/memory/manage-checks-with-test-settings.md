# Run management checks with test settings

This note helps contributors run management checks without development data.

```bash
dev/kasvimuseo app manage check --settings=ylaneenkasvit.test_settings
dev/kasvimuseo app manage makemigrations kasvimuseo --check --dry-run --settings=ylaneenkasvit.test_settings
```

[ylaneenkasvit/test_settings.py](../../ylaneenkasvit/test_settings.py) selects temporary media unless `KASVIMUSEO_MEDIA_ROOT` overrides it.
Check that variable before running these commands.
Keep development media links unchanged.
