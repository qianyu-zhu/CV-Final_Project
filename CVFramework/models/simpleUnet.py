from os import name
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class UNet(nn.Module):
    def __init__(self, in_channels=3, out_classes=24):
        super().__init__()
        self.n_channels = in_channels
        self.n_classes = out_classes

        self.double_conv1 = self.double_conv(in_channels, 64)
        self.double_conv2 = self.double_conv(64, 128)
        self.double_conv3 = self.double_conv(128, 256)
        self.double_conv4 = self.double_conv(256, 512)
        self.double_conv5 = self.double_conv(512, 1024)

        self.up_double_conv4 = self.double_conv(1024, 512)
        self.up_double_conv3 = self.double_conv(512, 256)
        self.up_double_conv2 = self.double_conv(256, 128)
        self.up_double_conv1 = self.double_conv(128, 64)

        self.up_conv4 = self.up_conv(1024)
        self.up_conv3 = self.up_conv(512)
        self.up_conv2 = self.up_conv(256)
        self.up_conv1 = self.up_conv(128)

        self.maxpool = nn.MaxPool2d(2)
        # self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)

        self.last_conv = nn.Conv2d(64, out_classes, 1)

    def forward(self, t):
        # print('this is torch size:', t.size())
        t1 = self.double_conv1(t)
        t = self.maxpool(t1)

        t2 = self.double_conv2(t)
        t = self.maxpool(t2)

        t3 = self.double_conv3(t)
        t = self.maxpool(t3)

        t4 = self.double_conv4(t)
        t = self.maxpool(t4)

        t = self.double_conv5(t)

        t = self.up_conv4(t)
        t = self.Up(t4, t)
        t = self.up_double_conv4(t)

        t = self.up_conv3(t)
        t = self.Up(t3, t)
        t = self.up_double_conv3(t)

        t = self.up_conv2(t)
        t = self.Up(t2, t)
        t = self.up_double_conv2(t)

        t = self.up_conv1(t)
        t = self.Up(t1, t)
        t = self.up_double_conv1(t)

        t = self.last_conv(t)

        return t

    def double_conv(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True)
        )

    def up_conv(self, in_channels):
        return nn.ConvTranspose2d(
            in_channels,
            out_channels=in_channels // 2,
            kernel_size=2,
            stride=2
        )

    def Up(self, copy, t):
        th, tw = copy.size()[2:]
        h, w = t.size()[2:]
        diffH = th - h
        diffW = tw - w
        t = F.pad(t, [diffW // 2, diffW - diffW // 2,
                      diffH // 2, diffH - diffH // 2], "constant", 0)
        # print(t.size(), copy.size())
        t = torch.cat([copy, t], dim=1)
        return t


if __name__ == "__main__":
    model = UNet()
    for layer, (name, module) in enumerate(model.named_modules()):
        if isinstance(module, torch.nn.Conv2d):
            print(module)
