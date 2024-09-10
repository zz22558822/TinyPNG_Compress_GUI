import tinify
import os
import sys

# API Key
tinify.key = "這邊輸入你的 Tinify API Key"

# 獲取執行文件所在的資料夾路徑
executable_dir = os.path.dirname(sys.executable)
# 獲取執行文件所在的資料夾路徑 (py用)
py_dir = os.path.dirname(os.path.realpath(__file__))

def GetOutput(input_folder, output_folder):

    # 檢查 input 資料夾是否存在，如果不存在則創建
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"input 資料夾不存在，已創建: {input_folder}")
        return  # 創建後直接結束，等待用戶將圖片放入資料夾


    # 檢查output 資料夾是否存在，如果不存在則創建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 獲取 input 資料夾中所有的文件
    files = os.listdir(input_folder)

    # 檢查 input 資料夾是否有圖片
    if not files:
        print(f"input 資料夾 {input_folder} 中沒有檔案。")
        return

    # 循環處理每個文件
    for file in files:
        # 拼接輸入文件的完整路徑
        input_file_path = os.path.join(input_folder, file)

        # 檢查文件是否為圖片
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.apng')):
            # 獲取輸出文件的完整路徑
            output_file_path = os.path.join(output_folder, file)

            try:
                # 壓縮圖片並保存到output 資料夾
                source = tinify.from_file(input_file_path)
                source.to_file(output_file_path)

                print(f"壓縮完成: {file}，已儲存到 {output_file_path}")
            except tinify.Error as e:
                # 錯誤處理
                print(f"壓縮失敗: {file}，錯誤訊息: {e}")

# 使用示例
input_folder = os.path.join(py_dir, "input")
output_folder = os.path.join(py_dir, "output")
GetOutput(input_folder, output_folder)

print()
os.system('pause')
