from typing import List, Set, Tuple, Type, Iterator  # noqa

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from document.json_importer.importer import import_json_doc
from document.models import DocNode
from document.serializers import util
from document.serializers.content import (NestedAnnotationSerializer,
                                          nest_annotations)
from document.serializers.meta import Meta, MetaSerializer
from document.tree import DocCursor, JSONAwareCursor, PrimitiveDict


class DocCursorField(serializers.Field):
    def get_attribute(self, instance: DocCursor) -> DocCursor:
        return instance


class ChildrenField(DocCursorField):
    def to_representation(self, instance: DocCursor) -> List[PrimitiveDict]:
        return DocCursorSerializer(
            instance.children(), many=True,
            context={**self.context, 'is_root': False},
        ).data

    def validate_type_emblem_uniqueness(self, data: List[PrimitiveDict]) \
            -> List[PrimitiveDict]:
        node_embs = [
            (child['node_type'], child['type_emblem'])
            for child in data
            if 'type_emblem' in child
        ]
        for node, emb in util.iter_non_unique(node_embs):
            raise ValidationError(
                f"Multiple occurrences of '{node}' with emblem "
                f"'{emb}' exist as siblings"
            )
        return data

    def to_internal_value(self,
                          data: List[PrimitiveDict]) -> List[PrimitiveDict]:
        serializer = DocCursorSerializer(data=data, many=True, context={
            **self.context, 'is_root': False})
        serializer.is_valid(raise_exception=True)
        return self.validate_type_emblem_uniqueness(serializer.validated_data)


class ContentField(DocCursorField):
    def to_representation(self, instance: DocCursor) -> List[PrimitiveDict]:
        annotations = nest_annotations(
            instance.annotations(), len(instance.text))
        return NestedAnnotationSerializer(
            annotations,
            context={'cursor': instance,
                     'parent_serializer': self.context['parent_serializer']},
            many=True,
        ).data

    def to_internal_value(self,
                          data: List[PrimitiveDict]) -> List[PrimitiveDict]:
        serializer = NestedAnnotationSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class DocCursorSerializer(serializers.Serializer):
    """
    A Serializer for the DocCursor class.

    Note that we're doing this manually instead of using
    DRF's serializers.ModelSerializer because:

        * DocCursor isn't actually a Django model.  It's *like*
          a model in a lot of ways, but it's not actually a
          model, so we don't want to cause complications with
          DRF down the road.

        * There are enough deviations between the Django model's
          validation and the REST API's validation that we'd
          still have to write a bunch of code to "undo"
          ModelSerializer's defaults.
    """

    # Read/write fields.
    children = ChildrenField()
    content = ContentField()
    marker = serializers.CharField(
        max_length=DocNode._meta.get_field('marker').max_length,
        allow_blank=True,
        required=False,
    )
    node_type = serializers.CharField(
        max_length=DocNode._meta.get_field('node_type').max_length,
    )
    title = serializers.CharField(
        max_length=DocNode._meta.get_field('title').max_length,
        allow_blank=True,
        required=False,
    )

    # Type emblems are required by our DocNode model, but they aren't
    # required by our API; if not supplied, they will be auto-generated.
    type_emblem = serializers.CharField(
        max_length=DocNode._meta.get_field('type_emblem').max_length,
        validators=DocNode._meta.get_field('type_emblem').validators,
        required=False,
    )

    # Read-only fields.
    meta = serializers.SerializerMethodField()
    depth = serializers.IntegerField(read_only=True)
    identifier = serializers.CharField(read_only=True)
    text = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context['parent_serializer'] = self

    @property
    def is_root(self) -> bool:
        return self.context.get('is_root', True)

    def get_meta(self, instance):
        """Include meta data which applies to the whole node."""
        meta = Meta(
            instance,
            self.is_root,
            self.context.get('policy'),
        )
        return MetaSerializer(meta, context={'parent_serializer': self}).data

    def validate_footnote_citations(self, data: PrimitiveDict,
                                    footnote_emblems: Set[str]):
        citations = [
            util.get_content_text(f['inlines']).strip()
            for f in util.iter_inlines(data['content'])
            if f['content_type'] == 'footnote_citation'
        ]

        for citation in citations:
            if citation not in footnote_emblems:
                raise ValidationError(
                    f"Citation for '{citation}' has no matching footnote"
                )

    def validate_footnote_emblems(self, data: PrimitiveDict) -> Set[str]:
        footnote_emblems = [
            f['type_emblem'] for f in util.iter_children(data['children'])
            if f['node_type'] == 'footnote'
        ]

        for emblem in util.iter_non_unique(footnote_emblems):
            raise ValidationError(
                f"Multiple footnotes exist with type emblem '{emblem}'"
            )

        return set(footnote_emblems)

    def validate(self, data: PrimitiveDict) -> PrimitiveDict:
        if data['node_type'] == 'footnote' and not data.get('type_emblem'):
            msg = f"'{data['node_type']}' nodes must have type emblems."
            raise ValidationError({'type_emblem': msg})
        if self.is_root:
            footnote_emblems = self.validate_footnote_emblems(data)
            self.validate_footnote_citations(data, footnote_emblems)
        return data

    def run_validation(self, data=serializers.empty):
        with util.add_sourceline_to_errors(data):
            return super().run_validation(data)

    def create(self, validated_data: PrimitiveDict) -> JSONAwareCursor:
        return import_json_doc(self.context['policy'], validated_data)

    def update(self, instance: DocCursor,
               validated_data: PrimitiveDict) -> JSONAwareCursor:
        return import_json_doc(instance.policy, validated_data)
