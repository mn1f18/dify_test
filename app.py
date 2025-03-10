import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 设置页面标题
st.set_page_config(page_title="文本翻译工具", layout="wide")

# DIFY API配置
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_API_BASE_URL = "https://api.dify.ai/v1"

def translate_text(text, target_language="Chinese"):
    """调用DIFY API进行翻译"""
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "inputs": {
            "input_text": text
        },
        "response_mode": "blocking",
        "user": "streamlit_user"
    }
    
    # 打印请求信息（调试用）
    st.write("发送的请求数据:", data)
    
    try:
        response = requests.post(
            f"{DIFY_API_BASE_URL}/workflows/run",
            headers=headers,
            json=data
        )
        
        # 打印响应信息（调试用）
        st.write("API响应状态码:", response.status_code)
        st.write("API响应内容:", response.text)
        
        if response.status_code == 200:
            result = response.json()
            # 打印完整的响应结构
            st.write("API响应结构:", result)
            
            # 获取翻译结果
            outputs = result.get('data', {}).get('outputs', {})
            if outputs:
                # 获取 second_translation 输出
                translated_text = outputs.get('second_translation')
                if translated_text:
                    return translated_text
                else:
                    st.error("未找到翻译结果")
                    return None
            else:
                st.error("未在响应中找到输出数据")
                return None
        else:
            st.error(f"API 响应错误: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"翻译出错: {str(e)}")
        st.error(f"详细错误信息: {response.text if 'response' in locals() else '无响应'}")
        return None

def main():
    # 页面标题
    st.title("📝 专业文本翻译工具")
    
    # 添加简单说明
    st.markdown("""
    ### 三步翻译流程
    1. 识别专业术语
    2. 直接翻译并分析问题
    3. 基于含义的优化翻译
    
    请输入要翻译的文本，然后点击翻译按钮。
    """)
    
    # 文本输入区
    input_text = st.text_area("输入文本", height=200)
    
    # 翻译按钮
    if st.button("翻译"):
        if input_text:
            with st.spinner('正在翻译...'):
                translated_text = translate_text(input_text)
                if translated_text:
                    st.success("翻译完成!")
                    st.text_area("翻译结果", translated_text, height=200)
        else:
            st.warning("请输入要翻译的文本")

if __name__ == "__main__":
    main() 