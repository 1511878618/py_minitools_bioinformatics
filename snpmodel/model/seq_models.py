from . import * 

class TextCNN(nn.Module):
    def __init__(self, vocab, embedding = None, kernel_size = [3, 4, 5], filter_num = 16, dropout=0.2, **kwargs):
        """
        - param:
            - embedding: if "pre" -> pre-train,wiki_word2vec_50, else int will be set as embedding_dim
        """
        super(TextCNN, self).__init__()
        
        if isinstance(embedding, int):
            self.embedding = nn.Embedding(num_embeddings=len(vocab), embedding_dim=embedding, padding_idx=vocab.vocab["<pad>"])
            self.d_m = embedding
        if embedding is None:  # 自定义传入embedding
            self.embedding = None
            self.d_m = len(vocab)
            pass
            
        self.convlution_block = nn.ModuleList([nn.Conv2d(1, filter_num, kernel_size=(i, self.d_m), padding="valid", ) for i in kernel_size ])
        
        self.linear = nn.Linear(filter_num * len(kernel_size), 2)
        self.dropout = nn.Dropout(dropout)
    def forward(self, x):
        tmp_device = x.device  # 由于有的时候device会改变，因为预训练的词向量没有加入到device中
        if self.embedding:
            tmp_device = x.device  # 由于有的时候device会改变，因为预训练的词向量没有加入到device中
            x = self.embedding(x)  #[bn, seqlen] -> [bn, seqlenm d_m]
            x = x.to(tmp_device)
        
        x = x.unsqueeze(1)  # [bn, seqlen, d_m] -> [bn, 1, seqlen, d_m]
        out = []
        for conv in self.convlution_block:
            x_conv = conv(x)
            # print(x.device, x_conv.device)
            x_conv = F.relu(x_conv)
            x_conv = nn.MaxPool2d(x_conv.shape[-2:])(x_conv)  # 使用卷积后的最后两个维度的大小作为池化的大小：[bn, channel, seq_len ,1] ->[bn, channel, 1, 1]，可以修改为avgpool
            out.append(x_conv.flatten(1))  # [bn, channel, 1, 1] -> [bn, channel]
        
        out = torch.cat(out, dim = 1)
        out = self.dropout(out)
        return F.softmax(self.linear(out), -1)
        # return torch.sigmoid(self.linear(out))



def test(net, dataIter, loss, device=try_gpu()):
    net.eval()
    
    test_accumulator = Accumulator(3)  #num, l, TP_TN
    
    iter_batch_num = len(dataIter)
    for _, x, y in dataIter:
        x, y = x.to(device), y.to(device)  # 送到device上
        
        output = net(x)
        
        test_accumulator.add(x.shape[0], loss(output, y.float()).item(), accuracy_score(output.cpu().detach().argmax(-1), y.cpu().detach().argmax(-1), normalize=False))
        
    test_l = test_accumulator[1]/iter_batch_num
    test_acc = test_accumulator[2]/test_accumulator[0]
    return test_l, test_acc


def train(net, train_dataIter, test_dataIter, optim, loss, summary_writer, epochs, savemodel=True, save_path="models", device=try_gpu()):

    net.to(device)
    iter_batch_num = len(train_dataIter)
    modelName = type(net).__name__


    if savemodel:
        model_root_path = os.path.join(save_path, modelName)
        mkdirs(model_root_path)
    for epoch in range(1, epochs + 1):
        net.train()
        t_start = time.time()
        accumulator = Accumulator(3)  # 句子个数, loss, TP+TN
        
        for _, x, y in train_dataIter:
            x, y = x.to(device), y.to(device)  # 送到device上
            optim.zero_grad()  # 梯度归零
            output = net(x)  # forward
            
            l = loss(output, y.float())  # 计算loss
            l.backward()  # 反向梯度计算
            optim.step()  # 梯度更新
            
            # accumulator.add(x.shape[0], l.cpu().detach().item())
            accumulator.add(x.shape[0], l.item(), accuracy_score(output.cpu().detach().argmax(-1), y.cpu().detach().argmax(-1), normalize=False))
            
        t_end = time.time()
        
        #  计算acc loss
        train_loss_epoch = accumulator[1]/iter_batch_num
        train_acc_epoch = accumulator[2]/accumulator[0]
        test_loss, test_acc = test(net, test_dataIter, loss, device)
        #  tensorboard记录 acc loss
        summary_writer.add_scalar(f"{modelName}_train_loss", train_loss_epoch, epoch)
        summary_writer.add_scalar(f"{modelName}_train_acc", train_acc_epoch, epoch)
        summary_writer.add_scalar(f"{modelName}_test_loss", test_loss, epoch)
        summary_writer.add_scalar(f"{modelName}_test_acc", test_acc, epoch)
        
        # save
        if savemodel:
            epoch_model_path = os.path.join(model_root_path, f"{modelName}_{epoch}.pt")
            torch.save(net, epoch_model_path)
        
        #  显示部分输出
        if epoch % 10 == 0:
            print("epoch {} : train: mean loss/per {:.3f} acc is {:.3f} and time is {}review/per sec".format(epoch, train_loss_epoch, train_acc_epoch, accumulator[0]/(t_end - t_start)))
            print(f"test: loss {test_loss:.3f} and acc is {test_acc:.3f}")

        
def predict(dataIter, model, device=try_gpu()):
    out = []
    for x in dataIter:
        x = x.to(device)
        o = model(x).cpu().detach()
        out.append(o)
        
    return torch.concat(out)