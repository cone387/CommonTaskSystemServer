# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2023/3/5 15:33
# software: PyCharm
from typing import Dict
from dateutil import parser


def nlp_config_to_schedule_config(nlp_syntax: Dict):
    type = nlp_syntax['type']
    definition = nlp_syntax['definition']
    config = {
        "nlp-sentence": nlp_syntax['sentence'],
    }
    nlp_time = nlp_syntax['time']
    if type == 'time_point':
        config['schedule_type'] = "O"
        config['O'] = {
            "schedule_start_time": nlp_syntax['time'][0],
        }
    elif type == 'time_period':
        delta = nlp_syntax['time']['delta']
        years = delta.get('year', 0)
        months = delta.get('month', 0)
        days = delta.get('day', 0)
        hours = delta.get('hour', 0)
        minutes = delta.get('minute', 0)
        seconds = delta.get('second', 0)
        seconds = seconds + minutes * 60 + hours * 3600
        if seconds:
            config['schedule_type'] = 'S'
            config['S'] = {
                "period": seconds,
                "schedule_start_time": nlp_time['point']['time'][0],
            }
        else:
            config['schedule_type'] = "T"
            config['T'] = {
                "type": "period",
                "time": nlp_time['point']['time'][0],
            }
            if days:
                config['T']["DAYS"] = {
                    "period": days,
                }
            elif months:
                config['T']["MONTHDAYS"] = {
                    "period": months,
                }
            elif years:
                config['T']["YEARS"] = {
                    "years": years
                }
    return config