# Generated by Django 2.2.10 on 2020-02-19 14:43


import json

from django.db import migrations, transaction
import django.contrib.postgres.fields.jsonb

import gi
gi.require_version('Modulemd', '2.0')
from gi.repository import Modulemd as mmdlib  # noqa: E402


def get_modulemd_dependencies(modulemd_index):
    # re:https://pulp.plan.io/issues/6214
    modulemd_name = modulemd_index.get_module_names()[0]
    modulemd_stream = modulemd_index.get_module(modulemd_name).get_all_streams()[0]
    dependencies_list = modulemd_stream.get_dependencies()
    dependencies = list()
    for dep in dependencies_list:
        depmodule_list = dep.get_runtime_modules()
        platform_deps = dict()
        for depmod in depmodule_list:
            platform_deps[depmod] = dep.get_runtime_streams(depmod)
        dependencies.append(platform_deps)
    return dependencies


def unflatten_json(apps, schema_editor):
    # re: https://pulp.plan.io/issues/6191
    with transaction.atomic():
        Modulemd = apps.get_model('rpm', 'Modulemd')
        for module in Modulemd.objects.all().only('artifacts', 'dependencies', '_artifacts'):
            modulemd_index = mmdlib.ModuleIndex.new()
            modulemd_index.update_from_string(module._artifacts.first().file.read().decode(), True)
            dependencies = get_modulemd_dependencies(modulemd_index)
            module.artifacts = json.loads(module.artifacts)
            module.dependencies = dependencies
            module.save()

        ModulemdDefaults = apps.get_model('rpm', 'ModulemdDefaults')
        for mod_defs in ModulemdDefaults.objects.all().only('profiles'):
            mod_defs.profiles = json.loads(mod_defs.profiles)
            mod_defs.save()


def replace_emptystring_with_null(apps, schema_editor):
    # An empty string can't be converted to JSON, so use a null instead
    with transaction.atomic():
        UpdateCollection = apps.get_model('rpm', 'UpdateCollection')
        for coll in UpdateCollection.objects.all().only('module'):
            if coll.module == '':
                coll.module = 'null'  # de-serializes to None,
                coll.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rpm', '0002_updaterecord_reboot_suggested'),
    ]

    operations = [
        # Bugfixes
        migrations.RunPython(unflatten_json),
        # In-place migrate JSON stored in text field to a JSONField
        migrations.RunPython(replace_emptystring_with_null),
        migrations.AlterField(
            model_name='updatecollection',
            name='module',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]