import torch, cv2
import numpy as np
import rasterio
from pathlib import Path
from PIL import Image
from transformers import BlipProcessor, BlipForQuestionAnswering, BlipForConditionalGeneration
from peft import PeftModel

# Required imports for BigEarthNet v2.0 model and configilm
import timm
import bigearthnet_encoder
import bigearthnet_common
from reben_publication.BigEarthNetv2_0_ImageClassifier import BigEarthNetv2_0_ImageClassifier
from configilm.extra.BENv2_utils import STANDARD_BANDS, stack_and_interpolate, NEW_LABELS

def load_image(path):
    if path.lower().endswith((".tif", ".tiff")):
        with rasterio.open(path) as src:
            arr = src.read()
            arr = np.transpose(arr, (1, 2, 0))
            arr = arr[:, :, :3] if arr.shape[2] >= 3 else np.repeat(arr, 3, axis=2)
            if arr.dtype != np.uint8:
                arr = arr.astype(np.float32)
                arr = ((arr - arr.min()) / (arr.max() - arr.min() + 1e-6) * 255).astype(np.uint8)
        return Image.fromarray(arr)
    return Image.open(path).convert("RGB")

vqa_base = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
vqa_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
vqa_model = PeftModel.from_pretrained(vqa_base, "../outputs/vqa_adapter")

cap_base = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
cap_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
cap_model = PeftModel.from_pretrained(cap_base, "../outputs/caption_adapter")

# Load the pretrained BigEarthNet v2.0 classifier for Optical-SAR fusion
sar_classifier = BigEarthNetv2_0_ImageClassifier.from_pretrained("hackelle/resnet18-all-v0.1.1")
sar_classifier.eval()

def run_vqa(image_path, query):
    img = load_image(image_path)
    inputs = vqa_processor(img, query, return_tensors="pt")
    out = vqa_model.generate(**inputs, max_new_tokens=30)
    return vqa_processor.decode(out[0], skip_special_tokens=True)

def run_captioning(image_path, query):
    img = load_image(image_path)
    inputs = cap_processor(img, return_tensors="pt")
    out = cap_model.generate(**inputs, max_new_tokens=60)
    return cap_processor.decode(out[0], skip_special_tokens=True)

def run_change_vqa(image1_path, image2_path, query):
    img1 = load_image(image1_path)
    img2 = load_image(image2_path)

    arr1, arr2 = np.array(img1), np.array(img2)
    diff = cv2.absdiff(arr1, arr2)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    cv2.imwrite("../outputs/change_mask.png", thresh)
    change_ratio = np.count_nonzero(thresh) / thresh.size

    cap1_inputs = cap_processor(img1, return_tensors="pt")
    cap2_inputs = cap_processor(img2, return_tensors="pt")
    desc1 = cap_processor.decode(cap_model.generate(**cap1_inputs, max_new_tokens=40)[0], skip_special_tokens=True)
    desc2 = cap_processor.decode(cap_model.generate(**cap2_inputs, max_new_tokens=40)[0], skip_special_tokens=True)

    if change_ratio < 0.01:
        return f"No significant change detected. Before: {desc1}. After: {desc2}."
    else:
        return f"Change detected in approximately {change_ratio*100:.1f}% of the image. Before: {desc1}. After: {desc2}."


def find_band_file(folder: Path, required_band: str, extensions):
    for ext in extensions:
        for file in folder.rglob(f"*{required_band}*.{ext}"):
            if file.is_file():
                return file
    return None


def load_patch(s1_dir: Path, s2_dir: Path, model):
    channels = model.config.channels
    image_size = model.config.image_size

    if channels == 12:
        s2_bands = STANDARD_BANDS[10]
        s1_bands = STANDARD_BANDS[2]
        data = {}
        for band in s2_bands:
            file = find_band_file(s2_dir, band, ["jp2","tif", "tiff"])
            if file is None:
                raise FileNotFoundError(f"Missing S2 band {band} in {s2_dir}")
            with rasterio.open(file) as src:
                data[band] = src.read(1)
        for band in s1_bands:
            file = find_band_file(s2_dir, band, ["tif", "tiff"])
            if file is None:
                raise FileNotFoundError(f"Missing S1 band {band} in {s1_dir}")
            with rasterio.open(file) as src:
                data[band] = src.read(1)
        img = stack_and_interpolate(data, order=s2_bands + s1_bands, img_size=image_size, upsample_mode="nearest")
    else:
        raise ValueError(f"Unsupported model channel count: {channels}")

    return img.unsqueeze(0)


def run_cross_modal_fusion(s1_path, s2_path, query):
    s1_dir = Path(s1_path)
    s2_dir = Path(s2_path)
    
    with torch.no_grad():
        tensor = load_patch(s1_dir, s2_dir, sar_classifier)
        output = sar_classifier(tensor)
        probs = torch.sigmoid(output)[0]
        top_idx = torch.argmax(probs).item()
        predicted_class = NEW_LABELS[top_idx]
        confidence = probs[top_idx].item()
        
    return f"Optical-SAR classification result: '{predicted_class}' (confidence: {confidence:.2f}). Query context: {query}"