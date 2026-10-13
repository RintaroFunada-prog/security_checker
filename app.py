import streamlit as st

st.set_page_config(page_title="生成AI 利用リスクチェック", page_icon="🛡️", layout="centered")


def evaluate(form):
    blockers, notes, high_risk = [], [], []
    restricted = form["restricted_data"]
    customer = form["customer_data"]
    closed = form["closed_environment"]

    if form["personal_data"]:
        blockers.append("個人情報を生成AIへ入力する計画です。ガイドラインでは入力は禁止されています。")
    if customer and not form["customer_permission"]:
        blockers.append("顧客から受領した情報を、顧客の許可なく入力する計画です。")
    if restricted or customer:
        if closed:
            notes.append("外部と遮断された閉鎖環境での社内・顧客情報利用は条件付きで可能とされています。生成物を社外向けに使わないでください。")
            if form["use_case"] == "社外へ提供・公開する":
                blockers.append("閉鎖環境で生成したデータを社外向けに利用する計画です。ガイドラインでは社外向け利用はしないよう定めています。")
        elif not form["enterprise_protection"]:
            blockers.append("社外秘等または顧客情報を、エンタープライズ保護のない環境へ入力する計画です。")
        if restricted and not closed and form["enterprise_protection"] and not form["division_head_approval"]:
            high_risk.append("保護環境であっても、社外秘等の情報を入力するには本部長以上の許可が必要です。")
        elif restricted and not closed and form["enterprise_protection"]:
            notes.append("保護環境と本部長以上の許可がある前提で判定しています。顧客情報は顧客の許可も必要です。")
    if customer and form["customer_permission"]:
        notes.append("顧客情報について、顧客から許可を得ている前提です。契約・顧客ルールも確認してください。")

    if form["service"] == "上記以外・未確認":
        high_risk.append("会社推奨リスト外のサービスです。利用可否をITPM部に相談し、業務利用前にクラウドサービス利用申請を確認してください。")
    elif form["service"] == "GitHub Copilot Business / Enterprise" and not form["public_code_filter"]:
        high_risk.append("GitHub Copilot Business/Enterpriseは、Suggestions matching public codeをブロックする設定が条件です。設定を確認してください。")
    if form["customer_rules"] == "確認済み":
        notes.append("顧客先の生成AIルールを確認した前提です。顧客ルールを優先してください。")
    elif (customer or form["use_case"] == "社外へ提供・公開する") and form["customer_rules"] == "未確認":
        high_risk.append("顧客先や顧客向けの利用を含みます。顧客の生成AIルールを確認してから進めてください。")

    use_messages = {
        "判断・意思決定に直接影響する": "AIの出力が意思決定に直接影響します。結果を鵜呑みにせず、人間が根拠を確認して判断してください。",
        "AIエージェントが自律的に実行・操作する": "AIエージェントによる自律実行を含みます。付与権限を最小限にし、危険な操作には人間の承認を設定してください。",
        "社外へ提供・公開する": "生成物を顧客へ提供、または社外公開する予定です。内容・根拠・権利関係を人間がレビューしてください。",
    }
    if form["use_case"] in use_messages:
        high_risk.append(use_messages[form["use_case"]])
    if form["dangerous_action"]:
        high_risk.append("削除・外部送信・権限変更などの危険な操作があります。必ず人間の承認を得て、権限を最小化してください。")

    if form["copyright_use"] == "記事・画像・音声等を社外利用":
        blockers.append("記事・論文・小説・画像・動画・3Dモデル・音声・音楽の生成物を社外利用する計画です。ガイドラインでは社内利用に限定されています。")
    elif form["copyright_use"] == "プログラムコード":
        notes.append("生成コードを顧客提供する場合は、顧客ルール、ステークホルダーとの調整、ライセンス・著作権対策も確認してください。")
    elif form["copyright_use"] == "その他／未確認":
        notes.append("生成物の用途に応じ、著作権法その他の関係法令を確認してください。")

    if blockers:
        return ("error", "利用禁止に該当する可能性があります", "この計画のまま生成AIを利用しないでください。入力内容や利用方法を変更するか、所定の相談先へ確認してください。", blockers, high_risk, notes)
    if high_risk:
        return ("warning", "高リスク・事前確認が必要です", "承認・設定・人手によるレビューを済ませるまで実行しないでください。", [], high_risk, notes)
    if not notes:
        notes.append("公開情報・個人情報に該当しない情報を使い、AIに判断や責任を委ねない補助的な使い方を前提とした判定です。")
    return ("success", "低リスクの目安です", "入力情報・サービス・用途に基づく目安です。正式な承認や審査の代わりにはなりません。", [], [], notes)


