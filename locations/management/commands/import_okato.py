# -*- coding:utf-8 -*-
import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Load locations data from OKATO to database"

    def handle(self, *args, **options):
        from locations.models import Location

        data = json.load(open(os.path.join(settings.PROJECT_PATH, 'data', 'locations.json')))
        print data

        hierarchy = {}
        for line in open(os.path.join(settings.PROJECT_PATH, 'data', 'regions.txt')):
            region_id, name = line.strip().split(' ', 1)
            hierarchy[region_id] = [name, {}]

        # build hierarchy of locations
        for okato_id, name in data.iteritems():
            if okato_id[5:8] == '000':
                hierarchy[okato_id[:2]][1][okato_id[:5]] = [name, {}]

        for okato_id, name in data.iteritems():
            if okato_id[5:8]!='000' and name[-1]!='/':
                hierarchy[okato_id[:2]][1][okato_id[:5]][1][okato_id] = name

        endings1 = ('ый', 'ий', 'ой')
        endings2 = ('ая',)
        endings3 = ('ое',)

        location_types = {
            'Районы': ('район', endings1),
            'Волости': ('волость', endings2),
            'Сельсоветы': ('сельсовет', endings1),
            'Округа': ('округ', endings1),
            'Сельские округа': ('сельский округ', endings1),
            'Сельские территории': ('сельская территория', endings2),
            'Наслеги': ('наслег', endings1),
            'Сумоны': ('сумон', endings1),
            'Территориальные округа': ('территориальный округ', endings1),
            'Внутригородские районы': ('район', endings1),
            'Муниципальные округа': ('округ', endings1),
            'Сельские муниципальные образования': ('сельское муниципальное образование', endings3),
            'Административные округа': ('округ', endings1),
            'Административные районы': ('район', endings1),
            'Поселения': ('поселение', endings3),
            'Администрации сельских поселений': ('администрация сельских поселений', endings2),
            'Сельские Администрации': ('сельская администрация', endings2),
            'Сельские администрации': ('сельская администрация', endings2),
        }

        end = {}

        for region in hierarchy.itervalues():
            for loc_id in region[1]:
                ids = sorted([id for id in data.iterkeys() if id.startswith(loc_id)])

                group_name = None

                for id in ids:
                    if data[id][-1] == '/':
                        group_name = data[id]
                        continue
                    if group_name:
                        for location_type, (postfix, endings) in location_types.iteritems():
                            if group_name.startswith(location_type):
                                end.setdefault(postfix, []).append(data[id][-4:])
                                if any(data[id].endswith(ending) for ending in endings):
                                    region[1][loc_id][1][id] += ' ' + postfix
                                    continue

        # TODO: append names at the second level
        # TODO: Муниципальные образования +- (by hands), сельсоветы, районы

        # TODO: remove it
        for p in end:
            end[p] = list(set(end[p]))

        with open('/home/serg/data/grakon/hierarchy.txt', 'w') as f:
            f.write(json.dumps([end, hierarchy], indent=4, ensure_ascii=False))
