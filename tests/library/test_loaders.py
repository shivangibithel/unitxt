import json
import os
import tempfile
from unittest.mock import patch

import ibm_boto3
import pandas as pd

from src.unitxt.loaders import LoadCSV, LoadFromIBMCloud, LoadHF
from src.unitxt.logging_utils import get_logger
from tests.utils import UnitxtTestCase

logger = get_logger()


CONTENT = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]


class DummyBody:
    def iter_lines():
        for line in CONTENT:
            line_as_str = json.dumps(line)
            line_as_bytes = line_as_str.encode()
            yield line_as_bytes


class DummyObject:
    def get(self):
        return {"ContentLength": 1, "Body": DummyBody}


class DummyBucket:
    def download_file(self, item_name, local_file, Callback):
        with open(local_file, "w") as f:
            logger.info(local_file)
            for line in CONTENT:
                f.write(json.dumps(line) + "\n")


class DummyS3:
    def Object(self, bucket_name, item_name):
        return DummyObject()

    def Bucket(self, bucket_name):
        return DummyBucket()


class TestLoaders(UnitxtTestCase):
    def test_load_csv(self):
        # Using a context for the temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            files = {}
            dfs = {}

            for file in ["train", "test"]:
                path = os.path.join(tmp_dir, file + ".csv")  # Adding a file extension
                df = pd.DataFrame({"x": [1, 2, 3, 4, 5]})  # Replace with your data
                dfs[file] = df
                df.to_csv(path, index=False)
                files[file] = path

            loader = LoadCSV(files=files)
            ms = loader()

            for file in ["train", "test"]:
                for saved_instance, loaded_instance in zip(
                    dfs[file].iterrows(), ms[file]
                ):
                    self.assertEqual(saved_instance[1].to_dict(), loaded_instance)

    def test_load_from_ibm_cos(self):
        os.environ["DUMMY_URL_ENV"] = "DUMMY_URL"
        os.environ["DUMMY_KEY_ENV"] = "DUMMY_KEY"
        os.environ["DUMMY_SECRET_ENV"] = "DUMMY_SECRET"
        for data_files in [
            ["train.jsonl", "test.jsonl"],
            {"train": "train.jsonl", "test": "test.jsonl"},
            {"train": ["train.jsonl"], "test": ["test.jsonl"]},
        ]:
            for loader_limit in [1, 2, None]:
                loader = LoadFromIBMCloud(
                    endpoint_url_env="DUMMY_URL_ENV",
                    aws_access_key_id_env="DUMMY_KEY_ENV",
                    aws_secret_access_key_env="DUMMY_SECRET_ENV",
                    bucket_name="DUMMY_BUCKET",
                    data_dir="DUMMY_DATA_DIR",
                    data_files=data_files,
                    loader_limit=loader_limit,
                )
                with patch.object(ibm_boto3, "resource", return_value=DummyS3()):
                    ms = loader()
                    ds = ms.to_dataset()
                    if loader_limit is None:
                        self.assertEqual(len(ds["test"]), 2)
                    else:
                        self.assertEqual(len(ds["test"]), loader_limit)
                    self.assertEqual(ds["test"][0], {"a": 1, "b": 2})

    def test_load_from_HF_compressed(self):
        loader = LoadHF(path="GEM/xlsum", name="igbo")  # the smallest file
        ms = loader.process()
        dataset = ms.to_dataset()
        self.assertEqual(
            ms.to_dataset()["train"][0]["url"],
            "https://www.bbc.com/igbo/afirika-43986554",
        )
        assert set(dataset.keys()) == {
            "train",
            "validation",
            "test",
        }, f"Unexpected fold {dataset.keys()}"

    def test_load_from_HF_compressed_split(self):
        loader = LoadHF(
            path="GEM/xlsum", name="igbo", split="train"
        )  # the smallest file
        ms = loader.process()
        dataset = ms.to_dataset()
        self.assertEqual(
            ms.to_dataset()["train"][0]["url"],
            "https://www.bbc.com/igbo/afirika-43986554",
        )
        assert list(dataset.keys()) == ["train"], f"Unexpected fold {dataset.keys()}"

    def test_load_from_HF(self):
        loader = LoadHF(path="sst2")
        ms = loader.process()
        dataset = ms.to_dataset()
        self.assertEqual(
            dataset["train"][0]["sentence"],
            "hide new secretions from the parental units ",
        )
        assert set(dataset.keys()) == {
            "train",
            "validation",
            "test",
        }, f"Unexpected fold {dataset.keys()}"

    def test_load_from_HF_split(self):
        loader = LoadHF(path="sst2", split="train")
        ms = loader.process()
        dataset = ms.to_dataset()
        self.assertEqual(
            dataset["train"][0]["sentence"],
            "hide new secretions from the parental units ",
        )
        assert list(dataset.keys()) == ["train"], f"Unexpected fold {dataset.keys()}"
