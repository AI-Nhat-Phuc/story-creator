# GPT Integration Guide - Story Creator

## Tổng Quan

Story Creator tích hợp OpenAI GPT-4o-mini để:
1. 🤖 **Character Simulation**: AI quyết định hành động nhân vật
2. 🌍 **World Analysis**: Phân tích mô tả thế giới, tạo entities/locations
3. 📖 **Story Enhancement**: Tạo mô tả câu chuyện phong phú
4. 🌐 **Translation**: Dịch English → Vietnamese (simulation mode)

## Environment Setup

### 1. Lấy API Key

1. Truy cập [OpenAI Platform](https://platform.openai.com/)
2. Đăng nhập/Đăng ký account
3. Vào **API Keys** section
4. Click **"Create new secret key"**
5. Copy key (chỉ hiển thị 1 lần!)

### 2. Tạo File `.env`

```bash
# Tạo file .env trong thư mục root
# c:\Users\PhucPN\OneDrive\Desktop\AI\Ideas\story-creator\.env
```

**Nội dung**:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ Lưu ý**:
- ❌ KHÔNG commit file `.env` lên Git
- ✅ File `.env` đã được thêm vào `.gitignore`
- ✅ API key bắt đầu bằng `sk-proj-` hoặc `sk-`

### 3. Cài Đặt Dependencies

```bash
pip install openai>=1.0.0
pip install python-dotenv>=0.19.0
```

### 4. Test API Key

```bash
# Kiểm tra API key có hoạt động
python test_api_key.py
```

**Expected Output**:
```
✅ API Key hợp lệ
📊 Model: gpt-4o-mini
💰 Quota available
```

## GPT Client Architecture

### File Structure
```
ai/
  ├── __init__.py
  ├── gpt_client.py           # Low-level GPT API wrapper
  ├── prompts.py              # Prompt templates
  └── simulation.py           # Simulation logic

services/
  └── gpt_service.py          # High-level service layer (RECOMMENDED)
```

## GPT Client (`ai/gpt_client.py`)

### Initialization

```python
from ai.gpt_client import GPTIntegration

# Auto-load API key từ .env
gpt = GPTIntegration()

# Check availability
if gpt.is_available():
    print("✅ GPT ready")
else:
    print("❌ GPT not available")
```

**What Happens**:
1. Load `OPENAI_API_KEY` từ `.env` (via `python-dotenv`)
2. Initialize OpenAI client
3. Set model = `gpt-4o-mini`
4. Validate API key

### Model Configuration

**Current Model**: `gpt-4o-mini`

**Why not gpt-4-turbo or gpt-5-nano**:
- ❌ `gpt-5-nano`: Có reasoning tokens issue
- ✅ `gpt-4o-mini`: Stable, fast, cost-effective
- ⚡ Response time: ~2-5 seconds
- 💰 Cost: $0.00015/1K input tokens, $0.0006/1K output tokens

**API Parameters**:
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    max_completion_tokens=1000,  # ❗ NOT max_tokens
    # temperature=1.0,            # ❗ NOT supported
)
```

### Core Methods

#### 1. Character Decision Making

```python
decision = gpt.generate_character_decision(
    character_name="Arthur",
    situation="You see a dragon approaching the village",
    story_context="Medieval fantasy world, you are a knight",
    character_traits="Brave, loyal, skilled with sword"
)

print(decision)
# Output: "I draw my sword and stand between the dragon and the village"
```

**Prompt Template** (trong `ai/prompts.py`):
```python
CHARACTER_DECISION_PROMPT = """
You are {character_name} with these traits: {character_traits}.

Current situation: {situation}

Story context: {story_context}

What do you do? Respond in first person, in one clear sentence.
"""
```

#### 2. Translation (Vietnamese)

```python
vietnamese_text = gpt.translate_eng_to_vn(
    "The hero bravely faces the dragon"
)

print(vietnamese_text)
# Output: "Người anh hùng dũng cảm đối mặt với con rồng"
```

**Use Case**: Simulation mode - dịch GPT responses sang tiếng Việt

#### 3. World Description Analysis (Raw)

```python
analysis = gpt.generate_world_description(
    world_type="fantasy",
    description="A kingdom with magic and dragons"
)

# Returns JSON string với entities và locations
```

**⚠️ Recommended**: Dùng `GPTService` thay vì gọi trực tiếp

## GPT Service (`services/gpt_service.py`)

### Why Use Service Layer?

✅ **Async execution** với threading
✅ **Callback pattern** cho UI updates
✅ **Error handling** tập trung
✅ **Business logic separation** từ GPT client

### Initialization

```python
from services import GPTService
from ai.gpt_client import GPTIntegration

gpt = GPTIntegration()
gpt_service = GPTService(gpt)

