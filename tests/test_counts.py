import responses
from pathlib import Path

import aiod
from aiod.config.settings import API_BASE_URL, LATEST_VERSION

resources_path = Path(__file__).parent / "resources"


def test_counts():
    with responses.RequestsMock() as mocked_requests:
        with open(resources_path / "counts.json", "r") as f:
            res_body = f.read()
        mocked_requests.add(
            responses.GET,
            API_BASE_URL + "counts/" + LATEST_VERSION,
            body=res_body,
            status=200,
        )
        counts = aiod.counts(data_format="json")

        assert isinstance(counts, dict)
        assert "datasets" in counts