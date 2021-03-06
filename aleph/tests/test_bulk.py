import os
from unittest import skip  # noqa
from alephclient.util import load_config_file

from aleph.logic.entities import bulk_load
from aleph.model import Collection
from aleph.tests.util import TestCase


class BulkLoadTestCase(TestCase):

    def setUp(self):
        super(BulkLoadTestCase, self).setUp()

    def test_load_sqlite(self):
        count = Collection.all().count()
        assert 0 == count, count

        db_uri = 'sqlite:///' + self.get_fixture_path('kek.sqlite')
        os.environ['ALEPH_TEST_BULK_DATABASE_URI'] = db_uri
        yml_path = self.get_fixture_path('kek.yml')
        config = load_config_file(yml_path)
        bulk_load(config)

        count = Collection.all().count()
        assert 1 == count, count

        coll = Collection.by_foreign_id('kek')
        assert coll.category == 'scrape', coll.category

        _, headers = self.login(is_admin=True)
        url = '/api/2/entities?filter:schemata=Thing&q=friede+springer'
        res = self.client.get(url, headers=headers)
        assert res.status_code == 200, res
        assert res.json['total'] == 1, res.json
        res0 = res.json['results'][0]
        key = '9895ccc1b3d6444ccc6371ae239a7d55c748a714'
        assert res0['id'].startswith(key), res0

    def test_load_csv(self):
        count = Collection.all().count()
        assert 0 == count, count

        db_uri = 'file://' + self.get_fixture_path('experts.csv')
        os.environ['ALEPH_TEST_BULK_CSV'] = db_uri
        yml_path = self.get_fixture_path('experts.yml')
        config = load_config_file(yml_path)
        bulk_load(config)

        coll = Collection.by_foreign_id('experts')
        assert coll.category == 'scrape', coll.category

        _, headers = self.login(is_admin=True)
        count = Collection.all().count()
        assert 1 == count, count

        url = '/api/2/entities?filter:schemata=Thing&q=Greenfield'
        res = self.client.get(url, headers=headers)
        assert res.status_code == 200, res
        assert res.json['total'] == 1, res.json
