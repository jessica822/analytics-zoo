#
# Copyright 2018 Analytics Zoo Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os.path
import pytest
from unittest import TestCase

import zoo.orca.data
import zoo.orca.data.pandas
from zoo.common.nncontext import *


class TestSparkBackend(TestCase):
    def setup_method(self, method):
        self.resource_path = os.path.join(os.path.split(__file__)[0], "../../resources")
        ZooContext.orca_pandas_read_backend = "spark"

    def tearDown(self):
        ZooContext.orca_pandas_read_backend = "pandas"

    def test_header_and_names(self):
        file_path = os.path.join(self.resource_path, "orca/data/csv")
        # Default header="infer"
        data_shard = zoo.orca.data.pandas.read_csv(file_path)
        data = data_shard.collect()
        assert len(data) == 2, "number of shard should be 2"
        df = data[0]
        assert "location" in df.columns
        file_path = os.path.join(self.resource_path, "orca/data/no_header.csv")
        # No header, default to be '0','1','2'
        data_shard = zoo.orca.data.pandas.read_csv(file_path, header=None)
        df2 = data_shard.collect()[0]
        assert '0' in df2.columns and '2' in df2.columns
        # Specify names as header
        data_shard = zoo.orca.data.pandas.read_csv(
            file_path, header=None, names=["ID", "sale_price", "location"])
        df3 = data_shard.collect()[0]
        assert "sale_price" in df3.columns

    def test_usecols(self):
        file_path = os.path.join(self.resource_path, "orca/data/csv")
        data_shard = zoo.orca.data.pandas.read_csv(file_path, usecols=[0, 1])
        data = data_shard.collect()
        df = data[0]
        assert "sale_price" in df.columns
        assert "location" not in df.columns
        data_shard = zoo.orca.data.pandas.read_csv(file_path, usecols=["ID"])
        data = data_shard.collect()
        df2 = data[0]
        assert "ID" in df2.columns and "location" not in df2.columns

        def filter_col(name):
            return name == "sale_price"

        data_shard = zoo.orca.data.pandas.read_csv(file_path, usecols=filter_col)
        data = data_shard.collect()
        df3 = data[0]
        assert "sale_price" in df3.columns and "location" not in df3.columns

    def test_dtype(self):
        file_path = os.path.join(self.resource_path, "orca/data/csv")
        data_shard = zoo.orca.data.pandas.read_csv(file_path, dtype="float")
        data = data_shard.collect()
        df = data[0]
        assert df.location.dtype == "float64"
        assert df.ID.dtype == "float64"
        data_shard = zoo.orca.data.pandas.read_csv(file_path, dtype={"sale_price": "float"})
        data = data_shard.collect()
        df2 = data[0]
        assert df2.sale_price.dtype == "float64" and df2.ID.dtype == "int64"

    def test_squeeze(self):
        import pandas as pd
        file_path = os.path.join(self.resource_path, "orca/data/single_column.csv")
        data_shard = zoo.orca.data.pandas.read_csv(file_path, squeeze=True)
        data = data_shard.collect()
        df = data[0]
        assert isinstance(df, pd.Series)

    def test_index_col(self):
        file_path = os.path.join(self.resource_path, "orca/data/csv/morgage1.csv")
        data_shard = zoo.orca.data.pandas.read_csv(file_path, index_col="ID")
        data = data_shard.collect()
        df = data[0]
        assert 100529 in df.index

    def test_read_invalid_path(self):
        file_path = os.path.join(self.resource_path, "abc")
        with self.assertRaises(Exception) as context:
            xshards = zoo.orca.data.pandas.read_csv(file_path)
        self.assertTrue('The file path is invalid/empty' in str(context.exception))

    def test_read_json(self):
        file_path = os.path.join(self.resource_path, "orca/data/json")
        data_shard = zoo.orca.data.pandas.read_json(file_path)
        data = data_shard.collect()
        df = data[0]
        assert "timestamp" in df.columns and "value" in df.columns
        data_shard = zoo.orca.data.pandas.read_json(file_path, names=["time", "value"])
        data = data_shard.collect()
        df2 = data[0]
        assert "time" in df2.columns and "value" in df2.columns
        data_shard = zoo.orca.data.pandas.read_json(file_path, usecols=[0])
        data = data_shard.collect()
        df3 = data[0]
        assert "timestamp" in df3.columns and "value" not in df3.columns
        data_shard = zoo.orca.data.pandas.read_json(file_path, dtype={"value": "float"})
        data = data_shard.collect()
        df4 = data[0]
        assert df4.value.dtype == "float64"


if __name__ == "__main__":
    pytest.main([__file__])
