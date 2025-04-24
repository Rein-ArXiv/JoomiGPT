import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# 1) device 설정: GPU가 있으면 0, 없으면 -1 (CPU)
device = 0 if torch.cuda.is_available() else -1
print(f"사용 중인 장치 인덱스: {device}  (-1: CPU,  ≥0: GPU 번호)")

# 2) 모델 및 토크나이저 로드
model_name = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if device >= 0 else torch.float32,
    low_cpu_mem_usage=True,
    device_map="auto" if device >= 0 else None
)
if device < 0:
    model.to("cpu")

# 3) 파이프라인 초기화
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    
)


# 프롬프트 형식 지정
def format_prompt(user_input):
    return f"USER: {user_input}\nASSISTANT:"

# 사용자 입력 처리 및 응답 생성
def generate_response(prompt, max_length=512):
    formatted_prompt = format_prompt(prompt)
    outputs = generator(
        formatted_prompt,
        max_length=max_length,
        truncation=True,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    
    # 응답에서 프롬프트 부분을 제거하고 ASSISTANT: 이후의 텍스트만 추출
    response = outputs[0]["generated_text"]
    assistant_response = response.split("ASSISTANT:")[-1].strip()
    return assistant_response

# 대화형 인터페이스
print("EXAONE 3.5 7.8B 모델과 대화를 시작합니다. 종료하려면 'exit'를 입력하세요.")
while True:
    user_input = input("\n질문: ")
    if user_input.lower() == 'exit':
        break
    
    response = generate_response(user_input)
    print(f"\n답변: {response}")