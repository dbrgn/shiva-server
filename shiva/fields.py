# -*- coding: utf-8 -*-
from flask.ext.restful import fields, marshal

from shiva.converter import get_converter
from shiva.media import get_mimetypes


class InstanceURI(fields.String):
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def output(self, key, obj):
        return '/%s/%i' % (self.base_uri, obj.pk)


class TrackFiles(fields.Raw):
    """
    Returns a list of files, one for each available mediatype, for a given
    track.

    """

    def output(self, key, track):
        ConverterClass = get_converter()
        paths = {}

        for mimetype in get_mimetypes():
            converter = ConverterClass(track, mimetype)
            paths[str(mimetype)] = converter.get_uri()

        return paths


class DownloadURI(InstanceURI):
    def output(self, key, obj):
        uri = super(DownloadURI, self).output(key, obj)

        return '%s/download.mp3' % uri


class ManyToManyField(fields.Raw):
    def __init__(self, foreign_obj, nested):
        self.foreign_obj = foreign_obj
        self.nested = nested

        super(ManyToManyField, self).__init__()

    def output(self, key, obj):
        items = list()
        for item in getattr(obj, key):
            items.append(marshal(item, self.nested))

        return items


class ForeignKeyField(fields.Raw):
    def __init__(self, foreign_obj, nested):
        self.foreign_obj = foreign_obj
        self.nested = nested

        super(ForeignKeyField, self).__init__()

    def output(self, key, obj):
        _id = getattr(obj, '%s_pk' % key)
        if not _id:
            return None

        obj = self.foreign_obj.query.get(_id)

        return marshal(obj, self.nested)


class Boolean(fields.Raw):
    def output(self, key, obj):
        return bool(super(Boolean, self).output(key, obj))
