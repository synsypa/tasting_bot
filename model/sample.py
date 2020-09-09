
import logging
import os
import pickle

import random
import torch
import torch.nn as nn
import transformers
from torch.utils.data import DataLoader, Dataset, RandomSampler, SequentialSampler
from transformers import (AutoConfig, AutoTokenizer, AutoModelWithLMHead, TextDataset, DataCollatorForLanguageModeling, AdamW, get_linear_schedule_with_warmup,
GPT2LMHeadModel, GPT2Tokenizer,
    Trainer)
from transformers import WEIGHTS_NAME, CONFIG_NAME
import pandas as pd

#FILE_PATH = "travel.csv"

FILE_PATH = "data/train_flextape_lang.csv"
logger = logging.getLogger(__name__)

from langdetect import detect
def text2language(text):
    try:
        language = detect(text)
        return language
    except Exception:
        return 'Unknown'

class TravelData(Dataset):
    """
    This will be superseded by a framework-agnostic approach
    soon.
    """

    def __init__(self, tokenizer, file_path: str, block_size: int=512, overwrite_cache=False):
        assert os.path.isfile(file_path)
        # Here, we do not cache the features, operating under the assumption
        # that we will soon use fast multithreaded tokenizers from the
        # `tokenizers` repo everywhere =)
        print("Creating features from dataset file at %s", file_path)
        directory, filename = os.path.split(file_path)
        block_size = 512 - (tokenizer.max_len - tokenizer.max_len_single_sentence)
        cached_features_file = os.path.join(
            directory, "gpt2" + "_" + str(block_size) + "_" + filename)


        if os.path.exists(cached_features_file) and not overwrite_cache:
            print(
                f"Loading features from your cached file {cached_features_file}"
            )
            with open(cached_features_file, "rb") as cache:
                self.examples = pickle.load(cache)
                print("Loaded examples from cache")
        else:
            self.travel = pd.read_csv(file_path)
            self.travel = self.travel.query("lang=='en'")

            lines = list()
            for i, df in self.travel.iterrows():
                if not df[['body', 'call_to_action', 'message']].isnull().any():
                    s = "<soc> " + df.call_to_action + ' ' + df.body +' <eoc> ' + df.message + '<|endoftext|>'
                    lines.append(s)

            text = ' '.join(lines)
            tokenized_text = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(text))
            self.examples = []
            for i in range(0, len(tokenized_text) - block_size + 1, block_size):
                self.examples.append(
                    tokenizer.build_inputs_with_special_tokens(
                        tokenized_text[i : i + block_size]
                    )
                )

            print(f"Saving features into cached file {cached_features_file}")
            with open(cached_features_file, "wb") as cache:
                pickle.dump(self.examples, cache, protocol=pickle.HIGHEST_PROTOCOL)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i) -> torch.Tensor:
        return torch.tensor(self.examples[i], dtype=torch.long)

if __name__ == "__main__":
    model_type = 'gpt2'
    config = AutoConfig.from_pretrained(model_type)
    tokenizer = AutoTokenizer.from_pretrained(model_type)
    model = AutoModelWithLMHead.from_pretrained(model_type, config=config)

    new_tokens = ['<soc>', '<eoc>']
    num_added_toks = tokenizer.add_tokens(new_tokens, special_tokens=True)
    print('We have added', num_added_toks, 'tokens')
    model.resize_token_embeddings(len(tokenizer))

    BATCH_SIZE = 5
    EPOCHS = 3
    LEARNING_RATE = 0.00002
    WARMUP_STEPS = 10000

    dataset = TravelData(tokenizer= tokenizer, file_path= FILE_PATH )
    script_loader = DataLoader(dataset,batch_size=BATCH_SIZE,shuffle=True)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using {device}")

    model = model.to(device)
    model.train()
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=WARMUP_STEPS, num_training_steps=-1)
    sum_loss = 0.0

    for epoch in range(EPOCHS):
        print(f"EPOCH {epoch} started" + '=' * 30)
        for idx,script in enumerate(script_loader):
            optimizer.zero_grad()
            model.zero_grad()

            outputs = model(script.to(device), labels=script.to(device))
            
            loss, logits = outputs[:2]                        
            loss.backward()
            sum_loss = sum_loss + loss.detach().data
                        
            optimizer.step()
            scheduler.step() 
                
            if idx % 100 == 0:
                print(f"{idx}:sum loss {sum_loss}")
                sum_loss = 0
            
    output_dir = 'output'
    output_model_file = os.path.join(output_dir, WEIGHTS_NAME)
    output_config_file = os.path.join(output_dir, CONFIG_NAME)

    torch.save(model.state_dict(), output_model_file)
    model.config.to_json_file(output_config_file)
    tokenizer.save_pretrained(output_dir)


    model = GPT2LMHeadModel.from_pretrained(output_dir)
    tokenizer = GPT2Tokenizer.from_pretrained(output_dir)
    print("starting to do an example")
    input_ids = tokenizer.encode('<soc> BOOK_TRAVEL Alex Airline gets your 22% off!<eoc>', return_tensors='pt')
    model.eval()


    sample_outputs = model.generate(
                            input_ids= input_ids,
                            max_length = 100,
                            do_sample=True,
                            top_p=0.85
                        )

    print("Output:\n" + 100 * '-')
    for i, sample_output in enumerate(sample_outputs):
        print("{}: {}".format(i, tokenizer.decode(sample_output, skip_special_tokens=True)))
