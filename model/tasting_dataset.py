from logzero import logger
import os

import torch
from torch.utils.data import Dataset
from transformers import (AutoConfig, AutoTokenizer, TextDataset, GPT2Tokenizer)
from transformers import WEIGHTS_NAME, CONFIG_NAME

import pandas as pd

def create_context(producer, name, vintage: int=None, score: int=90, price: int=30):
    '''
    This function creates the context string for each sample and prediction:
    `producer`: Producer Name
    `name`: Wine Name
    `vintage`: Wine Vintage, coded to 'NV' if none
    `score`: desired score, defaults to 90
    `price`: wine price in dollars, defaults to 30 dollars
    '''
    if vintage is None:
        vintage = 'NV'
    return f"<soc> {producer} {vintage} {name}, {score} points, ${price} <eoc>"

# Create Dataset class for tasting notes
class WineData(Dataset):
    
    def __init__(self, tokenizer, file_path: str, block_size: int=512):
        assert os.path.isfile(file_path)

        logger.info(f"Creating features from {file_path}...")
        block_size = (
            block_size - (
                tokenizer.model_max_length - tokenizer.max_len_single_sentence
            )
        )

        self.notes = pd.read_csv(file_path)

        # Create Blocks (GPT-2 Takes input as continuous blocks rather than
        # individual strings so the full text string must be constructed here
        # and broken into blocks for __get_item__ to retrieve
        lines = []
        for i, wine in self.notes.iterrows():
            context_str = create_context(wine['producer'],
                                        wine['name'],
                                        wine['vintage'],
                                        wine['score'],
                                        wine['price_usd'])
            full_str = f"{context_str} {wine['tasting_note']} <|endoftext|>"
            lines.append(full_str)
        all_text = ' '.join(lines)

        logger.info(f"Tokenizing text...")
        tokenized_text = tokenizer.convert_tokens_to_ids(
            tokenizer.tokenize(all_text)
        )

        logger.info(f"Creating blocks...")
        self.blocks = []
        # Create Blocks of size at most block_size from full text
        for i in range(0, len(tokenized_text) - block_size + 1, block_size):
            self.blocks.append(
                tokenizer.build_inputs_with_special_tokens(
                    tokenized_text[i : i + block_size]
                )
            )
        
    def __len__(self):
        return len(self.blocks)
        
    def __getitem__(self, idx):
        return torch.tensor(self.blocks[idx], dtype=torch.long)

if __name__ == '__main__':
    model_type = 'gpt2'
    config = AutoConfig.from_pretrained(model_type)
    tokenizer = AutoTokenizer.from_pretrained(model_type)
    file_path = 'processed_data/ws_merged_20200908.csv'

    test_dataset = WineData(tokenizer=tokenizer, file_path=file_path)

    ex = test_dataset[888]

    print(len(test_dataset))
    print(tokenizer.decode(ex))