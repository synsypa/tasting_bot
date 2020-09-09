from logzero import logger
import os

import time
import torch
import transformers
from torch.utils.data import DataLoader
from transformers import (AutoConfig, AutoTokenizer, AutoModelForCausalLM,
                         AdamW, get_linear_schedule_with_warmup)
from transformers import WEIGHTS_NAME, CONFIG_NAME
import tasting_dataset as taste

# Load Pretrained GPT2
model_type = 'gpt2'
config = AutoConfig.from_pretrained(model_type)
tokenizer = AutoTokenizer.from_pretrained(model_type)
model = AutoModelForCausalLM.from_pretrained(model_type, config=config)

# Add Special Context Delimiter Tokens
context_tokens = ['<soc>', '<eoc>']
n_added_tokens = tokenizer.add_tokens(context_tokens, special_tokens=True)
model.resize_token_embeddings(len(tokenizer))
logger.info(f"{n_added_tokens} new tokens added")


if __name__ == "__main__":
    # Training Parameters
    BATCH_SIZE = 5
    EPOCHS = 3
    LEARNING_RATE = 0.00002
    WARMUP_STEPS = 10000

    # Load Data
    training_path = 'processed_data/ws_merged_20200908.csv'

    dataset = taste.WineData(tokenizer=tokenizer, file_path=training_path)
    note_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Set Device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using {device}")

    # Initialize model and optimizer
    model = model.to(device)
    model.train()
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=WARMUP_STEPS, num_training_steps=-1
    )

    # Training Loop
    sum_loss = 0.0
    start_time = time.time()
    logger.info("Beginning Training...")
    for epoch in range(EPOCHS):
        epoch_loss = 0.0
        epoch_start = time.time()

        for idx, note in enumerate(note_loader):
            outputs = model(note.to(device), labels=note.to(device))

            optimizer.zero_grad()
            model.zero_grad()
            
            loss, logits = outputs[:2]                        
            loss.backward()
            epoch_loss = epoch_loss + loss.detach().data
                        
            optimizer.step()
            scheduler.step() 
                
            if idx % 100 == 99:
                logger.info(f"{time.time() - start_time :7.2f} s | "
                            f"Epoch: {epoch + 1}, Batches: {idx + 1 :4} | "
                            f"Loss: {epoch_loss / 100 :.5f}")
                epoch_loss = 0.0
        
        logger.info(f"Avg Training Batch Time: "
                    f"{(time.time() - epoch_start)/idx :7.2f} s")
    
    logger.info(f"Jobs Finished") 
            
    output_dir = 'model/output'
    output_model_file = os.path.join(output_dir, WEIGHTS_NAME)
    output_config_file = os.path.join(output_dir, CONFIG_NAME)

    torch.save(model.state_dict(), output_model_file)
    model.config.to_json_file(output_config_file)
    tokenizer.save_pretrained(output_dir)