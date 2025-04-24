from transformers import AutoTokenizer, AutoModelForCausalLM

# 토크나이저 다운로드
tokenizer = AutoTokenizer.from_pretrained("LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct")

# 모델 다운로드
model = AutoModelForCausalLM.from_pretrained("LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct")