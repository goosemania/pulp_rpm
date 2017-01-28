import shutil
import tempfile
import unittest

import mock

from pulp_rpm.plugins.db import models
from pulp_rpm.plugins.distributors.yum.metadata.primary import PrimaryXMLFileContext


class PrimaryXMLFileContextTests(unittest.TestCase):
    def setUp(self):
        self.working_dir = tempfile.mkdtemp()
        self.context = PrimaryXMLFileContext(self.working_dir, 3)

    def tearDown(self):
        shutil.rmtree(self.working_dir)

    def test_init(self):
        self.assertEquals(self.context.fast_forward, False)
        self.assertEquals(self.context.num_packages, 3)

    def test_add_unit_metadata(self):
        self.context.metadata_file_handle = mock.Mock()
        unit = models.RPM()
        unit.set_repodata('primary', 'bar')
        self.context.add_unit_metadata(unit)
        self.context.metadata_file_handle.write.assert_called_once_with('bar')