# Check availability
if gpt_service.is_available():
    print("✅ Service ready")
```

### World Description Generation

```python
def on_success(result):
    """Callback khi GPT hoàn thành"""
    print("✅ Entities:", result['entities'])
    print("✅ Locations:", result['locations'])

def on_error(error_message):
    """Callback khi có lỗi"""
    print("❌ Error:", error_message)

# Gọi async
gpt_service.generate_world_description(
    world_type="fantasy",
    callback_success=on_success,
    callback_error=on_error
)

# Code tiếp tục chạy, không block
print("⏳ GPT đang xử lý...")
```

**Result Format**:
```json
{
  "entities": [
    {
      "name": "King Arthur",
      "entity_type": "ruler",
      "description": "Noble king of Camelot",
      "attributes": {
        "Strength": 7,
        "Intelligence": 8,
        "Charisma": 9
      }
    }
  ],
  "locations": [
    {
      "name": "Camelot Castle",
      "description": "Majestic fortress",
      "coordinates": {"x": 0, "y": 0}
    }
  ]
}
```

### Story Description Generation

```python
gpt_service.generate_story_description(
    genre="adventure",
    world_context="Fantasy world with magic",
    character_names=["Arthur", "Merlin"],
    callback_success=on_success,
    callback_error=on_error
)
```

### Analyze World Entities (Web Interface)

```python
gpt_service.analyze_world_entities(
    world_description="A medieval kingdom with dragons and magic",
    world_type="fantasy",
    callback_success=on_success,
    callback_error=on_error
)
```

**Async Workflow**:
1. Client tạo unique `task_id`
2. Call service với callbacks lưu vào session storage
3. Service chạy GPT trong background thread
4. Client poll results từ session storage

## Web Interface Integration

### Task-Based GPT Calls

**Backend** (`interfaces/web_interface.py`):
```python
@self.app.route('/api/gpt/analyze', methods=['POST'])
def analyze_gpt():
    data = request.json
    task_id = str(uuid.uuid4())

    def on_success(result):
        self.gpt_results[task_id] = {
            'status': 'completed',
            'result': result
        }

    def on_error(error):
        self.gpt_results[task_id] = {
            'status': 'error',
            'error': str(error)
        }

    # Initialize pending status
    self.gpt_results[task_id] = {'status': 'pending'}

    # Start async GPT call
    self.gpt_service.analyze_world_entities(
        world_description=data['world_description'],
        world_type=data['world_type'],
        callback_success=on_success,
        callback_error=on_error
    )

    return jsonify({'task_id': task_id})

@self.app.route('/api/gpt/results/<task_id>')
def get_gpt_results(task_id):
    result = self.gpt_results.get(task_id, {'status': 'not_found'})
    return jsonify(result)
```

**Frontend** (`static/js/app.js`):
```javascript
async function analyzeWorldWithGPT() {
    const description = document.getElementById('worldDescription').value;
    const worldType = document.getElementById('worldType').value;

    // Start analysis
    const response = await fetch('/api/gpt/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            world_description: description,
            world_type: worldType
        })
    });

    const { task_id } = await response.json();

    // Poll for results
    pollGPTResults(task_id);
}

