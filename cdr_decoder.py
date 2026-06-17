"""
=============================================================
  CDR DECODER - STEP 1
  Company  : Echelon Edge
  Project  : Call Detail Record (CDR) Decoder
  File     : cdr_decoder.py

  What this file does:
    1. Reads a binary .dat file (BER-encoded ASN.1 format)
    2. Decodes each CDR record using the IMS ASN.1 schema
    3. Saves the decoded output as a readable JSON file

  How to run:
    python cdr_decoder.py
=============================================================
"""

import json   # To save output as JSON 
import os     # To check if file exists


# =============================================================
# SECTION 1: TAG MAP
# This is like a dictionary/phone-book.
# Each CDR field in the .dat file is stored as a NUMBER (tag).
# We map that number to a human-readable field name from ims.asn1
# Example: tag 7 → "callerno" (the caller's phone number)
# =============================================================

TAG_MAP = {
    0:  'cdfId',                    # ID of the Charging Data Function server
    1:  'cdrseqnum',               # CDR sequence number (1, 2, 3 ...)
    2:  'lclrcdseqnum',            # Local record sequence number
    3:  'rcdseqnum',               # Record sequence number
    4:  'calltype',                # Type of call (voice, video etc.)
    5:  'imschargingid',           # Unique IMS charging ID for this call
    6:  'lrn',                     # Location Routing Number
    7:  'callerno',                # Caller's phone number (who called)
    8:  'calledno',                # Called phone number (who was called)
    9:  'fullcalledno',            # Full called number with routing
    10: 'callarrivaltimestamp',    # When the call arrived at the network
    11: 'callanswertimestamp',     # When the call was answered
    12: 'callendtimestamp',        # When the call ended
    13: 'duration',                # Call duration in seconds
    14: 'servicereasonreturncode', # Why the call ended (16 = normal)
    15: 'serviceinvoke',           # Whether a service was invoked
    16: 'associatedpartyaddress',  # Third party address (e.g. in conference)
    17: 'srvcctype',               # SRVCC handover type
    18: 'initialicid',             # Initial IMS Charging ID
    19: 'accesstransfertype',      # Access transfer type
    20: 'origaccessnetworkinfo',   # Originating access network info
    21: 'termaccessnetworkinfo',   # Terminating access network info
    22: 'origincsessionid',        # Originating IMS session ID
    23: 'termincsessionid',        # Terminating IMS session ID
    24: 'origogsessionid',         # Originating OG session ID
    25: 'termogsessionid',         # Terminating OG session ID
    26: 'origioi',                 # Originating network operator ID (e.g. ims.bsnl)
    27: 'termioi',                 # Terminating network operator ID
    28: 'codecs',                  # Audio/video codecs used (e.g. "97,100")
    29: 'mediainitiatorflag',      # Who initiated the media (0=caller)
    30: 'mediainitiatorparty',     # Phone number of media initiator
    31: 'scscfinformation',        # S-CSCF server IP address
    32: 'asinformation',           # Application Server IP address
    33: 'imsemergencyindicator',   # 1 if this was an emergency call
    34: 'privateuserid',           # SIP private user identity (IMPI)
    35: 'origdeviceip',            # Originating device IP address
    36: 'termdeviceip',            # Terminating device IP address
    37: 'numofdiversions',         # Number of call diversions/forwards
    38: 'origcugid',               # Originating Closed User Group ID
    39: 'termcugid',               # Terminating Closed User Group ID
    40: 'resourcepri',             # Resource priority
    41: 'conferenceid',            # Conference call ID
    42: 'confchangetime',          # Time of conference change
    43: 'confnumparticipants',     # Number of conference participants
    44: 'confparticipationacttype',# Conference participation action type
    45: 'servedIMEI',              # IMEI of the caller's device (device ID)
    46: 'mmtelservicetype',        # MMTel service type
    47: 'imsvisitednetworkid',     # Visited network ID (roaming)
    48: 'firstcellIdorig',         # First cell tower ID (caller side)
    49: 'lastcellIdorig',          # Last cell tower ID (caller side)
    50: 'firstcellIdterm',         # First cell tower ID (receiver side)
    51: 'lastcellIdterm',          # Last cell tower ID (receiver side)
    52: 'cdrtype',                 # CDR type (2=originating, 4=terminating)
    53: 'subsPLMN',                # Subscriber's PLMN (network operator code)
    54: 'subsIMSI',                # Subscriber's IMSI (SIM card identity)
    55: 'substype',                # Subscriber type
    56: 'recordOpeningTime',       # When the CDR record was opened
    57: 'recordClosingTime',       # When the CDR record was closed
    58: 'termservedIMEI',          # IMEI of the called party's device
    59: 'termsubsPLMN',            # Called party's network operator code
    60: 'termsubsIMSI',            # Called party's IMSI
    61: 'callinggt',               # Calling Global Title
    62: 'callrefernum',            # Call reference number
    63: 'ringingtimestamp',        # When the phone started ringing
    64: 'dummy7',                  # Reserved field
    65: 'termsubstype',            # Called party's subscriber type
    66: 'servicekey',              # Service key (800 = VoLTE)
    67: 'rattype',                 # Radio Access Technology type
    68: 'audioduration',           # Audio portion duration in seconds
    69: 'videoduration',           # Video portion duration in seconds
    70: 'dummy13',                 # Reserved field
    71: 'dummy14',                 # Reserved field
    72: 'dummy15',                 # Reserved field
    73: 'dummy16',                 # Reserved field
    74: 'termnetworkid',           # Terminating network ID
    75: 'termscscfinformation',    # Terminating S-CSCF IP
    76: 'termasinformation',       # Terminating AS IP
    77: 'termcodec',               # Terminating codec
    78: 'confcalledstr',           # Conference called string
}


