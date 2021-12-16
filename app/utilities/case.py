import os

from datetime import datetime
from flask import current_app, json


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
                        'value': Case.enum_to_real_text(interaction['interaction'], 'case-history-enums.json')
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
    def enum_to_real_text(lookup_enum, lookup_filename):
        filename = os.path.join(current_app.static_folder, 'data', lookup_filename)
        with open(filename) as file:
            data = json.load(file)
            for enum in data:
                if enum['value'] == lookup_enum:
                    return enum['text']
