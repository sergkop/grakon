# -*- coding:utf-8 -*-
import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Prepare text file with OKATO data for manual processing"

    def handle(self, *args, **options):
        data_path = os.path.join(settings.PROJECT_PATH, 'data', 'locations.json')
        data = json.loads(open(data_path).read(), encoding='utf8')

        hierarchy = {}
        for line in open(os.path.join(settings.PROJECT_PATH, 'data', 'regions.txt')):
            region_id, name = line.strip().split(' ', 1)
            hierarchy[region_id] = [name.decode('utf8'), {}]

        # build hierarchy of locations
        for okato_id, name in data.iteritems():
            if okato_id[5:8] == '000':
                hierarchy[okato_id[:2]][1][okato_id[:5]] = [name, {}]

        for okato_id, name in data.iteritems():
            if okato_id[5:8]!='000' and name[-1]!='/':
                hierarchy[okato_id[:2]][1][okato_id[:5]][1][okato_id] = name

        endings1 = (u'ый', u'ий', u'ой')
        endings2 = (u'ая',)
        endings3 = (u'ое',)

        # TODO: detect location type and save it in model
        # {name_start: (name, endings, ignore)}
        location_types = {
            u'Районы': (u'район', endings1),
            u'Волости': (u'волость', endings2),
            u'Сельсоветы': (u'сельсовет', endings1),
            u'Округа': (u'округ', endings1),
            u'Сельские округа': (u'сельский округ', endings1),
            u'Сельские территории': (u'сельская территория', endings2),
            u'Наслеги': (u'наслег', endings1),
            u'Сумоны': (u'сумон', endings1),
            u'Территориальные округа': (u'территориальный округ', endings1),
            u'Внутригородские районы': (u'район', endings1),
            u'Муниципальные округа': (u'округ', endings1),
            u'Сельские муниципальные образования': (u'сельское муниципальное образование', endings3),
            u'Административные округа': (u'округ', endings1),
            u'Административные районы': (u'район', endings1),
            u'Поселения': (u'поселение', endings3),
            u'Администрации сельских поселений': (u'администрация сельских поселений', endings2),
            u'Сельские Администрации': (u'сельская администрация', endings2),
            u'Сельские администрации': (u'сельская администрация', endings2),
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
                                end.setdefault(postfix, []).append(data[id][-2:])
                                if any(data[id].endswith(ending) for ending in endings):
                                    region[1][loc_id][1][id] += ' ' + postfix
                                    continue

        # TODO: remove it
        #for p in end:
        #    end[p] = list(set(end[p]))

        #with open('/home/serg/data/grakon/hierarchy.txt', 'w') as f:
        #    f.write(json.dumps([end, hierarchy], indent=4, ensure_ascii=False).encode('utf8'))

        txt = u''
        for id in hierarchy:
            txt += u'%s|%s\n' % (hierarchy[id][0], id)

            for id1 in hierarchy[id][1]:
                txt += u'    %s|%s\n' % (hierarchy[id][1][id1][0], id1)

                if id1[2]=='2' and id1[:2] not in ['40', '45']: # Moscow and St.Petersburg are exceptions
                    continue

                for id2 in hierarchy[id][1][id1][1]:
                    if id2[5] in ['8', '9']: # ignore сельсоветы
                        continue
                    if id2[2]=='4' and id2[5] in ['5', '6']: # ignore поселки городского типа
                        continue
                    txt += u'        %s|%s\n' % (hierarchy[id][1][id1][1][id2], id2)

        with open('/home/serg/data/grakon/struct.txt', 'w') as f:
            f.write(txt.encode('utf8'))
