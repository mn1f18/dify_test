import streamlit as st
import json
from dotenv import load_dotenv
import os
from config import DIFY_API_BASE_URL
import asyncio
import aiohttp

# 加载环境变量
load_dotenv()

# 设置页面标题
st.set_page_config(page_title="文本翻译工具", layout="wide")

# DIFY API配置
DIFY_API_KEY = os.getenv("DIFY_API_KEY")

async def translate_text(text, target_language="Chinese"):
    """调用DIFY API进行翻译"""
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "inputs": {
            "input_text": text
        },
        "response_mode": "streaming",
        "user": "streamlit_user"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{DIFY_API_BASE_URL}/workflows/run",
                headers=headers,
                json=data
            ) as response:
                # 处理流式响应
                translated_text = None
                async for line in response.content:
                    if line:
                        try:
                            # 解码并移除 "data: " 前缀
                            text = line.decode('utf-8')
                            if text.startswith("data: "):
                                data = json.loads(text[6:])
                                
                                # 检查事件类型
                                if data.get("event") == "workflow_finished":
                                    # 获取最终翻译结果
                                    outputs = data.get("data", {}).get("outputs", {})
                                    translated_text = outputs.get("second_translation")
                                    break
                        except json.JSONDecodeError:
                            continue
        
        if translated_text:
            return translated_text
        
        st.error("未能获取翻译结果")
        return None
            
    except Exception as e:
        st.error(f"翻译出错: {str(e)}")
        return None

async def main():
    # 页面标题
    st.title("📝 专业文本翻译工具")
    
    # 添加简单说明
    st.markdown("""
    ### 三步翻译流程
    1. 识别专业术语
    2. 直接翻译并分析问题
    3. 基于含义的优化翻译
    
    ### 使用说明
    1. 每段建议不超过500字
    2. 可以同时输入多段文本（用 --- 分隔）
    3. 点击翻译后会依次翻译每段内容
    
    > 注意：
    > - 使用 "---" (三个横杠)分隔不同段落
    > - 如果文本较长，建议分段翻译
    > - 如果遇到超时，请稍后重试
    """)
    
    # 文本输入区
    input_text = st.text_area("输入文本（使用 --- 分隔不同段落）", height=200)
    
    # 显示字数统计
    st.caption(f"当前输入总字数：{len(input_text)}")
    
    # 翻译按钮
    if st.button("翻译"):
        if input_text:
            segments = [seg.strip() for seg in input_text.split('---') if seg.strip()]
            
            if not segments:
                st.warning("请输入要翻译的文本")
                return
            
            # 显示总体进度
            st.info(f"总共需要翻译 {len(segments)} 段文本")
            
            # 创建进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 存储所有翻译结果
            all_results = []
            
            # 依次翻译每段
            for i, segment in enumerate(segments):
                status_text.text(f'正在翻译第 {i+1}/{len(segments)} 段...')
                translated_text = await translate_text(segment)
                if translated_text:
                    all_results.append({
                        'original': segment,
                        'translated': translated_text
                    })
                progress_bar.progress((i + 1) / len(segments))
                if i < len(segments) - 1:
                    status_text.text("短暂暂停，准备翻译下一段...")
                    await asyncio.sleep(5)
            
            # 显示所有翻译结果
            if all_results:
                st.success(f"完成翻译！共 {len(all_results)} 段")
                
                for i, result in enumerate(all_results, 1):
                    st.markdown(f"### 第 {i} 段")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_area("原文", result['original'], height=150)
                    with col2:
                        st.text_area("译文", result['translated'], height=150)
                    st.markdown("---")
        else:
            st.warning("请输入要翻译的文本")

if __name__ == "__main__":
    asyncio.run(main()) 