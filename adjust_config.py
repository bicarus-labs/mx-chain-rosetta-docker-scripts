import sys
from argparse import ArgumentParser
from typing import List

import toml

"""
python3 adjust_config.py --mode=main --file=config.toml
python3 adjust_config.py --mode=prefs --file=prefs.toml
python3 adjust_config.py --mode=external --file=external.toml
"""

MODE_MAIN = "main"
MODE_PREFS = "prefs"
MODE_EXTERNAL = "external"
MODES = [MODE_MAIN, MODE_PREFS, MODE_EXTERNAL]


def main(cli_args: List[str]):
    parser = ArgumentParser()
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--api-simultaneous-requests", type=int, default=16384)
    parser.add_argument("--full-archive", type=bool, default=True)

    parser.add_argument("--elasticsearch-enable", type=bool, default=False)
    parser.add_argument("--elasticsearch-indexer-cache-size", type=int, default=0)
    parser.add_argument("--elasticsearch-bulk-request-max-size-in-bytes", type=int, default=4194304)
    parser.add_argument("--elasticsearch-url", type=str, default="http://localhost:9200")
    parser.add_argument("--elasticsearch-use-kibana", type=bool, default=False)
    parser.add_argument("--elasticsearch-username", type=str, default="")
    parser.add_argument("--elasticsearch-password", type=str, default="")

    parser.add_argument("--event-notifier-enable", type=bool, default=False)
    parser.add_argument("--event-notifier-use-authorization", type=bool, default=False)
    parser.add_argument("--event-notifier-proxy-url", type=str, default="http://localhost:5000")
    parser.add_argument("--event-notifier-username", type=str, default="")
    parser.add_argument("--event-notifier-password", type=str, default="")

    parser.add_argument("--covalent-enable", type=bool, default=False)
    parser.add_argument("--covalent-proxy-url", type=str, default="localhost:21111")
    parser.add_argument("--covalent-route-send-data", type=str, default="/block")
    parser.add_argument("--covalent-route-acknowledge-data", type=str, default="/acknowledge")

    parsed_args = parser.parse_args(cli_args)
    mode = parsed_args.mode
    file = parsed_args.file

    data = toml.load(file)

    if mode == MODE_MAIN:
        data["GeneralSettings"]["StartInEpochEnabled"] = False
        data["DbLookupExtensions"]["Enabled"] = True
        data["StateTriesConfig"]["AccountsStatePruningEnabled"] = False
        data["StoragePruning"]["ObserverCleanOldEpochsData"] = False
        data["StoragePruning"]["AccountsTrieCleanOldEpochsData"] = False
        data["Antiflood"]["WebServer"]["SimultaneousRequests"] = parsed_args.api_simultaneous_requests
    elif mode == MODE_PREFS:
        data["Preferences"]["FullArchive"] = parsed_args.full_archive
    elif mode == MODE_EXTERNAL:
        data["ElasticSearchConnector"]["Enabled"] = parsed_args.elasticsearch_enable
        data["ElasticSearchConnector"]["IndexerCacheSize"] = parsed_args.elasticsearch_indexer_cache_size
        data["ElasticSearchConnector"]["BulkRequestMaxSizeInBytes"] = parsed_args.elasticsearch_bulk_request_max_size_in_bytes
        data["ElasticSearchConnector"]["URL"] = parsed_args.elasticsearch_url
        data["ElasticSearchConnector"]["UseKibana"] = parsed_args.elasticsearch_use_kibana
        data["ElasticSearchConnector"]["Username"] = parsed_args.elasticsearch_username
        data["ElasticSearchConnector"]["Password"] = parsed_args.elasticsearch_password

        data["EventNotifierConnector"]["Enabled"] = parsed_args.event_notifier_enable
        data["EventNotifierConnector"]["UseAuthorization"] = parsed_args.event_notifier_use_authorization
        data["EventNotifierConnector"]["ProxyUrl"] = parsed_args.event_notifier_proxy_url
        data["EventNotifierConnector"]["Username"] = parsed_args.event_notifier_username
        data["EventNotifierConnector"]["Password"] = parsed_args.event_notifier_password

        data["CovalentConnector"]["Enabled"] = parsed_args.covalent_enable
        data["CovalentConnector"]["URL"] = parsed_args.covalent_proxy_url
        data["CovalentConnector"]["RouteSendData"] = parsed_args.covalent_route_send_data
        data["CovalentConnector"]["RouteAcknowledgeData"] = parsed_args.covalent_route_acknowledge_data
    else:
        raise Exception(f"Unknown mode: {mode}")

    with open(file, "w") as f:
        toml.dump(data, f)

    print(f"Configuration adjusted: mode = {mode}, file = {file}")


if __name__ == "__main__":
    main(sys.argv[1:])
