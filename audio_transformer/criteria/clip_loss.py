import torch
import clip
import torch
from collections import OrderedDict
import math

class SoundCLIPLoss(torch.nn.Module):

    def __init__(self, opts):
        super(SoundCLIPLoss, self).__init__()
        self.model, self.preprocess = clip.load("ViT-B/32", device="cuda")
        self.upsample = torch.nn.Upsample(scale_factor=7)
        self.avg_pool = torch.nn.AvgPool2d(kernel_size=opts.stylegan_size // 32)

        self.audio_encoder = AudioEncoder()

        self.audio_encoder.load_state_dict(copyStateDict(torch.load("./pretrained_models/resnet18.pth")))

        self.audio_encoder = self.audio_encoder.cuda()
        self.audio_encoder.eval()

    def forward(self, image, audio):
        image = self.avg_pool(self.upsample(image))
        image_features = self.model.encode_image(image).float()
        audio_features = self.audio_encoder(audio).float()

        audio_features = audio_features / audio_features.norm(dim=-1, keepdim=True)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        sim = (image_features @ audio_features.T)[0] * math.exp(0.07)
        loss = 1 - sim
        return loss