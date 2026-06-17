from .models import CDRRule

def apply_rules(cdr_record: dict) -> list:
    """
    Takes one decoded CDR record (dict),
    fetches ALL active rules from DB,
    returns list of triggered actions.
    No rules are hardcoded here.
    """
    results = []
    rules = CDRRule.objects.filter(is_active=True)  # read from DB every time

    for rule in rules:
        field_val = cdr_record.get(rule.field_name)
        if field_val is None:
            continue

        triggered = False

        # Compare based on operator stored in DB
        try:
            if rule.operator == 'equals':
                triggered = str(field_val) == rule.value
            elif rule.operator == 'not_equals':
                triggered = str(field_val) != rule.value
            elif rule.operator == 'greater':
                triggered = float(field_val) > float(rule.value)
            elif rule.operator == 'less':
                triggered = float(field_val) < float(rule.value)
            elif rule.operator == 'contains':
                triggered = rule.value in str(field_val)
            elif rule.operator == 'starts_with':
                triggered = str(field_val).startswith(rule.value)
            elif rule.operator == 'ends_with':
                triggered = str(field_val).endswith(rule.value)
        except:
            continue

        if triggered:
            results.append({
                'rule': rule.name,
                'action': rule.action,
                'label': rule.action_label
            })

    return results