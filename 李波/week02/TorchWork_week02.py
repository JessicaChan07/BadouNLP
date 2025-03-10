# coding:utf8

import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

"""
week02作业：
基于pytorch框架编写模型训练
实现一个自行构造的找规律(机器学习)任务
五维判断：x是一个5维向量，向量中哪个标量最大就输出哪一维下标
"""


class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        # 5个分类类别
        self.linear = nn.Linear(input_size, 5)  # bias默认是True，截距项框架自动计算
        # self.loss = nn.CrossEntropyLoss()
        self.loss = nn.functional.cross_entropy  # 交叉熵作为损失函数

    # 当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x, y=None):
        y_pred = self.linear(x)  # 通过线性层
        if y is not None:
            return self.loss(y_pred, y)  # 预测值和真实值计算损失
        else:
            return y_pred  # 输出预测结果


# 生成一个样本, 样本的生成方法，代表了我们要学习的规律
# 随机生成一个5维向量，哪个值最大就是哪一类
def build_sample():
    x = np.random.random(5)
    max_index = np.argmax(x)
    return x, max_index


# 随机生成一批样本
def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(X), torch.LongTensor(Y)


# 测试代码
# 用来测试每轮模型的准确率
def evaluate(model):
    model.eval()  # 测试
    test_sample_num = 100
    x, y = build_dataset(test_sample_num)
    correct, wrong = 0, 0
    with torch.no_grad():  # 告诉模型不计算梯度，降低模型计算时间-> with用法
        y_pred = model(x)  # 模型预测 model.forward(x)
        for y_p, y_t in zip(y_pred, y):  # 与真实标签进行对比 y_pred是一个5维向量-[1,2,3,4,5] y是一个索引/类别 0 或 1 或 2 类
            # if np.argmax(y_p) == y_t:
            if torch.argmax(y_p) == int(y_t):
                # print('evaluate.right: y_p=%s\ty_t=%s' % (y_p,y_t))
                correct += 1
            else:
                # print('evaluate.wrong: y_p=%s\ty_t=%s' % (y_p, y_t))
                wrong += 1

    print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)


def main():
    # 配置参数
    epoch_num = 20  # 训练轮数
    batch_size = 20  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    learning_rate = 0.001  # 学习率
    # 建立模型
    model = TorchModel(input_size)
    # 选择优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 创建训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample)  # x代表输入的样本，y代表属于哪一类别
    # 训练过程
    for epoch in range(epoch_num):
        model.train()  # 开始训练
        watch_loss = []  # 记录loss
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size: (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size: (batch_index + 1) * batch_size]
            loss = model(x, y)  # 计算loss  等效于 model.forward(x,y)
            loss.backward()  # 计算梯度
            optim.step()  # 更新权重
            optim.zero_grad()  # 梯度归零
            watch_loss.append(loss.item())
        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # 测试本轮模型结果,验证当前模型效果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "model.bin")
    # 画图
    print('【模型正确概率,损失函数值】->%s' % log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return


# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    model = TorchModel(input_size)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    print(f"模型的权重{model.state_dict()}")

    model.eval()  # 测试模式
    with torch.no_grad():  # 不计算梯度
        # result = model.forward(torch.FloatTensor(input_vec))  # 模型预测
        result = model(torch.FloatTensor(input_vec))
    for vec, res in zip(input_vec, result):
        print("输入：%s, 预测类别：%s, 预测概率值：%s ,真实类别：%s" % (
        vec, torch.argmax(res), res, np.argmax(vec)))  # 打印结果


if __name__ == "__main__":
    main()
    # test_vec = [[0.97889086, 0.15229675, 0.31082123, 0.03504317, 0.88920843],
    #             [0.74963533, 0.5524256, 0.95758807, 0.95520434, 0.84890681],
    #             [0.00797868, 0.67482528, 0.13625847, 0.34675372, 0.19871392],
    #             [0.09349776, 0.59416669, 0.92579291, 0.41567412, 0.1358894]]
    # predict("model.bin", test_vec)
