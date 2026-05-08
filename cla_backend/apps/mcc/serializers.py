from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from cla_provider.serializers import (
    CaseSerializer,
    NestedScopeTraversalSerializer,
    NestedDiagnosisSerializer,
    LogSerializer,
    CaseNotesHistorySerializer
)
from legalaid.serializers import (
    AdaptationDetailsSerializerBase,
    PersonalDetailsSerializerFull,
    ThirdPartyDetailsSerializerBase,
)


class DetailedCaseSerializer(CaseSerializer):
    """
    Extended case serializer that includes all nested details
    for the detailed endpoint
    """
    personal_details = PersonalDetailsSerializerFull(read_only=True)
    adaptation_details = AdaptationDetailsSerializerBase(read_only=True)
    thirdparty_details = ThirdPartyDetailsSerializerBase(read_only=True)
    scope_traversal = NestedScopeTraversalSerializer(read_only=True)
    diagnosis = NestedDiagnosisSerializer(read_only=True)
    notes_history = SerializerMethodField()
    state = serializers.CharField(read_only=True)
    state_note = LogSerializer(read_only=True)

    def get_notes_history(self, obj):
        """Fetch all notes history for the case"""
        from legalaid.models import CaseNotesHistory

        notes = CaseNotesHistory.objects.filter(case=obj).order_by('-created')
        return CaseNotesHistorySerializer(notes, many=True).data

    class Meta(CaseSerializer.Meta):
        fields = tuple(field for field in CaseSerializer.Meta.fields if field != "eligibility_check") + ("state", "state_note", "notes_history")
