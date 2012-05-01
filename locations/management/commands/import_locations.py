# -*- coding:utf-8 -*-
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

class Command(BaseCommand):
    help = "Load locations data from OKATO to database"

    def handle(self, *args, **options):
        from locations.models import Location

        data = {}
        path = []
        txt = open(os.path.join(settings.PROJECT_PATH, 'data', 'struct.txt')).read() \
                .decode("utf-8-sig")
        for line in txt.splitlines():
            level = (len(line)-len(line.lstrip())) / 4
            loc = tuple(line.strip().split('|'))

            if len(path) > level:
                path = path[:level]

            if len(path) == level:
                dt = data
                for p in path:
                    dt = dt[p]
                dt[loc] = {}
                path.append(loc)
            else:
                raise ValueError('incorrect file format')

        #import json
        #with open('/home/serg/data/grakon/test.txt', 'w') as f:
        #    f.write(json.dumps(data, indent=4, ensure_ascii=False).encode('utf8'))

        #locations = list(Location.objects.all())
        #locations_by_okato = dict((loc.okato_id, loc) for loc in locations if loc.okato_id!='')

        # Get or create Russia
        country, created = Location.objects.get_or_create(country=None, defaults={'name': u'Россия'})

        i = 0
        for (region_name, region_id), region_data in data.items():
            region = Location.objects.create(country=country, okato_id=region_id, name=region_name)
            for (district_name, district_id), district_data in region_data.iteritems():
                district = Location.objects.create(country=country, region=region,
                        okato_id=district_id, name=district_name)
                for location_name, location_id in district_data:
                    Location.objects.create(country=country, region=region,
                            district=district, okato_id=location_id, name=location_name)

            print_progress(i, len(data))
            i += 1

        """
        for (name, okato_id), region_data in data.iteritems():
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
                    # Manual hack because name is too long
                    if u'Таймырский Долгано-Ненецкий район' in district_data[0]:
                        district_data[0] = u'Таймырский Долгано-Ненецкий район'

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
        """
            