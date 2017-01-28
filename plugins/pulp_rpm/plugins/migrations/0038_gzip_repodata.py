import gzip

import bson

from pulp.server.db import connection


def migrate(*args, **kwargs):
    """
    Compress the content of repodata field for RPM and SRPM units.

    :param args:   unused
    :type  args:   list
    :param kwargs: unused
    :type  kwargs: dict
    """
    db = connection.get_database()
    rpm_collection = db['units_rpm']
    srpm_collection = db['units_srpm']

    for rpm in rpm_collection.find({}, ['repodata']).batch_size(100):
        migrate_rpm_base(rpm_collection, rpm)
    for srpm in srpm_collection.find({}, ['repodata']).batch_size(100):
        migrate_rpm_base(srpm_collection, srpm)


def migrate_rpm_base(collection, unit):
    """
    Compress 'primary', 'other' and 'filelists' metadata for a given unit.

    :param collection:  collection of RPM units
    :type  collection:  pymongo.collection.Collection
    :param unit:        the RPM unit being migrated
    :type  unit:        dict
    """

    delta = {'repodata': {}}
    for metadata_type in ['primary', 'other', 'filelists']:
        metadata = unit['repodata'].get(metadata_type)
        if metadata and not isinstance(metadata, bson.binary.Binary):
            compressed_data = gzip.zlib.compress(metadata.encode('utf-8'))
            delta['repodata'][metadata_type] = bson.binary.Binary(compressed_data)
    if delta['repodata']:
        collection.update_one({'_id': unit['_id']}, {'$set': delta})
