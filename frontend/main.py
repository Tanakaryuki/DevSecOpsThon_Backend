import threading
import requests
import streamlit as st
import time

# タイトルを設定
st.title("teamC")

# REST APIのエンドポイントを設定
streaming_endpoint = 'https://localhost:49510/lmm/streaming'
list_endpoint = 'https://localhost:49510/file/file_paths'
upload_endpoint = 'https://localhost:49510/file'
vram_endpoint = 'https://localhost:49510/gpudata'

# アクセストークンの保持
if "access_token" not in st.session_state:
    st.session_state.access_token = None
    
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ログインフォームの入力フィールド
if not st.session_state.logged_in:
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")

# ログインボタン
if not st.session_state.logged_in:
    if st.button("ログイン"):
        # 入力された情報を使用してトークンを取得
        form_data = {"username": username, "password": password}
        try:
            response = requests.post('https://localhost:49510/user/token', data=form_data,verify=False)
            response.raise_for_status()
            access_token = response.json()["access_token"]
            st.session_state.access_token = access_token
            st.session_state.logged_in = True
            st.success("ログインに成功しました。")
            st.experimental_rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"ログインに失敗しました: {e}")

def get_answer(question: str):
    with requests.get(f"{streaming_endpoint}?question={question}", stream=True,verify=False) as response:
        response.raise_for_status()
        message = ""
        for line in response.iter_lines():
            if line:
                yield line.decode("utf-8")
                message += line.decode("utf-8")
    st.session_state.messages.append({"role": "assistant", "content": message})
    
def get_list():
    try:
        response = requests.get(list_endpoint,verify=False)
        response.raise_for_status()
        return response.json()["file_paths"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        
def get_data():
    response = requests.get(vram_endpoint,verify=False)
    response.raise_for_status()
    data = response.json()
    return int(data["gpu_util"].split("%")[0])

class Worker(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
    
    def run(self):
        while True:
            self.data.append(1)
            time.sleep(1)

if "worker" not in st.session_state:
    st.session_state.worker = Worker()
    st.session_state.worker.start()

if st.session_state.access_token:
    uploaded_file = st.sidebar.file_uploader("ファイルをアップロードしてください", key="file_uploader")
    
# アップロードされたファイルを送信するボタンを追加
if st.session_state.access_token:
    if st.sidebar.button("送信"):
        if uploaded_file is not None:
            try:
                # ファイルをアップロード
                files = {'file': uploaded_file}
                response = requests.post(upload_endpoint, files=files,verify=False)
                response.raise_for_status()
                st.success("ファイルが正常にアップロードされました。")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
        else:
            st.warning("アップロードするファイルを選択してください。")

# ファイルパスを取得して表示
if st.session_state.access_token:
    file_paths = get_list()
    if file_paths:
        st.sidebar.write("## ファイル一覧")
        for file_path in file_paths:
            st.sidebar.write(file_path)
    else:
        st.write("ファイルが見つかりませんでした。")

# セッション内のメッセージが指定されていない場合のデフォルト値
if st.session_state.access_token:
    if "messages" not in st.session_state:
        st.session_state.messages = []

# 以前のメッセージを表示
if st.session_state.access_token:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ユーザーからの新しい入力を取得
if st.session_state.access_token:
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write(get_answer(prompt))

if st.session_state.access_token:
    holder = st.sidebar.empty()
    for _ in range(3):
        st.empty()
    while True:
        holder.line_chart(st.session_state.worker.data[-10:])
        time.sleep(1)