st.markdown("<style>.block-container{max-width:850px;padding-top:3rem}[data-testid='stForm']{border:1px solid #e5eaf2;border-radius:14px;padding:1.2rem 1.4rem}</style>", unsafe_allow_html=True)
st.caption("INTERNAL USE · PoC　/　社内ガイドライン v1.5")
st.title("生成AI 利用リスクチェック")
st.write("利用計画について回答すると、ガイドラインに基づく確認ポイントを表示します。")
st.info("判定は目安です。正式な承認やセキュリティ審査ではありません。迷った場合やグレーな利用は、本部長・ITPM部など所定の相談先に確認してください。")
st.caption("入力した回答は保存せず、この画面内で判定します。実際の文書・コード・顧客情報などは入力しないでください。")

with st.form("risk_check_form"):
    st.subheader("1. 入力する情報")
    personal = st.radio("個人情報（氏名・住所・マイナンバー等）を入力しますか？", ["いいえ", "はい"], horizontal=True) == "はい"
    restricted = st.radio("社外秘・秘密・極秘の社内情報を入力しますか？", ["いいえ", "はい"], horizontal=True) == "はい"
    customer = st.radio("顧客から受領した情報を入力しますか？", ["いいえ", "はい"], horizontal=True) == "はい"
    customer_permission = st.radio("顧客から生成AIへの入力許可を得ていますか？", ["いいえ／未確認", "はい"], horizontal=True) == "はい"
    enterprise = st.radio("利用環境にエンタープライズ保護（情報漏えい対策等）がありますか？", ["いいえ／未確認", "はい"], horizontal=True) == "はい"
    closed = st.radio("外部と遮断された閉鎖環境ですか？", ["いいえ／未確認", "はい"], horizontal=True) == "はい"
    division_approval = st.radio("社外秘等の入力について本部長以上の許可を得ていますか？", ["いいえ／未確認", "はい"], horizontal=True) == "はい"

    st.subheader("2. サービスと用途")
    service = st.selectbox("利用する生成AIサービス", ["Microsoft Copilot", "GitHub Copilot Business / Enterprise", "上記以外・未確認"], help="推奨リスト外のサービスは、ITPM部に相談してください。")
    public_code_filter = st.radio("GitHub CopilotのSuggestions matching public codeをブロックしていますか？", ["いいえ／未確認", "はい"], horizontal=True) == "はい"
    customer_rules = st.radio("顧客先・顧客向けの利用ですか？ 顧客のルールを確認しましたか？", ["該当しない", "未確認", "確認済み"], horizontal=True)
    use_case = st.selectbox("主な使い方", ["翻訳・要約・公開情報の整理など補助的な利用", "判断・意思決定に直接影響する", "AIエージェントが自律的に実行・操作する", "社外へ提供・公開する"])
    dangerous_action = st.radio("削除・外部送信・権限変更などの危険な操作がありますか？", ["いいえ", "はい"], horizontal=True) == "はい"
    copyright_use = st.selectbox("生成物の種類・利用先", ["社内での補助利用", "プログラムコード", "記事・画像・音声等を社外利用", "その他／未確認"])
    submitted = st.form_submit_button("リスクをチェック", type="primary", use_container_width=True)

if submitted:
    st.session_state["risk_result"] = evaluate({
        "personal_data": personal, "restricted_data": restricted, "customer_data": customer,
        "customer_permission": customer_permission, "enterprise_protection": enterprise,
        "closed_environment": closed, "division_head_approval": division_approval,
        "service": service, "public_code_filter": public_code_filter, "customer_rules": customer_rules,
        "use_case": use_case, "dangerous_action": dangerous_action, "copyright_use": copyright_use,
    })

result = st.session_state.get("risk_result")
if result:
    level, title, summary, blockers, actions, notes = result
    st.divider()
    getattr(st, level)(f"### {title}\n\n{summary}")
    for heading, items in [("利用を止めて確認", blockers), ("必要な確認・対応", actions), ("補足", notes)]:
        if items:
            st.markdown(f"**{heading}**")
            for item in items:
                st.markdown(f"- {item}")
    st.caption("判定根拠：生成AI利用ガイドライン v1.5（2026年5月1日版）第5章・付録のリスク判定フローチャート")

st.divider()
st.caption("社内PoC · 入力内容は保存されません · ガイドライン改定時は判定ルールも見直してください")
