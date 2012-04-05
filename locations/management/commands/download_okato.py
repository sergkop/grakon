import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from scrapy.selector import HtmlXPathSelector

from grakon.utils import print_progress, read_url

URL = 'http://www.mosclassific.ru/mClass/okato_view.php?filter=100&type=1&zone='

# TODO: temporary
import os
os.environ['http_proxy'] = 'http://wwwcache.lancs.ac.uk:8080'

class Command(BaseCommand):
    help = "Download locations data from OKATO"

    def handle(self, *args, **options):
        print "Downloading second level ids"
        ids = []
        i = 0
        for line in open(os.path.join(settings.PROJECT_PATH, 'data', 'regions.txt')):
            region_id, name = line.strip().split(' ', 1)

            for option in HtmlXPathSelector(text=read_url(URL+region_id)) \
                    .select("//table[@width='100%' and @cellspacing='2' and @cellpadding='5']//tr[2]//option"):
                id = option.select("@value").extract()[0]

                for option1 in HtmlXPathSelector(text=read_url(URL+id)) \
                        .select("//table[@width='100%' and @cellspacing='2' and @cellpadding='5']//tr[2]//option"):
                    ids.append(option1.select("@value").extract()[0])

            i += 1
            print_progress(i, 80)

        print "Downloading locations hierarchy"
        i = 0
        data = {}
        for id in set(ids):
            for tr in HtmlXPathSelector(text=read_url(URL+id)).select("//table[@class='list']/tr")[1:]:
                okato_id = tr.select(".//td[2]//b/text()").extract()[0].replace(' ', '')
                assert len(okato_id)==8

                data[okato_id] = tr.select("./td[3]/text()").extract()[0]

            i += 1
            print_progress(i, len(ids))

        with open(os.path.join(settings.PROJECT_PATH, 'data', 'locations.json'), 'w') as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False).encode('utf8'))