# =============================================================
# SECTION 2: HELPER FUNCTION - Read BER Length Bytes
#
# In BER (Basic Encoding Rules) format, lengths are encoded as:
#   - If < 128: just 1 byte
#   - If >= 128: first byte tells you HOW MANY bytes the length uses
#
# Example:
#   0x03        → length is 3
#   0x82 0x01 0xe0 → length is 0x01e0 = 480 (multi-byte)
#
# Returns: (length_value, new_position_in_data)
# =============================================================

def read_length(data, pos):
    b = data[pos]

    if b & 0x80:
        # Long form: first byte = 0x80 + number_of_length_bytes
        num_len_bytes = b & 0x7f
        length = int.from_bytes(data[pos + 1 : pos + 1 + num_len_bytes], 'big')
        return length, pos + 1 + num_len_bytes
    else:
        # Short form: the byte itself IS the length
        return b, pos + 1


# =============================================================
# SECTION 3: HELPER FUNCTION - Decode Timestamp
#
# Timestamps in this file are stored as BCD (Binary Coded Decimal)
# bytes. Each nibble (4 bits) = one digit.
#
# Example bytes: 20 03 20 26 11 54 41
#   → Year=2020, Month=03, Day=20, Hour=26(?), Min=11, Sec=54
#
# Note: Hour=26 appears in some records which is a timezone offset
# artifact in BCD encoding — this is normal for telecom CDRs.
# =============================================================

def decode_timestamp(raw_bytes):
    try:
        h = raw_bytes.hex()           # Convert bytes to hex string like "200320261154"
        year   = '20' + h[0:2]       # First 2 hex chars = last 2 digits of year
        month  = h[2:4]
        day    = h[4:6]
        hour   = h[6:8]
        minute = h[8:10]
        second = h[10:12]
        return f"{year}-{month}-{day} {hour}:{minute}:{second}"
    except Exception:
        return raw_bytes.hex()        # If decode fails, return raw hex


# =============================================================
# SECTION 4: HELPER FUNCTION - Decode a Single Field Value
#
# Every field in BER has an inner type tag:
#   0x02 = INTEGER  → decode as a number
#   0x04 = OCTET STRING → could be timestamp, IP, hex data
#   0x0c = UTF8String   → decode as UTF-8 text
#   0x16 = IA5String    → decode as ASCII text
#
# tag_num   = the field number (0-78) from the outer context tag
# raw_bytes = the actual value bytes
# inner_tag = the type of the value (INTEGER, STRING, etc.)
# =============================================================

# These tag numbers are timestamps (need special BCD decoding)
TIMESTAMP_TAGS = {10, 11, 12, 42, 56, 57, 63}

def decode_field(tag_num, raw_bytes, inner_tag):

    if inner_tag == 0x02:
        # INTEGER: convert bytes to a signed integer
        return int.from_bytes(raw_bytes, byteorder='big', signed=True)

    elif inner_tag in (0x0c, 0x16):
        # UTF8String or IA5String: decode bytes as text
        return raw_bytes.decode('utf-8', errors='replace')

    elif inner_tag == 0x04:
        # OCTET STRING: depends on which field it is
        if tag_num in TIMESTAMP_TAGS:
            return decode_timestamp(raw_bytes)

        # Try decoding as printable ASCII text first
        try:
            text = raw_bytes.decode('ascii')
            if all(32 <= ord(c) < 127 for c in text):
                return text
        except Exception:
            pass

        return raw_bytes.hex()

    # Fallback: return hex
    return raw_bytes.hex()


