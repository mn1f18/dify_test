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
st.set_page_config(page_title="AI 文本工具", layout="wide")

# DIFY API配置
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_CRAWLER_API_KEY = os.getenv("DIFY_CRAWLER_API_KEY")

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

async def crawl_website(url):
    """调用DIFY API进行网页爬取和总结"""
    headers = {
        "Authorization": f"Bearer {DIFY_CRAWLER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "inputs": {
            "input_url": url
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
                result_text = None
                async for line in response.content:
                    if line:
                        try:
                            text = line.decode('utf-8')
                            if text.startswith("data: "):
                                data = json.loads(text[6:])
                                if data.get("event") == "workflow_finished":
                                    outputs = data.get("data", {}).get("outputs", {})
                                    result_text = outputs.get("text")
                                    break
                        except json.JSONDecodeError:
                            continue
        
        if result_text:
            return result_text
        
        st.error("未能获取网页内容")
        return None
            
    except Exception as e:
        st.error(f"爬取出错: {str(e)}")
        return None

async def main():
    st.title("🛠️ AI 文本工具集")
    
    # 创建选项卡
    tab1, tab2 = st.tabs(["📝 文本翻译", "🌐 网页爬取"])
    
    with tab1:
        st.header("专业文本翻译工具")
        
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
        if st.button("翻译", key="translate_btn"):
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

    with tab2:
        st.header("网页内容爬取工具")
        
        st.markdown("""
        ### 使用说明
        1. 输入要爬取的网页URL
        2. 点击"开始爬取"按钮
        3. 等待系统返回网页内容摘要
        
        > 注意：
        > - 请确保输入的URL是完整的（包含 http:// 或 https://）
        > - 某些网站可能会限制爬取
        > - 处理时间取决于网页内容的大小
        """)
        
        # URL输入
        url = st.text_input("输入网页URL", placeholder="https://example.com")
        
        # 爬取按钮
        if st.button("开始爬取", key="crawl_btn"):
            if url:
                with st.spinner("正在爬取网页内容..."):
                    result = await crawl_website(url)
                    if result:
                        st.success("爬取成功！")
                        st.markdown("### 网页内容摘要")
                        st.markdown(result)
            else:
                st.warning("请输入要爬取的网页URL")

if __name__ == "__main__":
    asyncio.run(main()) 