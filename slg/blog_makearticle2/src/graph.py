import os
import subprocess
import pandas as pd
from pandasql import sqldf
from dotenv import load_dotenv
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import interrupt, Command

from blog_makearticle2.src.state import AgentState, initial_state, config

# Define the graph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

# 環境変数の取得
load_dotenv('.env') 
openai_api_key = os.environ.get("OPENAI_API_KEY")

# モデルの定義
from langchain_openai import ChatOpenAI
model = ChatOpenAI(openai_api_key=openai_api_key,model="gpt-4o-mini")

#会社情報を取得するノード
def QueryCompanyInfo(state: AgentState, config: dict):
    """
    指定された設定に基づいて、サービス情報をクエリします。
    この関数は、指定された設定からサイトIDとサービスIDを取得し、データセットをロードしてサービス情報を取得するSQLクエリを実行します。
    結果として得られた文字列を返します。
    """ 
    # configからsite_idとcompany_idを取得
    site_id = config.get("configurable", {}).get("siteId")
    company_id = config.get("configurable", {}).get("companyId")

    # データのロード
    df = pd.read_csv("db/aibow_customerTable - companies.csv")

    # SQLクエリを実行して該当するsite_idのフォームデータを取得
    query = f"""
    SELECT 
        site_id,
        company_name,
        industry,
        location,
        website_url
    FROM df 
    WHERE site_id = '{site_id}' AND company_id = {company_id}
    """
    result = sqldf(query, locals())

    # 結果を文字列として返す
    if not result.empty:
        query_result = "# 会社情報\n"
        query_result += f"会社名: {result.iloc[0]['company_name']}\n"
        query_result += f"業界: {result.iloc[0]['industry']}\n"
        query_result += f"所在地: {result.iloc[0]['location']}\n"
        query_result += f"ウェブサイト: {result.iloc[0]['website_url']}\n"
        query_result += "\n会社情報のクエリ結果は以上です。\n"
        return {"messages": [query_result]}
    else:
        query_result = "該当するデータが見つかりませんでした。"
        return {"messages": [query_result]}

#サービス・プロダクト情報を取得するノード
def QueryServiceProduct(state: AgentState, config: RunnableConfig) -> str:
    """
    指定された設定に基づいて、サービス・プロダクト情報をクエリします。
    この関数は、指定された設定からサイトIDとプロダクトIDを取得し、データセットをロードしてサービス・プロダクト情報を取得するSQLクエリを実行します。
    結果として得られた文字列を返します。
    """

    # configからsite_idとproduct_idを取得
    site_id = config.get("configurable", {}).get("siteId")
    product_id = config.get("configurable", {}).get("productId")

    # データのロード
    df = pd.read_csv("db/aibow_customerTable - products.csv")

    # SQLクエリを実行して該当する site_id のプロダクトデータを取得
    query = f"""
    SELECT 
        appeal_policy,
        product_introduction,
        functionality,
        feature_1,
        feature_2,
        feature_3,
        competitive_point,
        problem_and_solution_1,
        problem_and_solution_2,
        problem_and_solution_3,
        industry_pain_points,
        target_approach_to_pain,
        service_record,
        client_partners,
        credentials,
        organization_size,
        external_review,
        price_advantage,
        support_system,
        faq
    FROM df
    WHERE site_id = '{site_id}' AND product_id = {product_id}
    """
    result = sqldf(query, locals())

    # 結果を文字列として返す
    if not result.empty:
        query_result = "# 自社プロダクトの情報\n"
        query_result += f"アピールポイント: {result.iloc[0]['appeal_policy']}\n"
        query_result += f"製品紹介: {result.iloc[0]['product_introduction']}\n"
        query_result += f"機能: {result.iloc[0]['functionality']}\n"
        query_result += f"特徴: {result.iloc[0]['feature_1']}, {result.iloc[0]['feature_2']}, {result.iloc[0]['feature_3']}\n"
        query_result += f"競争優位性: {result.iloc[0]['competitive_point']}\n"
        query_result += f"課題と解決策: {result.iloc[0]['problem_and_solution_1']}, {result.iloc[0]['problem_and_solution_2']}, {result.iloc[0]['problem_and_solution_3']}\n"
        query_result += f"業界のペインポイント: {result.iloc[0]['industry_pain_points']}\n"
        query_result += f"ペインに対するアプローチ: {result.iloc[0]['target_approach_to_pain']}\n"
        query_result += f"導入実績: {result.iloc[0]['service_record']}\n"
        query_result += f"クライアント・パートナー: {result.iloc[0]['client_partners']}\n"
        query_result += f"認証・実績: {result.iloc[0]['credentials']}\n"
        query_result += f"組織規模: {result.iloc[0]['organization_size']}\n"
        query_result += f"外部レビュー: {result.iloc[0]['external_review']}\n"
        query_result += f"価格の優位性: {result.iloc[0]['price_advantage']}\n"
        query_result += f"サポート体制: {result.iloc[0]['support_system']}\n"
        query_result += f"FAQ: {result.iloc[0]['faq']}\n"
        query_result += "自社プロダクトのクエリ結果は以上です。\n"
        return {"messages": [query_result]}
    else:
        query_result = "No matching records found."  # 空の場合は文字列を返す
        return {"messages": [query_result]}

