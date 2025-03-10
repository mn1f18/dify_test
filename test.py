from translator import DifyTranslator

def main():
    # 创建翻译器实例
    translator = DifyTranslator()
    
    # 测试文件路径 (请确保这个文件存在)
    file_path = "test.txt"
    user_id = "test_user_001"
    
    try:
        # 执行翻译
        print("开始翻译...")
        result = translator.translate(file_path, user_id, target_language="Chinese")
        
        # 打印翻译结果
        print("翻译完成!")
        print("翻译结果:", result)
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 