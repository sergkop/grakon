# -*- coding:utf-8 -*-
import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Load locations data from OKATO to database"

    def handle(self, *args, **options):
        from locations.models import Location

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

        # TODO: detect location type it and save it in model
        # TODO: drop сельсоветы and other small districts
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

        # TODO: append names at the second level
        # TODO: Муниципальные образования +- (by hands), сельсоветы, районы

        # TODO: remove it
        for p in end:
            end[p] = list(set(end[p]))

        locations = list(Location.objects.all())
        locations_by_okato = dict((loc.okato_id, loc) for loc in locations if loc.okato_id!='')

        # TODO: get or create Russia
        country, created = Location.objects.get_or_create(country=None, defaults={'name': u'Россия'})

        for region_id, region_data in hierarchy.iteritems():
            if region_id in locations_by_okato:
                region = locations_by_okato[region_id]
                if region.name != region_data[0]:
                    # TODO: ask user what to do
                    print "Mismatch:", region.name, '!=', region_data[0]
            else:
                region = Location.objects.create(country=country, okato_id=region_id,
                        name=region_data[0])

            for district_id, district_data in region_data[1].iteritems():
                if district_id in locations_by_okato:
                    district = locations_by_okato[district_id]
                    if district.name != district_data[0]:
                        # TODO: ask user what to do
                        print "Mismatch:", district.name, '!=', district_data[0]
                else:
                    district = Location.objects.create(country=country, region=region,
                            okato_id=district_id, name=district_data[0])

                locations = []
                for loc_id, loc_data in district_data[1].iteritems():
                    if loc_id in locations_by_okato:
                        location = locations_by_okato[loc_id]
                        if location.name != loc_data:
                            # TODO: ask user what to do
                            print "Mismatch:", location.name, '!=', loc_data
                    else:
                        locations.append(Location(country=country, region=region,
                                district=district, okato_id=loc_id, name=loc_data))

                Location.objects.bulk_create(locations)

        # TODO: drop it
        with open('/home/serg/data/grakon/hierarchy.txt', 'w') as f:
            f.write(json.dumps([end, hierarchy], indent=4, ensure_ascii=False).encode('utf8'))