#顧客ペルソナを取得するノード
def QueryCustomerPersona(state: AgentState, config: RunnableConfig) -> str:
    """
    指定された設定に基づいて、顧客ペルソナをクエリします。
    この関数は、指定された設定からサイトIDとプロダクトIDを取得し、データセットをロードしてサービス・プロダクト情報を取得するSQLクエリを実行します。
    結果として得られた文字列を返します。
    """
    
    # configからsite_idとpersona_idを取得
    site_id = config.get("configurable", {}).get("siteId")
    persona_id = config.get("configurable", {}).get("personaId")
    product_id = config.get("configurable", {}).get("productId")

    # データのロード
    df = pd.read_csv("db/aibow_customerTable - customerpersonas.csv")

    # SQLクエリを実行して該当する site_id のペルソナデータを取得
    query = f"""
    SELECT 
        industry,
        companySize,
        employeeSize,
        targetRegion,
        existingClients,
        customerPriceRange,
        leadTimeToAdoption,
        serviceDepartment,
        position,
        roleAndMission,
        infoMethods,
        selectionCriteria,
        considerationTrigger,
        businessIssues,
        currentSolutionMethods,
        productKnowledge,
        persona_title,
        age,
        value,
        pain
    FROM df
    WHERE site_id = '{site_id}' AND product_id = {product_id} AND persona_id = {persona_id}
    """
    result = sqldf(query, locals())

    # 結果を文字列として返す
    if not result.empty:
        query_result = "# 顧客ペルソナの情報\n"
        query_result += f"業界: {result.iloc[0]['industry']}\n"
        query_result += f"企業規模: {result.iloc[0]['companySize']}\n"
        query_result += f"従業員数: {result.iloc[0]['employeeSize']}\n"
        query_result += f"ターゲット地域: {result.iloc[0]['targetRegion']}\n"
        query_result += f"既存クライアント: {result.iloc[0]['existingClients']}\n"
        query_result += f"顧客の価格帯: {result.iloc[0]['customerPriceRange']}\n"
        query_result += f"導入までのリードタイム: {result.iloc[0]['leadTimeToAdoption']}\n"
        query_result += f"サービス部門: {result.iloc[0]['serviceDepartment']}\n"
        query_result += f"ポジション: {result.iloc[0]['position']}\n"
        query_result += f"役割とミッション: {result.iloc[0]['roleAndMission']}\n"
        query_result += f"情報収集方法: {result.iloc[0]['infoMethods']}\n"
        query_result += f"選定基準: {result.iloc[0]['selectionCriteria']}\n"
        query_result += f"検討のきっかけ: {result.iloc[0]['considerationTrigger']}\n"
        query_result += f"ビジネス課題: {result.iloc[0]['businessIssues']}\n"
        query_result += f"現在の解決策: {result.iloc[0]['currentSolutionMethods']}\n"
        query_result += f"プロダクトの知識: {result.iloc[0]['productKnowledge']}\n"
        query_result += f"ペルソナのタイトル: {result.iloc[0]['persona_title']}\n"
        query_result += f"年齢: {result.iloc[0]['age']}\n"
        query_result += f"価値観: {result.iloc[0]['value']}\n"
        query_result += f"ペインポイント: {result.iloc[0]['pain']}\n"
        query_result += "顧客ペルソナのクエリ結果は以上です。\n"
        return {"messages": [query_result]}
    else:
        query_result = "No matching records found."  # 空の場合は文字列を返す
        return {"messages": [query_result]}

