# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from torch.optim import Adam, SGD
from torchcrf import CRF
from transformers import BertModel

"""
建立网络模型结构
"""

class TorchModel(nn.Module):
    def __init__(self, config):
        super(TorchModel, self).__init__()
        hidden_size = config["hidden_size"]
        class_num = config["class_num"]
        num_layers = config["num_layers"]

        self.layer = BertModel.from_pretrained(
            config["bert_model"], 
            num_hidden_layers=num_layers,
            return_dict=False)
        hidden_size = self.layer.config.hidden_size # use hidden size from bert model
        self.classify = nn.Linear(hidden_size, class_num) # bert output is mapped to hidden_size, not 2 * hidden_size
        
        self.crf_layer = CRF(class_num, batch_first=True)
        self.use_crf = config["use_crf"]
        self.loss = torch.nn.CrossEntropyLoss(ignore_index=-1)  #loss采用交叉熵损失

    #当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x, target=None):
        x = self.layer(x)[0] #output shape:(batch_size, sen_len, hidden_size)            
        predict = self.classify(x) #ouput:(batch_size, sen_len, num_tags) -> (batch_size * sen_len, num_tags)

        if target is not None:
            if self.use_crf:
                mask = target.gt(-1) 
                return - self.crf_layer(predict, target, mask, reduction="mean")
            else:
                #(number, class_num), (number)
                return self.loss(predict.view(-1, predict.shape[-1]), target.view(-1))
        else:
            if self.use_crf:
                return self.crf_layer.decode(predict)
            else:
                return predict


def choose_optimizer(config, model):
    optimizer = config["optimizer"]
    learning_rate = config["learning_rate"]
    # Regular optimization (all parameters)
    if optimizer == "adam":
        return Adam(model.parameters(), lr=learning_rate)
    elif optimizer == "sgd":
        return torch.optim.SGD(model.parameters(), lr=learning_rate)


if __name__ == "__main__":
    from config import Config
    model = TorchModel(Config)