function pollGPTResults(taskId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/gpt/results/${taskId}`);
        const data = await response.json();

        if (data.status === 'completed') {
            clearInterval(interval);
            // Use data.result
            console.log('✅ GPT completed:', data.result);
        } else if (data.status === 'error') {
            clearInterval(interval);
            console.error('❌ GPT error:', data.error);
        }
        // else: still pending, continue polling
    }, 500); // Poll every 500ms
}
```

## Simulation Mode Integration

### Character Simulation Flow

```python
from interfaces import SimulationInterface

sim = SimulationInterface(storage_type="nosql")
sim.run()
```

**User Flow**:
1. User chọn world
2. User chọn character để control
3. Tại mỗi time_index:
   - Đọc story content
   - GPT tạo situation từ story
   - User nhận 3 choices: A (action), B (opposite), C (abandon)
   - User chọn → Lưu decision
4. Các nhân vật khác → GPT tự động chọn
5. Tiến đến time_index tiếp theo

### GPT Decision Making

```python
# Trong simulation_interface.py
decision = self.gpt.generate_character_decision(
    character_name=character.name,
    situation=current_situation,
    story_context=world.description,
    character_traits=f"{character.entity_type}, {character.description}"
)

# Translation (nếu bật)
if enable_translation:
    decision_vn = self.gpt.translate_eng_to_vn(decision)
```

## Prompt Engineering

### Best Practices

1. **Be Specific**: Cung cấp đủ context
2. **Format Clear**: Yêu cầu JSON format khi cần
3. **Limit Scope**: Giới hạn response length
4. **Examples**: Cho examples trong prompt

### Prompt Templates (`ai/prompts.py`)

```python
WORLD_ANALYSIS_PROMPT = """
Analyze this {world_type} world description and extract entities and locations.

Description: {description}

Return a JSON object with:
{{
  "entities": [
    {{
      "name": "character name",
      "entity_type": "warrior/mage/ruler/merchant/etc",
      "description": "brief description",
      "attributes": {{"Strength": 0-10, "Intelligence": 0-10, "Charisma": 0-10}}
    }}
  ],
  "locations": [
    {{
      "name": "location name",
      "description": "brief description"
    }}
  ]
}}

Extract 3-5 entities and 2-4 locations.
"""
```

## Error Handling

### Common Errors

#### 1. API Key Invalid
```python
try:
    gpt = GPTIntegration()
except ValueError as e:
    print(f"❌ API Key error: {e}")
    # Hướng dẫn user check .env file
```

#### 2. Rate Limit
```python
try:
    response = gpt.generate_character_decision(...)
except Exception as e:
    if "rate_limit" in str(e).lower():
        print("⏳ Rate limit reached, please wait")
    else:
        print(f"❌ Error: {e}")
```

#### 3. Network Error
```python
try:
    response = gpt.generate_world_description(...)
except Exception as e:
    print("🌐 Network error, check connection")
```

### Graceful Degradation

```python
# Check GPT availability trước khi sử dụng
if self.has_gpt:
    # Use GPT features
    decision = self.gpt.generate_character_decision(...)
else:
    # Fallback: Random choice hoặc disable feature
    decision = random.choice(["Option A", "Option B"])
    print("⚠️ GPT not available, using fallback")
```

## Cost Management

### Token Usage

**Estimate**:
- World analysis: ~500 input + ~800 output = ~1300 tokens
- Character decision: ~200 input + ~100 output = ~300 tokens
- Translation: ~100 input + ~120 output = ~220 tokens

**Cost per Operation** (gpt-4o-mini):
- World analysis: $0.00075 + $0.00048 = **$0.00123**
- Character decision: $0.00003 + $0.00006 = **$0.00009**
- Translation: $0.000015 + $0.000072 = **$0.000087**

**Monthly Budget Example**:
- 1000 world analyses: $1.23
- 10,000 character decisions: $0.90
- 5,000 translations: $0.44
- **Total**: ~$2.60/month

### Optimization Tips

1. ✅ **Cache results**: Lưu GPT responses vào database
2. ✅ **Batch requests**: Gộp multiple operations nếu được
3. ✅ **Limit max_tokens**: Set reasonable limits
4. ✅ **Use callbacks**: Avoid retry loops

## Testing

### Unit Tests

```python
# test_gpt.py
import unittest
from ai.gpt_client import GPTIntegration

class TestGPT(unittest.TestCase):
    def setUp(self):
        self.gpt = GPTIntegration()

    def test_availability(self):
        self.assertTrue(self.gpt.is_available())

    def test_character_decision(self):
        decision = self.gpt.generate_character_decision(
            character_name="Test Hero",
            situation="Test situation",
            story_context="Test context",
            character_traits="Brave"
        )
        self.assertIsInstance(decision, str)
        self.assertGreater(len(decision), 0)
```

### Integration Tests

```bash
# Test với real API
python test_api_key.py

# Test simulation mode
python demo_gpt_simulation.py
```

## Security Best Practices

1. 🔒 **Never commit API keys**: Use `.env` file
2. 🔒 **Rotate keys regularly**: Generate new keys every 90 days
3. 🔒 **Monitor usage**: Check OpenAI dashboard cho unusual activity
4. 🔒 **Limit permissions**: Use restricted API keys nếu có option
5. 🔒 **Log cautiously**: Đừng log API keys hoặc sensitive prompts

## Troubleshooting

### GPT Not Working

```bash
# 1. Check .env file exists
dir .env

# 2. Check API key format
type .env

# 3. Test API key
python test_api_key.py

# 4. Check internet connection
ping api.openai.com

# 5. Check Python version
python --version  # Should be 3.7+

# 6. Reinstall packages
pip install --upgrade openai python-dotenv
```

### Common Issues

| Issue | Solution |
|-------|----------|
| `No API key found` | Tạo file `.env` với `OPENAI_API_KEY=...` |
| `Rate limit exceeded` | Đợi 1 phút hoặc upgrade plan |
| `Invalid request` | Check prompt format, max_tokens |
| `Timeout` | Increase timeout hoặc retry |

## Next Steps

1. 📖 Đọc [OpenAI API Documentation](https://platform.openai.com/docs)
2. 🧪 Test với `test_api_key.py` và `demo_gpt_simulation.py`
3. 🎮 Thử Simulation Mode để hiểu GPT workflow
4. 🔧 Customize prompts trong `ai/prompts.py`
