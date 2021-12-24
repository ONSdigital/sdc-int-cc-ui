from datetime import datetime

case_interactions = {
    "MANUAL_CASE_VIEW": "View case",
    "SCHEDULED_CASE_VIEW": "Scheduled case view",
    "SOFT_APPOINTMENT_MADE": "Soft appointment made",
    "HARD_APPOINTMENT_MADE": "Hard appointment made",
    "REFUSAL_REQUESTED": "Refusal requested",
    "CASE_UPDATE_REQUESTED": "Case update requested",
    "CONTACT_UPDATE_REQUESTED": "Contact update requested",
    "DATA_REMOVAL_REQUESTED": "Data removal requested",
    "TELEPHONE_CAPTURE_STARTED": "Telephone capture started",
    "FULFILMENT_REQUESTED": "New Access Code Requested",
    "CASE_NOTE_ADDED": "Note added by user",
    "OUTBOUND_APPOINTMENT_CALL": "Outgoing appointment call",
    "OUTBOUND_PRIORITISED_CALL": "Outgoing prioritised call",
    "OUTBOUND_MANUAL_CALL": "Outgoing manual call"
}

case_sub_interactions = {
    "CALL_NUMBER_ENGAGED": "engaged",
    "CALL_NUMBER_UNOBTAINABLE": "unobtainable",
    "CALL_ANSWERED": "answered",
    "CALL_UNANSWERED": "not answered",
    "CALL_VOICEMAIL": "went to voicemail",
    "FULFILMENT_PRINT": "print",
    "FULFILMENT_SMS": "SMS",
    "FULFILMENT_EMAIL": "email"
}


class Case:

    @staticmethod
    def build_case_history_content(interactions):
        case_history = []
        for interaction in interactions:
            date_to_format = datetime.fromisoformat(interaction['createdDateTime'])
            formatted_date = datetime.strftime(date_to_format, "%d %b %Y %H:%M:%S")
            formatted_sort_date = datetime.strftime(date_to_format, "%Y%m%d%H%M%S%f")
            case_history.append({
                'tds': [
                    {
                        'value': formatted_date,
                        'dataSort': formatted_sort_date
                    },
                    {
                        'value': interaction['interactionSource']
                    },
                    {
                        'value': Case.interaction_event(interaction)
                    },
                    {
                        'value': interaction['note']
                    },
                    {
                        'value': interaction['userName']
                    }
                ]
            })
        return case_history

    @staticmethod
    def interaction_event(interaction):
        event_type = interaction['interaction']
        event = case_interactions.get(event_type, event_type)
        outcome = case_sub_interactions.get(interaction['subInteraction'], "")
        if outcome:
            event = event + ' (' + outcome + ')'
        return event