# SEO記事のアウトラインを作成するノード
def CreateOutline(state: AgentState, config: RunnableConfig) -> str:
    """
    指定された設定に基づいて、記事戦略を作成します。
    この関数は、指定されたキーワードをとペルソナをもとに、記事のアウトラインを作成します。
    結果として得られた文字列を返します。
    """
    
    # stateから指定されたキーワードを取得
    write_word = state["write_word"]

    # プロンプトの定義
    outline_prompt = f"""
    # 指定キーワード
    {write_word}

    # 定義
    あなたはBtoB領域に特化した優秀なSEOライターです。

    # 指示
    ここまでの情報をもとにして、指定キーワードで検索順位上位を獲得するためのブログ記事のアウトラインを作成してください。
    ## 補足情報
    - アウトラインを作成する際は、ペルソナが抱えているであろう課題や疑問に焦点を当ててください。
    - 記事内での比率は、ペルソナの課題や疑問に対する解決策が70%、自社プロダクトが30%程度となるよう記載してください。
    - ペルソナが抱えている課題や疑問に対して、自社のサービス・プロダクトがどのように解決できるかを明確に示してください。
    - 記事のタイトルは、ペルソナが検索するであろうキーワードを含むものにしてください。
    - 記事の内容は、与えられている情報をすべて活用しようとせず、ペルソナが抱えている課題や疑問の解消を第一の目的としてください。
    """

    # OpenAI APIを呼び出してアウトラインを生成
    outline_response = model.invoke(state["messages"] + [outline_prompt])
    state["messages"].append(outline_response)

    return {"messages": [outline_response]}

# ヒューマンフィードバックノード
def HumanFeedback(state: AgentState, config: RunnableConfig) -> str:
    """
    ヒューマンフィードバックを取得するためのノードです。
    この関数は、ヒューマンフィードバックを取得して、結果を返します。
    """
    # ヒューマンフィードバックを取得
    feedback = interrupt("出力したアウトラインに満足していますか？（yes/no）:")
    # stateの更新
    return {'feedback': feedback}

# フィードバック評価ノード
def EvaluateFeedback(state: AgentState) -> Command:
    if state["feedback"] == 'yes':
        return Command(update={"remake_flag": False}, goto=END)
    else:
        return Command(update={"remake_flag": True}, goto="CreateOutline")

#######------------------------------------------------------------
#キーワードボリュームを取得するノード
def QueryKeywordVolume(state: AgentState, config: RunnableConfig) -> str:
    """
    指定された設定に基づいて、キーワードボリュームをクエリします。
    この関数は、指定されたキーワードでGoogle Ads APIによるキーワードボリュームクエリを実行します。
    結果として得られた内容をmarkdownの表形式で返します。
    """
    # stateからtarget_keywordを取得
    target_keyword = state["target_keyword"]

    # コマンドライン引数の作成
    result = subprocess.run([
        "python", "src/blog_features/utils.py",
        "-c", "9910458952",
        "-k", target_keyword,
        #"-l", "LOCATION_ID1", "LOCATION_ID2",
        #"-i", "LANGUAGE_ID",
        #"-p", "https://example.com"
    ], capture_output=True, text=True)

    # 結果を文字列として返す
    if result.stdout:
        return {"messages":[result.stdout]}
    else:
        return "No matching records found."  # 空の場合は文字列を返す
#######------------------------------------------------------------

# ノード・エッジの定義
import json
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

# Define the node that calls the model
def call_model( state: AgentState, config: RunnableConfig):
    # this is similar to customizing the create_react_agent with 'prompt' parameter, but is more flexible
    system_prompt = SystemMessage(
        "あなたは優秀なデータアナリストです。特にBtoB向けのSEO施策に深い知見を持っています。"
    )
    response = model.invoke([system_prompt] + state["messages"], config)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# Define a new graph
workflow = StateGraph(AgentState)

# Define the nodes
workflow.add_node("QueryCompanyInfo", QueryCompanyInfo)
workflow.add_node("QueryServiceProduct", QueryServiceProduct)
workflow.add_node("QueryCustomerPersona", QueryCustomerPersona)
workflow.add_node("CreateOutline", CreateOutline)
workflow.add_node("HumanFeedback", HumanFeedback)
workflow.add_node("EvaluateFeedback", EvaluateFeedback)

workflow.set_entry_point("QueryCompanyInfo")

workflow.add_edge("QueryCompanyInfo", "QueryServiceProduct")
workflow.add_edge("QueryServiceProduct", "QueryCustomerPersona")
workflow.add_edge("QueryCustomerPersona", "CreateOutline")
workflow.add_edge("CreateOutline", "HumanFeedback")
workflow.add_edge("HumanFeedback", "EvaluateFeedback")


memory = MemorySaver() # スレッド内記憶を維持するための設定
graph = workflow.compile(checkpointer=memory)