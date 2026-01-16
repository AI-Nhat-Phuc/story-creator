"""
Test OpenAI API Key
Script đơn giản để kiểm tra API key có hoạt động không
"""
import os
from dotenv import load_dotenv

# Load API key từ file .env
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

print("=" * 60)
print("  OPENAI API KEY TEST")
print("=" * 60)
print()

# Kiểm tra API key có tồn tại không
if not api_key:
    print("❌ Không tìm thấy OPENAI_API_KEY trong file .env")
    print("   Vui lòng thêm API key vào file .env")
    exit(1)

# Hiển thị một phần của API key (bảo mật)
print(f"✅ API key đã tìm thấy: {api_key[:20]}...{api_key[-4:]}")
print(f"   Độ dài: {len(api_key)} ký tự")
print()

# Test kết nối với OpenAI API
try:
    print("🔄 Đang test kết nối với OpenAI API...")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    # Gửi request đơn giản
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Dùng model rẻ hơn để test
        messages=[
            {"role": "user", "content": "Say 'API test successful' in Vietnamese"}
        ],
        max_tokens=50
    )

    result = response.choices[0].message.content

    print("✅ KẾT NỐI THÀNH CÔNG!")
    print(f"   Model: {response.model}")
    print(f"   Response: {result}")
    print()
    print("=" * 60)
    print("  🎉 API KEY HOẠT ĐỘNG BÌNH THƯỜNG!")
    print("=" * 60)

except Exception as e:
    print(f"❌ LỖI KHI KẾT NỐI:")
    print(f"   {str(e)}")
    print()
    print("Có thể do:")
    print("  - API key không hợp lệ")
    print("  - Hết quota/credit")
    print("  - Không có kết nối internet")
    print()
    exit(1)
