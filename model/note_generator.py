from logzero import logger
import os

import time
import torch
import torch.nn as nn
import transformers
from torch.utils.data import RandomSampler, SequentialSampler
from transformers import GPT2LMHeadModel, GPT2Tokenizer

import tasting_dataset as taste


model_path = 'model/output/'
#model = GPT2LMHeadModel.from_pretrained(model_path)
#tokenizer = GPT2Tokenizer.from_pretrained(model_path)

model = GPT2LMHeadModel.from_pretrained(model_path)
tokenizer = GPT2Tokenizer.from_pretrained(model_path)


# sample_wine = {
#     'producer': 'Duckhorn Vineyards',
#     'name': 'Sauvignon Blanc Napa Valley',
#     'vintage': 2016,
#     'score': 87,
#     'price': 30
# }

sample_wine = {
    'producer': 'Fake Vines',
    'name': 'Totally Gibberish',
    'vintage': None,
    'score': 20,
    'price': 100
}

input_str = taste.create_context(**sample_wine)

# Run sample
model.eval()
logger.info(f"Testing input string: {input_str}")
input_ids = tokenizer.encode(input_str, return_tensors='pt')

sample_notes = model.generate(
                    input_ids=input_ids,
                    max_length=100,
                    do_sample=True,
                    top_p=0.85,
                    num_return_sequences=5
                )

for i, note in enumerate(sample_notes):
    logger.info(f"Output {i}: " +
                tokenizer.decode(note, skip_special_tokens=True))