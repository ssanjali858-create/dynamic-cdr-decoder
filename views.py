import json
import os
import sys
from django.http import JsonResponse # pyright: ignore[reportMissingModuleSource]
from django.views.decorators.csrf import csrf_exempt # pyright: ignore[reportMissingModuleSource]
from .models import IMSVoiceRecord, CDRRule
from .rule_engine import apply_rules

# Allow importing cdr_decoder.py from the decoder/ folder
DECODER_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'decoder')
sys.path.append(DECODER_DIR)


@csrf_exempt
def upload_and_decode(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Use POST with a file'}, status=400)

    # 1. Receive uploaded .dat file
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    # 2. Save it temporarily inside decoder/ folder
    temp_path = os.path.join(DECODER_DIR, uploaded_file.name)
    with open(temp_path, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    # 3. Decode the file using your existing decoder functions
    from cdr_decoder import read_length, decode_record  # type: ignore # reuse your functions

    with open(temp_path, 'rb') as f:
        data = f.read()

    records = []
    i = 0
    while i < len(data):
        if data[i] == 0x31:
            length, next_pos = read_length(data, i + 1)
            record = decode_record(data, next_pos, length)
            records.append(record)
            i = next_pos + length
        else:
            i += 1

    # 4. Save each decoded record into MySQL, and apply dynamic rules
    saved_count = 0
    all_flags = []

    for rec in records:
        # Only keep keys that exist as model fields (avoids crash on unknown_tag_X)
        valid_fields = {f.name for f in IMSVoiceRecord._meta.get_fields()}
        clean_rec = {k: v for k, v in rec.items() if k in valid_fields}

        obj = IMSVoiceRecord.objects.create(**clean_rec)
        saved_count += 1

        # Apply dynamic rules to this record (rules come from DB, not code)
        triggered = apply_rules(rec)
        if triggered:
            all_flags.append({'record_id': obj.id, 'flags': triggered})

    return JsonResponse({
        'status': 'success',
        'records_saved': saved_count,
        'flags': all_flags
    })

from django.shortcuts import render # pyright: ignore[reportMissingModuleSource]

from rest_framework.decorators import api_view # pyright: ignore[reportMissingImports]
from rest_framework.response import Response # pyright: ignore[reportMissingImports]
from .serializers import IMSVoiceRecordSerializer, CDRRuleSerializer

@api_view(['GET'])
def list_records(request):
    records = IMSVoiceRecord.objects.all().order_by('-id')[:50]  # latest 50
    serializer = IMSVoiceRecordSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def manage_rules(request):
    if request.method == 'GET':
        rules = CDRRule.objects.all()
        serializer = CDRRuleSerializer(rules, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        # Frontend sends a new rule — saved directly to DB, no code change needed
        serializer = CDRRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
@api_view(['DELETE'])
def delete_rule(request, rule_id):
    try:
        rule = CDRRule.objects.get(id=rule_id)
        rule.delete()
        return Response({'status': 'deleted'})
    except CDRRule.DoesNotExist:
        return Response({'error': 'Rule not found'}, status=404)