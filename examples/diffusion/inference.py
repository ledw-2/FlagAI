import sys
sys.path.append("/home/yanzhaodong/test/FlagAI/")
import torch
from flagai.auto_model.auto_loader import AutoLoader
from flagai.model.predictor.predictor import Predictor
import pdb

# Initialize 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


loader = AutoLoader(task_name="text2img", #contrastive learning
                    model_name="AltDiffusion",
                    model_dir="/sharefs/baai-mrnd/yzd/")

model = loader.get_model()
tokenizer = loader.get_tokenizer()
model.eval()
model.to(device)
predictor = Predictor(model, tokenizer)
predictor.predict_generate_images("Anime portrait of natalie portman as an anime girl by stanley artgerm lau, wlop, rossdraws, james jean, andrei riabovitchev, marc simonetti, and sakimichan, trending on artstation")