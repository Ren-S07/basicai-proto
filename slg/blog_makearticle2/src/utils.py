#!/usr/bin/env python
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This example generates keyword ideas from a list of seed keywords."""


import argparse
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd

import os
from dotenv import load_dotenv

# 環境変数の取得
load_dotenv('.env') 
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
GOOGLE_ADS_CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

'''
都道府県ランキングトップ10
https://ja.wikipedia.org/wiki/%E9%83%BD%E9%81%93%E5%BA%9C%E7%9C%8C%E3%81%AE%E4%BA%BA%E5%8F%A3%E4%B8%80%E8%A6%A7
東京、神奈川、大阪、愛知、埼玉、千葉、兵庫、北海道、福岡、静岡
'''
ParentIDs = ["20636", "20637", "2392", "20646", "20634", "20635", "20651", "20624", "20663", "20645"]
# Location IDs are listed here:
# https://developers.google.com/google-ads/api/reference/data/geotargets
# and they can also be retrieved using the GeoTargetConstantService as shown
# here: https://developers.google.com/google-ads/api/docs/targeting/location-targeting
# _DEFAULT_LOCATION_IDS = ["1023191"]  # location ID for New York, NY
_DEFAULT_LOCATION_IDS = list(ParentIDs)[0:11]  # location ID for New York, NY
# A language criterion ID. For example, specify 1000 for English. For more
# information on determining this value, see the below link:
# https://developers.google.com/google-ads/api/reference/data/codes-formats#expandable-7
_DEFAULT_LANGUAGE_ID = "1005"  # language ID 1005 for 日本語

# [START generate_keyword_ideas]
def main(
    client, customer_id, location_ids, language_id, keyword_texts, page_url
):
    # KeywordPlanIdeaServiceを取得
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    # キーワード競争レベルの列挙型を取得
    keyword_competition_level_enum = (
        client.enums.KeywordPlanCompetitionLevelEnum
    )
    # キーワードプランネットワークを設定
    keyword_plan_network = (
        client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
    )
    # ロケーションIDをリソース名に変換
    location_rns = map_locations_ids_to_resource_names(client, location_ids)
    # 言語リソース名を取得
    language_rn = client.get_service("GoogleAdsService").language_constant_path(
        language_id
    )

    # キーワードまたはページURLが提供されていない場合はエラーを発生させる   
    if not (keyword_texts or page_url):
        raise ValueError(
            "At least one of keywords or page URL is required, "
            "but neither was specified."
        )

    # リクエストオブジェクトを作成
    ## url_seed、keyword_seed、keyword_and_url_seedの各フィールドは、
    ## 提供される入力（キーワード、ページURL、またはその両方）に応じて、リクエスト内で一度に1つだけ設定する必要がある
    ### 1. URLのみを使用する場合: url_seedフィールドにページのURLを設定します。
	### 2. キーワードのみを使用する場合: keyword_seedフィールドにキーワードのリストを設定します。
	### 3. URLとキーワードの両方を使用する場合: keyword_and_url_seedフィールドにページのURLとキーワードのリストを設定します。
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = language_rn
    request.geo_target_constants = location_rns
    request.include_adult_keywords = False
    request.keyword_plan_network = keyword_plan_network

    # キーワードを指定せずにページURLのみを使用する場合は、UrlSeedオブジェクトを初期化し、そのurlフィールドにページURLを設定する必要があります。
    if not keyword_texts and page_url:
        request.url_seed.url = page_url

    # キーワードのリストのみを使用し、ページURLを指定せずにキーワードアイデアを生成するには、KeywordSeedオブジェクトを初期化し、そのkeywordsフィールドにStringValueオブジェクトのリストを設定する必要があります。   
    if keyword_texts and not page_url:
        request.keyword_seed.keywords.extend(keyword_texts)

    # キーワードのリストとページURLの両方を使用してキーワードアイデアを生成するには、KeywordAndUrlSeedオブジェクトを初期化し、そのurlフィールドにページURLを、keywordsフィールドにキーワードのリストを設定する必要があります。
    if keyword_texts and page_url:
        request.keyword_and_url_seed.url = page_url
        request.keyword_and_url_seed.keywords.extend(keyword_texts)

    # キーワードアイデアを生成
    keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(
        request=request
    )

    # 生成されたキーワードアイデアをデータフレームに格納
    data = []
    for idea in keyword_ideas:
        competition_value = idea.keyword_idea_metrics.competition.name
        data.append({
            "Keyword": idea.text,
            "Avg Monthly Searches": idea.keyword_idea_metrics.avg_monthly_searches,
            "Competition": competition_value
        })

    df_keywords = pd.DataFrame(data)

    # ヘッダー名を変更
    df_keywords.rename(columns={
        "Keyword": "キーワード",
        "Avg Monthly Searches": "月平均検索ボリューム",
        "Competition": "広告競合度"
    }, inplace=True)

    # CompetitionがUNSPECIFIEDのものを削除
    df_filtered = df_keywords[~df_keywords["広告競合度"].isin(["UNSPECIFIED"])]

    # 月平均検索ボリュームが100以下の行を削除
    df_filtered = df_filtered[df_filtered["月平均検索ボリューム"] > 100]

    # CompetitionがLOW, MEDIUMの順に並べ替え、次に月平均検索数の降順で並べ替え
    df_sorted = df_filtered.sort_values(
        by=["広告競合度", "月平均検索ボリューム"],
        key=lambda col: col.map({"LOW": 0, "MEDIUM": 1, "HIGH": 2, "UNSPECIFIED": 3}) if col.name == "競合度" else col,
        ascending=[True, False]
    )

    # データフレームの内容をMarkdown形式でファイルに出力
    with open("/Users/suzukiren/blog_features/keyword_ideas.md", "w") as f:
        f.write(df_sorted.to_markdown(index=False))

    # データフレームの内容をMarkdown形式でコンソールに出力
    markdown_text = df_sorted.to_markdown(index=False)

    # マークダウンテキストを出力
    print(markdown_text)

    # [END generate_keyword_ideas]


def map_locations_ids_to_resource_names(client, location_ids):
    """Converts a list of location IDs to resource names.

    Args:
        client: an initialized GoogleAdsClient instance.
        location_ids: a list of location ID strings.

    Returns:
        a list of resource name strings using the given location IDs.
    """
    build_resource_name = client.get_service(
        "GeoTargetConstantService"
    ).geo_target_constant_path
    return [build_resource_name(location_id) for location_id in location_ids]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates keyword ideas from a list of seed keywords."
    )

    # The following argument(s) should be provided to run the example.
    parser.add_argument(
        "-c",
        "--customer_id",
        type=str,
        required=True,
        help="The Google Ads customer ID.",
    )
    parser.add_argument(
        "-k",
        "--keyword_texts",
        nargs="+",
        type=str,
        required=False,
        default=[],
        help="Space-delimited list of starter keywords",
    )
    # To determine the appropriate location IDs, see:
    # https://developers.google.com/google-ads/api/reference/data/geotargets
    parser.add_argument(
        "-l",
        "--location_ids",
        nargs="+",
        type=str,
        required=False,
        default=_DEFAULT_LOCATION_IDS,
        help="Space-delimited list of location criteria IDs",
    )
    # To determine the appropriate language ID, see:
    # https://developers.google.com/google-ads/api/reference/data/codes-formats#expandable-7
    parser.add_argument(
        "-i",
        "--language_id",
        type=str,
        required=False,
        default=_DEFAULT_LANGUAGE_ID,
        help="The language criterion ID.",
    )
    # Optional: Specify a URL string related to your business to generate ideas.
    parser.add_argument(
        "-p",
        "--page_url",
        type=str,
        required=False,
        help="A URL string related to your business",
    )

    args = parser.parse_args()

    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.

    # googleads_client = GoogleAdsClient.load_from_storage(version="v19")
    # ここでエラーが出るので、yamlファイルのパスを指定する
    googleads_client = GoogleAdsClient.load_from_storage("/Users/suzukiren/blog_features/google-ads.yaml")

    try:
        main(
            googleads_client,
            args.customer_id,
            args.location_ids,
            args.language_id,
            args.keyword_texts,
            args.page_url,
        )
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