# =============================================================
# SECTION 5: MAIN FUNCTION - Decode One CDR Record
#
# A single CDR record looks like this in BER bytes:
#
#   [outer context tag] [outer length] [inner type tag] [inner length] [value bytes]
#
# Example for callerno (tag 7, value = "+917838971488"):
#   a7       = context tag 7 (0xa0 | 7)
#   0f       = outer length = 15 bytes
#   0c       = UTF8String inner type
#   0d       = inner length = 13
#   2b 39 31 37 38 33 38 39 37 31 34 38 38 = "+917838971488"
#
# For tags > 30, the tag is encoded with an extra byte (0xbf prefix).
# =============================================================

def decode_record(data, start, length):
    record = {}         # This will hold all decoded fields for one CDR
    i = start           # Current byte position
    end = start + length

    while i < end:
       
        tag_byte = data[i]

        if (tag_byte & 0x1f) == 0x1f:
            # Long form tag (used for tag numbers > 30)
            # First byte: 0xbf (constructed, context class, long form)
            i += 1
            tag_num = 0
            while data[i] & 0x80:
                tag_num = (tag_num << 7) | (data[i] & 0x7f)
                i += 1
            tag_num = (tag_num << 7) | (data[i] & 0x7f)
            i += 1
        else:
            # Short form tag (tag numbers 0-30)
            # Lower 5 bits = tag number
            tag_num = tag_byte & 0x1f
            i += 1

        # --- Read the outer length ---
        outer_len, i = read_length(data, i)
        content_end = i + outer_len

        # --- Read the inner TLV (actual value) ---
        if i < content_end:
            inner_tag = data[i]       # The type (INTEGER, STRING etc.)
            i += 1
            inner_len, i = read_length(data, i)
            value_bytes = data[i : i + inner_len]
            i += inner_len

            # Look up the field name from our TAG_MAP
            field_name = TAG_MAP.get(tag_num, f'unknown_tag_{tag_num}')

            # Decode and store the value
            record[field_name] = decode_field(tag_num, value_bytes, inner_tag)
        else:
            i = content_end  # Skip to end if no inner content

    return record


# =============================================================
# SECTION 6: MAIN ENTRY POINT
#
# This is where the program starts running.
# It reads the .dat file, finds all CDR records,
# decodes each one, and saves to a JSON file.
# =============================================================

def main():
    # ---- File paths (change these if your files are elsewhere) ----
    INPUT_FILE  = "NZDLVOLTE202603201155167848.dat"
    OUTPUT_FILE = "decoded_cdrs.json"

    # ---- Check if input file exists ----
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File not found → {INPUT_FILE}")
        print("Make sure the .dat file is in the same folder as this script.")
        return

    print(f"Reading file: {INPUT_FILE}")

    # ---- Read all bytes from the binary file ----
    with open(INPUT_FILE, 'rb') as f:    # 'rb' = read binary (not text!)
        data = f.read()

    print(f"Total bytes read: {len(data)}")

    # ---- Walk through the bytes and find CDR records ----
    # Each CDR starts with byte 0x31 (ASN.1 SET tag = constructed SET)
    records = []
    i = 0

    while i < len(data):
        if data[i] == 0x31:
            # Found a CDR record!
            length, next_pos = read_length(data, i + 1)
            record = decode_record(data, next_pos, length)
            records.append(record)
            i = next_pos + length      # Jump to start of next record
        else:
            i += 1                     # Not a record start, keep scanning

    print(f"Total CDR records decoded: {len(records)}")

    # ---- Print a quick summary of each record ----
    print("\n--- SUMMARY ---")
    for idx, rec in enumerate(records, start=1):
        caller   = rec.get('callerno', 'N/A')
        called   = rec.get('calledno', 'N/A')
        duration = rec.get('duration', 'N/A')
        cdr_type = rec.get('cdrtype', 'N/A')
        print(f"Record {idx:2d} | Caller: {caller:20s} → Called: {called:20s} | Duration: {duration:4}s | CDR Type: {cdr_type}")

    # ---- Save full output to JSON file ----
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"\nFull decoded output saved to: {OUTPUT_FILE}")
    print("You can open this JSON file in VS Code or any text editor.")

if __name__ == "__main__":
    main()