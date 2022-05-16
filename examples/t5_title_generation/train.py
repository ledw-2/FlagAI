import sys

sys.path.append('/data/liuguang/Sailing')
from flagai.trainer import Trainer
from flagai.auto_model.auto_loader import AutoLoader
import os
import numpy as np
import torch
from torch.utils.data import Dataset
from flagai.trainer import Trainer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

trainer = Trainer(
    env_type="deepspeed+mpu",
    experiment_name="roberta_seq2seq",
    batch_size=1,
    gradient_accumulation_steps=1,
    lr=2e-4,
    weight_decay=1e-3,
    epochs=10,
    log_interval=10,
    eval_interval=10000,
    load_dir=None,
    pytorch_device=device,
    save_dir="checkpoints",
    save_epoch=1,
    num_checkpoints=1,
    master_ip='127.0.0.1',
    master_port=17750,
    num_nodes=1,
    num_gpus=2,
    hostfile=
    '/data/liuguang/test_Sailing/Sailing/examples/bert_title_generation/hostfile',
    deepspeed_config=
    '/data/liuguang/test_Sailing/Sailing/examples/bert_title_generation/deepspeed.json',
    training_script=__file__,
)
src_dir = '/data/auto_title/train.src'
tgt_dir = '/data/auto_title/train.tgt'
maxlen = 256
loader = AutoLoader("seq2seq", "t5_base_ch", model_dir="./state_dict/")
model = loader.get_model()
tokenizer = loader.get_tokenizer()


def read_file():
    src = []
    tgt = []

    with open(src_dir, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            src.append(line.strip('\n').lower())

    with open(tgt_dir, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            tgt.append(line.strip('\n').lower())

    return src, tgt


class BertSeq2seqDataset(Dataset):

    def __init__(self,
                 sents_src,
                 sents_tgt,
                 tokenizer,
                 max_src_length=300,
                 max_tgt_length=200):
        super(BertSeq2seqDataset, self).__init__()
        self.sents_src = sents_src
        self.sents_tgt = sents_tgt
        self.tokenizer = tokenizer
        self.max_src_length = max_src_length
        self.max_tgt_length = max_tgt_length
        self.no_block_position = False

    def __getitem__(self, i):
        src = self.sents_src[i]
        tgt = self.sents_tgt[i]

        src_ids = tokenizer.encode_plus(src)['input_ids']
        tgt_ids = tokenizer.encode_plus('[SEP]' + tgt + '[SEP]')['input_ids']

        def length_proc(tokens, max_len=200):
            if len(tokens) <= max_len:
                tokens += [0] * (max_len - len(tokens))
            if len(tokens) > max_len:
                tokens = tokens[:max_len]
            return tokens

        src_ids = length_proc(src_ids, max_len=100)
        tgt_ids = length_proc(tgt_ids, max_len=50)
        output = {}
        output['input_ids'] = torch.LongTensor(src_ids)
        output['decoder_input_ids'] = torch.LongTensor(tgt_ids[:-1])
        output['labels'] = torch.LongTensor(tgt_ids[1:])

        return output

    def __len__(self):

        return len(self.sents_src)


sents_src, sents_tgt = read_file()
data_len = len(sents_tgt)
train_size = int(data_len * 0.8)
train_src = sents_src[:train_size][:2000]
train_tgt = sents_tgt[:train_size][:2000]

val_src = sents_src[train_size:]
val_tgt = sents_tgt[train_size:]

train_dataset = BertSeq2seqDataset(train_src,
                                   train_tgt,
                                   tokenizer=tokenizer,
                                   max_src_length=300,
                                   max_tgt_length=200)
val_dataset = BertSeq2seqDataset(val_src,
                                 val_tgt,
                                 tokenizer=tokenizer,
                                 max_src_length=300,
                                 max_tgt_length=200)

trainer.train(model, train_dataset=train_dataset, valid_dataset=val_dataset)