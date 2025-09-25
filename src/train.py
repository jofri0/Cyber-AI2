import os
from transformers import GPT2Config, GPT2LMHeadModel, GPT2TokenizerFast, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling

# Paths
DATA_PATH = "data/train.txt"
CONFIG_PATH = "configs/gpt2_config.json"
OUTPUT_DIR = "checkpoints"

# 1. Load config
print("Loading GPT2 config...")
config = GPT2Config.from_json_file(CONFIG_PATH)

# 2. Create tokenizer
print("Training tokenizer...")
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")  # Start from GPT-2 tokenizer
tokenizer.save_pretrained(OUTPUT_DIR)

# 3. Load dataset
def load_dataset(file_path, tokenizer, block_size=128):
    return TextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=block_size
    )

print("Loading dataset...")
train_dataset = load_dataset(DATA_PATH, tokenizer)

# 4. Create model
print("Creating GPT2 model from scratch...")
model = GPT2LMHeadModel(config=config)

# 5. Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# 6. Training args
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=1,       # start small
    per_device_train_batch_size=2,
    save_steps=500,
    save_total_limit=2,
    logging_dir='./logs',
    logging_steps=100,
)

# 7. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
)

# 8. Train
print("Starting training...")
trainer.train()

# 9. Save model
print("Saving model...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("Done! Model is saved in:", OUTPUT_DIR)
